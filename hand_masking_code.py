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

print("Tekan 'q' untuk keluar.")
print("Version 1: Basic hand tracking setup")

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
    
    # Display current state
    cv2.putText(frame, f"State: {current_state}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    cv2.imshow("Guess The Word Game - v1", frame)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
