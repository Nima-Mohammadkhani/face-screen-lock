import glob
import os
import platform
import subprocess

DEFAULT_MEETING_PROCESS_NAMES = [
    "zoom.us",
    "zoom",
    "cpthost",
    "teams",
    "ms-teams",
    "msteams",
    "microsoft teams",
    "skype",
    "webexmta",
    "webex",
    "cisco webex",
    "gotomeeting",
    "goto",
    "facetime",
    "jitsi",
    "ringcentral",
    "bluejeans",
    "around",
]


def _camera_in_use_linux():
    our_pid = str(os.getpid())
    for dev in glob.glob("/dev/video*"):
        try:
            result = subprocess.run(
                ["fuser", dev],
                capture_output=True,
                text=True,
                timeout=3,
            )
            other_pids = [p for p in result.stdout.split() if p != our_pid]
            if other_pids:
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
            pass
    return False


def is_meeting_active(extra_names=None):
    process_found = False

    try:
        import psutil

        names = set(n.lower() for n in DEFAULT_MEETING_PROCESS_NAMES)
        if extra_names:
            names.update(n.lower() for n in extra_names)

        for proc in psutil.process_iter(["name"]):
            pname = (proc.info.get("name") or "").lower()
            if any(n in pname for n in names):
                process_found = True
                break
    except Exception:
        pass

    if process_found:
        return True

    if platform.system() == "Linux":
        try:
            if _camera_in_use_linux():
                return True
        except Exception:
            pass

    return False


if __name__ == "__main__":
    print("حالت جلسه فعاله؟", is_meeting_active())
