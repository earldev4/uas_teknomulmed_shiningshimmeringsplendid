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

# =========================
# 3. SETUP MEDIAPIPE & KAMERA
# =========================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6,
)

cv2.namedWindow(WINDOW_NAME, cv2.WINDOW_NORMAL)
cv2.setWindowProperty(
    WINDOW_NAME,
    cv2.WND_PROP_FULLSCREEN,
    cv2.WINDOW_FULLSCREEN
)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses.")
    exit()

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# =========================
# 4. LOAD TOMBOL
# =========================

header_btn = load_button_image(HEADER_BUTTON_PATH, size=(400, 100))
play_btn   = load_button_image(PLAY_BUTTON_PATH, size=(260, 100))

CAT_BTN_SIZE = (380, 130)
cat_buah_btn      = load_button_image(CAT_BUAH_PATH, CAT_BTN_SIZE)
cat_hewan_btn     = load_button_image(CAT_HEWAN_PATH, CAT_BTN_SIZE)
cat_kendaraan_btn = load_button_image(CAT_KENDARAAN_PATH, CAT_BTN_SIZE)

# =========================
# 5. STATE GAME
# =========================

state = STATE_HOME
selected_category = None  # "hewan" / "buah" / "kendaraan"

print("Tekan 'q' untuk keluar.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h_frame, w_frame, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    # Kurangi cooldown
    if hit_cooldown > 0:
        hit_cooldown -= 1

    fingertip = None

    # =========================
    # DETEKSI TANGAN & JARI
    # =========================
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2),
            )

            cx = int(hand_landmarks.landmark[8].x * w_frame)
            cy = int(hand_landmarks.landmark[8].y * h_frame)
            fingertip = (cx, cy)

            cv2.circle(frame, (cx, cy), 10, (255, 255, 0), cv2.FILLED)
            break  # pakai 1 tangan saja

    # =========================
    # TAMPILKAN UI BERDASARKAN STATE
    # =========================

    header_x = (w_frame - header_btn.shape[1]) // 2
    header_y = 20

    # ---------- STATE HOME ----------
    if state == STATE_HOME:
        # Header hanya di HOME
        frame = overlay_png(frame, header_btn, header_x, header_y)

        play_x = (w_frame - play_btn.shape[1]) // 2
        play_y = int(h_frame * 0.7)
        frame = overlay_png(frame, play_btn, play_x, play_y)

        if fingertip and hit_cooldown == 0:
            if point_on_png_button(fingertip[0], fingertip[1], play_x, play_y, play_btn):
                play_click_sfx()
                print("[INFO] Play ditekan → masuk menu kategori")
                state = STATE_CATEGORY
                hit_cooldown = HIT_COOLDOWN_MAX

    # ---------- STATE CATEGORY ----------
    elif state == STATE_CATEGORY:
        buttons = [
            ("hewan", cat_hewan_btn),
            ("buah", cat_buah_btn),
            ("kendaraan", cat_kendaraan_btn),
        ]

        total_width = sum(btn.shape[1] for _, btn in buttons) + 60 * (len(buttons) - 1)
        start_x = (w_frame - total_width) // 2
        y = int(h_frame * 0.72)

        x = start_x
        for key, btn_img in buttons:
            frame = overlay_png(frame, btn_img, x, y)

            if fingertip and hit_cooldown == 0:
                if point_on_png_button(fingertip[0], fingertip[1], x, y, btn_img):
                    selected_category = key
                    play_click_sfx()
                    print(f"[INFO] Kategori dipilih: {selected_category}")
                    hit_cooldown = HIT_COOLDOWN_MAX

            x += btn_img.shape[1] + 60

        if selected_category:
            cv2.putText(
                frame,
                f"Terpilih: {selected_category}",
                (40, h_frame - 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1,
                (255, 255, 255),
                2
            )

    # =========================
    # UPDATE BGM & TAMPILKAN FRAME
    # =========================

    update_bgm_for_state(state)

    cv2.imshow(WINDOW_NAME, frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

if AUDIO_OK:
    pygame.mixer.quit()