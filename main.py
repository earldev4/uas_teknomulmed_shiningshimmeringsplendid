import cv2
import mediapipe as mp
import numpy as np
import os
import pygame
import random
import time

# =========================
# 1. KONSTANTA & PATH ASSET
# =========================

HEADER_BUTTON_PATH = os.path.join("assets", "image", "buttons", "Guess The Word.png")
PLAY_BUTTON_PATH   = os.path.join("assets", "image", "buttons", "Play.png")
CAT_BUAH_PATH      = os.path.join("assets", "image", "buttons", "Kategori - Buah.png")
CAT_HEWAN_PATH     = os.path.join("assets", "image", "buttons", "Kategori - Hewan.png")
CAT_KENDARAAN_PATH = os.path.join("assets", "image", "buttons", "Kategori - Kendaraan.png")

# Button jawaban (asset PNG, nanti sesuaikan nama file)
ANS_A_PATH = os.path.join("assets", "image", "buttons", "Answer - A.png")
ANS_B_PATH = os.path.join("assets", "image", "buttons", "Answer - B.png")
ANS_C_PATH = os.path.join("assets", "image", "buttons", "Answer - C.png")
ANS_D_PATH = os.path.join("assets", "image", "buttons", "Answer - D.png")

# Button ulangi audio
REPEAT_AUDIO_PATH = os.path.join("assets", "image", "buttons", "Ulangi Suara.png")

# Audio – nanti kamu ganti ke file aslimu
BGM_MENU_PATH     = os.path.join("assets", "audio", "BG NCS.mp3")
SFX_CLICK_PATH    = os.path.join("assets", "audio", "Button Pressed.mp3")
SFX_CORRECT_PATH  = os.path.join("assets", "audio", "Correct.mp3")
SFX_WRONG_PATH    = os.path.join("assets", "audio", "Wrong.mp3")

# Root audio soal (chipmunk, hasil audio_processing.py)
PITCH_AUDIO_ROOT = os.path.join("pitch_audio")

WINDOW_NAME = "Guess The Word Filter"

STATE_HOME     = "home"
STATE_CATEGORY = "category"
STATE_GAME     = "game"
STATE_RESULT   = "result"

# Cooldown sentuh tombol biar gak dobel-dobel
HIT_COOLDOWN_MAX = 8
hit_cooldown = 30   # sedikit delay di awal supaya tidak auto-klik PLAY

# =========================
# 1a. DATA SOAL PER KATEGORI
# (sinkron dengan audio_code.py)
# =========================

CATEGORY_DATA = {
    "buah": {
        "dir": os.path.join(PITCH_AUDIO_ROOT, "buah"),
        "id_words": ['apel', 'jeruk', 'pisang', 'mangga', 'semangka'],
        "en_words": ['strawberry', 'grape', 'papaya', 'kiwi', 'pineapple']
    },
    "kendaraan": {
        "dir": os.path.join(PITCH_AUDIO_ROOT, "kendaraan"),
        "id_words": ['mobil', 'motor', 'sepeda', 'bus', 'kereta'],
        "en_words": ['airplane', 'boat', 'helicopter', 'scooter', 'truck']
    },
    "hewan": {
        "dir": os.path.join(PITCH_AUDIO_ROOT, "hewan"),
        "id_words": ['kucing', 'anjing', 'gajah', 'harimau', 'singa'],
        "en_words": ['monkey', 'horse', 'dolphin', 'giraffe', 'rabbit']
    }
}

# =========================
# 1b. INIT AUDIO (pygame)
# =========================

AUDIO_OK = False
bgm_available = False
click_sfx = None
correct_sfx = None
wrong_sfx = None

try:
    pygame.mixer.init()
    AUDIO_OK = True

    if os.path.exists(BGM_MENU_PATH):
        pygame.mixer.music.load(BGM_MENU_PATH)
        bgm_available = True
    else:
        print("[AUDIO] File BGM tidak ditemukan, skip backsong.")

    if os.path.exists(SFX_CLICK_PATH):
        click_sfx = pygame.mixer.Sound(SFX_CLICK_PATH)
    else:
        print("[AUDIO] File SFX click tidak ditemukan.")

    if os.path.exists(SFX_CORRECT_PATH):
        correct_sfx = pygame.mixer.Sound(SFX_CORRECT_PATH)
    else:
        print("[AUDIO] File SFX benar tidak ditemukan.")

    if os.path.exists(SFX_WRONG_PATH):
        wrong_sfx = pygame.mixer.Sound(SFX_WRONG_PATH)
    else:
        print("[AUDIO] File SFX salah tidak ditemukan.")

except Exception as e:
    print("[AUDIO] Gagal inisialisasi audio:", e)
    AUDIO_OK = False


def play_click_sfx():
    if AUDIO_OK and click_sfx is not None:
        click_sfx.play()


def play_correct():
    if AUDIO_OK and correct_sfx is not None:
        correct_sfx.play()


def play_wrong():
    if AUDIO_OK and wrong_sfx is not None:
        wrong_sfx.play()


def update_bgm_for_state(state):
    """
    HOME + CATEGORY  -> BGM menyala (loop)
    STATE lain (GAME, RESULT) -> BGM mati
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
# 4. LOAD TOMBOL (ASSET PNG)
# =========================

header_btn = load_button_image(HEADER_BUTTON_PATH, size=(400, 100))
play_btn   = load_button_image(PLAY_BUTTON_PATH,   size=(260, 100))

CAT_BTN_SIZE = (380, 130)
cat_buah_btn      = load_button_image(CAT_BUAH_PATH,      CAT_BTN_SIZE)
cat_hewan_btn     = load_button_image(CAT_HEWAN_PATH,     CAT_BTN_SIZE)
cat_kendaraan_btn = load_button_image(CAT_KENDARAAN_PATH, CAT_BTN_SIZE)

ANS_BTN_SIZE = (340, 120)
ans_a_btn = load_button_image(ANS_A_PATH, ANS_BTN_SIZE)
ans_b_btn = load_button_image(ANS_B_PATH, ANS_BTN_SIZE)
ans_c_btn = load_button_image(ANS_C_PATH, ANS_BTN_SIZE)
ans_d_btn = load_button_image(ANS_D_PATH, ANS_BTN_SIZE)
ANSWER_BTN_IMGS = [ans_a_btn, ans_b_btn, ans_c_btn, ans_d_btn]

REPEAT_BTN_SIZE = (260, 80)
repeat_audio_btn = load_button_image(REPEAT_AUDIO_PATH, REPEAT_BTN_SIZE)

# =========================
# 5. STATE & VARIABEL GAME
# =========================

state = STATE_HOME
selected_category = None  # "hewan" / "buah" / "kendaraan"

score = 0
questions = []           # list dict: {word, lang, audio_path}
current_q_index = 0
current_q = None
current_options = []     # list of 4 string jawaban
correct_answer = None

question_sound = None        # pygame.mixer.Sound untuk soal saat ini
question_start_time = 0      # ms
audio_initial_played = False
repeat_used = False          # tombol ulangi audio per soal

print("Tekan 'q' untuk keluar.")


def now_ms():
    """Waktu dalam millisecond."""
    if AUDIO_OK:
        return pygame.time.get_ticks()
    else:
        return int(time.time() * 1000)


def build_questions_for_category(cat_key):
    """Bangun list 10 soal (5 ID, 5 EN) untuk kategori tertentu."""
    data = CATEGORY_DATA[cat_key]
    id_words = data["id_words"]
    en_words = data["en_words"]

    id_pick = random.sample(id_words, min(5, len(id_words)))
    en_pick = random.sample(en_words, min(5, len(en_words)))

    q_list = []
    for w in id_pick:
        q_list.append({
            "word": w,
            "lang": "id",
            "audio_path": os.path.join(data["dir"], f"{w}_pitch.wav")
        })
    for w in en_pick:
        q_list.append({
            "word": w,
            "lang": "en",
            "audio_path": os.path.join(data["dir"], f"{w}_pitch.wav")
        })

    random.shuffle(q_list)
    return q_list[:10]


def setup_question(cat_key, index):
    """Siapkan soal ke-index, load audio & opsi jawaban."""
    global current_q, correct_answer, current_options
    global question_sound, question_start_time, audio_initial_played, repeat_used

    data = CATEGORY_DATA[cat_key]
    current_q = questions[index]
    correct_answer = current_q["word"]

    # Buat opsi: 1 benar + 3 salah
    all_words = data["id_words"] + data["en_words"]
    distractors = [w for w in all_words if w != correct_answer]
    if len(distractors) >= 3:
        distractors = random.sample(distractors, 3)

    current_options = [correct_answer] + distractors
    random.shuffle(current_options)

    # Load audio soal
    question_sound = None
    if AUDIO_OK and os.path.exists(current_q["audio_path"]):
        try:
            question_sound = pygame.mixer.Sound(current_q["audio_path"])
        except Exception as e:
            print("[AUDIO] Gagal load audio soal:", current_q["audio_path"], e)
    else:
        print("[AUDIO] File audio soal tidak ditemukan:", current_q["audio_path"])

    question_start_time = now_ms()
    audio_initial_played = False
    repeat_used = False

    print(f"[SOAL] Q{index+1}: {correct_answer} ({current_q['lang']})")


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
            ("buah",  cat_buah_btn),
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

                    score = 0
                    questions = build_questions_for_category(selected_category)
                    current_q_index = 0
                    setup_question(selected_category, current_q_index)

                    state = STATE_GAME
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

    # ---------- STATE GAME ----------
    elif state == STATE_GAME:
        # Skor di pojok kiri atas
        cv2.putText(
            frame,
            f"Skor: {score}",
            (30, 60),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            (255, 255, 255),
            2
        )

        # Info soal
        total_q = len(questions)
        cv2.putText(
            frame,
            f"Soal: {current_q_index+1}/{total_q}",
            (30, 110),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (255, 255, 255),
            2
        )

        # Delay 2 detik sebelum audio soal pertama kali diputar
        t_now = now_ms()
        if not audio_initial_played and question_sound is not None:
            if t_now - question_start_time >= 2000:
                question_sound.play()
                audio_initial_played = True

        # Tampilkan 4 opsi jawaban sebagai 4 tombol PNG (A,B,C,D)
        gap_x, gap_y = 40, 30
        start_x = int(w_frame * 0.1)
        start_y = int(h_frame * 0.55)

        for i, opt_text in enumerate(current_options):
            if i >= len(ANSWER_BTN_IMGS):
                break
            btn_img = ANSWER_BTN_IMGS[i]

            row = i // 2
            col = i % 2
            x = start_x + col * (btn_img.shape[1] + gap_x)
            y = start_y + row * (btn_img.shape[0] + gap_y)

            frame = overlay_png(frame, btn_img, x, y)

            # teks jawaban di atas tombol
            text_size, _ = cv2.getTextSize(opt_text, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)
            tx = x + (btn_img.shape[1] - text_size[0]) // 2
            ty = y + (btn_img.shape[0] + text_size[1]) // 2 - 5
            cv2.putText(
                frame,
                opt_text,
                (tx, ty),
                cv2.FONT_HERSHEY_DUPLEX,
                0.8,
                (255, 255, 255),
                2
            )

            # cek klik jawaban
            if fingertip and hit_cooldown == 0:
                if point_on_png_button(fingertip[0], fingertip[1], x, y, btn_img):
                    play_click_sfx()
                    print(f"[JAWAB] {opt_text}")

                    if opt_text == correct_answer:
                        score += 1
                        play_correct()
                        print("[HASIL] Benar!")
                    else:
                        play_wrong()
                        print("[HASIL] Salah!")

                    hit_cooldown = HIT_COOLDOWN_MAX
                    current_q_index += 1

                    if current_q_index < len(questions):
                        setup_question(selected_category, current_q_index)
                    else:
                        print("[INFO] Semua soal selesai.")
                        state = STATE_RESULT
                    break  # stop loop opsi setelah jawab

        # Tombol "Ulangi Audio" (1x per soal) pakai asset PNG
        if not repeat_used and question_sound is not None:
            rx = (w_frame - repeat_audio_btn.shape[1]) // 2
            ry = int(h_frame * 0.82)

            frame = overlay_png(frame, repeat_audio_btn, rx, ry)

            if fingertip and hit_cooldown == 0:
                if point_on_png_button(fingertip[0], fingertip[1], rx, ry, repeat_audio_btn):
                    if audio_initial_played:
                        question_sound.play()
                        repeat_used = True
                        hit_cooldown = HIT_COOLDOWN_MAX
                        print("[INFO] Audio diulang sekali.")

    # ---------- STATE RESULT ----------
    elif state == STATE_RESULT:
        cv2.putText(
            frame,
            "Kuis Selesai!",
            (int(w_frame * 0.3), int(h_frame * 0.4)),
            cv2.FONT_HERSHEY_DUPLEX,
            1.4,
            (255, 255, 255),
            3
        )
        cv2.putText(
            frame,
            f"Skor Akhir: {score} / {len(questions)}",
            (int(w_frame * 0.23), int(h_frame * 0.5)),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            (255, 255, 255),
            2
        )
        cv2.putText(
            frame,
            "Tekan 'q' untuk keluar",
            (int(w_frame * 0.3), int(h_frame * 0.6)),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
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
