<div align="center">

# 🔒 Face Screen Lock 🔒

### *Automatically locks your screen when you step away — powered by real-time facial recognition*

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB.svg?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-LBPH-5C3EE8.svg?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![Platform](https://img.shields.io/badge/Platform-Win%20%7C%20Mac%20%7C%20Linux-lightgrey.svg?style=for-the-badge&logo=linux&logoColor=white)]()
[![i18n](https://img.shields.io/badge/i18n-EN%20%2F%20FA-FF6B6B.svg?style=for-the-badge&logo=googletranslate&logoColor=white)]()
[![License](https://img.shields.io/badge/License-Educational-22C55E.svg?style=for-the-badge)]()

---

</div>

## Features

**Smart Face Recognition**
- Trains a personal LBPH model from your own face samples (one-time enrollment)
- Detects and recognizes your face every few seconds via webcam
- Locks the screen automatically when you've been away too long
- No heavy dependencies like `dlib` — pure `opencv-contrib-python`

**Adaptive Learning**
- Automatically updates the model as your appearance gradually changes (new beard, glasses, seasonal lighting)
- Retrains in the background when a high-confidence match is detected
- No need to re-enroll for gradual changes — only for drastic ones

**Activity Awareness**
- Won't lock while you're actively typing or moving the mouse
- Cross-platform idle detection: `ioreg` on macOS, `GetLastInputInfo` on Windows, `xprintidle` on Linux
- Configurable grace period and a security ceiling to prevent bypass by prolonged typing

**Stranger Detection**
- Detects faces that don't match the owner and locks faster
- Overrides activity-based lock prevention when an unrecognized face is visible
- Configurable separate timeout for stranger-triggered locking

**Meeting Mode**
- Detects running meeting apps (Zoom, Teams, Skype, Webex, GoToMeeting) via process list
- Multiplies the lock timeout during active meetings to account for natural gaze shifts
- Add custom app names for unlisted meeting software

**Bilingual UI (English / Persian)**
- Full Persian (فارسی) and English support across menu, settings window, and logs
- Right-to-left (RTL) layout support for Persian
- Switch languages at runtime — no restart required

**System Tray Status Icon**
- 🟢 Green — owner detected
- 🟠 Orange — away (within grace period before locking)
- 🔴 Dark red — unrecognized face detected (fast-lock mode)
- ⚫ Gray — monitoring paused
- 🔵 Blue — starting up
- 🔴 Red — error (camera unavailable or model missing)

## Tech Stack

<div align="center">

![Python](https://img.shields.io/badge/-Python_3.9+-3776AB?style=flat-square&logo=python&logoColor=white)
![OpenCV](https://img.shields.io/badge/-OpenCV_contrib-5C3EE8?style=flat-square&logo=opencv&logoColor=white)
![NumPy](https://img.shields.io/badge/-NumPy-013243?style=flat-square&logo=numpy&logoColor=white)
![pystray](https://img.shields.io/badge/-pystray-555555?style=flat-square&logo=python&logoColor=white)

![Pillow](https://img.shields.io/badge/-Pillow-FFD43B?style=flat-square&logo=python&logoColor=black)
![Tkinter](https://img.shields.io/badge/-Tkinter-3776AB?style=flat-square&logo=python&logoColor=white)
![psutil](https://img.shields.io/badge/-psutil-22C55E?style=flat-square&logo=python&logoColor=white)
![arabic-reshaper](https://img.shields.io/badge/-arabic--reshaper-FF6B6B?style=flat-square&logo=googletranslate&logoColor=white)
![python-bidi](https://img.shields.io/badge/-python--bidi-FF6B6B?style=flat-square&logo=googletranslate&logoColor=white)

</div>

## Project Structure

```
face-screen-lock/
├── monitor.py               # Entry point — headless monitoring (--debug for live preview)
├── monitor_core.py          # MonitorEngine: main loop, face detection & locking logic
├── enroll.py                # Guided face enrollment wizard (run once)
├── menubar.py               # System tray icon, menu, threading, config hot-reload
├── settings_window.py       # Tkinter settings GUI (4 tabs)
│
├── camera_utils.py          # Webcam open + Haar Cascade face detection
├── activity_utils.py        # Cross-platform keyboard/mouse idle detection
├── lock_screen.py           # OS-specific screen lock commands
├── meeting_utils.py         # Meeting app detection via psutil
├── i18n.py                  # Bilingual string table (EN / FA)
├── text_render.py           # Persian/Arabic RTL text renderer (Pillow + reshaper)
├── config_utils.py          # config.json load/save
│
├── config.json              # User configuration
├── requirements.txt         # Python dependencies
├── run.sh                   # Launch menubar (system tray icon)
├── monitor.sh               # Launch headless monitor
├── enroll.sh                # Launch enrollment wizard
│
└── data/
    ├── model.yml            # Trained LBPH model (~5 MB)
    ├── labels.json          # Face label mappings
    └── activity.log         # Detection and lock event log
```

## Quick Start

### 1. Install Dependencies

```bash
# Inside a virtualenv (recommended)
pip install -r requirements.txt
```

> **macOS:** Do **not** use Apple's system Python (`/usr/bin/python3`) — it ships with an ancient Tcl/Tk 8.5 that crashes the settings window. Use a modern Python via Homebrew:
> ```bash
> brew install python@3.12 python-tk@3.12
> python3.12 -m venv .venv
> .venv/bin/python -m pip install -r requirements.txt
> ```

> **Linux:** If `tkinter` is missing, install it with your package manager:
> ```bash
> sudo apt install python3-tk   # Debian/Ubuntu
> ```

### 2. Enroll Your Face (once)

```bash
./enroll.sh
```

A guided wizard opens and walks you through 6 steps:

1. Face forward — normal position
2. Slight left turn
3. Slight right turn
4. Slightly up
5. Slightly down
6. *(Optional)* Low-light — press `c` when ready, `s` to skip

After all steps, the model trains automatically and saves to `data/model.yml`.

### 3. Start Monitoring

```bash
./run.sh          # System tray icon (recommended)
./monitor.sh      # Headless (no icon)
./monitor.sh --debug   # With live camera preview window
```

> **macOS:** Go to **System Settings → Lock Screen** and set *"Require password after screen saver begins or display is turned off"* to **Immediately** — otherwise the screen turns off but doesn't actually lock.

## Configuration (`config.json`)

| Key | Description | Default |
|-----|-------------|---------|
| `language` | UI language: `"en"` or `"fa"` | `"en"` |
| `camera_index` | Which camera to use (0 = first) | `0` |
| `check_interval_seconds` | How often to capture a frame | `2` |
| `away_seconds_threshold` | Lock after N seconds without owner face | `15` |
| `lock_cooldown_seconds` | Minimum gap between consecutive locks | `30` |
| `confidence_threshold` | LBPH match sensitivity — lower = stricter | `70` |
| `require_activity_check` | Skip lock while actively typing/moving mouse | `true` |
| `activity_grace_seconds` | "Recent" activity window in seconds | `5` |
| `activity_override_max_seconds` | Security ceiling: max seconds activity alone can delay lock | `120` |
| `lock_faster_on_unrecognized_face` | Fast-lock when a stranger's face is detected | `true` |
| `unrecognized_face_seconds_threshold` | Lock timeout when stranger detected | `5` |
| `adaptive_learning` | Auto-update model from high-confidence detections | `true` |
| `adaptive_learning_interval_minutes` | Min gap between adaptive retrains | `10` |
| `adaptive_learning_confidence_threshold` | Confidence required to accept a sample | `40` |
| `adaptive_learning_max_samples` | Max adaptive samples kept (oldest pruned) | `80` |
| `meeting_mode_enabled` | Extend lock timeout during meeting apps | `true` |
| `meeting_mode_multiplier` | Multiply lock threshold by this during meetings | `3` |
| `meeting_app_names` | Extra process names to treat as meeting apps | `[]` |

Most settings can be changed live from the **Settings window** (menu → Settings…) without editing the file manually. The monitor picks up changes immediately.

## Auto-Start at Boot

### macOS — LaunchAgent

Create `~/Library/LaunchAgents/com.nima.facelock.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>          <string>com.nima.facelock</string>
  <key>ProgramArguments</key>
  <array>
    <string>/full/path/to/face-screen-lock/run.sh</string>
  </array>
  <key>RunAtLoad</key>      <true/>
  <key>KeepAlive</key>      <true/>
  <key>StandardOutPath</key>
  <string>/full/path/to/face-screen-lock/data/launchd.log</string>
  <key>StandardErrorPath</key>
  <string>/full/path/to/face-screen-lock/data/launchd.err</string>
</dict>
</plist>
```

```bash
launchctl load ~/Library/LaunchAgents/com.nima.facelock.plist
# To stop:
launchctl unload ~/Library/LaunchAgents/com.nima.facelock.plist
```

### Windows — Task Scheduler

1. Open Task Scheduler → **Create Task**
2. **General:** name it `FaceLock`, keep *"Run only when user is logged on"* (camera needs an active session)
3. **Triggers → New:** Begin the task: **At log on**
4. **Actions → New:** Program: `.venv\Scripts\pythonw.exe` · Arguments: full path to `monitor.py` · Start in: project folder
5. Save — no admin password needed

Simpler alternative: place a shortcut to `pythonw.exe "C:\path\face-screen-lock\monitor.py"` in `shell:startup`.

### Linux — systemd user service

Create `~/.config/systemd/user/facelock.service`:

```ini
[Unit]
Description=Face Lock Monitor

[Service]
ExecStart=/full/path/to/face-screen-lock/run.sh
Restart=on-failure
Environment=DISPLAY=:0

[Install]
WantedBy=default.target
```

```bash
systemctl --user daemon-reload
systemctl --user enable --now facelock.service
```

## Implementation Notes

**LBPH Face Recognition**
- Lightweight OpenCV algorithm — no GPU, no `dlib`, no compilation required
- Works well for personal/office use; not suitable as a primary security layer
- Degrades in very low light or extreme angles — cover these during enrollment

**Adaptive Learning**
- New samples saved with UNIX timestamp in filename (`adaptive_1234567890.png`)
- Oldest adaptive samples auto-pruned when limit is reached
- Original enrollment samples (`owner_*.png`) are never deleted

**Security Design**
- Activity-based lock delay has a hard ceiling (`activity_override_max_seconds`) to prevent bypass by prolonged typing
- Stranger detection overrides the activity exception entirely — even if the keyboard is active
- Face images stored locally in `data/faces/` — never transmitted anywhere

**Cross-Platform Locking**
- **Windows:** `LockWorkStation()` via `ctypes` — always works, no permissions needed
- **macOS:** `pmset displaysleepnow` — requires "Require password immediately" in System Settings
- **Linux:** tries `loginctl lock-session` → `gnome-screensaver-command` → `xdg-screensaver` → `dbus-send` → `xscreensaver-command` in order

**Known Limitations**
- If Zoom/Teams uses the same webcam, frame capture fails silently (logs the error, does **not** lock — safe but unmonitored until the camera is free)
- Meeting detection is process-name based, not call-state based — Zoom open but idle still activates meeting mode
- Browser-based meetings (Google Meet in Chrome) cannot be detected — only standalone apps

## License

This project is for educational and personal use. For commercial deployment, configure identifiers and service keys according to your organization's requirements.

---
