"""
sound.py — Sistem suara prosedural (tanpa file audio eksternal).
Menggunakan pygame.mixer untuk men-generate dan memutar suara retro di Ursina.
"""
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import array
import math
import random
import time

_RATE = 22050
_CHANNELS = 1  # mono

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
        elif shape == 'noise':
            v = random.uniform(-1, 1)
        else:
            v = math.sin(2 * math.pi * freq * t)
        env = (i / fade) if i < fade else ((n - i) / fade if i > n - fade else 1.0)
        buf[i] = int(min(32767, max(-32767, vol * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)

def _sweep(f0: float, f1: float, dur_ms: int, vol: float = 0.3) -> pygame.mixer.Sound:
    n = max(1, int(_RATE * dur_ms / 1000))
    fade = min(n // 4, int(_RATE * 0.015))
    buf = array.array('h', [0] * n)
    phase = 0.0
    for i in range(n):
        freq = f0 + (f1 - f0) * (i / n)
        phase += 2 * math.pi * freq / _RATE
        v = math.sin(phase)
        env = (i / fade) if i < fade else ((n - i) / fade if i > n - fade else 1.0)
        buf[i] = int(min(32767, max(-32767, vol * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)

def _chord(freqs: list, dur_ms: int, vol: float = 0.3) -> pygame.mixer.Sound:
    n = max(1, int(_RATE * dur_ms / 1000))
    fade = min(n // 4, int(_RATE * 0.02))
    buf = array.array('h', [0] * n)
    per = vol / max(1, len(freqs))
    for i in range(n):
        t = i / _RATE
        v = sum(math.sin(2 * math.pi * f * t) for f in freqs)
        env = (i / fade) if i < fade else ((n - i) / fade if i > n - fade else 1.0)
        buf[i] = int(min(32767, max(-32767, per * 32767 * v * env)))
    return pygame.mixer.Sound(buffer=buf)

SOUNDS: dict = {}
_enabled: bool = False

def init_sound() -> bool:
    global _enabled
    try:
        pygame.mixer.pre_init(_RATE, -16, _CHANNELS, 512)
        pygame.mixer.init()
        _enabled = True
        return True
    except Exception as e:
        print(f"[Sound] Mixer gagal: {e}")
        return False

def build_sounds():
    global SOUNDS, _enabled
    if not _enabled: return
    try:
        SOUNDS.update({
            'step_grass': _wave(190, 42, 0.10, 'noise'),
            'step_dirt':  _wave(140, 52, 0.13, 'noise'),
            'step_path':  _wave(360, 38, 0.11, 'noise'),
            'step_floor': _wave(480, 35, 0.09, 'noise'),
            'hoe':        _wave(105, 95, 0.36, 'square'),
            'water':      _sweep(720, 240, 170, 0.26),
            'plant':      _wave(440, 65, 0.20, 'sine'),
            'harvest':    _chord([523, 659, 784], 230, 0.30),
            'axe':        _wave(88, 115, 0.40, 'square'),
            'sword':      _sweep(800, 300, 100, 0.30),
            'gift':       _chord([440, 554, 659], 210, 0.26),
            'dialog':     _wave(860, 32, 0.11, 'sine'),
            'notif':      _chord([523, 784], 165, 0.20),
            'quest':      _chord([392, 494, 587, 784], 440, 0.36),
            'blocked':    _wave(175, 95, 0.16, 'square'),
            'menu_move':  _wave(630, 26, 0.09, 'sine'),
            'menu_select':_chord([440, 550], 85, 0.16),
            'buy':        _sweep(370, 590, 105, 0.26),
            'sell':       _chord([660, 880], 160, 0.26),
            'sleep':      _sweep(450, 215, 560, 0.26),
            'morning':    _chord([261, 329, 392, 523], 580, 0.30),
            'capture':    _sweep(275, 740, 330, 0.36),
            'heal':       _sweep(330, 560, 210, 0.20),
        })
    except Exception:
        _enabled = False

_cooldowns: dict = {}
_CD_DEFAULTS = {'step_grass': 320, 'step_dirt': 320, 'step_path': 320, 'step_floor': 320}

def play(name: str, volume: float = 1.0):
    if not _enabled or name not in SOUNDS: return
    now = time.time() * 1000
    cd = _CD_DEFAULTS.get(name, 0)
    if cd and now < _cooldowns.get(name, 0): return
    if cd: _cooldowns[name] = now + cd
    try:
        s = SOUNDS[name]
        s.set_volume(max(0.0, min(1.0, volume)))
        s.play()
    except Exception: pass

def get_step_sound(tile_name: str) -> str:
    if tile_name in ('grass',): return 'step_grass'
    elif tile_name in ('dirt', 'tilled_dry', 'tilled_wet'): return 'step_dirt'
    elif tile_name in ('path_stone',): return 'step_path'
    elif tile_name in ('floor_wood', 'cave_floor'): return 'step_floor'
    return 'step_grass'