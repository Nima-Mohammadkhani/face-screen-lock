import platform
import subprocess


def _try_run(cmd):
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return False


def _lock_macos():
    if _try_run(["pmset", "displaysleepnow"]):
        return True

    if _try_run(["open", "-a", "ScreenSaverEngine"]):
        return True

    script = 'tell application "System Events" to keystroke "q" using {control down, command down}'
    if _try_run(["osascript", "-e", script]):
        return True

    cgsession = (
        "/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession"
    )
    if _try_run([cgsession, "-suspend"]):
        return True

    return False


def _lock_windows():
    try:
        import ctypes

        return bool(ctypes.windll.user32.LockWorkStation())
    except Exception:
        return False


def _lock_linux():
    candidates = [
        ["loginctl", "lock-session"],
        ["gnome-screensaver-command", "-l"],
        ["xdg-screensaver", "lock"],
        [
            "dbus-send",
            "--type=method_call",
            "--dest=org.gnome.ScreenSaver",
            "/org/gnome/ScreenSaver",
            "org.gnome.ScreenSaver.Lock",
        ],
        [
            "dbus-send",
            "--type=method_call",
            "--dest=org.freedesktop.ScreenSaver",
            "/org/freedesktop/ScreenSaver",
            "org.freedesktop.ScreenSaver.Lock",
        ],
        ["xscreensaver-command", "-lock"],
        ["cinnamon-screensaver-command", "--lock"],
        ["mate-screensaver-command", "--lock"],
    ]
    for cmd in candidates:
        if _try_run(cmd):
            return True
    return False


def lock_screen():
    system = platform.system()
    if system == "Darwin":
        return _lock_macos()
    if system == "Windows":
        return _lock_windows()
    if system == "Linux":
        return _lock_linux()
    return False


if __name__ == "__main__":
    ok = lock_screen()
    print("قفل شد." if ok else "قفل کردن سیستم ناموفق بود.")
