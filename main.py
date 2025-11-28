import cv2
import mediapipe as mp
import numpy as np
import os
import pygame

# =========================
# 1. KONSTANTA & AUDIO
# =========================

HEADER_BUTTON_PATH = os.path.join("assets", "image", "buttons", "Guess The Word.png")
PLAY_BUTTON_PATH   = os.path.join("assets", "image", "buttons", "Play.png")
CAT_BUAH_PATH      = os.path.join("assets", "image", "buttons", "Kategori - Buah.png")
CAT_HEWAN_PATH     = os.path.join("assets", "image", "buttons", "Kategori - Hewan.png")
CAT_KENDARAAN_PATH = os.path.join("assets", "image", "buttons", "Kategori - Kendaraan.png")

# Dummy path audio – nanti kamu ganti ke file asli
BGM_MENU_PATH  = os.path.join("assets", "audio", "BG NCS.mp3")
SFX_CLICK_PATH = os.path.join("assets", "audio", "Button Pressed.mp3")

WINDOW_NAME = "Guess The Word Filter"

STATE_HOME     = "home"
STATE_CATEGORY = "category"
STATE_GAME     = "game"   # nanti dipakai saat permainan dimulai

# Cooldown sentuh tombol biar gak dobel-dobel
HIT_COOLDOWN_MAX = 8
hit_cooldown = 30   # sedikit delay di awal supaya tidak auto-klik PLAY

# =========================
# 1a. INIT AUDIO (pygame)
# =========================

AUDIO_OK = False
bgm_available = False
click_sfx = None

try:
    pygame.mixer.init()
    AUDIO_OK = True

    if os.path.exists(BGM_MENU_PATH):
        pygame.mixer.music.load(BGM_MENU_PATH)
        bgm_available = True
    else:
        print("[AUDIO] File BGM tidak ditemukan (dummy), skip backsong.")

    if os.path.exists(SFX_CLICK_PATH):
        click_sfx = pygame.mixer.Sound(SFX_CLICK_PATH)
    else:
        print("[AUDIO] File SFX click tidak ditemukan (dummy), skip efek klik.")

except Exception as e:
    print("[AUDIO] Gagal inisialisasi audio:", e)
    AUDIO_OK = False


def play_click_sfx():
    if AUDIO_OK and click_sfx is not None:
        click_sfx.play()


def update_bgm_for_state(state):
    """
    HOME + CATEGORY  -> BGM menyala (loop)
    STATE lain (misal GAME) -> BGM mati
    """
    if not (AUDIO_OK and bgm_available):
        return

    if state in (STATE_HOME, STATE_CATEGORY):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)  # loop
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()