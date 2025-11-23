import cv2
import mediapipe as mp
# import random

"""
# Contoh Bahan untuk buat elemen (UI)
box_size = 100
box_color = (0, 0, 255)
score = 0
box_x = 200
box_y = 200

# Logika ketika telunjuk menyentuh kotak
if (box_x < cx < box_x + box_size) and (box_y < cy < box_y + box_size):
                
                # JIKA KENA:
                score += 1 # Tambah skor
                
                # Acak posisi baru (jangan sampai keluar layar)
                box_x = random.randint(50, w_frame - 150)
                box_y = random.randint(50, h_frame - 150)
                
                print(f"Kena! Skor: {score}")

# Logika untuk menggambar kotaknya
cv2.rectangle(frame, (box_x, box_y), (box_x + box_size, box_y + box_size), box_color, -1)

    # Tampilkan Skor di Pojok Kiri Atas
    cv2.putText(frame, f'Skor: {score}', (30, 80), 
                cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 2)

    cv2.imshow("Game Tangkap Kotak", frame)
"""

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# static_image_mode=False: Mengoptimalkan untuk video (tracking antar frame)
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2, # deteksi berapa tangan yang bisa terdeteksi
    min_detection_confidence=0.6, # tingkat kepercayaaan deteksi
    min_tracking_confidence=0.6 # tingkat kepercayaan tracking
)

cap = cv2.VideoCapture(0) # cv2.VideoCapture(0) untuk membuka webcam

if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses.")
    exit()

print("Tekan 'q' untuk keluar.")

while True:
    success, frame = cap.read()
    if not success:
        break

    h_frame, w_frame, _ = frame.shape

    frame = cv2.flip(frame, 1) # Supaya hasil kamera mirror
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) 

    # Proses deteksi tangan
    results = hands.process(frame_rgb)

    # Jika tangan terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            # Gambar titik (landmarks) dan garis hubung
            mp_drawing.draw_landmarks(
                frame, 
                hand_landmarks, 
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2), # Warna titik
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2) # Warna garis
            )

            # Mengambil koordinat Ujung Telunjuk (ID 8)
            h, w, c = frame.shape
            # Landmark dinormalisasi, kalikan dengan lebar/tinggi frame
            cx, cy = int(hand_landmarks.landmark[8].x * w), int(hand_landmarks.landmark[8].y * h)
            
            # Gambar lingkaran khusus di ujung telunjuk
            cv2.circle(frame, (cx, cy), 10, (255, 255, 0), cv2.FILLED)

    # Tampilkan hasil
    cv2.imshow("MediaPipe Hand Tracking", frame)

    # Keluar jika tombol 'q' ditekan
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()