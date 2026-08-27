import platform
import re
import shutil
import subprocess


def _macos_idle_seconds():
    try:
        out = subprocess.run(
            ["ioreg", "-c", "IOHIDSystem"],
            capture_output=True,
            text=True,
            timeout=3,
        ).stdout
        match = re.search(r'"HIDIdleTime"\s*=\s*(\d+)', out)
        if not match:
            return None
        idle_ns = int(match.group(1))
        return idle_ns / 1_000_000_000
    except Exception:
        return None


def _windows_idle_seconds():
    try:
        import ctypes

        class LASTINPUTINFO(ctypes.Structure):
            _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_uint)]

        info = LASTINPUTINFO()
        info.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if not ctypes.windll.user32.GetLastInputInfo(ctypes.byref(info)):
            return None
        millis_since_boot = ctypes.windll.kernel32.GetTickCount()
        idle_millis = millis_since_boot - info.dwTime
        return idle_millis / 1000.0
    except Exception:
        return None


def _linux_idle_seconds():
    if shutil.which("xprintidle"):
        try:
            out = subprocess.run(
                ["xprintidle"], capture_output=True, text=True, timeout=3
            ).stdout.strip()
            return int(out) / 1000.0
        except Exception:
            pass

    try:
        from Xlib import display

        d = display.Display()
        info = d.screen().root.screensaver_query_info()
        return info.idle / 1000.0
    except Exception:
        return None


def seconds_since_last_input():
    system = platform.system()
    if system == "Darwin":
        return _macos_idle_seconds()
    if system == "Windows":
        return _windows_idle_seconds()
    if system == "Linux":
        return _linux_idle_seconds()
    return None


if __name__ == "__main__":
    idle = seconds_since_last_input()
    if idle is None:
        print("تشخیص فعالیت کیبورد/موس روی این سیستم پشتیبانی نمی‌شه.")
    else:
        print(f"{idle:.1f} ثانیه از آخرین فعالیت کیبورد/موس گذشته.")
