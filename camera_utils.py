import cv2

from i18n import t

CASCADE_PATH = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"


def get_face_detector():
    detector = cv2.CascadeClassifier(CASCADE_PATH)
    if detector.empty():
        raise RuntimeError(t("cascade_load_failed"))
    return detector


def open_camera(index=0):
    cap = cv2.VideoCapture(index)
    if not cap.isOpened():
        raise RuntimeError(t("camera_open_failed", index=index))
    return cap


def detect_faces(gray_frame, detector, min_size=100):
    return detector.detectMultiScale(
        gray_frame,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(min_size, min_size),
    )
