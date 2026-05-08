"""
sound.py — Sistem suara prosedural (tanpa file audio eksternal).
Suara di-generate dari gelombang sinus/kotak/noise pakai array + pygame.mixer.
Inspired by Harvest Moon & Octopath Traveller SFX style.
"""
import pygame
import array
import math
import random

_RATE = 22050
_CHANNELS = 1  # mono

# ─── Gelombang dasar ──────────────────────────────────────
def _wave(freq: float, dur_ms: int, vol: float = 0.35, shape: str = 'sine') -> pygame.mixer.Sound:
    n = max(1, int(_RATE * dur_ms / 1000))
    fade = min(n // 4, int(_RATE * 0.015))
    buf = array.array('h', [0] * n)
    for i in range(n):
        t = i / _RATE
        if shape == 'sine':
            v = math.sin(2 * math.pi * freq * t)
        elif shape == 'square':
            v = 0.6 if math.sin(2 * math.pi * freq * t) > 0 else -0.6
        elif shape == 'tri':
            phase = (freq * t) % 1.0
            v = 4 * abs(phase - 0.5) - 1.0
        elif shape == 'noise':
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * freq * t)
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        buf[i] = int(min(32767, max(-32767, vol * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)


def _sweep(f0: float, f1: float, dur_ms: int, vol: float = 0.3) -> pygame.mixer.Sound:
    """Frequency sweep f0 → f1."""
    n = max(1, int(_RATE * dur_ms / 1000))
    fade = min(n // 4, int(_RATE * 0.015))
    buf = array.array('h', [0] * n)
    phase = 0.0
    for i in range(n):
        freq = f0 + (f1 - f0) * (i / n)
        phase += 2 * math.pi * freq / _RATE
        v = math.sin(phase)
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        buf[i] = int(min(32767, max(-32767, vol * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)


def _chord(freqs: list, dur_ms: int, vol: float = 0.3) -> pygame.mixer.Sound:
    """Beberapa nada sekaligus (akord)."""
    n = max(1, int(_RATE * dur_ms / 1000))
    fade = min(n // 4, int(_RATE * 0.02))
    buf = array.array('h', [0] * n)
    per = vol / max(1, len(freqs))
    for i in range(n):
        t = i / _RATE
        v = sum(math.sin(2 * math.pi * f * t) for f in freqs)
        env = 1.0
        if i < fade:
            env = i / fade
        elif i > n - fade:
            env = (n - i) / fade
        buf[i] = int(min(32767, max(-32767, per * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)


def _mix(sounds: list, dur_ms: int) -> pygame.mixer.Sound:
    """Mix beberapa sound sekaligus dalam satu buffer."""
    n = max(1, int(_RATE * dur_ms / 1000))
    buf = array.array('h', [0] * n)
    per = 1.0 / max(1, len(sounds))
    for s in sounds:
        raw = pygame.sndarray.array(s)
        for i in range(min(n, len(raw))):
            buf[i] = int(min(32767, max(-32767, buf[i] + raw[i] * per)))
    return pygame.mixer.Sound(buffer=buf)


# ─── Registry suara ───────────────────────────────────────
SOUNDS: dict = {}
_enabled: bool = False


def init_sound() -> bool:
    """Inisialisasi mixer. Return True jika berhasil."""
    global _enabled
    try:
        pygame.mixer.pre_init(_RATE, -16, _CHANNELS, 512)
        pygame.mixer.init()
        _enabled = True
        return True
    except Exception as e:
        print(f"[Sound] Mixer gagal: {e}")
        _enabled = False
        return False


def build_sounds():
    """Generate semua SFX. Panggil setelah pygame.init() + init_sound()."""
    global SOUNDS, _enabled
    if not _enabled:
        return
    try:
        SOUNDS.update({
            # Langkah kaki (pendek & tipis)
            'step_grass': _wave(190, 42, 0.10, 'noise'),
            'step_dirt':  _wave(140, 52, 0.13, 'noise'),
            'step_path':  _wave(360, 38, 0.11, 'noise'),
            'step_floor': _wave(480, 35, 0.09, 'noise'),

            # Alat pertanian
            'hoe':    _wave(105, 95, 0.36, 'square'),
            'water':  _sweep(720, 240, 170, 0.26),
            'plant':  _wave(440, 65, 0.20, 'sine'),
            'harvest':_chord([523, 659, 784], 230, 0.30),
            'axe':    _wave(88, 115, 0.40, 'square'),

            # Interaksi NPC / hadiah
            'gift':   _chord([440, 554, 659], 210, 0.26),
            'dialog': _wave(860, 32, 0.11, 'sine'),

            # Notifikasi & UI
            'notif':      _chord([523, 784], 165, 0.20),
            'quest':      _chord([392, 494, 587, 784], 440, 0.36),
            'blocked':    _wave(175, 95, 0.16, 'square'),
            'menu_move':  _wave(630, 26, 0.09, 'sine'),
            'menu_select':_chord([440, 550], 85, 0.16),

            # Toko & upgrade
            'buy':  _sweep(370, 590, 105, 0.26),
            'sell': _chord([660, 880], 160, 0.26),

            # Tidur & pagi hari
            'sleep':  _sweep(450, 215, 560, 0.26),
            'morning':_chord([261, 329, 392, 523], 580, 0.30),

            # Supernatural
            'capture': _sweep(275, 740, 330, 0.36),
            'magic':   _chord([330, 415, 523], 280, 0.22),

            # Pemulihan energi
            'heal': _sweep(330, 560, 210, 0.20),

            # Ambient (volume rendah)
            'fire_crackle': _wave(75, 130, 0.06, 'noise'),
        })
    except Exception as e:
        _enabled = False
        print(f"[Sound] Build gagal: {e}")


# Cooldown per-sound agar tidak terlalu sering berbunyi (ms)
_cooldowns: dict = {}
_CD_DEFAULTS = {
    'step_grass': 200, 'step_dirt': 200, 'step_path': 200, 'step_floor': 200,
    'fire_crackle': 1200,
}


def play(name: str, volume: float = 1.0):
    """Mainkan suara. Gagal diam jika mixer tidak tersedia."""
    if not _enabled or name not in SOUNDS:
        return
    now = pygame.time.get_ticks()
    cd = _CD_DEFAULTS.get(name, 0)
    if cd and now < _cooldowns.get(name, 0):
        return
    if cd:
        _cooldowns[name] = now + cd
    try:
        s = SOUNDS[name]
        s.set_volume(max(0.0, min(1.0, volume)))
        s.play()
    except Exception:
        pass


def get_step_sound(tile_name: str) -> str:
    """Return nama suara langkah berdasarkan tipe tile."""
    if tile_name in ('grass',):
        return 'step_grass'
    elif tile_name in ('dirt', 'tilled_dry', 'tilled_wet'):
        return 'step_dirt'
    elif tile_name in ('path',):
        return 'step_path'
    elif tile_name in ('floor',):
        return 'step_floor'
    return 'step_grass'
