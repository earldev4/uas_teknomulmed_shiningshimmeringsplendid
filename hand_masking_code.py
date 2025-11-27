import cv2
import mediapipe as mp
import numpy as np
import random
import os
import pygame

# ============================================================
# INISIALISASI SISTEM AUDIO PYGAME
# ============================================================
pygame.mixer.init()

# ============================================================
# DEFINISI STATE GAME
# ============================================================
class GameState:
    MENU = "menu"           # Tampilan awal game
    CATEGORY = "category"   # Pemilihan kategori
    PLAYING = "playing"     # Mode permainan aktif

current_state = GameState.MENU
selected_category = None
current_word = None
current_options = []
score = 0

# Variabel untuk feedback visual ketika benar/salah
show_feedback = False
feedback_text = ""
feedback_color = (0, 255, 0)
feedback_timer = 0

# ============================================================
# PATH FOLDER ASSET
# ============================================================
BASE_PATH = os.getcwd()
IMAGE_PATH = os.path.join(BASE_PATH, "assets", "image", "buttons")
AUDIO_PATH = os.path.join(BASE_PATH, "data_audio")

# ============================================================
# KOMPILASI DATA KATEGORI
# ============================================================
word_data = {
    "Hewan": [
        {"word": "Anjing", "audio": "anjing.wav", "image": "Hewan - Anjing.png"},
        {"word": "Dolphin", "audio": "dolphin.wav", "image": "Hewan - Dolphin.png"},
        {"word": "Gajah", "audio": "gajah.wav", "image": "Hewan - Gajah.png"},
        {"word": "Giraffe", "audio": "giraffe.wav", "image": "Hewan - Giraffe.png"},
        {"word": "Harimau", "audio": "harimau.wav", "image": "Hewan - Harimau.png"},
        {"word": "Horse", "audio": "horse.wav", "image": "Hewan - Horse.png"},
        {"word": "Kucing", "audio": "kucing.wav", "image": "Hewan - Kucing.png"},
        {"word": "Monkey", "audio": "monkey.wav", "image": "Hewan - Monkey.png"},
        {"word": "Rabbit", "audio": "rabbit.wav", "image": "Hewan - Rabbit.png"},
        {"word": "Singa", "audio": "singa.wav", "image": "Hewan - Singa.png"}
    ],
    "Buah": [
        {"word": "Apel", "audio": "apel.wav", "image": "Buah - Apel.png"},
        {"word": "Grape", "audio": "grape.wav", "image": "Buah - Grape.png"},
        {"word": "Jeruk", "audio": "jeruk.wav", "image": "Buah - Jeruk.png"},
        {"word": "Kiwi", "audio": "kiwi.wav", "image": "Buah - Kiwi.png"},
        {"word": "Mangga", "audio": "mangga.wav", "image": "Buah - Mangga.png"},
        {"word": "Papaya", "audio": "papaya.wav", "image": "Buah - Papaya.png"},
        {"word": "Pineapple", "audio": "pineapple.wav", "image": "Buah - Pineapple.png"},
        {"word": "Pisang", "audio": "pisang.wav", "image": "Buah - Pisang.png"},
        {"word": "Semangka", "audio": "semangka.wav", "image": "Buah - Semangka.png"},
        {"word": "Strawberry", "audio": "strawberry.wav", "image": "Buah - Strawberry.png"}
    ],
    "Kendaraan": [
        {"word": "Airplane", "audio": "airplane.wav", "image": "Kendaraan - Airplane.png"},
        {"word": "Boat", "audio": "boat.wav", "image": "Kendaraan - Boat.png"},
        {"word": "Bus", "audio": "bus.wav", "image": "Kendaraan - Bus.png"},
        {"word": "Helicopter", "audio": "helicopter.wav", "image": "Kendaraan - Helicopter.png"},
        {"word": "Kereta", "audio": "kereta.wav", "image": "Kendaraan - Kereta.png"},
        {"word": "Mobil", "audio": "mobil.wav", "image": "Kendaraan - Mobil.png"},
        {"word": "Motor", "audio": "motor.wav", "image": "Kendaraan - Motor.png"},
        {"word": "Scooter", "audio": "scooter.wav", "image": "Kendaraan - Scooter.png"},
        {"word": "Sepeda", "audio": "sepeda.wav", "image": "Kendaraan - Sepeda.png"},
        {"word": "Truck", "audio": "truck.wav", "image": "Kendaraan - Truck.png"}
    ]
}

# ============================================================
# FUNGSI MEMUAT GAMBAR PNG DENGAN ALPHA CHANNEL
# ============================================================
def load_image_with_alpha(filename):
    filepath = os.path.join(IMAGE_PATH, filename)
    img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"WARNING: Gambar tidak ditemukan -> {filename}")
    return img


def overlay_png(bg, png, x, y, scale=1.0):
    """Menempelkan PNG transparan ke frame background"""
    if png is None:
        return bg

    if scale != 1.0:
        new_w = int(png.shape[1] * scale)
        new_h = int(png.shape[0] * scale)
        png = cv2.resize(png, (new_w, new_h))

    h, w = png.shape[:2]

    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg

    if png.shape[2] == 4:
        roi = bg[y:y+h, x:x+w]
        bgr = png[..., :3]
        alpha = png[..., 3:] / 255.0
        roi = (alpha * bgr + (1 - alpha) * roi).astype(np.uint8)
        bg[y:y+h, x:x+w] = roi
    else:
        bg[y:y+h, x:x+w] = png

    return bg

# ============================================================
# CLASS BUTTON
# ============================================================
class Button:
    def __init__(self, x, y, width, height, text, color=(100, 150, 255), image_file=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = (150, 200, 255)
        self.is_hovered = False
        self.image = load_image_with_alpha(image_file) if image_file else None

    def draw(self, frame):
        if self.image is not None:
            scale = min(self.width / self.image.shape[1], self.height / self.image.shape[0])
            overlay_png(frame, self.image, self.x, self.y, scale)
        else:
            color = self.hover_color if self.is_hovered else self.color
            overlay = frame.copy()
            cv2.rectangle(overlay, (self.x, self.y),
                          (self.x + self.width, self.y + self.height),
                          color, -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

            cv2.rectangle(frame, (self.x, self.y),
                          (self.x + self.width, self.y + self.height),
                          (255, 255, 255), 2)

            font = cv2.FONT_HERSHEY_SIMPLEX
            text_size = cv2.getTextSize(self.text, font, 1, 2)[0]
            text_x = self.x + (self.width - text_size[0]) // 2
            text_y = self.y + (self.height + text_size[1]) // 2
            cv2.putText(frame, self.text, (text_x, text_y),
                        font, 1, (255, 255, 255), 2)

    def is_clicked(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def check_hover(self, x, y):
        self.is_hovered = self.is_clicked(x, y)

# ============================================================
# KONFIGURASI MEDIAPIPE HAND TRACKING
# ============================================================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# ============================================================
# PEMUTARAN AUDIO
# ============================================================
def play_word_audio(category, audio_file):
    try:
        audio_path = os.path.join(AUDIO_PATH, category.lower(), audio_file)
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        else:
            print(f"Audio tidak ditemukan: {audio_path}")
    except Exception as e:
        print("Error saat memutar audio:", e)

# ============================================================
# GENERATE PERTANYAAN BARU
# ============================================================
def generate_question(category):
    global current_word, current_options, option_buttons

    words = word_data[category]

    if len(words) < 4:
        print(f"Kategori {category} membutuhkan minimal 4 item")
        return

    selected_words = random.sample(words, 4)
    correct = random.choice(selected_words)
    current_word = correct

    current_options = selected_words.copy()
    random.shuffle(current_options)

    option_buttons = []
    play_word_audio(category, correct["audio"])

# ============================================================
# AKSES KAMERA
# ============================================================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Kamera tidak terdeteksi.")
    exit()

ret, test_frame = cap.read()
if ret:
    h_frame, w_frame, _ = test_frame.shape
else:
    h_frame, w_frame = 480, 640

# ============================================================
# INISIALISASI BUTTON UTAMA
# ============================================================
play_button = Button(w_frame//2 - 125, h_frame//2 - 50, 250, 100, "PLAY!", image_file="Play.png")

category_buttons = [
    Button(w_frame//2 - 150, h_frame//2 - 180, 300, 100, "Hewan", image_file="Kategori - Hewan.png"),
    Button(w_frame//2 - 150, h_frame//2 - 50, 300, 100, "Buah", image_file="Kategori - Buah.png"),
    Button(w_frame//2 - 150, h_frame//2 + 80, 300, 100, "Kendaraan", image_file="Kategori - Kendaraan.png")
]

option_buttons = []
click_cooldown = 0
CLICK_COOLDOWN_MAX = 20

print("Tekan Q untuk keluar dari permainan.")

# ============================================================
# LOOP UTAMA GAME
# ============================================================
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    if click_cooldown > 0:
        click_cooldown -= 1

    if feedback_timer > 0:
        feedback_timer -= 1
    else:
        show_feedback = False

    finger_x, finger_y = None, None

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            h, w, c = frame.shape
            finger_x = int(hand_landmarks.landmark[8].x * w)
            finger_y = int(hand_landmarks.landmark[8].y * h)
            cv2.circle(frame, (finger_x, finger_y), 15, (255, 255, 0), cv2.FILLED)

    # ============================================================
    # MENU UTAMA
    # ============================================================
    if current_state == GameState.MENU:
        if finger_x and finger_y:
            play_button.check_hover(finger_x, finger_y)
            if play_button.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                current_state = GameState.CATEGORY
                click_cooldown = CLICK_COOLDOWN_MAX

        play_button.draw(frame)

    # ============================================================
    # PEMILIHAN KATEGORI
    # ============================================================
    elif current_state == GameState.CATEGORY:
        for btn in category_buttons:
            if finger_x and finger_y:
                btn.check_hover(finger_x, finger_y)
                if btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                    selected_category = btn.text
                    current_state = GameState.PLAYING
                    generate_question(selected_category)
                    click_cooldown = CLICK_COOLDOWN_MAX
            btn.draw(frame)

    # ============================================================
    # MODE PERMAINAN
    # ============================================================
    elif current_state == GameState.PLAYING:

        cv2.putText(frame, "Dengarkan kata...", (w_frame//2 - 150, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

        cv2.putText(frame, f"Skor: {score}", (w_frame - 200, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)

        if show_feedback and feedback_timer > 0:
            cv2.putText(frame, feedback_text, (50, 80),
                        cv2.FONT_HERSHEY_DUPLEX, 2, feedback_color, 4)

        if len(option_buttons) != len(current_options):
            option_buttons = []
            for i, option in enumerate(current_options):
                btn_x = 50 if i < 2 else w_frame - 250
                btn_y = 150 if i % 2 == 0 else 350
                option_buttons.append(
                    Button(btn_x, btn_y, 200, 150, option["word"], image_file=option["image"])
                )

        for i, btn in enumerate(option_buttons):
            if finger_x and finger_y:
                btn.check_hover(finger_x, finger_y)
                if btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                    if current_options[i] == current_word:
                        score += 1
                        show_feedback = True
                        feedback_text = "BENAR! +1"
                        feedback_color = (0, 255, 0)
                        feedback_timer = 30
                        click_cooldown = CLICK_COOLDOWN_MAX
                        generate_question(selected_category)
                    else:
                        show_feedback = True
                        feedback_text = "SALAH!"
                        feedback_color = (0, 0, 255)
                        feedback_timer = 30
                        play_word_audio(selected_category, current_word["audio"])
                        click_cooldown = CLICK_COOLDOWN_MAX
            btn.draw(frame)

        back_btn = Button(w_frame//2 - 75, h_frame - 150, 150, 60, "Kembali", (200, 100, 100))
        if finger_x and finger_y:
            back_btn.check_hover(finger_x, finger_y)
            if back_btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                current_state = GameState.CATEGORY
                pygame.mixer.music.stop()
                score = 0
                click_cooldown = CLICK_COOLDOWN_MAX
        back_btn.draw(frame)

    cv2.imshow("Guess The Word Game", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
