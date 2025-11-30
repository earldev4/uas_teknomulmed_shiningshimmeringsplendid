import os
import cv2
import numpy as np

from .config import ANSWER_BUTTONS_DIR

# =========================
# FUNGSI GRAFIS & BUTTON
# =========================

def load_button_image(path, size):
    w, h = size
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if img is None:
        dummy = np.zeros((h, w, 4), dtype=np.uint8)
        dummy[..., :3] = (0, 0, 255)
        dummy[..., 3] = 255
        cv2.putText(
            dummy,
            "BTN",
            (10, int(h * 0.65)),
            cv2.FONT_HERSHEY_DUPLEX,
            1,
            (255, 255, 255, 255),
            2,
            cv2.LINE_AA,
        )
        return dummy

    img = cv2.resize(img, (w, h))
    if img.shape[2] == 3:
        bgr = img
        alpha = np.full((h, w, 1), 255, dtype=np.uint8)
        img = np.concatenate([bgr, alpha], axis=2)
    return img


def overlay_png(bg, png, x, y):
    h, w, _ = png.shape

    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg

    roi = bg[y:y + h, x:x + w]

    bgr = png[..., :3]
    alpha = png[..., 3:] / 255.0

    roi = (alpha * bgr + (1 - alpha) * roi).astype(np.uint8)
    bg[y:y + h, x:x + w] = roi
    return bg


def point_on_png_button(cx, cy, x, y, png):
    h, w, _ = png.shape

    if not (x <= cx < x + w and y <= cy < y + h):
        return False

    local_x = cx - x
    local_y = cy - y
    alpha = png[local_y, local_x, 3]
    return alpha > 10


def draw_button_with_effect(frame, btn_img, base_x, base_y, fingertip,
                            press_offset=8):
    """
    Gambar tombol. Kalau jari menyentuh tombol, tombol digambar sedikit
    lebih atas (press_offset pixel).
    Hitbox tetap di posisi base_x, base_y.
    """
    y_draw = base_y
    if fingertip is not None:
        if point_on_png_button(fingertip[0], fingertip[1], base_x, base_y, btn_img):
            y_draw = base_y - press_offset  # efek naik

    frame = overlay_png(frame, btn_img, base_x, y_draw)
    return frame


def put_text_with_outline(
    img,
    text,
    org,
    font,
    font_scale,
    color,
    thickness,
    outline_color=(0, 0, 0),
    outline_thickness=None
):
    x, y = org
    if outline_thickness is None:
        outline_thickness = thickness + 2

    for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
        cv2.putText(
            img,
            text,
            (x + dx, y + dy),
            font,
            font_scale,
            outline_color,
            outline_thickness,
            cv2.LINE_AA,
        )
    cv2.putText(
        img,
        text,
        (x, y),
        font,
        font_scale,
        color,
        thickness,
        cv2.LINE_AA,
    )
    return img


def load_all_answer_assets():
    all_assets = {
        "hewan": [],
        "buah": [],
        "kendaraan": []
    }

    if not os.path.isdir(ANSWER_BUTTONS_DIR):
        print("[ASSET] Folder tombol jawaban tidak ditemukan:", ANSWER_BUTTONS_DIR)
        return all_assets

    for fname in os.listdir(ANSWER_BUTTONS_DIR):
        if not fname.lower().endswith(".png"):
            continue

        name_no_ext = os.path.splitext(fname)[0]
        parts = name_no_ext.split("-")
        if len(parts) < 2:
            continue

        cat_label = parts[0].strip().lower()
        word = parts[1].strip().lower()

        if cat_label in all_assets:
            path = os.path.join(ANSWER_BUTTONS_DIR, fname)
            img = load_button_image(path, (290, 95))
            all_assets[cat_label].append({
                "word": word,
                "img": img
            })

    for k, v in all_assets.items():
        print(f"[ASSET] Kategori {k} punya {len(v)} tombol jawaban.")
    return all_assets
