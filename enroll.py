import os
import sys
import time

import cv2

from camera_utils import get_face_detector, open_camera, detect_faces
from i18n import set_language, t
from monitor_core import FACES_DIR, FACE_SIZE, load_config, train_from_faces_dir
from text_render import put_text

STEP_DEFINITIONS = [
    ("front", "enroll_step_front", 0.30, False),
    ("left", "enroll_step_left", 0.15, False),
    ("right", "enroll_step_right", 0.15, False),
    ("up", "enroll_step_up", 0.15, False),
    ("down", "enroll_step_down", 0.15, False),
    ("lowlight", "enroll_step_lowlight", 0.10, True),
]


def build_steps(total):
    steps = []
    allocated = 0
    for i, (key, instruction_key, ratio, wait_for_key) in enumerate(STEP_DEFINITIONS):
        if i == len(STEP_DEFINITIONS) - 1:
            count = max(total - allocated, 0)
        else:
            count = int(total * ratio)
            allocated += count
        steps.append(
            {
                "key": key,
                "instruction_key": instruction_key,
                "count": count,
                "wait_for_key": wait_for_key,
            }
        )
    return steps


def run_step(cap, detector, config, step, start_index):
    samples_needed = step["count"]
    if samples_needed <= 0:
        return 0

    saved = 0
    last_capture = 0.0
    waiting = step["wait_for_key"]

    while saved < samples_needed:
        ret, frame = cap.read()
        if not ret:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detect_faces(gray, detector, config.get("min_face_size", 100))

        display = frame.copy()
        for (x, y, w, h) in faces:
            cv2.rectangle(display, (x, y), (x + w, y + h), (0, 255, 0), 2)

        put_text(display, t(step["instruction_key"]), (10, 30), 0.7, (0, 255, 255), 2)

        if waiting:
            put_text(display, t("enroll_ready_prompt"), (10, 60), 0.6, (0, 255, 255), 2)
        else:
            put_text(
                display,
                t("enroll_progress", saved=saved, needed=samples_needed),
                (10, 60),
                0.7,
                (0, 255, 0),
                2,
            )

        cv2.imshow("Enroll", display)
        key = cv2.waitKey(1) & 0xFF

        if key == ord("q"):
            raise KeyboardInterrupt

        if waiting:
            if key == ord("c"):
                waiting = False
            elif key == ord("s"):
                return 0
            continue

        now = time.time()
        if len(faces) == 1 and (now - last_capture) > 0.2:
            (x, y, w, h) = faces[0]
            face_img = gray[y : y + h, x : x + w]
            face_img = cv2.resize(face_img, FACE_SIZE)
            fname = os.path.join(FACES_DIR, f"owner_{start_index + saved:03d}.png")
            cv2.imwrite(fname, face_img)
            saved += 1
            last_capture = now

    return saved


def main():
    os.makedirs(FACES_DIR, exist_ok=True)
    config = load_config()
    set_language(config.get("language", "en"))
    detector = get_face_detector()
    cap = open_camera(config.get("camera_index", 0))

    total = config.get("enroll_sample_count", 40)
    steps = build_steps(total)

    print(t("enroll_started"))
    print(t("enroll_follow_instructions"))
    print(t("enroll_quit_hint"))

    total_saved = 0
    try:
        for step in steps:
            saved = run_step(cap, detector, config, step, total_saved)
            total_saved += saved
    except KeyboardInterrupt:
        pass
    except Exception as e:
        import traceback

        print(t("enroll_unexpected_error", error=e))
        traceback.print_exc()
    finally:
        cap.release()
        cv2.destroyAllWindows()

    if total_saved < 10:
        print(t("enroll_too_few_samples", count=total_saved))
        sys.exit(1)

    print(t("enroll_total_saved", count=total_saved))
    train_from_faces_dir()
    print(t("enroll_model_saved"))
    print(t("enroll_next_steps"))


if __name__ == "__main__":
    main()
