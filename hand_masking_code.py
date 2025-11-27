import cv2
import mediapipe as mp
import numpy as np
import random
import os
import pygame

# =========================
# INISIALISASI PYGAME AUDIO
# =========================
pygame.mixer.init()

# =========================
# GAME STATE
# =========================
class GameState:
    MENU = "menu"
    CATEGORY = "category"
    PLAYING = "playing"
    
current_state = GameState.MENU
selected_category = None
current_word = None
current_options = []
score = 0

# =========================
# PATH ASSET
# =========================
BASE_PATH = os.getcwd()
IMAGE_PATH = os.path.join(BASE_PATH, "assets", "image", "buttons")
AUDIO_PATH = os.path.join(BASE_PATH, "data_audio")

# =========================
# DATA KATEGORI & KATA
# =========================
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
        {"word": "Apel", "audio": "apel.wav", "image": "Buah - Pisang.png"},
        {"word": "Grape", "audio": "grape.wav", "image": "Buah - Pisang.png"},
        {"word": "Jeruk", "audio": "jeruk.wav", "image": "Buah - Pisang.png"},
        {"word": "Kiwi", "audio": "kiwi.wav", "image": "Buah - Pisang.png"},
        {"word": "Mangga", "audio": "mangga.wav", "image": "Buah - Pisang.png"},
        {"word": "Papaya", "audio": "papaya.wav", "image": "Buah - Pisang.png"},
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

# =========================
# FUNGSI LOAD GAMBAR PNG
# =========================
def load_image_with_alpha(filename):
    """Load PNG image dengan alpha channel"""
    filepath = os.path.join(IMAGE_PATH, filename)
    img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"Warning: Tidak dapat memuat gambar {filename}")
    return img

def overlay_png(bg, png, x, y, scale=1.0):
    """Overlay PNG dengan alpha ke background"""
    if png is None:
        return bg
    
    # Resize jika perlu
    if scale != 1.0:
        new_w = int(png.shape[1] * scale)
        new_h = int(png.shape[0] * scale)
        png = cv2.resize(png, (new_w, new_h))
    
    h, w = png.shape[:2]
    
    # Cek batas
    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg
    
    # Cek apakah ada alpha channel
    if png.shape[2] == 4:
        roi = bg[y:y+h, x:x+w]
        bgr = png[..., :3]
        alpha = png[..., 3:] / 255.0
        roi = (alpha * bgr + (1 - alpha) * roi).astype(np.uint8)
        bg[y:y+h, x:x+w] = roi
    else:
        bg[y:y+h, x:x+w] = png
    
    return bg

# =========================
# BUTTON CLASS
# =========================
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
            # Gambar menggunakan image
            scale = min(self.width / self.image.shape[1], self.height / self.image.shape[0])
            overlay_png(frame, self.image, self.x, self.y, scale)
        else:
            # Gambar kotak biasa
            color = self.hover_color if self.is_hovered else self.color
            overlay = frame.copy()
            cv2.rectangle(overlay, (self.x, self.y), 
                         (self.x + self.width, self.y + self.height), 
                         color, -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            cv2.rectangle(frame, (self.x, self.y), 
                         (self.x + self.width, self.y + self.height), 
                         (255, 255, 255), 2)
            
            # Draw text
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

# =========================
# SETUP MEDIAPIPE HANDS
# =========================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# =========================
# FUNGSI AUDIO
# =========================
def play_word_audio(category, audio_file):
    """Play audio untuk kata"""
    try:
        audio_path = os.path.join(AUDIO_PATH, category.lower(), audio_file)
        if os.path.exists(audio_path):
            pygame.mixer.music.load(audio_path)
            pygame.mixer.music.play()
        else:
            print(f"Audio tidak ditemukan: {audio_path}")
    except Exception as e:
        print(f"Error playing audio: {e}")

# =========================
# FUNGSI GENERATE SOAL
# =========================
def generate_question(category):
    global current_word, current_options
    
    words = word_data[category]
    correct = random.choice(words)
    current_word = correct
    
    # Ambil 3 jawaban salah
    wrong_answers = [w for w in words if w != correct]
    selected_wrong = random.sample(wrong_answers, min(3, len(wrong_answers)))
    
    # Gabung dan acak
    current_options = [correct] + selected_wrong
    random.shuffle(current_options)
    
    # Play audio
    play_word_audio(category, correct["audio"])

# =========================
# SETUP KAMERA
# =========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses.")
    exit()

# Get frame dimensions
ret, test_frame = cap.read()
if ret:
    h_frame, w_frame, _ = test_frame.shape
else:
    h_frame, w_frame = 480, 640

# =========================
# CREATE BUTTONS
# =========================
# Menu button
play_button = Button(w_frame//2 - 125, h_frame//2 - 50, 250, 100, "PLAY!", image_file="Play.png")

# Category buttons
category_buttons = [
    Button(w_frame//2 - 150, h_frame//2 - 180, 300, 100, "Hewan", image_file="Kategori - Hewan.png"),
    Button(w_frame//2 - 150, h_frame//2 - 50, 300, 100, "Buah", image_file="Kategori - Buah.png"),
    Button(w_frame//2 - 150, h_frame//2 + 80, 300, 100, "Kendaraan", image_file="Kategori - Kendaraan.png")
]

# Option buttons (dinamis)
option_buttons = []

# Cooldown
click_cooldown = 0
CLICK_COOLDOWN_MAX = 20

print("Tekan 'q' untuk keluar.")

# =========================
# MAIN LOOP
# =========================
while True:
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Process hand tracking
    results = hands.process(frame_rgb)
    
    # Decrease cooldown
    if click_cooldown > 0:
        click_cooldown -= 1
    
    # Get finger position
    finger_x, finger_y = None, None
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                frame, hand_landmarks, mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )
            
            h, w, c = frame.shape
            finger_x = int(hand_landmarks.landmark[8].x * w)
            finger_y = int(hand_landmarks.landmark[8].y * h)
            
            cv2.circle(frame, (finger_x, finger_y), 15, (255, 255, 0), cv2.FILLED)
    
    # =========================
    # RENDER BASED ON STATE
    # =========================
    
    if current_state == GameState.MENU:
        # Draw play button
        if finger_x and finger_y:
            play_button.check_hover(finger_x, finger_y)
            if play_button.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                current_state = GameState.CATEGORY
                click_cooldown = CLICK_COOLDOWN_MAX
        
        play_button.draw(frame)
    
    elif current_state == GameState.CATEGORY:
        # Draw category buttons
        for btn in category_buttons:
            if finger_x and finger_y:
                btn.check_hover(finger_x, finger_y)
                if btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                    selected_category = btn.text
                    current_state = GameState.PLAYING
                    generate_question(selected_category)
                    click_cooldown = CLICK_COOLDOWN_MAX
            
            btn.draw(frame)
    
    elif current_state == GameState.PLAYING:
        # Draw speaker icon
        speaker_text = "Dengarkan kata..."
        cv2.putText(frame, speaker_text, (w_frame//2 - 150, 80), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Create option buttons
        if len(option_buttons) != len(current_options):
            option_buttons = []
            for i, option in enumerate(current_options):
                btn_x = 50 if i < 2 else w_frame - 250
                btn_y = 150 if i % 2 == 0 else 350
                option_buttons.append(
                    Button(btn_x, btn_y, 200, 150, option["word"], image_file=option["image"])
                )
        
        # Draw option buttons
        for i, btn in enumerate(option_buttons):
            if finger_x and finger_y:
                btn.check_hover(finger_x, finger_y)
                if btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                    # Check answer
                    if current_options[i] == current_word:
                        print("✓ Benar!")
                        score += 1
                        generate_question(selected_category)
                    else:
                        print("✗ Salah!")
                        # Replay audio
                        play_word_audio(selected_category, current_word["audio"])
                    
                    click_cooldown = CLICK_COOLDOWN_MAX
            
            btn.draw(frame)
        
        # Back button
        back_btn = Button(w_frame//2 - 75, h_frame - 100, 150, 60, "Kembali", (200, 100, 100))
        if finger_x and finger_y:
            back_btn.check_hover(finger_x, finger_y)
            if back_btn.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                current_state = GameState.CATEGORY
                pygame.mixer.music.stop()
                click_cooldown = CLICK_COOLDOWN_MAX
        back_btn.draw(frame)
    
    cv2.imshow("Guess The Word Game", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
pygame.mixer.quit()
