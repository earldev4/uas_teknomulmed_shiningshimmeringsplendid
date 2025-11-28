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
PLAY_AGAIN_PATH   = os.path.join("assets", "image", "buttons", "Mainkan Lagi.png")

# Folder semua tombol jawaban, contoh file:
# "Hewan - Monkey.png", "Buah - Apel.png", "Kendaraan - Bus.png", dst.
ANSWER_BUTTONS_DIR = os.path.join("assets", "image", "buttons")

# Button ulangi audio
REPEAT_AUDIO_PATH = os.path.join("assets", "image", "buttons", "Ulang Suara.png")

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

def put_text_with_outline(
    img,
    text,
    org,                 # (x, y)
    font,
    font_scale,
    color,               # warna teks utama, misal (255,255,255)
    thickness,           # ketebalan teks utama
    outline_color=(0, 0, 0),    # warna outline, default hitam
    outline_thickness=None      # kalau None => thickness+2
):
    x, y = org
    if outline_thickness is None:
        outline_thickness = thickness + 2

    # gambar outline di empat arah (atas-bawah-kiri-kanan/diagonal)
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

    # gambar teks utama di tengah outline
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

# =========================
# 2a. LOAD SEMUA ASSET JAWABAN DARI FOLDER
# =========================

def load_all_answer_assets():
    """
    Baca semua file .png di ANSWER_BUTTONS_DIR yang namanya:
    'Hewan - Monkey.png', 'Buah - Apel.png', 'Kendaraan - Bus.png', dst.
    Hasil: dict per kategori -> list {word, img}
    """
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

        name_no_ext = os.path.splitext(fname)[0]   # "Hewan - Monkey"
        parts = name_no_ext.split("-")
        if len(parts) < 2:
            continue

        cat_label = parts[0].strip().lower()   # "hewan", "buah", "kendaraan"
        word = parts[1].strip().lower()        # "monkey", "apel", "bus"

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


ALL_ANSWER_ASSETS = load_all_answer_assets()

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
# 4. LOAD TOMBOL MENU & REPEAT
# =========================

header_btn = load_button_image(HEADER_BUTTON_PATH, size=(400, 100))
play_btn   = load_button_image(PLAY_BUTTON_PATH,   size=(260, 100))

CAT_BTN_SIZE = (380, 130)
cat_buah_btn      = load_button_image(CAT_BUAH_PATH,      CAT_BTN_SIZE)
cat_hewan_btn     = load_button_image(CAT_HEWAN_PATH,     CAT_BTN_SIZE)
cat_kendaraan_btn = load_button_image(CAT_KENDARAAN_PATH, CAT_BTN_SIZE)

REPEAT_BTN_SIZE = (260, 80)
repeat_audio_btn = load_button_image(REPEAT_AUDIO_PATH, REPEAT_BTN_SIZE)

PLAY_AGAIN_BTN_SIZE = (320, 110)
play_again_btn = load_button_image(PLAY_AGAIN_PATH, PLAY_AGAIN_BTN_SIZE)

# =========================
# 5. STATE & VARIABEL GAME
# =========================

state = STATE_HOME
selected_category = None  # "hewan" / "buah" / "kendaraan"

score = 0
questions = []           # list dict: {word, lang, audio_path}
current_q_index = 0
current_q = None
correct_answer = None

question_sound = None        # pygame.mixer.Sound untuk soal saat ini
question_start_time = 0      # ms
audio_initial_played = False
repeat_used = False          # tombol ulangi audio per soal

answer_buttons = []          # list tombol jawaban {word, img}

print("Tekan 'q' untuk keluar.")


def now_ms():
    """Waktu dalam millisecond (tanpa tergantung pygame)."""
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
            "word": w.lower(),
            "lang": "id",
            "audio_path": os.path.join(data["dir"], f"{w}.wav")
        })
    for w in en_pick:
        q_list.append({
            "word": w.lower(),
            "lang": "en",
            "audio_path": os.path.join(data["dir"], f"{w}.wav")
        })

    random.shuffle(q_list)
    return q_list[:10]


def setup_question(cat_key, index):
    """Siapkan soal ke-index, load audio & opsi jawaban dari asset PNG."""
    global current_q, correct_answer, answer_buttons
    global question_sound, question_start_time, audio_initial_played, repeat_used

    assets_for_cat = ALL_ANSWER_ASSETS.get(cat_key, [])
    if not assets_for_cat:
        print("[ASSET] Tidak ada asset jawaban untuk kategori:", cat_key)

    current_q = questions[index]
    correct_answer = current_q["word"]  # lowercase

    # Cari tombol PNG yang cocok sebagai jawaban benar
    correct_btn = None
    wrong_btns = []
    for item in assets_for_cat:
        if item["word"] == correct_answer:
            correct_btn = item
        else:
            wrong_btns.append(item)

    if correct_btn is None:
        print(f"[WARN] Tidak ketemu asset untuk kata '{correct_answer}' di kategori '{cat_key}'")
        # fallback: ambil max 4 acak
        answer_buttons = random.sample(assets_for_cat, min(4, len(assets_for_cat)))
    else:
        # ambil 3 jawaban salah random
        if len(wrong_btns) >= 3:
            wrong_btns = random.sample(wrong_btns, 3)
        answer_buttons = wrong_btns + [correct_btn]
        random.shuffle(answer_buttons)

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

        #
        if selected_category:
            put_text_with_outline(
                frame,
                f"Terpilih: {selected_category}",
                (40, h_frame - 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (255, 255, 255),   # teks putih
                2,                 # ketebalan teks utama
                (0, 0, 0)          # outline hitam
            )


    # ---------- STATE GAME ----------
    elif state == STATE_GAME:
        # Skor di pojok kiri atas
        put_text_with_outline(
            frame,
            f"Skor: {score}",
            (30, 60),
            cv2.FONT_HERSHEY_DUPLEX,
            1.0,
            (255, 255, 255),
            2,
            (0, 0, 0)
        )

        # Hitung total soal
        total_q = len(questions)

        put_text_with_outline(
            frame,
            f"Soal: {current_q_index+1}/{total_q}",
            (30, 110),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (255, 255, 255),
            2,
            (0, 0, 0)
        )

        # Delay 2 detik sebelum audio soal pertama kali diputar
        t_now = now_ms()
        if not audio_initial_played and question_sound is not None:
            if t_now - question_start_time >= 2000:
                question_sound.play()
                audio_initial_played = True

        #
        # Tampilkan 4 opsi jawaban sebagai 4 tombol PNG dalam 1 baris horizontal
        if answer_buttons:
            gap_x = 30  # jarak antar tombol
            # total lebar semua tombol + jarak antar tombol
            total_width = sum(btn["img"].shape[1] for btn in answer_buttons) + \
                          gap_x * (len(answer_buttons) - 1)

            start_x = int((w_frame - total_width) / 2)   # rata tengah
            y_btn   = int(h_frame * 0.65)                # tinggi baris tombol

            x = start_x
            for i, btn in enumerate(answer_buttons):
                img  = btn["img"]
                word = btn["word"]   # lowercase

                frame = overlay_png(frame, img, x, y_btn)

                # cek klik jawaban
                if fingertip and hit_cooldown == 0:
                    if point_on_png_button(fingertip[0], fingertip[1], x, y_btn, img):
                        play_click_sfx()
                        print(f"[JAWAB] {word}")

                        if word == correct_answer:
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

                # geser X ke kanan untuk tombol berikutnya
                x += img.shape[1] + gap_x

        # =========================
        # Tombol "Ulangi Audio"
        # =========================
        if not repeat_used and question_sound is not None:
            rx = w_frame - repeat_audio_btn.shape[1] - 30  # pojok kanan
            ry = 30                                        # atas

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
        put_text_with_outline(
            frame,
            "Kuis Selesai!",
            (int(w_frame * 0.3), int(h_frame * 0.4)),
            cv2.FONT_HERSHEY_DUPLEX,
            1.4,
            (255, 255, 255),
            3,
            (0, 0, 0)
        )

        put_text_with_outline(
            frame,
            f"Skor Akhir: {score} / {len(questions)}",
            (int(w_frame * 0.23), int(h_frame * 0.5)),
            cv2.FONT_HERSHEY_DUPLEX,
            1.2,
            (255, 255, 255),
            2,
            (0, 0, 0)
        )

        put_text_with_outline(
            frame,
            "Tekan 'q' untuk keluar",
            (int(w_frame * 0.3), int(h_frame * 0.6)),
            cv2.FONT_HERSHEY_DUPLEX,
            0.9,
            (255, 255, 255),
            2,
            (0, 0, 0)
        )

        # ============ TOMBOL "MAINkan LAGI" ============
        btn_x = (w_frame - play_again_btn.shape[1]) // 2
        btn_y = int(h_frame * 0.72)   # di bawah teks hasil

        frame = overlay_png(frame, play_again_btn, btn_x, btn_y)

        if fingertip and hit_cooldown == 0:
            if point_on_png_button(fingertip[0], fingertip[1], btn_x, btn_y, play_again_btn):
                play_click_sfx()
                print("[INFO] Mainkan lagi ditekan → kembali ke menu kategori")

                # reset state game
                score = 0
                selected_category = None
                questions = []
                current_q_index = 0
                current_q = None
                correct_answer = None
                question_sound = None
                audio_initial_played = False
                repeat_used = False

                state = STATE_CATEGORY
                hit_cooldown = HIT_COOLDOWN_MAX

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
