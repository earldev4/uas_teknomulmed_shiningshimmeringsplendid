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