import threading

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = ("en", "fa")

_lock = threading.Lock()
_current_language = DEFAULT_LANGUAGE

STRINGS = {
    "model_not_found": {
        "en": "No trained model found. Run './enroll.sh' first.",
        "fa": "مدل آموزش‌دیده پیدا نشد. اول './enroll.sh' را اجرا کنید.",
    },
    "no_training_samples": {
        "en": "No samples found to train on.",
        "fa": "هیچ نمونه‌ای برای آموزش پیدا نشد.",
    },
    "camera_read_failed": {
        "en": "Failed to read a frame from the camera.",
        "fa": "خواندن فریم از دوربین ناموفق بود.",
    },
    "meeting_detected": {
        "en": "A video meeting app was detected; the lock threshold is temporarily increased.",
        "fa": "یه اپ جلسه‌ی ویدیویی شناسایی شد؛ آستانه‌ی قفل موقتاً بیشتر می‌شه.",
    },
    "adaptive_updated": {
        "en": "Model updated with a fresh sample (adaptive learning).",
        "fa": "مدل با یه نمونه‌ی تازه به‌روزرسانی شد (یادگیری تطبیقی).",
    },
    "adaptive_update_failed": {
        "en": "Adaptive model update failed: {error}",
        "fa": "به‌روزرسانی تطبیقی مدل ناموفق بود: {error}",
    },
    "owner_recognized": {
        "en": "Owner recognized.",
        "fa": "صاحب سیستم شناسایی شد.",
    },
    "stranger_face_detected": {
        "en": "A face that does not match the owner was seen; another person may be present.",
        "fa": "صورتی دیده شد که با صاحب سیستم تطبیق ندارد؛ احتمال حضور فرد دیگری.",
    },
    "activity_override_expired": {
        "en": (
            "More than {max_override:.0f}s passed relying only on keyboard/mouse activity "
            "without confirming the owner's face; this override no longer applies and normal "
            "lock behavior resumes."
        ),
        "fa": (
            "بیش از {max_override:.0f} ثانیه فقط با تکیه بر فعالیت کیبورد/موس قفل نشده، بدون "
            "این‌که چهره‌ی صاحب سیستم تأیید بشه؛ این حالت دیگر اعمال نمی‌شود و روال عادی قفل "
            "از سر گرفته می‌شود."
        ),
    },
    "activity_override_active": {
        "en": "No face seen, but keyboard/mouse was recently active; not locking.",
        "fa": "چهره دیده نشد ولی کیبورد/موس به‌تازگی فعال بوده؛ قفل نمی‌شه.",
    },
    "owner_not_recognized": {
        "en": "Owner's face not recognized.",
        "fa": "صورت صاحب سیستم شناسایی نشد.",
    },
    "locking_system": {
        "en": (
            "Owner's face not confirmed for more than {threshold:.0f}s. Locking the system..."
        ),
        "fa": "بیش از {threshold:.0f} ثانیه صورت صاحب سیستم تأیید نشد. در حال قفل کردن سیستم...",
    },
    "lock_command_executed": {
        "en": "Lock command executed.",
        "fa": "دستور قفل کردن سیستم اجرا شد.",
    },
    "lock_command_failed": {
        "en": "Locking the system failed. Check lock_screen.py for your OS.",
        "fa": "قفل کردن سیستم ناموفق بود. lock_screen.py را برای سیستم‌عامل‌تان بررسی کنید.",
    },
    "generic_error": {
        "en": "Error: {error}",
        "fa": "خطا: {error}",
    },

    "cascade_load_failed": {
        "en": "Could not load the Haar Cascade file.",
        "fa": "نتوانستم فایل Haar Cascade را بارگذاری کنم.",
    },
    "camera_open_failed": {
        "en": (
            "Could not open camera index {index}. Check the camera connection and camera "
            "permission (on macOS: System Settings > Privacy & Security > Camera)."
        ),
        "fa": (
            "دوربین با ایندکس {index} باز نشد. اتصال دوربین و مجوز دسترسی به دوربین را بررسی "
            "کنید (در مک: System Settings > Privacy & Security > Camera)."
        ),
    },

    "monitoring_started": {
        "en": "Monitoring started (lock threshold: {threshold}s, check interval: {interval}s).",
        "fa": "مانیتورینگ شروع شد (آستانه‌ی قفل: {threshold} ثانیه، فاصله‌ی بررسی: {interval} ثانیه).",
    },
    "monitoring_stopped": {
        "en": "Monitoring stopped (Ctrl+C).",
        "fa": "مانیتورینگ متوقف شد (Ctrl+C).",
    },

    "menubar_monitoring_started": {
        "en": "Monitoring (menu bar) started.",
        "fa": "مانیتورینگ (نوار منو) شروع شد.",
    },
    "open_settings_failed": {
        "en": "Failed to open the settings window: {error}",
        "fa": "باز کردن پنجره‌ی تنظیمات ناموفق بود: {error}",
    },
    "open_path_failed": {
        "en": "Failed to open {path}: {error}",
        "fa": "باز کردن {path} ناموفق بود: {error}",
    },
    "config_reload_failed": {
        "en": "Failed to reload config.json: {error}",
        "fa": "خواندن دوباره‌ی config.json ناموفق بود: {error}",
    },
    "macos_lock_config_warning": {
        "en": (
            '[macOS] Lock may not work: "Require password immediately after display is turned off" '
            "is OFF in System Settings > Lock Screen. "
            'pmset will only dim the screen, not lock it. '
            'Fix: System Settings > Lock Screen > set password requirement to "Immediately".'
        ),
        "fa": (
            '[macOS] قفل ممکنه کار نکنه: گزینه‌ی "نیاز به رمز عبور فوری بعد از خاموش شدن نمایشگر" '
            "در System Settings > Lock Screen خاموشه. "
            "pmset فقط صفحه رو خاموش می‌کنه ولی سیستم رو قفل نمی‌کنه. "
            'راه‌حل: System Settings > Lock Screen > رمز عبور را روی "Immediately" تنظیم کنید.'
        ),
    },
    "language_changed": {
        "en": "Language changed to {language}.",
        "fa": "زبان به {language} تغییر کرد.",
    },

    "status_checking": {"en": "Status: checking...", "fa": "وضعیت: در حال بررسی..."},
    "status_paused": {"en": "Status: paused", "fa": "وضعیت: مکث‌شده"},
    "status_error": {"en": "Error: {error}", "fa": "خطا: {error}"},
    "status_present": {"en": "Status: present", "fa": "وضعیت: حضور"},
    "status_present_activity_suffix": {
        "en": " (due to keyboard/mouse activity)",
        "fa": " (به‌خاطر فعالیت کیبورد/موس)",
    },
    "status_absent": {"en": "Status: away", "fa": "وضعیت: غایب"},
    "status_stranger_suffix": {
        "en": " — a face other than the owner was seen!",
        "fa": " — صورتی غیر از صاحب سیستم دیده شد!",
    },
    "status_meeting_suffix": {
        "en": " · Meeting mode active",
        "fa": " · حالت جلسه فعال",
    },
    "menu_lock_warning": {
        "en": "macOS lock not configured — click to view log",
        "fa": "قفل macOS پیکربندی نشده — برای مشاهده‌ی لاگ کلیک کنید",
    },
    "menu_pause": {"en": "Pause monitoring", "fa": "مکث مانیتورینگ"},
    "menu_settings": {"en": "Settings...", "fa": "تنظیمات..."},
    "menu_open_config": {
        "en": "Open full settings file...",
        "fa": "باز کردن فایل تنظیمات کامل...",
    },
    "menu_view_log": {"en": "View activity log...", "fa": "مشاهده‌ی لاگ فعالیت..."},
    "menu_language": {"en": "Language", "fa": "زبان"},
    "menu_quit": {"en": "Quit", "fa": "خروج"},

    "settings_title": {"en": "Face Screen Lock Settings", "fa": "تنظیمات Face Screen Lock"},
    "settings_close": {"en": "Close", "fa": "بستن"},
    "tab_basic": {"en": "Basic", "fa": "پایه"},
    "tab_activity": {"en": "Keyboard/Mouse Activity", "fa": "فعالیت کیبورد/موس"},
    "tab_adaptive": {"en": "Adaptive Learning", "fa": "یادگیری تطبیقی"},
    "tab_meeting": {"en": "Meeting Mode", "fa": "حالت جلسه"},
    "field_language": {"en": "Language:", "fa": "زبان:"},
    "field_away_threshold": {
        "en": "Lock after (seconds away):",
        "fa": "زمان قفل (بعد از غیبت):",
    },
    "field_check_interval": {
        "en": "Camera check interval:",
        "fa": "فاصله‌ی بررسی دوربین:",
    },
    "field_sensitivity": {"en": "Face-match sensitivity:", "fa": "حساسیت تشخیص چهره:"},
    "field_lock_cooldown": {
        "en": "Cooldown between consecutive locks:",
        "fa": "فاصله‌ی بین دو قفل پشت‌سرهم:",
    },
    "field_enabled": {"en": "Enabled", "fa": "فعال باشه"},
    "field_activity_grace": {"en": "Recent-activity grace period:", "fa": "مهلت فعالیت اخیر:"},
    "field_activity_override_max": {
        "en": "Max activity override (without face confirmation):",
        "fa": "حداکثر اعتبار فعالیت (بدون تأیید چهره):",
    },
    "field_lock_faster_on_stranger": {
        "en": "Lock faster if a stranger's face is seen",
        "fa": "قفل سریع اگه صورت غریبه دیده بشه",
    },
    "field_unrecognized_face_threshold": {
        "en": "Lock delay when a stranger's face is seen:",
        "fa": "مهلت قفل هنگام دیدن صورت غریبه:",
    },
    "field_adapt_interval": {"en": "Learning interval:", "fa": "فاصله‌ی یادگیری:"},
    "field_adapt_confidence": {"en": "Learning strictness:", "fa": "سخت‌گیری یادگیری:"},
    "field_adapt_max_samples": {
        "en": "Max adaptive samples:",
        "fa": "حداکثر نمونه‌های تطبیقی:",
    },
    "field_meeting_multiplier": {
        "en": "Lock-threshold multiplier during meetings:",
        "fa": "ضریب افزایش زمان قفل حین جلسه:",
    },

    "opt_seconds": {"en": "{v}s", "fa": "{v} ثانیه"},
    "opt_every_seconds": {"en": "every {v}s", "fa": "هر {v} ثانیه"},
    "opt_every_minutes": {"en": "every {v} min", "fa": "هر {v} دقیقه"},
    "opt_samples": {"en": "{v} samples", "fa": "{v} نمونه"},
    "opt_multiplier": {"en": "×{v}", "fa": "×{v}"},
    "opt_sensitivity_strict": {
        "en": "Strict (more accurate, higher risk of not recognizing you)",
        "fa": "سخت‌گیرانه (دقیق‌تر، ریسک نشناختن خودت بیشتر)",
    },
    "opt_sensitivity_medium": {"en": "Medium (default)", "fa": "متوسط (پیش‌فرض)"},
    "opt_sensitivity_relaxed": {
        "en": "Relaxed (higher risk of mistaken match)",
        "fa": "راحت‌تر (ریسک اشتباه‌گرفتن بیشتر)",
    },
    "opt_adapt_very_cautious": {
        "en": "Very cautious (only excellent matches)",
        "fa": "خیلی محتاط (فقط تطبیق‌های عالی)",
    },
    "opt_adapt_cautious": {"en": "Cautious (default)", "fa": "محتاط (پیش‌فرض)"},
    "opt_adapt_relaxed": {"en": "Relaxed", "fa": "راحت‌تر"},

    "enroll_step_front": {
        "en": "Look straight ahead, normal pose",
        "fa": "روبه‌رو نگاه کن، حالت عادی",
    },
    "enroll_step_left": {
        "en": "Turn your head slightly left",
        "fa": "سرت را کمی به چپ بچرخان",
    },
    "enroll_step_right": {
        "en": "Turn your head slightly right",
        "fa": "سرت را کمی به راست بچرخان",
    },
    "enroll_step_up": {"en": "Tilt your head up slightly", "fa": "سرت را کمی بالا ببر"},
    "enroll_step_down": {"en": "Tilt your head down slightly", "fa": "سرت را کمی پایین ببر"},
    "enroll_step_lowlight": {
        "en": "Dim the room lighting if you can (optional)",
        "fa": "اگه می‌تونی نور اتاق را کم‌تر کن (اختیاری)",
    },
    "enroll_ready_prompt": {
        "en": "Ready? Press c. To skip this step press s",
        "fa": "آماده‌ای؟ c را بزن، برای رد کردن این مرحله s را بزن",
    },
    "enroll_progress": {
        "en": "{saved}/{needed}   (q = quit)",
        "fa": "{saved}/{needed}   (q = خروج)",
    },
    "enroll_started": {
        "en": "Guided face enrollment started.",
        "fa": "ثبت هدایت‌شده‌ی چهره شروع شد.",
    },
    "enroll_follow_instructions": {
        "en": "Instructions for each step are shown on the preview; just follow them.",
        "fa": "برای هر مرحله راهنمایی روی خود تصویر نشون داده می‌شه؛ فقط دنبالش کن.",
    },
    "enroll_quit_hint": {
        "en": "Press q at any time to quit early.\n",
        "fa": "در هر لحظه q یعنی خروج زودهنگام.\n",
    },
    "enroll_unexpected_error": {
        "en": "\nUnexpected error during enrollment: {error}",
        "fa": "\nخطای غیرمنتظره حین ثبت: {error}",
    },
    "enroll_too_few_samples": {
        "en": (
            "\nOnly {count} samples were saved, which is too few. Run enroll.py again "
            "and make sure there's enough light and only one face in front of the camera."
        ),
        "fa": (
            "\nفقط {count} نمونه ذخیره شد که خیلی کم است. enroll.py را دوباره اجرا کنید "
            "و مطمئن شوید نور کافی و فقط یک صورت جلوی دوربین است."
        ),
    },
    "enroll_total_saved": {
        "en": "\n{count} samples saved in total. Training the model...",
        "fa": "\n{count} نمونه در مجموع ذخیره شد. در حال آموزش مدل...",
    },
    "enroll_model_saved": {
        "en": "Model saved successfully.",
        "fa": "مدل با موفقیت ذخیره شد.",
    },
    "enroll_next_steps": {
        "en": "You can now run ./monitor.sh or ./run.sh.",
        "fa": "حالا می‌توانید ./monitor.sh یا ./run.sh را اجرا کنید.",
    },
}


def set_language(language):
    global _current_language
    with _lock:
        _current_language = language if language in SUPPORTED_LANGUAGES else DEFAULT_LANGUAGE


def get_language():
    with _lock:
        return _current_language


def t(key, **kwargs):
    entry = STRINGS.get(key)
    if entry is None:
        return key
    template = entry.get(get_language()) or entry.get(DEFAULT_LANGUAGE) or key
    return template.format(**kwargs) if kwargs else template
