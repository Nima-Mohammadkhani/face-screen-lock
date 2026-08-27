import json
import logging
import os
import platform
import subprocess
import time

import cv2
import numpy as np

from activity_utils import seconds_since_last_input
from camera_utils import get_face_detector, open_camera, detect_faces
from config_utils import BASE_DIR, CONFIG_PATH, load_config, save_config
from i18n import set_language, t
from lock_screen import lock_screen
from meeting_utils import is_meeting_active

DATA_DIR = os.path.join(BASE_DIR, "data")
FACES_DIR = os.path.join(DATA_DIR, "faces")
MODEL_PATH = os.path.join(DATA_DIR, "model.yml")
LABELS_PATH = os.path.join(DATA_DIR, "labels.json")
LOG_PATH = os.path.join(DATA_DIR, "activity.log")

OWNER_LABEL = 0
FACE_SIZE = (200, 200)
ADAPTIVE_PREFIX = "adaptive_"


def setup_logging():
    os.makedirs(DATA_DIR, exist_ok=True)
    logging.basicConfig(
        filename=LOG_PATH,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    root = logging.getLogger()
    has_console = any(
        isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler)
        for h in root.handlers
    )
    if not has_console:
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
        root.addHandler(console)


def check_macos_lock_config():
    if platform.system() != "Darwin":
        return True
    try:
        r1 = subprocess.run(
            ["defaults", "-currentHost", "read", "com.apple.screensaver", "askForPassword"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        r2 = subprocess.run(
            ["defaults", "-currentHost", "read", "com.apple.screensaver", "askForPasswordDelay"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        password_required = r1.stdout.strip() == "1"
        delay_immediate = r2.stdout.strip() == "0"
        return password_required and delay_immediate
    except Exception:
        return True


def train_from_faces_dir(faces_dir=FACES_DIR, model_path=MODEL_PATH, labels_path=LABELS_PATH):
    images = []
    labels = []
    for fname in sorted(os.listdir(faces_dir)):
        if not fname.lower().endswith(".png"):
            continue
        img = cv2.imread(os.path.join(faces_dir, fname), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        images.append(img)
        labels.append(OWNER_LABEL)

    if not images:
        raise RuntimeError(t("no_training_samples"))

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(images, np.array(labels))
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    recognizer.save(model_path)

    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump({str(OWNER_LABEL): "owner"}, f, ensure_ascii=False, indent=2)

    return recognizer


class MonitorEngine:

    def __init__(self, config=None):
        if not os.path.exists(MODEL_PATH):
            raise RuntimeError(t("model_not_found"))

        self.config = config if config is not None else load_config()
        set_language(self.config.get("language", "en"))
        self.detector = get_face_detector()
        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.recognizer.read(MODEL_PATH)

        self.macos_lock_ok = check_macos_lock_config()
        if not self.macos_lock_ok:
            logging.warning(t("macos_lock_config_warning"))

        self.away_since = None
        self.last_lock_time = 0.0
        self.was_present = None
        self.cap = None

        self.activity_override_since = None

        self.last_adapt_time = 0.0

        self._meeting_check_time = 0.0
        self._meeting_active_cached = False
        self._meeting_logged = False

    @property
    def check_interval(self):
        return self.config.get("check_interval_seconds", 2)

    @property
    def away_threshold(self):
        return self.config.get("away_seconds_threshold", 15)

    @property
    def lock_cooldown(self):
        return self.config.get("lock_cooldown_seconds", 30)

    def _ensure_camera(self):
        if self.cap is None:
            self.cap = open_camera(self.config.get("camera_index", 0))

    def release_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None

    def find_owner(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray, self.detector, self.config.get("min_face_size", 100))
        present = False
        best_confidence = None
        best_face_img = None
        for (x, y, w, h) in faces:
            face_img = cv2.resize(gray[y : y + h, x : x + w], FACE_SIZE)
            label, confidence = self.recognizer.predict(face_img)
            if label == OWNER_LABEL and confidence < self.config.get("confidence_threshold", 70):
                present = True
                if best_confidence is None or confidence < best_confidence:
                    best_confidence = confidence
                    best_face_img = face_img
        return present, faces, best_confidence, best_face_img

    def _meeting_active(self):
        if not self.config.get("meeting_mode_enabled", True):
            self._meeting_logged = False
            return False

        now = time.time()
        if now - self._meeting_check_time > 10:
            self._meeting_check_time = now
            self._meeting_active_cached = is_meeting_active(self.config.get("meeting_app_names"))

        if self._meeting_active_cached:
            if not self._meeting_logged:
                logging.info(t("meeting_detected"))
                self._meeting_logged = True
        else:
            self._meeting_logged = False

        return self._meeting_active_cached

    def _effective_away_threshold(self):
        if self._meeting_active():
            multiplier = self.config.get("meeting_mode_multiplier", 3)
            return self.away_threshold * multiplier
        return self.away_threshold

    def _maybe_adapt(self, confidence, face_img):
        if not self.config.get("adaptive_learning", True):
            return
        if confidence is None or face_img is None:
            return

        threshold = self.config.get("adaptive_learning_confidence_threshold", 40)
        if confidence >= threshold:
            return

        interval = self.config.get("adaptive_learning_interval_minutes", 10) * 60
        now = time.time()
        if now - self.last_adapt_time < interval:
            return
        self.last_adapt_time = now

        try:
            os.makedirs(FACES_DIR, exist_ok=True)
            fname = f"{ADAPTIVE_PREFIX}{int(now * 1000)}.png"
            cv2.imwrite(os.path.join(FACES_DIR, fname), face_img)
            self._prune_adaptive_samples()
            self.recognizer = train_from_faces_dir()
            logging.info(t("adaptive_updated"))
        except Exception as e:
            logging.error(t("adaptive_update_failed", error=e))

    def _prune_adaptive_samples(self):
        max_samples = self.config.get("adaptive_learning_max_samples", 80)
        files = sorted(
            (f for f in os.listdir(FACES_DIR) if f.startswith(ADAPTIVE_PREFIX)),
            key=lambda f: os.path.getmtime(os.path.join(FACES_DIR, f)),
        )
        excess = len(files) - max_samples
        for f in files[: max(0, excess)]:
            try:
                os.remove(os.path.join(FACES_DIR, f))
            except OSError:
                pass

    def tick(self):
        result = {
            "present": None,
            "faces": [],
            "frame": None,
            "locked": False,
            "error": None,
            "activity_override": False,
            "meeting_active": False,
            "stranger_detected": False,
        }
        try:
            self._ensure_camera()
            ret, frame = self.cap.read()
            if not ret:
                raise RuntimeError(t("camera_read_failed"))

            present, faces, best_confidence, best_face_img = self.find_owner(frame)
            result["faces"] = faces
            result["frame"] = frame
            result["meeting_active"] = self._meeting_active()
            now = time.time()

            if present:
                if self.was_present is False:
                    logging.info(t("owner_recognized"))
                self.away_since = None
                self.was_present = True
                self.activity_override_since = None
                result["present"] = True
                self._maybe_adapt(best_confidence, best_face_img)
            else:
                stranger_detected = len(faces) > 0
                result["stranger_detected"] = stranger_detected

                activity_override = False
                if self.config.get("require_activity_check", True) and not stranger_detected:
                    idle = seconds_since_last_input()
                    grace = self.config.get("activity_grace_seconds", 5)
                    if idle is not None and idle < grace:
                        activity_override = True

                if activity_override:
                    if self.activity_override_since is None:
                        self.activity_override_since = now
                    override_elapsed = now - self.activity_override_since
                    max_override = self.config.get("activity_override_max_seconds", 120)
                    if override_elapsed > max_override:
                        logging.warning(t("activity_override_expired", max_override=max_override))
                        activity_override = False
                else:
                    self.activity_override_since = None

                if stranger_detected and self.was_present is not False:
                    logging.warning(t("stranger_face_detected"))

                if activity_override:
                    if self.was_present is not True:
                        logging.info(t("activity_override_active"))
                    self.away_since = None
                    self.was_present = True
                    result["present"] = True
                    result["activity_override"] = True
                else:
                    if self.was_present is not False:
                        logging.info(t("owner_not_recognized"))
                    self.was_present = False
                    result["present"] = False
                    if self.away_since is None:
                        self.away_since = now
                    elapsed = now - self.away_since
                    effective_threshold = self._effective_away_threshold()
                    if stranger_detected and self.config.get(
                        "lock_faster_on_unrecognized_face", True
                    ):
                        effective_threshold = min(
                            effective_threshold,
                            self.config.get("unrecognized_face_seconds_threshold", 5),
                        )
                    if (
                        elapsed >= effective_threshold
                        and (now - self.last_lock_time) >= self.lock_cooldown
                    ):
                        logging.warning(t("locking_system", threshold=effective_threshold))
                        ok = lock_screen()
                        self.last_lock_time = now
                        result["locked"] = ok
                        if ok:
                            logging.info(t("lock_command_executed"))
                        else:
                            logging.error(t("lock_command_failed"))
        except Exception as e:
            logging.error(t("generic_error", error=e))
            result["error"] = str(e)
            self.release_camera()
            time.sleep(3)

        return result
