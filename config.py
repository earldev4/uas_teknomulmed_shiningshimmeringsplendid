import os

# =========================
# KONSTANTA & PATH ASSET
# =========================

HEADER_BUTTON_PATH = os.path.join("assets", "image", "buttons", "Guess The Word.png")
PLAY_BUTTON_PATH   = os.path.join("assets", "image", "buttons", "Play.png")
CAT_BUAH_PATH      = os.path.join("assets", "image", "buttons", "Kategori - Buah.png")
CAT_HEWAN_PATH     = os.path.join("assets", "image", "buttons", "Kategori - Hewan.png")
CAT_KENDARAAN_PATH = os.path.join("assets", "image", "buttons", "Kategori - Kendaraan.png")
PLAY_AGAIN_PATH    = os.path.join("assets", "image", "buttons", "Mainkan Lagi.png")
PILIH_KATEGORI_PATH = os.path.join("assets", "image", "buttons", "Pilih Kategori.png")

# Folder semua tombol jawaban
ANSWER_BUTTONS_DIR = os.path.join("assets", "image", "buttons")

# Button ulangi audio
REPEAT_AUDIO_PATH = os.path.join("assets", "image", "buttons", "Ulang Suara.png")

# Audio
BGM_MENU_PATH     = os.path.join("assets", "audio", "BG NCS.mp3")
SFX_CLICK_PATH    = os.path.join("assets", "audio", "Button Pressed.mp3")
SFX_CORRECT_PATH  = os.path.join("assets", "audio", "Correct.mp3")
SFX_WRONG_PATH    = os.path.join("assets", "audio", "Wrong.mp3")

# Root audio soal
PITCH_AUDIO_ROOT = os.path.join("pitch_audio")

WINDOW_NAME = "Guess The Word Filter"

STATE_HOME     = "home"
STATE_CATEGORY = "category"
STATE_GAME     = "game"
STATE_RESULT   = "result"

# Cooldown berbasis waktu (ms)
BUTTON_COOLDOWN_MS = 2000   # 2 detik: setelah klik tombol, tombol lain tidak merespons
QUESTION_DELAY_MS  = 2500   # 2.5 detik: delay sebelum pindah ke soal berikutnya

# =========================
# DATA SOAL PER KATEGORI
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
