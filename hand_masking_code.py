import cv2
import mediapipe as mp
import numpy as np
import os

# =========================
# GAME STATE
# =========================
class GameState:
    MENU = "menu"
    CATEGORY = "category"
    PLAYING = "playing"
    
current_state = GameState.MENU

# =========================
# PATH ASSET
# =========================
BASE_PATH = os.getcwd()
IMAGE_PATH = os.path.join(BASE_PATH, "assets", "image", "buttons")

# =========================
# BUTTON CLASS
# =========================
class Button:
    def __init__(self, x, y, width, height, text, color=(100, 150, 255)):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.color = color
        self.hover_color = (150, 200, 255)
        self.is_hovered = False
        
    def draw(self, frame):
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
# SETUP KAMERA
# =========================
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses.")
    exit()

ret, test_frame = cap.read()
if ret:
    h_frame, w_frame, _ = test_frame.shape
else:
    h_frame, w_frame = 480, 640

# =========================
# CREATE BUTTONS
# =========================
play_button = Button(w_frame//2 - 125, h_frame//2 - 50, 250, 100, "PLAY!")

click_cooldown = 0
CLICK_COOLDOWN_MAX = 20

print("Version 2: Basic button interaction added")
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
    
    results = hands.process(frame_rgb)
    
    if click_cooldown > 0:
        click_cooldown -= 1
    
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
    
    # MENU STATE
    if current_state == GameState.MENU:
        if finger_x and finger_y:
            play_button.check_hover(finger_x, finger_y)
            if play_button.is_clicked(finger_x, finger_y) and click_cooldown == 0:
                current_state = GameState.CATEGORY
                click_cooldown = CLICK_COOLDOWN_MAX
                print("Moving to CATEGORY")
        
        play_button.draw(frame)
    
    # Display current state
    cv2.putText(frame, f"State: {current_state}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow("Guess The Word Game - v2", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
