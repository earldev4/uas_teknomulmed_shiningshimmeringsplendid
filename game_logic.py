import os
import random
import pygame

from config import CATEGORY_DATA
from audio_manager import AUDIO_OK
from utils import now_ms

def build_questions_for_category(cat_key):
    """
    Bangun list 10 soal (5 ID, 5 EN) untuk kategori tertentu.
    """
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


def setup_question(cat_key, index, questions, all_answer_assets):
    """
    Siapkan soal ke-index, load audio & opsi jawaban dari asset PNG.
    Mengembalikan:
      current_q, correct_answer, answer_buttons,
      question_sound, question_start_time,
      audio_initial_played, repeat_used,
      question_answered, question_transition_deadline
    """
    assets_for_cat = all_answer_assets.get(cat_key, [])
    if not assets_for_cat:
        print("[ASSET] Tidak ada asset jawaban untuk kategori:", cat_key)

    current_q = questions[index]
    correct_answer = current_q["word"]

    correct_btn = None
    wrong_btns = []
    for item in assets_for_cat:
        if item["word"] == correct_answer:
            correct_btn = item
        else:
            wrong_btns.append(item)

    if correct_btn is None:
        print(f"[WARN] Tidak ketemu asset untuk kata '{correct_answer}' di kategori '{cat_key}'")
        answer_buttons = random.sample(assets_for_cat, min(4, len(assets_for_cat)))
    else:
        if len(wrong_btns) >= 3:
            wrong_btns = random.sample(wrong_btns, 3)
        answer_buttons = wrong_btns + [correct_btn]
        random.shuffle(answer_buttons)

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

    question_answered = False
    question_transition_deadline = None

    print(f"[SOAL] Q{index+1}: {correct_answer} ({current_q['lang']})")

    return (
        current_q,
        correct_answer,
        answer_buttons,
        question_sound,
        question_start_time,
        audio_initial_played,
        repeat_used,
        question_answered,
        question_transition_deadline,
    )
