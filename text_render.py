import functools
import os
import platform

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

_FONT_CANDIDATES = {
    "Darwin": [
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
        "/System/Library/Fonts/Supplemental/Tahoma.ttf",
        "/Library/Fonts/Arial Unicode.ttf",
    ],
    "Windows": [
        r"C:\Windows\Fonts\tahoma.ttf",
        r"C:\Windows\Fonts\arial.ttf",
        r"C:\Windows\Fonts\segoeui.ttf",
    ],
    "Linux": [
        "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
}


@functools.lru_cache(maxsize=None)
def _find_font_path():
    for path in _FONT_CANDIDATES.get(platform.system(), []):
        if os.path.exists(path):
            return path
    return None


@functools.lru_cache(maxsize=None)
def _load_font(size):
    path = _find_font_path()
    if path is None:
        return None
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return None


def _shape_bidi(text):
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        return get_display(arabic_reshaper.reshape(text))
    except Exception:
        return text


def put_text(frame, text, org, font_scale=0.7, color=(0, 255, 255), thickness=2):
    font = _load_font(max(int(round(24 * font_scale / 0.7)), 10))
    if font is None:
        cv2.putText(
            frame, text, org, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness
        )
        return frame

    display_text = _shape_bidi(text)

    img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    x, y = org
    bbox = draw.textbbox((0, 0), display_text, font=font)
    draw.text(
        (x, y - (bbox[3] - bbox[1]) - bbox[1]),
        display_text,
        font=font,
        fill=(color[2], color[1], color[0]),
    )
    frame[:, :, :] = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    return frame
