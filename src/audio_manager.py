import os
import pygame

from .config import (
    BGM_MENU_PATH,
    SFX_CLICK_PATH,
    SFX_CORRECT_PATH,
    SFX_WRONG_PATH,
    STATE_HOME,
    STATE_CATEGORY,
    SFX_APPLAUSE_PATH, 
    SFX_BOO_PATH
)

AUDIO_OK = False
bgm_available = False
click_sfx = None
correct_sfx = None
wrong_sfx = None
applause_sfx = None
boo_sfx = None


# =========================
# INIT AUDIO
# =========================

try:
    pygame.mixer.init()
    AUDIO_OK = True

    if os.path.exists(BGM_MENU_PATH):
        pygame.mixer.music.load(BGM_MENU_PATH)
        bgm_available = True
    else:
        print("[AUDIO] File BGM tidak ditemukan, skip backsong.")

    if os.path.exists(SFX_CLICK_PATH):
        click_sfx = pygame.mixer.Sound(SFX_CLICK_PATH)
    else:
        print("[AUDIO] File SFX click tidak ditemukan.")

    if os.path.exists(SFX_CORRECT_PATH):
        correct_sfx = pygame.mixer.Sound(SFX_CORRECT_PATH)
    else:
        print("[AUDIO] File SFX benar tidak ditemukan.")

    if os.path.exists(SFX_WRONG_PATH):
        wrong_sfx = pygame.mixer.Sound(SFX_WRONG_PATH)
    else:
        print("[AUDIO] File SFX salah tidak ditemukan.")
    
    if os.path.exists(SFX_APPLAUSE_PATH):
        applause_sfx = pygame.mixer.Sound(SFX_APPLAUSE_PATH)
    else:
        print("[AUDIO] File applause tidak ditemukan.")

    if os.path.exists(SFX_BOO_PATH):
        boo_sfx = pygame.mixer.Sound(SFX_BOO_PATH)
    else:
        print("[AUDIO] File boo tidak ditemukan.")

except Exception as e:
    print("[AUDIO] Gagal inisialisasi audio:", e)
    AUDIO_OK = False


def play_click_sfx():
    if AUDIO_OK and click_sfx is not None:
        click_sfx.play()


def play_correct():
    if AUDIO_OK and correct_sfx is not None:
        correct_sfx.play()


def play_wrong():
    if AUDIO_OK and wrong_sfx is not None:
        wrong_sfx.play()

def play_applause():
    if AUDIO_OK and applause_sfx is not None:
        applause_sfx.play()

def play_boo():
    if AUDIO_OK and boo_sfx is not None:
        boo_sfx.play()

def update_bgm_for_state(state):
    if not (AUDIO_OK and bgm_available):
        return

    if state in (STATE_HOME, STATE_CATEGORY):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.play(-1)  # loop
    else:
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
