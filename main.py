import cv2
import mediapipe as mp
import numpy as np
import os
import pygame

# =========================
# 1. KONSTANTA & AUDIO
# =========================

HEADER_BUTTON_PATH = os.path.join("assets", "image", "buttons", "Guess The Word.png")
PLAY_BUTTON_PATH   = os.path.join("assets", "image", "buttons", "Play.png")
CAT_BUAH_PATH      = os.path.join("assets", "image", "buttons", "Kategori - Buah.png")
CAT_HEWAN_PATH     = os.path.join("assets", "image", "buttons", "Kategori - Hewan.png")
CAT_KENDARAAN_PATH = os.path.join("assets", "image", "buttons", "Kategori - Kendaraan.png")

# Dummy path audio – nanti kamu ganti ke file asli
BGM_MENU_PATH  = os.path.join("assets", "audio", "BG NCS.mp3")
SFX_CLICK_PATH = os.path.join("assets", "audio", "Button Pressed.mp3")

WINDOW_NAME = "Guess The Word Filter"

STATE_HOME     = "home"
STATE_CATEGORY = "category"
STATE_GAME     = "game"   # nanti dipakai saat permainan dimulai

# Cooldown sentuh tombol biar gak dobel-dobel
HIT_COOLDOWN_MAX = 8
hit_cooldown = 30   # sedikit delay di awal supaya tidak auto-klik PLAY

# =========================
# 1a. INIT AUDIO (pygame)
# =========================

AUDIO_OK = False
bgm_available = False
click_sfx = None

try:
    pygame.mixer.init()
    AUDIO_OK = True

    if os.path.exists(BGM_MENU_PATH):
        pygame.mixer.music.load(BGM_MENU_PATH)
        bgm_available = True
    else:
        print("[AUDIO] File BGM tidak ditemukan (dummy), skip backsong.")

    if os.path.exists(SFX_CLICK_PATH):
        click_sfx = pygame.mixer.Sound(SFX_CLICK_PATH)
    else:
        print("[AUDIO] File SFX click tidak ditemukan (dummy), skip efek klik.")

except Exception as e:
    print("[AUDIO] Gagal inisialisasi audio:", e)
    AUDIO_OK = False


def play_click_sfx():
    if AUDIO_OK and click_sfx is not None:
        click_sfx.play()


def update_bgm_for_state(state):
    """
    HOME + CATEGORY  -> BGM menyala (loop)
    STATE lain (misal GAME) -> BGM mati
    """
    if not (AUDIO_OK and bgm_available):
        return

    if state in (STATE_HOME, STATE_CATEGORY):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)  # loop
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()

# =========================
# 2. FUNGSI BANTUAN GAMBAR
# =========================

def load_button_image(path, size):
    """
    Load gambar tombol (BGRA). Kalau gagal, buat dummy tombol.
    size: (width, height)
    """
    w, h = size
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)

    if img is None:
        # Buat dummy BGRA
        dummy = np.zeros((h, w, 4), dtype=np.uint8)
        dummy[..., :3] = (0, 0, 255)      # merah
        dummy[..., 3] = 255               # alpha penuh
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
    # Kalau tidak ada alpha, tambahkan
    if img.shape[2] == 3:
        bgr = img
        alpha = np.full((h, w, 1), 255, dtype=np.uint8)
        img = np.concatenate([bgr, alpha], axis=2)
    return img


def overlay_png(bg, png, x, y):
    """
    Gambar PNG (BGRA) di atas background (BGR) dengan alpha blending.
    (x, y) = posisi kiri-atas.
    """
    h, w, _ = png.shape

    # Cek batas frame
    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg

    roi = bg[y:y + h, x:x + w]

    bgr = png[..., :3]
    alpha = png[..., 3:] / 255.0  # (h,w,1)

    roi = (alpha * bgr + (1 - alpha) * roi).astype(np.uint8)
    bg[y:y + h, x:x + w] = roi
    return bg


def point_on_png_button(cx, cy, x, y, png):
    """
    Cek apakah titik (cx, cy) menyentuh tombol PNG dan bukan area transparan.
    """
    h, w, _ = png.shape

    if not (x <= cx < x + w and y <= cy < y + h):
        return False

    local_x = cx - x
    local_y = cy - y
    alpha = png[local_y, local_x, 3]
    return alpha > 10
