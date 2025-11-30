import time
from config import BUTTON_COOLDOWN_MS

last_hit_time = 0  # timestamp terakhir kena klik


def now_ms():
    return int(time.time() * 1000)


def can_interact():
    """True kalau sudah lewat cooldown tombol."""
    return now_ms() - last_hit_time >= BUTTON_COOLDOWN_MS


def set_cooldown():
    global last_hit_time
    last_hit_time = now_ms()
