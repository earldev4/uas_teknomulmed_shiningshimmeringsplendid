import cv2
import mediapipe as mp
import numpy as np
import random
import os

# =========================
# 1. SETUP GAMBAR TOMBOL
# =========================

# Load gambar tombol (PNG dengan alpha)
button_path = os.path.join(os.getcwd(),"assets/image/buttons", "Guess The Word.png")
button_img = cv2.imread(button_path, cv2.IMREAD_UNCHANGED)  # BGRA

if button_img is None:
    raise FileNotFoundError("Gambar tombol tidak ditemukan. Pastikan 'assets/button.png' ada dan path-nya benar.")

# Resize tombol (sesuaikan dengan kebutuhan)
button_img = cv2.resize(button_img, (200, 100))  # (width, height)

btn_h, btn_w, btn_c = button_img.shape

# Posisi awal tombol
button_x = 200
button_y = 200

# Skor
score = 0

# Cooldown biar gak spam hit dalam beberapa frame
hit_cooldown = 0
HIT_COOLDOWN_MAX = 10  # dalam jumlah frame


def overlay_png(bg, png, x, y):
    """
    Gambar PNG (BGRA) di atas background (BGR) dengan alpha blending.
    bg : frame dari kamera (BGR)
    png: gambar tombol (BGRA)
    (x, y): posisi kiri-atas tombol
    """
    h, w, _ = png.shape

    # Cek batas frame, kalau kelewatan jangan digambar
    if x < 0 or y < 0 or x + w > bg.shape[1] or y + h > bg.shape[0]:
        return bg

    roi = bg[y:y+h, x:x+w]

    # Pisah BGR dan alpha
    bgr = png[..., :3]
    alpha = png[..., 3:] / 255.0  # (h,w,1) float 0-1

    # Alpha blending
    roi = (alpha * bgr + (1 - alpha) * roi).astype(np.uint8)

    bg[y:y+h, x:x+w] = roi
    return bg


# =========================
# 2. SETUP MEDIAPIPE HANDS
# =========================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.6
)

# =========================
# 3. SETUP KAMERA
# =========================

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Kamera tidak dapat diakses.")
    exit()

print("Tekan 'q' untuk keluar.")

# =========================
# 4. MAIN LOOP
# =========================

while True:
    success, frame = cap.read()
    if not success:
        break

    # Simpan ukuran frame
    h_frame, w_frame, _ = frame.shape

    # Mirror supaya lebih natural
    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Proses Mediapipe
    results = hands.process(frame_rgb)

    # Kurangi cooldown setiap frame
    if hit_cooldown > 0:
        hit_cooldown -= 1

    # Jika tangan terdeteksi
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # Gambar landmark & koneksi
            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing.DrawingSpec(color=(0, 255, 0), thickness=2, circle_radius=2),
                mp_drawing.DrawingSpec(color=(0, 0, 255), thickness=2)
            )

            # Ambil koordinat ujung telunjuk (ID 8)
            h, w, c = frame.shape
            cx = int(hand_landmarks.landmark[8].x * w)
            cy = int(hand_landmarks.landmark[8].y * h)

            # Gambar lingkaran di ujung telunjuk
            cv2.circle(frame, (cx, cy), 10, (255, 255, 0), cv2.FILLED)

            # =========================
            # 5. LOGIKA SENTUH TOMBOL
            # =========================

            # Cek apakah telunjuk berada di area bounding tombol
            if (button_x <= cx < button_x + btn_w) and (button_y <= cy < button_y + btn_h):
                # Koordinat lokal relatif terhadap gambar tombol
                local_x = cx - button_x
                local_y = cy - button_y

                # Cek alpha di pixel tersebut (hanya kena kalau bukan area transparan)
                alpha_value = button_img[local_y, local_x, 3]  # channel alpha

                # Tambah skor hanya jika:
                # - pixel tombol tidak transparan
                # - cooldown sudah habis
                if alpha_value > 10 and hit_cooldown == 0:
                    score += 1
                    print(f"Kena tombol! Skor: {score}")

                    # Set cooldown
                    hit_cooldown = HIT_COOLDOWN_MAX

                    # Acak posisi tombol baru
                    button_x = random.randint(0, max(0, w_frame - btn_w))
                    button_y = random.randint(0, max(0, h_frame - btn_h))

    # =========================
    # 6. GAMBAR TOMBOL & SKOR
    # =========================

    frame = overlay_png(frame, button_img, button_x, button_y)

    cv2.putText(
        frame,
        f'Skor: {score}',
        (30, 80),
        cv2.FONT_HERSHEY_DUPLEX,
        2,
        (255, 255, 255),
        2
    )

    cv2.imshow("Game Tombol dengan Hand Tracking", frame)

    # Keluar jika tekan 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Bersihkan resource
cap.release()
cv2.destroyAllWindows()