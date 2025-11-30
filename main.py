import cv2
import mediapipe as mp
import numpy as np
import pygame  # untuk quit mixer di akhir

from src.config import (
    WINDOW_NAME,
    HEADER_BUTTON_PATH, PLAY_BUTTON_PATH,
    CAT_BUAH_PATH, CAT_HEWAN_PATH, CAT_KENDARAAN_PATH,
    PLAY_AGAIN_PATH, PILIH_KATEGORI_PATH,
    REPEAT_AUDIO_PATH,
    STATE_HOME, STATE_CATEGORY, STATE_GAME, STATE_RESULT,
    QUESTION_DELAY_MS,
)
from src.audio_manager import (
    play_click_sfx, play_correct, play_wrong,
    play_applause, play_boo,
    update_bgm_for_state, AUDIO_OK,
)
from src.graphics import (
    load_button_image, overlay_png, draw_button_with_effect,
    point_on_png_button, put_text_with_outline,
    load_all_answer_assets,
)
from src.game_logic import (
    build_questions_for_category, setup_question,
)
from src.utils import now_ms, can_interact, set_cooldown

# =========================
# LOAD ASSET IMAGE
# =========================

header_btn = load_button_image(HEADER_BUTTON_PATH, size=(400, 100))
play_btn   = load_button_image(PLAY_BUTTON_PATH,   size=(260, 100))

CAT_BTN_SIZE = (380, 130)
cat_buah_btn      = load_button_image(CAT_BUAH_PATH,      CAT_BTN_SIZE)
cat_hewan_btn     = load_button_image(CAT_HEWAN_PATH,     CAT_BTN_SIZE)
cat_kendaraan_btn = load_button_image(CAT_KENDARAAN_PATH, CAT_BTN_SIZE)

kategori_header_btn = load_button_image(PILIH_KATEGORI_PATH, size=(400, 100))

REPEAT_BTN_SIZE = (260, 80)
repeat_audio_btn = load_button_image(REPEAT_AUDIO_PATH, REPEAT_BTN_SIZE)

PLAY_AGAIN_BTN_SIZE = (320, 110)
play_again_btn = load_button_image(PLAY_AGAIN_PATH, PLAY_AGAIN_BTN_SIZE)

ALL_ANSWER_ASSETS = load_all_answer_assets()

# =========================
# STATE & VARIABEL GAME
# =========================

state = STATE_HOME
selected_category = None

score = 0
questions = []
current_q_index = 0

current_q = None
correct_answer = None
answer_buttons = []

question_sound = None
question_start_time = 0
audio_initial_played = False
repeat_used = False
result_sound_played = False

question_answered = False
question_transition_deadline = None

print("Tekan 'q' untuk keluar.")

# =========================
# SETUP MEDIAPIPE & KAMERA
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
# MAIN LOOP
# =========================

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    h_frame, w_frame, _ = frame.shape
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = hands.process(frame_rgb)

    fingertip = None

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
            break

    header_x = (w_frame - header_btn.shape[1]) // 2
    header_y = 20

    # ---------- STATE HOME ----------
    if state == STATE_HOME:
        frame = overlay_png(frame, header_btn, header_x, header_y)

        play_x = (w_frame - play_btn.shape[1]) // 2
        play_y = int(h_frame * 0.7)
        frame = draw_button_with_effect(frame, play_btn, play_x, play_y, fingertip)

        if fingertip and can_interact():
            if point_on_png_button(fingertip[0], fingertip[1], play_x, play_y, play_btn):
                play_click_sfx()
                set_cooldown()
                print("[INFO] Play ditekan → masuk menu kategori")
                state = STATE_CATEGORY

    # ---------- STATE CATEGORY ----------
    elif state == STATE_CATEGORY:
        cat_header_x = (w_frame - kategori_header_btn.shape[1]) // 2
        frame = overlay_png(frame, kategori_header_btn, cat_header_x, header_y)

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
            frame = draw_button_with_effect(frame, btn_img, x, y, fingertip)

            if fingertip and can_interact():
                if point_on_png_button(fingertip[0], fingertip[1], x, y, btn_img):
                    selected_category = key
                    play_click_sfx()
                    set_cooldown()
                    print(f"[INFO] Kategori dipilih: {selected_category}")

                    score = 0
                    questions = build_questions_for_category(selected_category)
                    current_q_index = 0

                    (
                        current_q,
                        correct_answer,
                        answer_buttons,
                        question_sound,
                        question_start_time,
                        audio_initial_played,
                        repeat_used,
                        question_answered,
                        question_transition_deadline,
                    ) = setup_question(selected_category, current_q_index, questions, ALL_ANSWER_ASSETS)

                    state = STATE_GAME

            x += btn_img.shape[1] + 60

        if selected_category:
            put_text_with_outline(
                frame,
                f"Terpilih: {selected_category}",
                (40, h_frame - 40),
                cv2.FONT_HERSHEY_DUPLEX,
                1.0,
                (255, 255, 255),
                2,
                (0, 0, 0)
            )

    # ---------- STATE GAME ----------
    elif state == STATE_GAME:
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

        t_now = now_ms()
        if not audio_initial_played and question_sound is not None:
            if t_now - question_start_time >= 2000:
                question_sound.play()
                audio_initial_played = True

        # Opsi jawaban
        if answer_buttons:
            gap_x = 30
            total_width = sum(btn["img"].shape[1] for btn in answer_buttons) + \
                          gap_x * (len(answer_buttons) - 1)

            start_x = int((w_frame - total_width) / 2)
            y_btn   = int(h_frame * 0.65)

            x = start_x
            for btn in answer_buttons:
                img  = btn["img"]
                word = btn["word"]

                frame = draw_button_with_effect(frame, img, x, y_btn, fingertip)

                if (not question_answered) and fingertip and can_interact():
                    if point_on_png_button(fingertip[0], fingertip[1], x, y_btn, img):
                        play_click_sfx()
                        set_cooldown()
                        print(f"[JAWAB] {word}")

                        if word == correct_answer:
                            score += 1
                            play_correct()
                            print("[HASIL] Benar!")
                        else:
                            play_wrong()
                            print("[HASIL] Salah!")

                        question_answered = True
                        question_transition_deadline = now_ms() + QUESTION_DELAY_MS

                x += img.shape[1] + gap_x

        # Tombol ulangi audio (sebelum dijawab)
        if (not question_answered) and (not repeat_used) and question_sound is not None:
            rx = w_frame - repeat_audio_btn.shape[1] - 30
            ry = 30

            frame = draw_button_with_effect(frame, repeat_audio_btn, rx, ry, fingertip)

            if fingertip and can_interact():
                if point_on_png_button(fingertip[0], fingertip[1], rx, ry, repeat_audio_btn):
                    if audio_initial_played:
                        play_click_sfx()
                        question_sound.play()
                        repeat_used = True
                        set_cooldown()
                        print("[INFO] Audio diulang sekali.")

        # Setelah delay, pindah soal / result
        if question_answered and question_transition_deadline is not None:
            if now_ms() >= question_transition_deadline:
                question_transition_deadline = None
                current_q_index += 1

                if current_q_index < len(questions):
                    (
                        current_q,
                        correct_answer,
                        answer_buttons,
                        question_sound,
                        question_start_time,
                        audio_initial_played,
                        repeat_used,
                        question_answered,
                        question_transition_deadline,
                    ) = setup_question(selected_category, current_q_index, questions, ALL_ANSWER_ASSETS)
                else:
                    print("[INFO] Semua soal selesai.")
                    state = STATE_RESULT

    # ---------- STATE RESULT ----------
    elif state == STATE_RESULT:
        if not result_sound_played:
            if score >= 8:      # nilai di atas 7
                play_applause()
                print("[RESULT] Applause!")
            else:
                play_boo()
                print("[RESULT] Boo!")
            result_sound_played = True

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

        btn_x = (w_frame - play_again_btn.shape[1]) // 2
        btn_y = int(h_frame * 0.72)

        frame = draw_button_with_effect(frame, play_again_btn, btn_x, btn_y, fingertip)

        if fingertip and can_interact():
            if point_on_png_button(fingertip[0], fingertip[1], btn_x, btn_y, play_again_btn):
                play_click_sfx()
                set_cooldown()
                print("[INFO] Mainkan lagi ditekan → kembali ke menu kategori")

                score = 0
                selected_category = None
                questions = []
                current_q_index = 0
                current_q = None
                correct_answer = None
                question_sound = None
                audio_initial_played = False
                repeat_used = False
                result_sound_played = False
                question_answered = False
                question_transition_deadline = None

                state = STATE_CATEGORY

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
