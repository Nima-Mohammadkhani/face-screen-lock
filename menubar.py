import logging
import os
import platform
import subprocess
import sys
import threading
import time

import pystray
from PIL import Image, ImageDraw

from i18n import set_language, t
from monitor_core import (
    BASE_DIR,
    CONFIG_PATH,
    LOG_PATH,
    MonitorEngine,
    load_config,
    save_config,
    setup_logging,
)

STATE_LOCK = threading.Lock()
STATE = {
    "present": None,
    "paused": False,
    "error": None,
    "activity_override": False,
    "meeting_active": False,
    "stranger_detected": False,
    "lock_warning": False,
}

stop_event = threading.Event()

COLOR_PRESENT = (52, 199, 89, 255)
COLOR_AWAY = (255, 149, 0, 255)
COLOR_STRANGER = (139, 0, 0, 255)
COLOR_PAUSED = (142, 142, 147, 255)
COLOR_UNKNOWN = (0, 122, 255, 255)
COLOR_ERROR = (255, 59, 48, 255)

SETTINGS_SCRIPT_PATH = os.path.join(BASE_DIR, "settings_window.py")

config = load_config()
set_language(config.get("language", "en"))
_config_mtime = os.path.getmtime(CONFIG_PATH) if os.path.exists(CONFIG_PATH) else 0.0


def status_text(item=None):
    with STATE_LOCK:
        if STATE["error"]:
            return t("status_error", error=STATE["error"])
        if STATE["paused"]:
            return t("status_paused")

        if STATE["present"] is True:
            base = t("status_present")
            if STATE["activity_override"]:
                base += t("status_present_activity_suffix")
        elif STATE["present"] is False:
            base = t("status_absent")
            if STATE["stranger_detected"]:
                base += t("status_stranger_suffix")
        else:
            return t("status_checking")

        if STATE["meeting_active"]:
            base += t("status_meeting_suffix")
        return base


def make_icon_image(color):
    size = 64
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    margin = 10
    draw.ellipse([margin, margin, size - margin, size - margin], fill=color)
    return img


def current_icon_image():
    with STATE_LOCK:
        if STATE["error"]:
            return make_icon_image(COLOR_ERROR)
        if STATE["paused"]:
            return make_icon_image(COLOR_PAUSED)
        if STATE["present"] is True:
            return make_icon_image(COLOR_PRESENT)
        if STATE["present"] is False:
            if STATE["stranger_detected"]:
                return make_icon_image(COLOR_STRANGER)
            return make_icon_image(COLOR_AWAY)
        return make_icon_image(COLOR_UNKNOWN)


def is_paused(item=None):
    with STATE_LOCK:
        return STATE["paused"]


def toggle_pause(icon, item):
    with STATE_LOCK:
        STATE["paused"] = not STATE["paused"]
    icon.icon = current_icon_image()
    icon.update_menu()


def quit_app(icon, item):
    stop_event.set()
    icon.stop()


def open_settings_window(icon, item):
    try:
        subprocess.Popen([sys.executable, SETTINGS_SCRIPT_PATH])
    except Exception as e:
        logging.error(t("open_settings_failed", error=e))


def open_path(path):
    try:
        system = platform.system()
        if system == "Darwin":
            subprocess.run(["open", path])
        elif system == "Windows":
            os.startfile(path)  # noqa: S606
        else:
            subprocess.run(["xdg-open", path])
    except Exception as e:
        logging.error(t("open_path_failed", path=path, error=e))


def make_language_setter(language):
    def handler(icon, item):
        config["language"] = language
        save_config(config)
        set_language(language)
        logging.info(t("language_changed", language=language))
        icon.update_menu()

    return handler


def language_checker(language):
    def checker(item):
        return config.get("language", "en") == language

    return checker


def build_language_menu():
    return pystray.Menu(
        pystray.MenuItem(
            "English", make_language_setter("en"), radio=True, checked=language_checker("en")
        ),
        pystray.MenuItem(
            "فارسی", make_language_setter("fa"), radio=True, checked=language_checker("fa")
        ),
    )


def _reload_config_if_changed():
    global _config_mtime
    try:
        mtime = os.path.getmtime(CONFIG_PATH)
    except OSError:
        return
    if mtime == _config_mtime:
        return
    _config_mtime = mtime
    try:
        fresh = load_config()
    except Exception as e:
        logging.error(t("config_reload_failed", error=e))
        return
    config.clear()
    config.update(fresh)
    set_language(config.get("language", "en"))


def monitor_thread_func(icon, engine):
    if engine is None:
        while not stop_event.is_set():
            time.sleep(1)
        return

    logging.info(t("menubar_monitoring_started"))

    while not stop_event.is_set():
        _reload_config_if_changed()

        with STATE_LOCK:
            paused = STATE["paused"]

        if paused:
            time.sleep(1)
            continue

        result = engine.tick()
        with STATE_LOCK:
            if result["present"] is not None:
                STATE["present"] = result["present"]
            STATE["error"] = result["error"]
            STATE["activity_override"] = result["activity_override"]
            STATE["meeting_active"] = result["meeting_active"]
            STATE["stranger_detected"] = result["stranger_detected"]

        icon.icon = current_icon_image()
        time.sleep(engine.check_interval)

    engine.release_camera()


def setup(icon):
    icon.visible = True

    try:
        engine = MonitorEngine(config)
        with STATE_LOCK:
            STATE["lock_warning"] = not engine.macos_lock_ok
        if STATE["lock_warning"]:
            icon.update_menu()
    except RuntimeError as e:
        logging.error(str(e))
        with STATE_LOCK:
            STATE["error"] = str(e)
        icon.icon = current_icon_image()
        icon.update_menu()
        engine = None

    thread = threading.Thread(target=monitor_thread_func, args=(icon, engine), daemon=True)
    thread.start()


def _lock_warning_visible(item):
    with STATE_LOCK:
        return STATE.get("lock_warning", False)


def build_menu():
    return pystray.Menu(
        pystray.MenuItem(
            lambda item: t("menu_lock_warning"),
            lambda icon, item: open_path(LOG_PATH),
            visible=_lock_warning_visible,
        ),
        pystray.MenuItem(status_text, None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: t("menu_pause"), toggle_pause, checked=is_paused),
        pystray.MenuItem(lambda item: t("menu_settings"), open_settings_window),
        pystray.MenuItem(lambda item: t("menu_language"), build_language_menu()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(
            lambda item: t("menu_open_config"), lambda icon, item: open_path(CONFIG_PATH)
        ),
        pystray.MenuItem(
            lambda item: t("menu_view_log"), lambda icon, item: open_path(LOG_PATH)
        ),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(lambda item: t("menu_quit"), quit_app),
    )


def main():
    setup_logging()

    icon = pystray.Icon("face-screen-lock", current_icon_image(), "Face Screen Lock", build_menu())
    icon.run(setup=setup)


if __name__ == "__main__":
    main()
