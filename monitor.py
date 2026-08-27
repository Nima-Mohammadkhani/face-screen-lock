import argparse
import logging
import time

import cv2

from i18n import t
from monitor_core import MonitorEngine, setup_logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--debug", action="store_true", help="نمایش پنجره‌ی پیش‌نمایش برای تنظیم دقیق‌تر"
    )
    args = parser.parse_args()

    setup_logging()

    try:
        engine = MonitorEngine()
    except RuntimeError as e:
        logging.error(str(e))
        return

    logging.info(
        t("monitoring_started", threshold=engine.away_threshold, interval=engine.check_interval)
    )

    try:
        while True:
            result = engine.tick()

            if args.debug and result.get("frame") is not None:
                display = result["frame"].copy()
                present = result["present"]
                for (x, y, w, h) in result["faces"]:
                    color = (0, 255, 0) if present else (0, 0, 255)
                    cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)
                status = "OWNER" if present else "AWAY"
                cv2.putText(
                    display, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2
                )
                cv2.imshow("Face Screen Lock - debug", display)
                if cv2.waitKey(1) & 0xFF == ord("q"):
                    break

            time.sleep(engine.check_interval)
    except KeyboardInterrupt:
        logging.info(t("monitoring_stopped"))
    finally:
        engine.release_camera()
        if args.debug:
            cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
