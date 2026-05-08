"""
╔══════════════════════════════════════════════════════════════╗
║            🌱  LEMBAH KARSA  🌾                             ║
║         Farming RPG bergaya Harvest Moon SNES                ║
║              Python + Pygame Edition                         ║
╚══════════════════════════════════════════════════════════════╝

Cara menjalankan:
    1. Install Python 3.8+
    2. Install pygame:  pip install pygame
    3. Jalankan:        python lembah_karsa.py

Kontrol:
    WASD / Arrow Keys  - Gerak
    SPACE              - Pakai alat aktif
    E / Enter          - Interaksi / Lanjut dialog
    1-7                - Pilih alat (termasuk pancing)
    Q / R              - Ganti jenis benih
    T                  - Tidur (dekat rumah)
    F                  - Tangkap makhluk halus (Fitur V4)
    I                  - Buka Inventori
    ESC                - Menu utama
    F5                 - Save game

Dependencies: pygame (pip install pygame)
Python 3.8+
"""

import pygame
import sys
import os
import json
import random
import math
from dataclasses import dataclass, field
from typing import Optional

# ══════════════════════════════════════════════════════════════
#  KONFIGURASI
# ══════════════════════════════════════════════════════════════
TILE = 48                      # ukuran tile DIPERBESAR (Gaya Retro 3x)
SPRITE = 16                    # ukuran sprite asli (pixel art 16x16)
SCALE = TILE // SPRITE         # faktor scaling (3x)
VIEW_W = 18                    # viewport lebar
VIEW_H = 12                    # viewport tinggi
SCREEN_W = VIEW_W * TILE       # 640
SCREEN_H = VIEW_H * TILE + 80  # extra untuk HUD
FPS = 30

SAVE_FILE = "lembah_karsa_save.json"

# Pygame colors (RGB)
class C:
    # Transparan
    T = None  # pygame alpha handled separately
    # Rumput
    g0, g1, g2, g3 = (45,107,48), (61,138,64), (77,160,80), (30,72,32)
    # Tanah
    d0, d1, d2, d3 = (90,58,24), (122,82,40), (106,72,32), (74,48,16)
    dw = (74,90,40)
    # Air
    w0, w1, w2 = (24,72,168), (32,104,208), (96,160,240)
    # Jalan batu
    p0, p1, p2 = (128,112,96), (160,144,128), (96,88,72)
    # Kayu
    wo0, wo1, wo2 = (122,80,32), (90,56,16), (154,112,56)
    # Atap merah
    r0, r1, r2 = (192,56,48), (160,32,32), (224,112,96)
    # Dinding beige
    b0, b1, b2 = (208,168,112), (184,136,80), (232,200,152)
    # Kulit
    sk, sk2, sk3 = (248,200,144), (224,160,104), (248,224,192)
    # Rambut
    h0, h1, h2 = (96,40,16), (128,64,32), (58,24,8)
    # Baju
    s0, s1, s2 = (48,80,160), (32,64,128), (96,128,200)
    pn, pn2 = (64,96,48), (48,72,32)
    ht, ht2 = (248,208,32), (208,168,16)
    # Tanaman warna
    cg, cg2 = (128,224,64), (80,176,32)
    cy = (248,224,32)
    cr, co, cp = (240,56,24), (248,112,32), (192,128,240)
    # Furniture
    fn, fn2, fn3 = (96,64,32), (64,40,16), (128,88,48)
    # UI
    wt, bk, gl = (255,255,255), (16,8,8), (248,216,48)
    # Lantai indoor
    fl, fl2, fl3 = (176,144,96), (160,128,80), (200,168,112)
    # Pasir Pantai
    sd0, sd1, sd2 = (240,220,150), (220,200,130), (250,230,160)
    wl, wl2 = (200,184,152), (184,168,136)
    # Fire
    fire1, fire2, fire3 = (255,68,0), (255,136,0), (255,204,0)
    # NPC clothes
    nc_sari = (192,40,64)
    nc_raka = (240,240,224)
    nc_maya = (144,32,192)
    nc_budi = (72,72,72)
    ng = (160,160,144)
    # UI background
    ui_bg = (20,10,35)
    ui_bg2 = (35,20,55)
    ui_border = (120,80,180)
    ui_text = (220,200,255)
    ui_gold = (245,215,80)
    ui_green = (127,255,127)
    ui_red = (255,112,112)
    # --- Tambahan V7 Colors ---
    jin_aura = (180, 120, 255)
    jin_skin = (100, 200, 100)
    demit_dark = (30, 20, 40)
    demit_glow = (255, 50, 50)
    sapi_white = (240, 240, 240)
    sapi_brown = (139, 69, 19)
    # --- Naga Colors ---
    naga_body = (180, 40, 40)
    naga_body_lt = (220, 60, 60)
    naga_body_dk = (120, 20, 20)
    naga_belly = (240, 200, 100)
    naga_scale = (200, 150, 50)
    naga_horn = (220, 220, 200)
    naga_eye = (100, 255, 100)
    naga_whiskers = (255, 220, 80)

# ══════════════════════════════════════════════════════════════
#  PIXEL ART SPRITE GENERATOR (generate semua sprite di memory)
# ══════════════════════════════════════════════════════════════
def make_surface(w=SPRITE, h=SPRITE, fill=None):
    """Buat pygame.Surface 16x16 dengan alpha."""
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    if fill:
        surf.fill(fill)
    return surf

def px(surf, x, y, color):
    if 0 <= x < surf.get_width() and 0 <= y < surf.get_height():
        surf.set_at((x, y), color)

def rect(surf, x1, y1, x2, y2, color):
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            px(surf, x, y, color)

def hline(surf, y, x1, x2, color):
    for x in range(x1, x2+1):
        px(surf, x, y, color)

def vline(surf, x, y1, y2, color):
    for y in range(y1, y2+1):
        px(surf, x, y, color)

def darker(c, amt=40):
    return tuple(max(0, ch - amt) for ch in c[:3])

def lighter(c, amt=30):
    return tuple(min(255, ch + amt) for ch in c[:3])

def outline_sprite(s, color=(20, 10, 20)):
    w, h = s.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(s, (0, 0))
    for y in range(h):
        for x in range(w):
            if s.get_at((x, y))[3] == 0:
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if s.get_at((nx, ny))[3] > 0:
                            out.set_at((x, y), color)
                            break
    return out

def make_cave_wall():
    s = make_surface(fill=(45, 45, 55))
    for y in range(16):
        for x in range(16):
            if x % 6 == 0 or y % 5 == 0:
                px(s, x, y, (30, 30, 40))
            if (x+y) % 7 == 0:
                px(s, x, y, (60, 60, 70))
    return s

# ── TERRAIN SPRITES ────────────────────────────────────────────
def make_grass_tile(seed=42):
    rng = random.Random(seed)
    s = make_surface(fill=C.g1)
    for _ in range(14):
        x, y = rng.randint(0,15), rng.randint(0,15)
        c = rng.choice([C.g0, C.g2, C.g3])
        px(s, x, y, c)
    return s

def make_dirt_tile(seed=43):
    rng = random.Random(seed)
    s = make_surface(fill=C.d1)
    for _ in range(12):
        x, y = rng.randint(0,15), rng.randint(0,15)
        c = rng.choice([C.d0, C.d2, C.d3])
        px(s, x, y, c)
    return s

def make_tilled_dry():
    s = make_surface(fill=C.d0)
    for y in range(16):
        for x in range(16):
            if y % 4 == 0: px(s, x, y, C.d2)
            elif y % 4 == 1: px(s, x, y, C.d1)
            elif y % 4 == 3: px(s, x, y, C.d3)
    return s

def make_tilled_wet():
    s = make_surface(fill=C.d3)
    for y in range(16):
        for x in range(16):
            if y % 4 == 0: px(s, x, y, C.w0)
            elif y % 4 == 1: px(s, x, y, C.d3)
            elif y % 4 == 3: px(s, x, y, C.d2)
    return s

def make_water_tile(frame=0):
    s = make_surface(fill=C.w0)
    for y in range(16):
        for x in range(16):
            if math.sin((x + y*2 + frame*0.5) * 0.7) > 0.3:
                px(s, x, y, C.w2)
            elif (x + y) % 3 == 0:
                px(s, x, y, C.w1)
    return s

def make_sand_tile(seed=45):
    rng = random.Random(seed)
    s = make_surface(fill=C.sd0)
    for _ in range(16):
        x, y = rng.randint(0,15), rng.randint(0,15)
        c = rng.choice([C.sd1, C.sd2])
        px(s, x, y, c)
    return s

def make_path_tile(seed=44):
    rng = random.Random(seed)
    s = make_surface(fill=C.p0)
    for _ in range(16):
        x, y = rng.randint(0,15), rng.randint(0,15)
        c = rng.choice([C.p1, C.p2])
        px(s, x, y, c)
    for x in range(0, 16, 5):
        vline(s, x, 0, 15, C.p2)
    return s

def make_floor_tile():
    s = make_surface(fill=C.fl)
    for y in range(16):
        for x in range(16):
            if x % 8 == 0 or y % 8 == 0: px(s, x, y, C.fl2)
            elif (x + y) % 16 == 7: px(s, x, y, C.fl3)
    return s

def make_wall_tile():
    s = make_surface(fill=C.wl)
    for y in range(16):
        if y % 5 == 0:
            hline(s, y, 0, 15, C.wl2)
        elif y % 5 == 2:
            step = 4 if y < 8 else 0
            for x in range(step, 16, 8):
                px(s, x, y, C.wl2)
    return s

def make_tree():
    s = make_surface()
    # Batang Pohon (Trunk) - bertekstur
    rect(s, 6, 11, 9, 15, C.wo0)
    vline(s, 7, 11, 15, C.wo1)  # Highlight
    vline(s, 9, 11, 15, darker(C.wo0, 20))  # Bayangan
    px(s, 5, 15, C.wo0); px(s, 10, 15, darker(C.wo0, 20)) # Akar kecil
    
    # Daun (Crown) - lebih bervolume
    rect(s, 3, 5, 12, 11, C.g3)
    rect(s, 4, 3, 11, 4, C.g3)
    rect(s, 5, 2, 10, 2, C.g3)
    rect(s, 4, 5, 11, 10, C.g1)
    rect(s, 5, 3, 10, 4, C.g1)
    rect(s, 6, 2, 9, 2, C.g1)
    rect(s, 4, 4, 8, 7, C.g2)
    rect(s, 5, 3, 7, 3, C.g2)
    px(s, 4, 8, C.g0); px(s, 10, 6, C.g0); px(s, 11, 9, C.g0)
    px(s, 6, 10, C.g3); px(s, 9, 10, C.g3); px(s, 5, 5, C.g2); px(s, 7, 4, C.g2)
    px(s, 5, 4, (120, 200, 90)); px(s, 6, 3, (120, 200, 90))
    return outline_sprite(s, color=(20, 30, 20))

def make_fence():
    s = make_surface()
    # Tiang Vertical
    rect(s, 3, 3, 5, 14, C.wo0); rect(s, 10, 3, 12, 14, C.wo0)
    vline(s, 3, 3, 14, C.wo1); vline(s, 10, 3, 14, C.wo1)
    vline(s, 5, 4, 14, darker(C.wo0, 20)); vline(s, 12, 4, 14, darker(C.wo0, 20))
    # Papan Horizontal
    rect(s, 0, 5, 15, 7, C.wo0); rect(s, 0, 10, 15, 12, C.wo0)
    hline(s, 5, 0, 15, C.wo1); hline(s, 10, 0, 15, C.wo1)
    hline(s, 7, 0, 15, darker(C.wo0, 20)); hline(s, 12, 0, 15, darker(C.wo0, 20))
    # Paku
    px(s, 4, 6, (100, 100, 100)); px(s, 11, 6, (100, 100, 100))
    px(s, 4, 11, (100, 100, 100)); px(s, 11, 11, (100, 100, 100))
    return outline_sprite(s, color=(40, 20, 10))

def make_mailbox():
    s = make_surface()
    # Box
    rect(s, 3, 3, 12, 9, C.gl)
    rect(s, 4, 4, 11, 8, C.ht2)
    rect(s, 4, 4, 11, 5, C.ht)
    # Slot
    rect(s, 5, 6, 10, 7, C.bk)
    # Post
    vline(s, 7, 9, 15, C.p0)
    vline(s, 8, 9, 15, C.p1)
    return s

def make_door():
    s = make_surface()
    rect(s, 2, 0, 13, 15, C.wo0)
    hline(s, 0, 2, 13, C.wo2)
    vline(s, 2, 0, 15, C.wo1)
    vline(s, 13, 0, 15, C.wo1)
    rect(s, 4, 2, 11, 7, C.wo2)
    rect(s, 4, 9, 11, 14, C.wo2)
    rect(s, 11, 7, 12, 9, C.gl)
    return s

def make_weed():
    s = make_surface()
    px(s, 5, 11, C.g1); px(s, 4, 10, C.g2); px(s, 3, 9, C.g2)
    px(s, 10, 11, C.g1); px(s, 11, 10, C.g2); px(s, 12, 9, C.g2)
    px(s, 6, 10, C.g0); px(s, 5, 9, C.g1); px(s, 5, 8, C.g2)
    px(s, 9, 10, C.g0); px(s, 10, 9, C.g1); px(s, 10, 8, C.g2)
    rect(s, 7, 8, 8, 14, C.g0)
    vline(s, 7, 7, 13, C.g2)
    px(s, 7, 6, C.g2); px(s, 8, 6, C.g1)
    rect(s, 6, 13, 9, 14, C.g3)
    return outline_sprite(s, color=darker(C.g3, 20))

def make_stone():
    s = make_surface()
    rect(s, 3, 10, 12, 14, (100, 100, 100))
    rect(s, 4, 8, 11, 9, (100, 100, 100))
    rect(s, 4, 9, 11, 13, (140, 140, 140))
    rect(s, 5, 7, 10, 8, (140, 140, 140))
    rect(s, 5, 7, 9, 10, (180, 180, 180))
    px(s, 6, 6, (180, 180, 180)); px(s, 8, 6, (180, 180, 180))
    px(s, 6, 7, (220, 220, 220)); px(s, 7, 8, (220, 220, 220))
    px(s, 10, 10, (80, 80, 80)); px(s, 11, 11, (80, 80, 80))
    px(s, 6, 12, (80, 80, 80)); px(s, 8, 13, (80, 80, 80))
    px(s, 5, 11, (100, 100, 100))
    return outline_sprite(s, color=(60, 60, 60))

def make_tv():
    s = make_surface()
    rect(s, 2, 4, 13, 13, (40, 40, 40))
    rect(s, 3, 5, 12, 11, (100, 180, 220)) # Layar
    px(s, 12, 12, (255, 50, 50)) # Lampu indikator LED
    rect(s, 6, 14, 9, 14, (60, 60, 60)) # Stand TV
    return outline_sprite(s)

# ── CROP SPRITES ────────────────────────────────────────────
def make_crop_sprite(stage, c1, c2):
    s = make_surface()
    if stage == 0:  # tunas
        px(s, 7, 13, C.cg2)
        px(s, 7, 12, C.cg)
        px(s, 6, 12, C.cg2)
        px(s, 8, 12, C.cg2)
    elif stage == 1:  # kecil
        vline(s, 7, 9, 15, C.cg)
        vline(s, 8, 9, 15, C.cg)
        hline(s, 10, 5, 10, C.cg)
        hline(s, 9, 6, 9, c2)
    elif stage == 2:  # medium
        vline(s, 7, 10, 15, C.g0)
        vline(s, 8, 10, 15, C.g0)
        rect(s, 3, 5, 12, 9, c1)
        rect(s, 4, 4, 11, 8, c2)
        rect(s, 5, 3, 10, 7, c1)
        for y in range(6, 10):
            px(s, 2, y, c2)
            px(s, 13, y, c2)
    else:  # siap panen
        vline(s, 7, 11, 15, C.g0)
        vline(s, 8, 11, 15, C.g0)
        rect(s, 2, 3, 13, 10, c1)
        rect(s, 3, 2, 12, 9, c2)
        rect(s, 4, 1, 11, 8, c1)
        rect(s, 5, 2, 10, 7, c2)
        # Sparkle
        for sx, sy in [(3,1),(12,1),(2,5),(13,5)]:
            px(s, sx, sy, C.wt)
        px(s, 6, 3, C.wt)
        px(s, 7, 2, C.wt)
    return s

# ── CHARACTER SPRITE ─────────────────────────────────────────
def make_char(direction, frame, hair=C.h0, shirt=C.s0, pants=C.pn, hat=True, blink=False, role=None):
    if role in ['shop', 'doc', 'smith']:
        hat = False
    s = make_surface()
    
    # 1. HAT / HAIR (Top/Back)
    if hat:
        if role == 'artist':
            rect(s, 4, 1, 10, 3, C.cp)
            px(s, 11, 2, C.cp)
            px(s, 5, 0, C.cp); px(s, 6, 0, C.cp)
            px(s, 6, 1, lighter(C.cp, 20)); px(s, 7, 1, lighter(C.cp, 20))
        else:
            rect(s, 4, 1, 11, 1, darker(C.ht, 30))
            rect(s, 5, 0, 10, 0, C.ht)
            rect(s, 4, 1, 11, 2, C.ht)
            rect(s, 3, 2, 12, 2, C.ht2)
            rect(s, 4, 3, 11, 3, darker(C.ht2, 20))
            hline(s, 2, 5, 10, (180, 40, 40)) # Pita merah topi jerami
            
    head_top = 3 if hat else 2
    
    # 2. HEAD & FACE
    rect(s, 4, head_top, 11, 7, C.sk)
    px(s, 4, 6, lighter(C.sk, 10))
    px(s, 11, 6, lighter(C.sk, 10))
    px(s, 5, 6, (255, 150, 150)) # Blush pipi merona
    px(s, 10, 6, (255, 150, 150))
    
    if role == 'smith':
        hline(s, head_top, 4, 11, (200, 40, 40)) # Ikat kepala merah
        px(s, 3, head_top+1, (200, 40, 40))
        px(s, 12, head_top+1, (200, 40, 40))
        
    if direction == "up":
        rect(s, 4, head_top, 11, head_top+2, hair)
        px(s, 5, head_top, lighter(hair, 20))
        px(s, 9, head_top, lighter(hair, 20))
        if role in ['shop', 'artist']: # Rambut terurai di belakang (Karakter perempuan)
            rect(s, 4, head_top+3, 11, head_top+5, hair)
            rect(s, 5, head_top+6, 10, head_top+7, hair)
    else:
        for xi in [4, 5]:
            for yi in [head_top, head_top+1]: px(s, xi, yi, hair)
        for xi in [10, 11]:
            for yi in [head_top, head_top+1]: px(s, xi, yi, hair)
        px(s, 6, head_top, hair)
        px(s, 9, head_top, hair)
        px(s, 7, head_top, lighter(hair, 15))
        if role in ['shop', 'artist']: # Rambut panjang depan
            vline(s, 3, head_top+2, head_top+5, hair)
            vline(s, 12, head_top+2, head_top+5, hair)
            px(s, 4, head_top+2, hair)
            px(s, 11, head_top+2, hair)

    if direction != "up":
        if blink:
            hline(s, 5, 5, 6, C.bk); hline(s, 5, 9, 10, C.bk)
        else:
            px(s, 5, 5, C.wt); px(s, 6, 5, C.wt)
            px(s, 9, 5, C.wt); px(s, 10, 5, C.wt)
            pup = (160, 80, 60) if role == 'shop' else (60, 80, 160) # Warna mata berbeda
            if direction == "left":
                px(s, 5, 5, pup); px(s, 9, 5, pup)
            elif direction == "right":
                px(s, 6, 5, pup); px(s, 10, 5, pup)
            else:
                px(s, 5, 5, pup); px(s, 9, 5, pup)
            if direction != "left": px(s, 6, 5, C.wt)
        if not blink:
            px(s, 7, 7, (200, 80, 80)); px(s, 8, 7, (200, 80, 80)) # Mulut yang lebih cerah
            
    px(s, 6, 8, C.sk2); px(s, 9, 8, C.sk2)
    
    # 3. TORSO
    rect(s, 4, 8, 11, 12, shirt)
    rect(s, 5, 8, 10, 8, lighter(shirt, 20))
    rect(s, 4, 12, 11, 12, darker(shirt, 25))
    if direction in ("down", "left", "right"):
        px(s, 7, 8, C.wt); px(s, 8, 8, C.wt) # Kerah Baju
    
    if role == 'doc':
        rect(s, 4, 8, 11, 14, C.wt)
        rect(s, 5, 8, 10, 8, (220,220,220)) # Coat shoulder
        if direction in ("down", "left", "right"):
            vline(s, 7, 8, 14, (200,200,200))
            px(s, 7, 9, (200, 40, 40)); px(s, 8, 9, (200, 40, 40)) # Tie
            px(s, 5, 9, (40,40,40)); px(s, 9, 9, (40,40,40)) # Stethoscope
            hline(s, 10, 6, 8, (40,40,40))
    elif role == 'shop':
        rect(s, 5, 10, 10, 14, C.wt)
        if direction in ("down", "left", "right"):
            hline(s, 9, 6, 9, C.wt) # Tali apron
            px(s, 7, 12, (240, 220, 220)); px(s, 8, 12, (240, 220, 220)) # Kantong kecil
    elif role == 'farmer':
        vline(s, 5, 9, 11, pants)
        vline(s, 9, 9, 11, pants)
        if direction in ("down", "left", "right"):
            px(s, 5, 8, (220, 180, 50)); px(s, 9, 8, (220, 180, 50)) # Kancing emas overalls
    elif role == 'smith':
        rect(s, 5, 10, 10, 14, (80, 60, 40))
        if direction in ("down", "left", "right"):
            px(s, 5, 9, (100, 60, 30)); px(s, 9, 9, (100, 60, 30)) # Strap kulit celemek
            px(s, 4, 6, (80, 80, 80)); px(s, 9, 7, (80, 80, 80))
    elif role == 'artist':
        if direction in ("down", "left", "right"):
            hline(s, 9, 6, 9, (200, 200, 50)) # Syal kuning di leher
            px(s, 6, 10, (200, 200, 50)); px(s, 6, 11, (200, 200, 50))
        
    if direction in ("left", "right"):
        off = 1 if frame else 0
        px(s, 3, 8, C.sk); px(s, 3, 9 + off, C.sk)
        px(s, 12, 8 + (1 - off), C.sk); px(s, 12, 9, C.sk)
    else:
        px(s, 3, 8, shirt); px(s, 3, 9, C.sk)
        px(s, 12, 8, shirt); px(s, 12, 9, C.sk)
        
    if role not in ['doc']: # Dokter berjubah panjang jadi celana tertutup
        rect(s, 4, 13, 11, 15, pants)
        vline(s, 8, 13, 15, C.pn2)
        px(s, 5, 13, lighter(pants, 15)); px(s, 10, 13, lighter(pants, 15)) # Highlight lutut
        
    rect(s, 4, 15, 5, 15, C.h2); rect(s, 10, 15, 11, 15, C.h2)
    px(s, 5, 15, lighter(C.h2, 20)); px(s, 11, 15, lighter(C.h2, 20)) # Sepatu berkilau
    if frame and direction in ("left","right"):
        px(s, 4, 14, pants)
        px(s, 11, 15, C.h2)
    return outline_sprite(s, color=(15, 8, 12))

def make_jin(direction, frame):
    s = make_surface()
    for r in range(2):
        rect(s, 3-r, 3-r, 12+r, 12+r, (180, 120, 255, 40))
    rect(s, 4, 2, 11, 12, C.jin_aura)
    rect(s, 5, 1, 10, 11, C.jin_skin)
    rect(s, 4, 3, 11, 7, C.jin_skin)
    px(s, 5, 5, C.bk); px(s, 9, 5, C.bk)
    px(s, 5, 4, C.gl); px(s, 9, 4, C.gl)
    px(s, 5, 0, C.gl); px(s, 8, 0, C.gl)
    px(s, 7, 0, C.gl); px(s, 10, 0, C.gl)
    if frame:
        rect(s, 5, 13, 10, 15, (180, 120, 255, 150))
    else:
        rect(s, 4, 14, 11, 15, (180, 120, 255, 150))
        px(s, 6, 13, (180, 120, 255, 180))
        px(s, 9, 13, (180, 120, 255, 180))
    px(s, 3, 7, C.jin_skin); px(s, 3, 8, C.jin_skin)
    px(s, 12, 7, C.jin_skin); px(s, 12, 8, C.jin_skin)
    return outline_sprite(s, color=(20, 10, 30))

def make_demit(direction, frame):
    s = make_surface()
    rect(s, 4, 2, 11, 15, C.demit_dark)
    rect(s, 5, 1, 10, 14, C.demit_dark)
    rect(s, 3, 5, 12, 12, C.demit_dark)
    px(s, 5, 5, C.demit_glow); px(s, 9, 5, C.demit_glow)
    px(s, 5, 4, (180, 80, 255)); px(s, 9, 4, (180, 80, 255))
    if frame:
        px(s, 2, 7, C.demit_glow); px(s, 13, 9, C.demit_glow)
    else:
        px(s, 2, 9, C.demit_glow); px(s, 13, 7, C.demit_glow)
    px(s, 7, 7, C.wt); px(s, 8, 7, C.wt)
    return outline_sprite(s)

def make_sapi(direction, frame):
    s = make_surface()
    bob = 1 if frame else 0
    
    kaki_c = C.sapi_brown
    if frame:
        rect(s, 3, 13, 4, 15, kaki_c)
        rect(s, 6, 13, 7, 14, kaki_c)
        rect(s, 10, 13, 11, 15, kaki_c)
        rect(s, 13, 13, 14, 14, kaki_c)
    else:
        rect(s, 3, 13, 4, 14, kaki_c)
        rect(s, 6, 13, 7, 15, kaki_c)
        rect(s, 10, 13, 11, 14, kaki_c)
        rect(s, 13, 13, 14, 15, kaki_c)

    rect(s, 3, 6+bob, 14, 12+bob, C.sapi_white)
    rect(s, 5, 7+bob, 7, 9+bob, C.bk)
    rect(s, 10, 8+bob, 12, 11+bob, C.bk)
    px(s, 13, 7+bob, C.bk)
    
    vline(s, 15, 7+bob, 11+bob, C.sapi_white)
    px(s, 15, 12+bob, C.bk)
    
    rect(s, 0, 4+bob, 4, 10+bob, C.sapi_white)
    rect(s, 0, 8+bob, 2, 10+bob, (230, 150, 160)) 
    px(s, 0, 9+bob, C.bk)
    px(s, 2, 6+bob, C.bk)
    px(s, 2, 3+bob, C.sapi_brown)
    px(s, 4, 3+bob, C.sapi_brown)
    px(s, 4, 6+bob, C.bk)

    if direction == 'right':
        s = pygame.transform.flip(s, True, False)
    elif direction == 'up':
        s.fill((0,0,0,0))
        rect(s, 3, 6+bob, 12, 14+bob, C.sapi_white)
        rect(s, 4, 7+bob, 6, 9+bob, C.bk)
        rect(s, 9, 10+bob, 11, 12+bob, C.bk)
        rect(s, 4, 4+bob, 11, 8+bob, C.sapi_white)
        px(s, 3, 4+bob, C.sapi_brown); px(s, 12, 4+bob, C.sapi_brown)
    
    return outline_sprite(s)

def make_ayam(direction, frame):
    s = make_surface()
    bob = 1 if frame else 0
    # Badan
    rect(s, 4, 8+bob, 10, 13+bob, C.wt)
    rect(s, 11, 7+bob, 12, 11+bob, C.wt) # Ekor
    rect(s, 3, 5+bob, 6, 8+bob, C.wt) # Kepala
    px(s, 4, 7+bob, C.bk) # Mata
    px(s, 1, 7+bob, C.ht); px(s, 2, 7+bob, C.ht) # Paruh
    px(s, 4, 4+bob, C.r0); px(s, 5, 4+bob, C.r0) # Jengger
    px(s, 6, 14, C.ht); px(s, 8, 14, C.ht) # Kaki
    if direction == 'right':
        s = pygame.transform.flip(s, True, False)
    elif direction == 'up':
        s.fill((0,0,0,0))
        rect(s, 4, 8+bob, 11, 13+bob, C.wt)
        px(s, 6, 14, C.ht); px(s, 9, 14, C.ht)
    return outline_sprite(s)

def make_naga(direction='down', frame=0):
    s = make_surface(48, 32)
    bob = 1 if frame else 0
    # Ekor
    rect(s, 42, 18+bob, 47, 21+bob, C.naga_body)
    rect(s, 43, 19+bob, 46, 20+bob, C.naga_body_lt)
    rect(s, 44, 17+bob, 45, 18+bob, C.naga_body)
    px(s, 47, 19+bob, C.naga_body_dk)
    for x in range(35, 42):
        y_off = int(math.sin((x-35)*0.9) * 2) + bob
        rect(s, x, 19 + y_off, x, 22 + y_off, C.naga_body)
        px(s, x, 19 + y_off, C.naga_body_lt)
        px(s, x, 22 + y_off, C.naga_body_dk)
    # Tubuh
    rect(s, 18, 14+bob, 35, 24+bob, C.naga_body)
    rect(s, 19, 21+bob, 34, 24+bob, C.naga_belly)
    px(s, 19, 21+bob, C.naga_body_dk)
    px(s, 34, 21+bob, C.naga_body_dk)
    hline(s, 14+bob, 19, 34, C.naga_body_lt)
    for sx in range(20, 34, 3):
        px(s, sx, 16+bob, C.naga_scale)
        px(s, sx+1, 18+bob, C.naga_scale)
        px(s, sx, 19+bob, C.naga_belly)
    hline(s, 13+bob, 18, 35, C.naga_body_dk)
    hline(s, 25+bob, 18, 35, C.naga_body_dk)
    # Kaki kiri
    rect(s, 22, 24+bob, 25, 28+bob, C.naga_body)
    rect(s, 23, 25+bob, 24, 27+bob, C.naga_body_lt)
    px(s, 22, 28+bob, (255, 240, 180)); px(s, 23, 28+bob, (255, 240, 180)); px(s, 25, 28+bob, (255, 240, 180))
    # Kaki kanan
    rect(s, 30, 24+bob, 33, 28+bob, C.naga_body)
    rect(s, 31, 25+bob, 32, 27+bob, C.naga_body_lt)
    px(s, 30, 28+bob, (255, 240, 180)); px(s, 32, 28+bob, (255, 240, 180)); px(s, 33, 28+bob, (255, 240, 180))
    # Leher
    rect(s, 12, 12+bob, 18, 18+bob, C.naga_body)
    rect(s, 13, 13+bob, 17, 17+bob, C.naga_body_lt)
    px(s, 12, 18+bob, C.naga_belly); px(s, 13, 18+bob, C.naga_belly)
    # Kepala
    head_y = 6 + bob
    rect(s, 4, head_y, 16, head_y+10, C.naga_body)
    rect(s, 5, head_y+1, 15, head_y+9, C.naga_body)
    hline(s, head_y, 6, 14, C.naga_body_lt); hline(s, head_y+1, 5, 15, C.naga_body_lt)
    hline(s, head_y+9, 5, 13, C.naga_belly)
    rect(s, 4, head_y+8, 7, head_y+10, C.naga_body_dk)
    # Tanduk & Mata
    rect(s, 7, head_y-3, 8, head_y, C.naga_horn); rect(s, 11, head_y-3, 12, head_y, C.naga_horn)
    px(s, 7, head_y-4, C.naga_horn); px(s, 12, head_y-4, C.naga_horn)
    px(s, 6, head_y-2, C.naga_horn); px(s, 13, head_y-2, C.naga_horn)
    rect(s, 8, head_y+3, 9, head_y+4, C.wt); rect(s, 11, head_y+3, 12, head_y+4, C.wt)
    px(s, 8, head_y+3, C.naga_eye); px(s, 11, head_y+3, C.naga_eye)
    px(s, 8, head_y+2, (140, 255, 140)); px(s, 11, head_y+2, (140, 255, 140))
    # Janggut & Sparkle
    rect(s, 0, head_y+5, 4, head_y+5, C.naga_whiskers); rect(s, 0, head_y+7, 3, head_y+7, C.naga_whiskers)
    px(s, 4, head_y+6, C.naga_whiskers); px(s, 1, head_y+8, C.naga_whiskers)
    if frame: px(s, 3, head_y+8, C.fire2); px(s, 2, head_y+9, C.fire1); px(s, 1, head_y+9, C.fire3); px(s, 0, head_y+10, C.fire1)
    for sx, sy in [(20, 5), (28, 10), (38, 16), (15, 28), (32, 4)][:2 + frame]:
        px(s, sx, sy, C.gl); px(s, sx+1, sy, (255, 255, 200))
    return s

def make_tool_sprite(idx):
    s = make_surface(16, 16)
    if idx == 0: # Cangkul
        rect(s, 3, 4, 12, 5, (180, 180, 180)) 
        rect(s, 7, 5, 8, 13, C.wo1)
    elif idx == 1: # Siram
        rect(s, 5, 7, 11, 13, (60, 120, 200))
        rect(s, 12, 8, 14, 9, (180, 180, 180))
        vline(s, 3, 7, 11, (50, 100, 180))
        px(s, 4, 7, (50, 100, 180)); px(s, 4, 11, (50, 100, 180))
    elif idx == 2: # Tanam (Benih)
        rect(s, 5, 7, 11, 14, (160, 110, 60))
        hline(s, 6, 6, 10, (140, 90, 40))
        px(s, 7, 10, C.cg); px(s, 9, 11, C.cg); px(s, 6, 12, C.cg)
    elif idx == 3: # Panen (Sabit)
        rect(s, 6, 3, 11, 4, (200, 200, 200))
        rect(s, 10, 5, 11, 8, (200, 200, 200))
        rect(s, 6, 5, 7, 13, C.wo1)
    elif idx == 4: # Kapak
        rect(s, 8, 4, 12, 8, (180, 180, 180))
        rect(s, 6, 5, 7, 14, C.wo1)
    elif idx == 5: # Pancing
        for i in range(10): px(s, 3+i, 13-i, C.wo1); px(s, 4+i, 13-i, C.wo1)
        for i in range(6): px(s, 13, 4+i, (200, 200, 200))
    elif idx == 6: # Hadiah
        rect(s, 4, 6, 12, 13, C.cr)
        vline(s, 8, 6, 13, C.cy)
        hline(s, 10, 4, 12, C.cy)
        px(s, 7, 5, C.cy); px(s, 9, 5, C.cy)
    elif idx == 7: # Palu (Hammer)
        rect(s, 4, 4, 12, 7, (120, 120, 120))
        rect(s, 5, 5, 11, 6, (180, 180, 180))
        rect(s, 7, 8, 8, 14, C.wo1)
        
    return pygame.transform.scale(outline_sprite(s), (28, 28))

# ── FURNITURE ────────────────────────────────────────────────
def make_bed():
    s = make_surface()
    rect(s, 1, 4, 14, 13, C.fn)
    vline(s, 1, 4, 13, C.fn2)
    vline(s, 14, 4, 13, C.fn2)
    rect(s, 2, 5, 13, 12, C.wt)
    rect(s, 3, 5, 13, 12, C.s0)
    rect(s, 3, 5, 7, 7, C.wl)
    return s

def make_stove():
    s = make_surface()
    rect(s, 1, 1, 14, 14, (64,64,64))
    rect(s, 2, 2, 13, 13, (80,80,80))
    for bx, by in [(3,3),(9,3),(3,9),(9,9)]:
        rect(s, bx, by, bx+3, by+3, (40,40,40))
        rect(s, bx+1, by+1, bx+2, by+2, C.fire1)
    rect(s, 2, 12, 13, 14, (96,96,96))
    return s

def make_table():
    s = make_surface()
    rect(s, 0, 3, 15, 5, C.fn)
    hline(s, 3, 0, 15, C.fn2)
    hline(s, 4, 0, 15, C.fn3)
    vline(s, 2, 5, 15, C.fn)
    vline(s, 13, 5, 15, C.fn)
    rect(s, 6, 0, 9, 3, C.cy)  # candle
    return s

def make_bookshelf():
    s = make_surface(fill=C.fn)
    for y in [0, 5, 10, 15]:
        hline(s, y, 0, 15, C.fn2)
    book_colors = [C.cr, C.s0, C.cg, C.gl, C.cp, C.co, (0,160,180), C.nc_sari]
    for row_y in [1, 6, 11]:
        bx = 2
        for color in book_colors[:4]:
            rect(s, bx, row_y, bx+1, row_y+3, color)
            bx += 3
    return s

def make_mirror():
    s = make_surface(fill=C.fn)
    rect(s, 2, 1, 13, 14, C.fn2)
    rect(s, 3, 2, 12, 13, (200,232,248))
    rect(s, 4, 3, 6, 12, (220,245,255))
    return s

def make_fireplace():
    s = make_surface(fill=(64,64,64))
    rect(s, 2, 4, 13, 14, (32,32,32))
    rect(s, 3, 5, 12, 14, (24,24,24))
    rect(s, 4, 7, 11, 14, C.fire1)
    rect(s, 5, 6, 10, 12, C.fire2)
    rect(s, 6, 5, 9, 10, C.fire3)
    rect(s, 7, 5, 8, 8, C.wt)
    rect(s, 0, 0, 15, 2, C.p1)
    return s

def make_clock():
    s = make_surface(fill=C.fn)
    rect(s, 3, 1, 12, 14, C.fn2)
    vline(s, 3, 1, 14, C.fn3)
    vline(s, 12, 1, 14, C.fn3)
    rect(s, 5, 5, 10, 11, C.fl3)
    # Clock face
    cx, cy, cr = 7, 8, 4
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int(cr * math.sin(rad))
        ey = cy - int(cr * math.cos(rad))
        px(s, ex, ey, C.wl2)
    px(s, cx, cy, (40,40,40))
    return s

def make_plant_pot():
    s = make_surface()
    rect(s, 5, 11, 10, 15, C.d0)
    rect(s, 4, 13, 11, 15, C.d1)
    vline(s, 7, 4, 12, C.g0)
    vline(s, 8, 4, 12, C.g0)
    rect(s, 3, 5, 6, 9, C.g1)
    rect(s, 9, 7, 12, 10, C.g1)
    rect(s, 5, 2, 10, 6, C.g2)
    return outline_sprite(s, color=(40, 20, 10))

def make_chest():
    s = make_surface()
    rect(s, 1, 5, 14, 14, C.fn)
    rect(s, 1, 3, 14, 6, C.fn2)
    hline(s, 5, 1, 14, C.wo2)
    rect(s, 6, 8, 9, 11, C.gl)
    rect(s, 7, 9, 8, 10, C.ht)
    return s

def make_counter():
    s = make_surface(fill=C.fn)
    rect(s, 0, 4, 15, 14, C.fn)
    hline(s, 4, 0, 15, C.fn2)
    hline(s, 5, 0, 15, C.fn3)
    for ox in [2, 6, 10]:
        rect(s, ox, 1, ox+2, 3, C.cg)
    return s

def make_shelf_store():
    s = make_surface(fill=C.fn)
    for y in [0, 5, 10, 15]:
        hline(s, y, 0, 15, C.fn2)
    for bx in [1, 4, 7, 10, 13]:
        px(s, bx, 2, C.cr); px(s, bx, 3, C.cr)
        px(s, bx, 7, C.cy); px(s, bx, 8, C.cy)
        px(s, bx, 12, C.s0); px(s, bx, 13, C.s0)
    return s

# ══════════════════════════════════════════════════════════════
#  ASSET LOADER
# ══════════════════════════════════════════════════════════════
def load_sprite(path, fallback_fn=None, size=(TILE, TILE)):
    """Load PNG asset jika ada, otherwise generate procedurally."""
    if os.path.exists(path):
        try:
            surf = pygame.image.load(path).convert_alpha()
            return pygame.transform.scale(surf, size) if size else surf
        except Exception:
            pass
    if fallback_fn is not None:
        surf = fallback_fn()
        return pygame.transform.scale(surf, size) if size else surf
    return pygame.Surface(size or (TILE, TILE), pygame.SRCALPHA)


def _load_char(folder, direction, frame, fallback_fn, size=(TILE, TILE)):
    """Load karakter PNG dari folder, fallback ke fungsi generator."""
    candidates = [
        os.path.join(folder, f"{direction}_{frame}.png"),
    ]
    # tambah variasi nama file dengan prefix
    base = os.path.basename(folder)
    candidates.append(os.path.join(folder, f"{base}_{direction}_{frame}.png"))
    for path in candidates:
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
                return pygame.transform.scale(surf, size)
            except Exception:
                continue
    surf = fallback_fn(direction, frame)
    return pygame.transform.scale(surf, size)


# ══════════════════════════════════════════════════════════════
#  SPRITE REGISTRY (lazy init after pygame.init)
# ══════════════════════════════════════════════════════════════
SPRITES = {}
ANIMATED = {}

def get_wet_sprite(surf):
    if not hasattr(get_wet_sprite, 'cache'):
        get_wet_sprite.cache = {}
    if surf in get_wet_sprite.cache:
        return get_wet_sprite.cache[surf]
    wet = surf.copy()
    wet.fill((20, 20, 40, 0), special_flags=pygame.BLEND_RGBA_SUB)
    get_wet_sprite.cache[surf] = wet
    return wet

def _remove_checker_bg(surf):
    """Hapus background putih/abu checkered (hasil AI) dari surface."""
    bg = surf.get_at((0, 0))
    for y in range(surf.get_height()):
        for x in range(surf.get_width()):
            c = surf.get_at((x, y))
            if c[3] > 0:
                is_bg = (c[:3] == bg[:3])
                is_gray = (c[0] > 180 and c[1] > 180 and c[2] > 180
                           and abs(c[0]-c[1]) < 15 and abs(c[1]-c[2]) < 15)
                if is_bg or is_gray:
                    surf.set_at((x, y), (0, 0, 0, 0))
    return surf


def init_sprites():
    """Generate & cache semua sprite — PNG assets diprioritaskan, fallback ke procedural."""
    global SPRITES, ANIMATED

    # ── TERRAIN ──────────────────────────────────────────────────
    SPRITES['grass']      = load_sprite("assets/tiles/grass.png",      make_grass_tile)
    SPRITES['dirt']       = load_sprite("assets/tiles/dirt.png",        make_dirt_tile)
    SPRITES['tilled_dry'] = load_sprite("assets/tiles/tilled_dry.png",  make_tilled_dry)
    SPRITES['tilled_wet'] = load_sprite("assets/tiles/tilled_wet.png",  make_tilled_wet)
    SPRITES['path']       = load_sprite("assets/tiles/path.png",        make_path_tile)
    SPRITES['floor']      = load_sprite("assets/tiles/floor.png",       make_floor_tile)
    SPRITES['wall']       = load_sprite("assets/tiles/wall.png",        make_wall_tile)
    SPRITES['sand']       = load_sprite("assets/tiles/sand.png",        make_sand_tile)

    # ── AIR (animated, 4 frames) ─────────────────────────────────
    ANIMATED['water'] = [
        load_sprite(f"assets/tiles/water_{i}.png", lambda i=i: make_water_tile(i * 4))
        for i in range(4)
    ]

    # ── OBJEK ────────────────────────────────────────────────────
    SPRITES['tree']      = load_sprite("assets/objects/tree.png",      make_tree)
    SPRITES['fence']     = load_sprite("assets/objects/fence.png",     make_fence)
    SPRITES['mailbox']   = load_sprite("assets/objects/mailbox.png",   make_mailbox)
    SPRITES['door']      = load_sprite("assets/objects/door.png",      make_door)
    SPRITES['weed']      = load_sprite("assets/objects/weed.png",      make_weed)
    SPRITES['stone']     = load_sprite("assets/objects/stone.png",     make_stone)
    SPRITES['cave_wall'] = load_sprite("assets/tiles/cave_wall.png",   make_cave_wall)

    # ── FURNITURE ────────────────────────────────────────────────
    SPRITES['chest']       = load_sprite("assets/objects/chest.png",       make_chest)
    SPRITES['bed']         = load_sprite("assets/objects/bed.png",         make_bed)
    SPRITES['stove']       = load_sprite("assets/objects/stove.png",       make_stove)
    SPRITES['table']       = load_sprite("assets/objects/table.png",       make_table)
    SPRITES['bookshelf']   = load_sprite("assets/objects/bookshelf.png",   make_bookshelf)
    SPRITES['mirror']      = load_sprite("assets/objects/mirror.png",      make_mirror)
    SPRITES['fireplace']   = load_sprite("assets/objects/fireplace.png",   make_fireplace)
    SPRITES['clock']       = load_sprite("assets/objects/clock.png",       make_clock)
    SPRITES['plant_pot']   = load_sprite("assets/objects/plant_pot.png",   make_plant_pot)
    SPRITES['counter']     = load_sprite("assets/objects/counter.png",     make_counter)
    SPRITES['shelf_store'] = load_sprite("assets/objects/shelf_store.png", make_shelf_store)
    SPRITES['tv']          = load_sprite("assets/objects/tv.png",          make_tv)

    # ── ALAT (tool icons, 28×28) ──────────────────────────────────
    tool_names = ['cangkul', 'siram', 'tanam', 'panen', 'kapak', 'pancing', 'hadiah', 'palu']
    SPRITES['tools'] = []
    for i, tname in enumerate(tool_names):
        path = f"assets/items/{tname}.png"
        if os.path.exists(path):
            try:
                surf = pygame.image.load(path).convert_alpha()
                SPRITES['tools'].append(pygame.transform.scale(surf, (28, 28)))
                continue
            except Exception:
                pass
        SPRITES['tools'].append(make_tool_sprite(i))

    # ── PLAYER (4 dir × 2 frame) ──────────────────────────────────
    ANIMATED['player'] = {}
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(2):
            candidates = [
                f"assets/chars/player/player_{direction}_{f}.png",
                f"assets/chars/player/{direction}_{f}.png",
            ]
            surf = None
            for path in candidates:
                if os.path.exists(path):
                    try:
                        surf = pygame.image.load(path).convert_alpha()
                        surf = pygame.transform.scale(surf, (TILE, TILE))
                        break
                    except Exception:
                        surf = None
            if surf is None:
                dir_s = 'right' if direction == 'left' else direction
                flip  = (direction == 'left')
                surf = make_char(dir_s, f, role='farmer')
                surf = pygame.transform.scale(surf, (TILE, TILE))
                if flip:
                    surf = pygame.transform.flip(surf, True, False)
            frames.append(surf)
        ANIMATED['player'][direction] = frames

    # ── NPC STANDAR (4 dir × 2 frame) ────────────────────────────
    npc_configs = {
        'arya': (C.ng, C.g1,      C.pn, 'farmer'),
        'sari': (C.cr, C.nc_sari, C.pn, 'shop'),
        'raka': (C.ng, C.nc_raka, C.s0, 'doc'),
        'maya': (C.gl, C.nc_maya, C.pn, 'artist'),
        'budi': (C.ng, C.nc_budi, C.p2, 'smith'),
        'pedagang': (C.h0, (100, 50, 150), C.pn2, 'shop'),
    }
    for npc_id, (hair, shirt, pants, role) in npc_configs.items():
        ANIMATED[f'npc_{npc_id}'] = {}
        for direction in ['up', 'down', 'left', 'right']:
            frames = []
            for f in range(2):
                path = f"assets/chars/npc/{npc_id}/{direction}_{f}.png"
                surf = None
                if os.path.exists(path):
                    try:
                        surf = pygame.image.load(path).convert_alpha()
                        surf = pygame.transform.scale(surf, (TILE, TILE))
                    except Exception:
                        surf = None
                if surf is None:
                    dir_s = 'right' if direction == 'left' else direction
                    flip  = (direction == 'left')
                    surf = make_char(dir_s, f, hair, shirt, pants, role=role)
                    surf = pygame.transform.scale(surf, (TILE, TILE))
                    if flip:
                        surf = pygame.transform.flip(surf, True, False)
                frames.append(surf)
            ANIMATED[f'npc_{npc_id}'][direction] = frames

    # ── MOB / MAKHLUK KHUSUS (4 dir × 2 frame) ───────────────────
    special_configs = {
        'jin':        make_jin,
        'betsy':      make_sapi,
        'sapi':       make_sapi,
        'ayam':       make_ayam,
        'kuntilanak': make_demit,
        'genderuwo':  make_demit,
        'banaspati':  make_jin,
        'serigala':   make_demit,   # fallback ke demit sampai sprite tersedia
        'tuyul':      make_jin,     # fallback ke jin sampai sprite tersedia
    }
    for npc_id, maker_func in special_configs.items():
        ANIMATED[f'npc_{npc_id}'] = {}
        for direction in ['up', 'down', 'left', 'right']:
            frames = []
            for f in range(2):
                path = f"assets/chars/mob/{npc_id}/{direction}_{f}.png"
                surf = None
                if os.path.exists(path):
                    try:
                        surf = pygame.image.load(path).convert_alpha()
                        surf = pygame.transform.scale(surf, (TILE, TILE))
                    except Exception:
                        surf = None
                if surf is None:
                    dir_s = 'right' if direction == 'left' else direction
                    flip  = (direction == 'left')
                    surf = maker_func(dir_s, f)
                    surf = pygame.transform.scale(surf, (TILE, TILE))
                    if flip:
                        surf = pygame.transform.flip(surf, True, False)
                frames.append(surf)
            ANIMATED[f'npc_{npc_id}'] [direction] = frames

    # ── NAGA / DEWA HUTAN BOSS (2.5× TILE) ───────────────────────
    ANIMATED['npc_naga'] = {}
    naga_w = int(TILE * 2.5)
    naga_h = int(TILE * 2.5)
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(2):
            candidates = [
                os.path.join("assets", "chars", "boss", "dewa_hutan", f"{direction}_{f}.png"),
                os.path.join("assets", "chars", "npc_naga", f"{direction}_{f}.png"),
            ]
            surf = None
            for path in candidates:
                if os.path.exists(path):
                    try:
                        raw = pygame.image.load(path).convert_alpha()
                        raw = _remove_checker_bg(raw)
                        surf = pygame.transform.scale(raw, (naga_w, naga_h))
                        break
                    except Exception:
                        surf = None
            if surf is None:
                surf = make_naga(direction, f)
                surf = pygame.transform.scale(surf, (naga_w, naga_h))
                if direction == 'right':
                    surf = pygame.transform.flip(surf, True, False)
            frames.append(surf)
        ANIMATED['npc_naga'][direction] = frames

    # ── TANAMAN (4 tahap × tiap crop) ────────────────────────────
    SPRITES['crops'] = {}
    CROP_COLORS = {
        'lobak':    (C.cg, C.cg2),
        'wortel':   (C.co, C.d1),
        'stroberi': (C.cr, C.cg),
        'jagung':   (C.cy, C.cg),
        'tomat':    (C.cr, (255, 80, 80)),
        'labu':     (C.co, C.fn),
        'bayam':    (C.g2, C.g0),
        'jamur':    ((212, 164, 116), C.fn2),
    }
    for crop_id, (c1, c2) in CROP_COLORS.items():
        stages = []
        for stage in range(4):
            path = f"assets/crops/{crop_id}_{stage}.png"
            if os.path.exists(path):
                try:
                    surf = pygame.image.load(path).convert_alpha()
                    stages.append(pygame.transform.scale(surf, (TILE, TILE)))
                    continue
                except Exception:
                    pass
            stages.append(pygame.transform.scale(make_crop_sprite(stage, c1, c2), (TILE, TILE)))
        SPRITES['crops'][crop_id] = stages

# ══════════════════════════════════════════════════════════════
#  GAME DATA
# ══════════════════════════════════════════════════════════════
CROPS = {
    'lobak':    {'name':'Lobak',    'icon':'🥬', 'days':2, 'sell':22, 'cost':5,  'seasons':['Semi']},
    'wortel':   {'name':'Wortel',   'icon':'🥕', 'days':3, 'sell':35, 'cost':8,  'seasons':['Semi','Gugur']},
    'stroberi': {'name':'Stroberi', 'icon':'🍓', 'days':4, 'sell':55, 'cost':12, 'seasons':['Semi']},
    'jagung':   {'name':'Jagung',   'icon':'🌽', 'days':4, 'sell':48, 'cost':10, 'seasons':['Panas']},
    'tomat':    {'name':'Tomat',    'icon':'🍅', 'days':5, 'sell':65, 'cost':14, 'seasons':['Panas']},
    'labu':     {'name':'Labu',     'icon':'🎃', 'days':5, 'sell':70, 'cost':15, 'seasons':['Gugur']},
    'bayam':    {'name':'Bayam',    'icon':'🥬', 'days':2, 'sell':30, 'cost':7,  'seasons':['Dingin']},
    'jamur':    {'name':'Jamur',    'icon':'🍄', 'days':3, 'sell':55, 'cost':12, 'seasons':['Dingin']},
    'api_magis': {'name':'Api Magis', 'icon':'🔥', 'days':0, 'sell':40, 'cost':0, 'seasons':[]},
    'taring':    {'name':'Taring',  'icon':'🦷', 'days':0, 'sell':30, 'cost':0, 'seasons':[]},
    'kain_putih':{'name':'Kain Kusam', 'icon':'👻', 'days':0, 'sell':25, 'cost':0, 'seasons':[]},
}

SEASONS = ['Semi','Panas','Gugur','Dingin']
SEASON_NAMES = {'Semi':'Musim Semi','Panas':'Musim Panas','Gugur':'Musim Gugur','Dingin':'Musim Dingin'}
DAYS_PER_SEASON = 28

TOOLS = ['Cangkul', 'Siram', 'Tanam', 'Panen', 'Kapak', 'Pancing', 'Hadiah', 'Palu']
TOOL_ICONS = ['⛏', '💧', '🌱', '🌾', '🪓', '🎣', '🎁', '🔨']

NPCS = {
    'arya': {'name':'Pak Arya','gift':'wortel',
        'talks':[['Anak muda! Selamat datang di Lembah Karsa.','Mulailah dengan lobak. Mudah tumbuh.'],
                 ['Tanah yang dirawat tiap hari selalu memberi hasil.'],
                 ['Wortel segar itu favoritku!']],
        'gift_r':'Wortel segar! Tanahmu rupanya subur. Terima kasih!'},
    'sari': {'name':'Bu Sari','gift':'jagung',
        'talks':[['Selamat datang di Warung Sari!','Aku jual benih dan beli hasil panenmu.'],
                 ['Ada benih baru musim ini!'],
                 ['Mau beli atau jual sesuatu?']],
        'gift_r':'Jagungnya besar-besar! Terima kasih!'},
    'raka': {'name':'Pak Raka','gift':'stroberi',
        'talks':[['Jaga kesehatanmu, ya.','Istirahat cukup itu penting.'],
                 ['Tidur tepat waktu itu sehat.']],
        'gift_r':'Stroberi segar! Langka. Terima kasih!'},
    'maya': {'name':'Maya','gift':'tomat',
        'talks':[['Kamu pemilik kebun baru itu?','Aku Maya, seniman lembah ini.'],
                 ['Warna ladangmu waktu pagi indah sekali.']],
        'gift_r':'Tomat merah sempurna!'},
    'budi': {'name':'Budi','gift':'jamur',
        'talks':[['Aku Budi. Beli upgrade alat di sini ya.'],
                 ['Cangkul baja bisa hemat energi.']],
        'gift_r':'Jamur segarnya banyak! Makasih!'},
    'naga': {'name':'Naga Sang Hyang', 'gift':'wortel',
        'talks':[['Hmmm... seorang petani muda mendekat... menarik...'],
                 ['Aku Sang Hyang, naga penjaga lembah ini.', 'Hutan, sungai, dan tanah... semua tahu namaku.'],
                 ['Kebijakan tidak datang dari berlari.', 'Datang dari menanam, menunggu, memanen.']],
        'gift_r':'ROAR! Tubuhku terasa muda kembali. Berkat untukmu, Manusia.'},
    'kuntilanak': {'name':'Kuntilanak', 'gift':'lobak',
        'talks':[['Hihihi... kau lihat aku?'],
                 ['Kekekek... rambut panjangku. Manusia takut padaku.']],
        'gift_r':'Hihihi... lama tak kurasakan kebaikan.'},
    'genderuwo': {'name':'Genderuwo', 'gift':'tomat',
        'talks':[['GRRRRRR!', 'Manusia kecil berani sekali!'],
                 ['Hutan ini rumahku 500 tahun. Jangan tebang sembarangan.']],
        'gift_r':'GRRRR! Tomat merah, aku suka!'},
    'banaspati': {'name':'Banaspati', 'gift':'kayu',
        'talks':[['*api melayang dengan wajah* Whoooo... fuh fuh!'],
                 ['Aku Banaspati. Kepala api pelindung gua.']],
        'gift_r':'WHOOSH! Kayu bakar nikmat!'},
    'jin': {'name':'Jin Kebun', 'gift':'lobak',
        'talks':[['Hehehe... Energi bumi di sini sangat kuat.'],
                 ['Tanam lebih banyak, aku suka melihatnya tumbuh.']],
        'gift_r':'Hihihi! Sayuran segar! Terima kasih, manusia!'},
    'betsy': {'name':'Sapi Betsy', 'gift':'jagung',
        'talks':[['Mooo...', '*Betsy mengunyah rumput dengan tenang*']],
        'gift_r':'Mooo! *Betsy terlihat sangat senang*'},
    'sapi': {'name':'Sapi Ternak', 'gift':'jagung',
        'talks':[['Mooo!'], ['*sapi itu memakan jerami dengan lahap*']],
        'gift_r':'Mooo~ *sapi itu menyukai pemberianmu*'},
    'ayam': {'name':'Ayam Ternak', 'gift':'jagung',
        'talks':[['Petok petok!'], ['*ayam itu mengais-ngais tanah*']],
        'gift_r':'Petok! *ayam itu mematuk makananmu*'},
    'pedagang': {'name':'Pedagang Misterius', 'gift':'api_magis',
        'talks':[['Aku berkeliling mencari barang langka.', 'Jika kau punya sesuatu yang menarik, aku berani bayar mahal.']],
        'gift_r':'Ini barang langka yang kucari! Terima kasih!'},
}

QUEST_STAGES = [
    {'t':'Prolog',      'd':'Baca surat di kotak pos.'},
    {'t':'Bab I',       'd':'Tanam & siram 3 lobak.'},
    {'t':'Bab I',       'd':'Panen 3 lobak.'},
    {'t':'Bab II',      'd':'Kumpulkan 150G.'},
    {'t':'Bab II',      'd':'Upgrade alat dari Budi.'},
    {'t':'Bab III',     'd':'Panen 2 jagung.'},
    {'t':'Bab III',     'd':'Beri hadiah ke 3 warga.'},
    {'t':'Bab IV',      'd':'Perbaiki rumah kaca (400G).'},
    {'t':'Bab IV',      'd':'Panen dari 4 musim.'},
    {'t':'Bab V',      'd':'Selesaikan tahun pertama.'},
    {'t':'Tamat!',     'd':'Lembah Karsa bangkit!'},
]

FESTIVALS = {
    'gugur_15': {
        'name': 'Festival Panen',
        'season': 'Gugur',
        'day': 15,
        'scene': 'town',
        'judge': 'arya',
        'locations': {
            'arya': (18, 11),
            'sari': (16, 11),
            'maya': (17, 12),
            'budi': (19, 12),
            'raka': (18, 13),
        },
        'dialogs': {
            'arya': ["Selamat datang di Festival Panen!", "Bawa hasil panen terbaikmu untuk dinilai. Hadiah besar menanti!"],
            'sari': ["Semua orang berkumpul! Senang sekali rasanya."],
            'maya': ["Aku mencari inspirasi dari warna-warni hasil panen."],
            'budi': ["Aku istirahat dari bengkel hari ini. Festival setahun sekali!"],
            'raka': ["Makan makanan segar dari kebun baik untuk kesehatan."],
            'default': ["Selamat festival!"]
        }
    }
}

# ══════════════════════════════════════════════════════════════
#  TILE TYPES
# ══════════════════════════════════════════════════════════════
# Simple tile IDs
G, D, P, W, FL, WL, TR, H, MB, DR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, WD, STN, CV, TV, SD = range(27)

TILE_NAMES = {
    G: 'grass', D: 'dirt', P: 'path', W: 'water', FL: 'floor', WL: 'wall',
    TR: 'tree', H: 'house', MB: 'mailbox', DR: 'door', FN: 'fence',
    BD: 'bed', ST: 'stove', TB: 'table', BS: 'bookshelf', MR: 'mirror',
    FP: 'fireplace', CL: 'clock', PP: 'plant_pot', CH: 'chest', CT: 'counter',
    SH: 'shelf_store', WD: 'weed', STN: 'stone', CV: 'cave_wall', TV: 'tv', SD: 'sand'
}

WALKABLE = {G, D, P, FL, WD, SD}  # tile yang bisa diinjak
TILLABLE = {G, D}          # tile yang bisa dicangkul
BLOCKING = {W, WL, TR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, STN, CV, TV}

# ══════════════════════════════════════════════════════════════
#  SCENE MAPS
# ══════════════════════════════════════════════════════════════
class Scene:
    def __init__(self, name, display, tiles, portals=None, npcs=None, indoor=False):
        self.name = name
        self.display = display
        self.tiles = tiles  # 2D list
        self.w = len(tiles[0])
        self.h = len(tiles)
        self.portals = portals or []  # [(fx,fy,target_scene,tx,ty)]
        self.indoor = indoor
        self.npcs = []
        for n in (npcs or []):
            self.npcs.append({
                'id': n[0], 'x': n[1], 'y': n[2], 'px': float(n[1]), 'py': float(n[2]),
                'facing': 'down', 'timer': random.randint(1000, 3000), 'moving': False, 'hp': 5,
                'home_x': n[1], 'home_y': n[2], 'attack_timer': 0
            })

def build_outdoor():
    W_, H_ = 25, 25
    m = [[G]*W_ for _ in range(H_)]

    def rect_fill(x,y,w,h,t):
        for dy in range(h):
            for dx in range(w):
                if 0<=y+dy<H_ and 0<=x+dx<W_:
                    m[y+dy][x+dx] = t
    def hline_(y,x1,x2,t):
        for x in range(x1,x2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
    def vline_(x,y1,y2,t):
        for y in range(y1,y2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t

    # Farmland
    rect_fill(1, 1, 14, 11, D)
    # Player house
    rect_fill(1, 1, 5, 4, H)
    m[4][3] = DR  # door into house
    m[2][6] = MB  # mailbox
    m[5][6] = CH  # kotak pengiriman hasil panen

    # Fence around farm
    hline_(0, 1, 15, FN); vline_(0, 0, 12, FN)
    hline_(12, 1, 15, FN); vline_(15, 0, 12, FN)
    # Pintu pagar keluar kebun
    m[12][14] = P
    m[12][15] = P

    # Jalan ke Kota (Timur)
    hline_(13, 14, W_-1, P)
    
    # Jalan ke Hutan (Selatan)
    vline_(14, 14, H_-1, P)
    vline_(15, 14, H_-1, P)

    # Sungai kecil di pinggir
    rect_fill(17, 0, 2, 18, W)
    m[13][17] = P; m[13][18] = P

    return Scene('outdoor', 'Kebun', m,
        portals=[
            (3,4,'house',7,9),
            (12,11,'barn',7,12),
            (24,13,'town',1,13),
            (14,24,'forest',14,1),
            (15,24,'forest',15,1),
        ],
        npcs=[('betsy', 4, 16)])

def build_town():
    W_, H_ = 40, 30
    m = [[G]*W_ for _ in range(H_)]
    def rect_fill(x,y,w,h,t):
        for dy in range(h):
            for dx in range(w):
                if 0<=y+dy<H_ and 0<=x+dx<W_: m[y+dy][x+dx] = t
    def hline_(y,x1,x2,t):
        for x in range(x1,x2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
    def vline_(x,y1,y2,t):
        for y in range(y1,y2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t

    # Jalan Raya Kota
    hline_(13, 0, W_-1, P)
    vline_(20, 13, H_-1, P)
    vline_(21, 13, H_-1, P)

    # Bangunan Utara Jalan
    rect_fill(5, 7, 5, 4, H); m[10][7] = DR
    vline_(7, 11, 12, P) # Shop
    rect_fill(12, 7, 5, 4, H); m[10][14] = DR
    vline_(14, 11, 12, P) # Clinic
    rect_fill(20, 4, 10, 6, H); m[9][24] = DR
    vline_(24, 10, 12, P) # Town Hall
    rect_fill(32, 7, 5, 4, H); m[10][34] = DR
    vline_(34, 11, 12, P) # Studio

    # Bangunan Selatan Jalan
    rect_fill(8, 15, 5, 4, H); m[14][10] = DR # Smith
    rect_fill(28, 15, 5, 4, H); m[14][30] = DR # Greenhouse

    # Dekorasi Kota
    for x, y in [(25, 15), (26, 17), (23, 16), (35, 16), (36, 18)]:
        m[y][x] = TR

    return Scene('town', 'Kota Mineral', m,
        portals=[
            (0,13,'outdoor',23,13),
            (7,10,'shop',7,9),
            (14,10,'clinic',7,9),
            (24,9,'town_hall',9,13),
            (34,10,'studio',7,9),
            (10,14,'smith',7,9),
            (30,14,'greenhouse',7,9),
            (20,29,'beach',15,1),
            (21,29,'beach',16,1),
        ],
        npcs=[('arya', 15, 14), ('sari', 7, 12), ('raka', 14, 12), ('maya', 32, 14), ('budi', 10, 21)])

def build_town_hall():
    W_, H_ = 20, 15
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][9] = DR; m[H_-1][10] = DR
    
    m[2][9] = CL
    for x in range(2, 6): m[2][x] = BS
    for x in range(14, 18): m[2][x] = BS
    for x in range(8, 12): m[6][x] = TB
    
    return Scene('town_hall', 'Balai Kota', m,
        portals=[(9,14,'town',24,10), (10,14,'town',24,10)],
        indoor=True)

def build_beach():
    W_, H_ = 30, 20
    m = [[SD]*W_ for _ in range(H_)]
    
    m[0][15] = P; m[0][16] = P
    m[1][15] = P; m[1][16] = P

    for y in range(12, H_):
        for x in range(W_):
            m[y][x] = W
            
    m[10][5] = STN
    m[9][25] = STN
    m[11][15] = STN

    return Scene('beach', 'Pantai Mineral', m,
        portals=[(15,0,'town',20,28), (16,0,'town',21,28)],
        npcs=[])

def build_forest():
    W_, H_ = 30, 30
    m = [[G]*W_ for _ in range(H_)]
    def hline_(y,x1,x2,t):
        for x in range(x1,x2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
    def vline_(x,y1,y2,t):
        for y in range(y1,y2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
            
    rng = random.Random(13)
    for y in range(H_):
        for x in range(W_):
            if rng.random() < 0.25:
                m[y][x] = TR
                
    # Jalan Setapak Hutan
    vline_(14, 0, H_-1, P)
    vline_(15, 0, H_-1, P)
    hline_(15, 0, 15, P)
    
    for y in range(H_):
        if m[y][14] == TR: m[y][14] = G
        if m[y][15] == TR: m[y][15] = G
    for x in range(16):
        if m[15][x] == TR: m[15][x] = G
                    
    return Scene('forest', 'Hutan Dalam', m,
        portals=[
            (14, 0, 'outdoor', 14, 23),
            (15, 0, 'outdoor', 15, 23),
            (14, 29, 'lake', 14, 1),
            (15, 29, 'lake', 15, 1),
            (0, 15, 'cave_path', 18, 10),
        ],
        npcs=[('genderuwo', 20, 15), ('kuntilanak', 8, 20)])

def build_lake():
    W_, H_ = 30, 25
    m = [[G]*W_ for _ in range(H_)]
    m[0][14] = P; m[0][15] = P
    m[1][14] = P; m[1][15] = P
    
    for y in range(5, 20):
        for x in range(5, 25):
            m[y][x] = W
            
    m[10][4] = P; m[10][5] = P; m[10][6] = P # Dermaga

    return Scene('lake', 'Danau Pancing', m,
        portals=[(14,0,'forest',14,28), (15,0,'forest',15,28)],
        npcs=[])

def build_cave_path():
    W_, H_ = 20, 20
    m = [[G]*W_ for _ in range(H_)]
    def hline_(y,x1,x2,t):
        for x in range(x1,x2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
    def vline_(x,y1,y2,t):
        for y in range(y1,y2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
            
    rng = random.Random(42)
    for y in range(H_):
        for x in range(W_):
            if rng.random() < 0.4: m[y][x] = D
            if rng.random() < 0.1: m[y][x] = STN
                
    hline_(10, 0, W_-1, P)
    vline_(10, 0, 10, P)

    for x in range(W_): m[10][x] = P
    for y in range(11): m[y][10] = P

    return Scene('cave_path', 'Jalan ke Goa', m,
        portals=[
            (19,10,'forest',1,15),
            (10,0,'cave',10,18),
            (0,10,'mountain_peak',18,10)
        ], npcs=[])

def build_cave():
    W_, H_ = 20, 20
    m = [[D]*W_ for _ in range(H_)]
    for y in range(H_):
        for x in range(W_):
            if x == 0 or x == W_-1 or y == 0 or y == H_-1:
                m[y][x] = CV
            elif random.random() < 0.1:
                m[y][x] = FL
    # BUG FIX: Pastikan portal keluar dan area chest tidak terhalang dinding
    m[19][10] = P
    m[2][10] = CH # Power-up Rahasia
    return Scene('cave', 'Gua Misterius', m,
        portals=[(10, 19, 'cave_path', 10, 1)],
        npcs=[('banaspati', 5, 10), ('banaspati', 15, 10), ('naga', 10, 5)], indoor=True)

def build_mountain_peak():
    W_, H_ = 20, 20
    m = [[G]*W_ for _ in range(H_)]
    def hline_(y,x1,x2,t):
        for x in range(x1,x2+1):
            if 0<=y<H_ and 0<=x<W_: m[y][x] = t
            
    rng = random.Random(99)
    for y in range(H_):
        for x in range(W_):
            if y < 5 and rng.random() < 0.5: m[y][x] = STN
            elif y >= 5 and rng.random() < 0.2: m[y][x] = TR
                
    hline_(10, 10, 19, P)
    for y in range(5, 10):
        for x in range(5, 15): m[y][x] = G

    return Scene('mountain_peak', 'Puncak Gunung', m,
        portals=[(19,10,'cave_path',1,10)], npcs=[('jin', 10, 8)])

def build_house():
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    # Walls
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    # Door out
    m[H_-1][7] = DR
    # Windows (decorative - still walkable not needed since on top wall row)
    # Furniture
    m[1][1] = BD; m[1][2] = BD
    m[2][1] = CH
    m[1][4] = BS; m[1][5] = BS
    m[3][1] = MR
    m[4][1] = PP
    m[1][7] = FP
    m[1][9] = CL
    m[1][10] = TV
    m[3][6] = TB; m[3][7] = TB
    m[1][11] = ST; m[1][12] = ST
    m[2][11] = SH; m[2][12] = SH
    m[5][13] = PP
    return Scene('house', 'Rumah Kamu', m,
        portals=[(7,11,'outdoor',3,5)],
        indoor=True)

def build_shop():
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    # Shop counter across middle
    for x in range(1, W_-1):
        m[4][x] = CT
    # Shelves on back
    for x in range(1, W_-1):
        m[1][x] = SH
    return Scene('shop', 'Warung Bu Sari', m,
        portals=[(7,11,'town',7,11)],
        npcs=[('sari',7,3)],
        indoor=True)

def build_clinic():
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    m[1][1] = BD; m[1][2] = BD
    m[1][12] = BD; m[1][13] = BD
    m[3][1] = TB; m[3][13] = BS
    return Scene('clinic', 'Klinik Pak Raka', m,
        portals=[(7,11,'town',14,11)],
        npcs=[('raka',7,3)],
        indoor=True)

def build_studio():
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    m[1][6] = TB; m[1][7] = TB; m[1][8] = TB
    m[3][1] = BS; m[3][2] = BS
    return Scene('studio', 'Studio Maya', m,
        portals=[(7,11,'town',34,11)],
        npcs=[('maya',7,3)],
        indoor=True)

def build_smith():
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    m[1][6] = TB
    m[2][1] = SH
    m[1][12] = FP  # forge
    return Scene('smith', 'Bengkel Budi', m,
        portals=[(7,11,'town',10,15)],
        npcs=[('budi',7,3)],
        indoor=True)

def build_greenhouse():
    W_, H_ = 15, 12
    m = [[D]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    for x in range(1, W_-1):
        m[5][x] = P
    return Scene('greenhouse', 'Rumah Kaca', m,
        portals=[(7,11,'town',30,15)],
        indoor=True)

def build_barn():
    W_, H_ = 16, 14
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    for x in range(2, 6): m[2][x] = TB # Tempat makan hewan
    for x in range(10, 14): m[2][x] = TB
    return Scene('barn', 'Kandang Hewan', m,
        portals=[(7,13,'outdoor',12,12)],
        npcs=[('ayam', 4, 6), ('sapi', 10, 7)], indoor=True)

SCENES = {
    'outdoor': build_outdoor(),
    'house': build_house(),
    'shop': build_shop(),
    'clinic': build_clinic(),
    'studio': build_studio(),
    'smith': build_smith(),
    'greenhouse': build_greenhouse(),
    'barn': build_barn(),
    'town': build_town(),
    'town_hall': build_town_hall(),
    'beach': build_beach(),
    'forest': build_forest(),
    'lake': build_lake(),
    'cave_path': build_cave_path(),
    'cave': build_cave(),
    'mountain_peak': build_mountain_peak(),
}

# ══════════════════════════════════════════════════════════════
#  GAME STATE
# ══════════════════════════════════════════════════════════════
@dataclass
class GameState:
    # Scene & player
    scene_name: str = 'outdoor'
    player_x: int = 5
    player_y: int = 7
    facing: str = 'down'

    # Stats
    hp: int = 100
    max_hp: int = 100

    # Time
    day: int = 1
    year: int = 1
    day_in_season: int = 1
    season_index: int = 0
    time_minutes: float = 360.0  # 6:00 AM
    weather: str = 'Cerah'
    tomorrow_weather: str = 'Cerah'

    # Stats
    energy: int = 100
    max_energy: int = 100
    gold: int = 100
    tool_index: int = 0
    seed_key: str = 'lobak'

    # Inventory
    inventory: dict = field(default_factory=lambda: {'lobak_seed': 3})
    chest_inventory: dict = field(default_factory=dict)

    # Soil: key "x,y,scene" -> dict
    soil: dict = field(default_factory=dict)

    # NPC
    npc_hearts: dict = field(default_factory=lambda: {n:0 for n in NPCS})
    npc_dialog_index: dict = field(default_factory=lambda: {n:0 for n in NPCS})

    # Upgrades
    upgrades: dict = field(default_factory=lambda: {'hoe':False,'water':False,'bag':False,'axe':False, 'bag_level':1})

    # Quest
    quest_stage: int = 0
    mail_read: bool = False
    shop_unlocked: bool = False
    greenhouse_open: bool = False
    naga_met: bool = False

    # Stats
    festival_submitted: dict = field(default_factory=dict)
    stats: dict = field(default_factory=lambda: {
        'lobak_planted':0,'watered':0,'lobak_harvested':0,
        'corn_harvested':0,'earned':0,'gifts':0,
        'seasons_harvested':[],
    })

    def save(self):
        data = {
            'scene_name': self.scene_name, 'player_x': self.player_x, 'player_y': self.player_y,
            'facing': self.facing, 'day': self.day, 'year': self.year,
            'day_in_season': self.day_in_season, 'season_index': self.season_index,
            'time_minutes': self.time_minutes, 'weather': self.weather, 'tomorrow_weather': getattr(self, 'tomorrow_weather', 'Cerah'),
            'hp': getattr(self, 'hp', 100), 'max_hp': getattr(self, 'max_hp', 100),
            'energy': self.energy, 'max_energy': self.max_energy, 'gold': self.gold,
            'tool_index': self.tool_index, 'seed_key': self.seed_key,
            'inventory': self.inventory, 'chest_inventory': getattr(self, 'chest_inventory', {}), 'soil': self.soil,
            'npc_hearts': self.npc_hearts, 'npc_dialog_index': self.npc_dialog_index,
            'upgrades': self.upgrades, 'quest_stage': self.quest_stage,
            'mail_read': self.mail_read, 'shop_unlocked': self.shop_unlocked, 'festival_submitted': getattr(self, 'festival_submitted', {}),
            'greenhouse_open': self.greenhouse_open, 'naga_met': self.naga_met, 'stats': self.stats,
        }
        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    @classmethod
    def load(cls):
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            gs = cls()
            for k, v in data.items():
                if hasattr(gs, k):
                    setattr(gs, k, v)
            return gs
        except Exception as e:
            print(f"Load error: {e}")
            return None

    def get_season(self):
        return SEASONS[self.season_index]

    def get_season_name(self):
        return SEASON_NAMES[self.get_season()]

    def get_time_str(self):
        h = int(self.time_minutes // 60)
        mi = int(self.time_minutes % 60)
        return f"{h:02d}:{mi:02d}"

# ══════════════════════════════════════════════════════════════
#  GAME
# ══════════════════════════════════════════════════════════════
class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🌱 Lembah Karsa — Farming RPG")
        self.clock = pygame.time.Clock()

        # Fonts
        self.font_small = pygame.font.Font(None, 16)
        self.font = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 28)
        self.font_title = pygame.font.Font(None, 40)

        # Init sprites
        init_sprites()

        # State
        self.state = GameState()
        self.running = True
        self.mode = 'title'  # title, play, dialog, menu, shop, upgrade, sleep, fade
        self.fade_alpha = 0
        self.fade_dir = 0  # -1 = fade in, 1 = fade out
        self.fade_callback = None

        # Animation
        self.anim_tick = 0
        self.walk_frame = 0
        self.moving = False

        # Dialog
        self.dialog_lines = []
        self.dialog_index = 0
        self.dialog_speaker = ''
        self.dialog_callback = None
        self.typewriter_progress = 0
        self.typewriter_speed = 2

        # Menu
        self.menu_items = []
        self.menu_selected = 0
        self.menu_title = ''
        self.menu_callback = None

        # Notification
        self.notif_text = ''
        self.notif_timer = 0

        # Camera
        self.cam_x = 0
        self.cam_y = 0
        
        # --- FITUR V4: Smooth Visual & Parallax ---
        self.px_vis = 0.0
        self.py_vis = 0.0
        self.cloud_x = 0.0
        self.particles = []
        self.make_clouds_and_shadows()

        # NPC positions (for wandering)
        self.npc_frame_tick = 0

        # Input cooldowns
        self.move_cooldown = 0
        self.move_delay = 140  # ms between moves
        self.invuln_timer = 0

        # Action Tool Animation
        self.action_timer = 0
        self.action_duration = 200

        # --- BGM Init ---
        self.current_bgm = None
        self.playing_bgm_path = None
        try:
            pygame.mixer.init()
        except Exception as e:
            print(f"BGM Info: {e}")

        # --- SFX Init ---
        self.sfx = {}
        try:
            pygame.mixer.init()
            for sfx_name in ['cangkul', 'kapak', 'siram', 'panen', 'palu']:
                sfx_path = os.path.join("assets", f"{sfx_name}.wav")
                if os.path.exists(sfx_path):
                    self.sfx[sfx_name] = pygame.mixer.Sound(sfx_path)
                    self.sfx[sfx_name].set_volume(0.6)
        except Exception as e:
            print(f"SFX Info: {e}")

    def play_sfx(self, name):
        if hasattr(self, 'sfx') and name in self.sfx:
            self.sfx[name].play()

    def update_audio(self):
        if not pygame.mixer.get_init():
            return
            
        if self.mode not in ('play', 'inventory', 'chest', 'dialog', 'menu'):
            return
            
        scene = SCENES[self.state.scene_name]
        is_wet = not scene.indoor and self.state.weather in ('Hujan', 'Badai')
        is_night = self.state.time_minutes >= 18 * 60 or self.state.time_minutes < 5 * 60
        
        target_bgm = "bgm_day"
        if is_wet:
            target_bgm = "ambient_rain"
        elif is_night:
            target_bgm = "ambient_night"
        elif scene.indoor:
            target_bgm = "bgm_indoor"
            
        if getattr(self, 'current_bgm', None) != target_bgm:
            self.current_bgm = target_bgm
            
            loaded_path = None
            for ext in ['.ogg', '.mp3', '.wav', '.mid']:
                path = os.path.join("assets", f"{target_bgm}{ext}")
                if os.path.exists(path):
                    loaded_path = path
                    break
                    
            if not loaded_path:
                for ext in ['.ogg', '.mp3', '.wav', '.mid']:
                    path = os.path.join("assets", f"bgm{ext}")
                    if os.path.exists(path):
                        loaded_path = path
                        break
                        
            if loaded_path and getattr(self, 'playing_bgm_path', None) != loaded_path:
                try:
                    pygame.mixer.music.load(loaded_path)
                    pygame.mixer.music.set_volume(0.3 if 'bgm' in target_bgm else 0.5)
                    pygame.mixer.music.play(-1)
                    self.playing_bgm_path = loaded_path
                except Exception:
                    pass

    def make_clouds_and_shadows(self):
        self.cloud_surf = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        for _ in range(12):
            cx = random.randint(0, SCREEN_W)
            cy = random.randint(0, SCREEN_H//2)
            for _ in range(6):
                pygame.draw.circle(self.cloud_surf, (255,255,255, 40), 
                    (cx + random.randint(-40,40), cy + random.randint(-20,20)), random.randint(20, 60))
        
        self.shadow_std = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_std, (0,0,0, 80), (6, TILE - 12, TILE - 12, 12))
        
        self.shadow_std_small = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_std_small, (0,0,0, 50), (10, TILE - 10, TILE - 20, 8))
        
        # Bayangan naga dinamis mengikuti ukuran asli sprite naga
        naga_w = ANIMATED['npc_naga']['down'][0].get_width()
        naga_h = ANIMATED['npc_naga']['down'][0].get_height()
        self.shadow_naga = pygame.Surface((naga_w, naga_h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.shadow_naga, (0,0,0, 80), (naga_w * 0.15, naga_h - naga_h * 0.25, naga_w * 0.7, naga_h * 0.25))

        # Firefly sprite
        self.firefly_surf = pygame.Surface((12, 12), pygame.SRCALPHA)
        pygame.draw.circle(self.firefly_surf, (200, 255, 100, 40), (6, 6), 6)
        pygame.draw.circle(self.firefly_surf, (220, 255, 150, 150), (6, 6), 3)
        pygame.draw.circle(self.firefly_surf, (255, 255, 255, 255), (6, 6), 1)

        # Vignette for indoor
        self.vignette_surf = pygame.Surface((SCREEN_W, VIEW_H * TILE), pygame.SRCALPHA)
        cx, cy = SCREEN_W // 2, (VIEW_H * TILE) // 2
        max_d = math.hypot(cx, cy)
        for y in range(0, VIEW_H * TILE, 6):
            for x in range(0, SCREEN_W, 6):
                d = math.hypot(x - cx, y - cy)
                alpha = min(220, int(220 * (d / max_d)**2.5))
                if alpha > 0:
                    pygame.draw.rect(self.vignette_surf, (10, 5, 20, alpha), (x, y, 6, 6))

    # ═══════════════════════════════════════════════════
    #  MAIN LOOP
    # ═══════════════════════════════════════════════════
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                elif event.type == pygame.MOUSEWHEEL:
                    # Fitur QoL terinspirasi dari Harvest Moon 2.0: Mengganti alat dengan scroll mouse
                    if self.mode == 'play':
                        if event.y > 0: # Scroll atas
                            self.state.tool_index = (self.state.tool_index - 1) % len(TOOLS)
                        elif event.y < 0: # Scroll bawah
                            self.state.tool_index = (self.state.tool_index + 1) % len(TOOLS)
                        self.notif(f"Alat: {TOOLS[self.state.tool_index]}")

            self.update(dt)
            self.render()
            pygame.display.flip()

        pygame.quit()

    # ═══════════════════════════════════════════════════
    #  INPUT
    # ═══════════════════════════════════════════════════
    def handle_keydown(self, event):
        if self.mode == 'title':
            if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                self.start_new_game()
            elif event.key == pygame.K_l:
                self.try_load_game()
            return

        if self.mode == 'fade':
            return

        if self.mode == 'dialog':
            if event.key in (pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
                self.advance_dialog()
            return

        if self.mode == 'menu':
            if event.key in (pygame.K_UP, pygame.K_w):
                self.menu_selected = (self.menu_selected - 1) % len(self.menu_items)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.menu_selected = (self.menu_selected + 1) % len(self.menu_items)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_e):
                self.menu_activate()
            elif event.key == pygame.K_ESCAPE:
                self.close_menu()
            return

        if self.mode in ('inventory', 'chest'):
            if event.key == pygame.K_ESCAPE or (self.mode == 'inventory' and event.key == pygame.K_i) or (self.mode == 'chest' and event.key == pygame.K_e):
                self.mode = 'play'
            elif event.key == pygame.K_TAB and self.mode == 'chest':
                self.chest_active = not getattr(self, 'chest_active', False)
                self.inventory_cursor = 0
            elif event.key in (pygame.K_UP, pygame.K_w):
                self.inventory_cursor = max(0, getattr(self, 'inventory_cursor', 0) - 6)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                active_list = getattr(self, 'chest_list', []) if getattr(self, 'chest_active', False) else getattr(self, 'inventory_list', [])
                self.inventory_cursor = min(max(0, len(active_list) - 1), getattr(self, 'inventory_cursor', 0) + 6)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                self.inventory_cursor = max(0, getattr(self, 'inventory_cursor', 0) - 1)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                active_list = getattr(self, 'chest_list', []) if getattr(self, 'chest_active', False) else getattr(self, 'inventory_list', [])
                self.inventory_cursor = min(max(0, len(active_list) - 1), getattr(self, 'inventory_cursor', 0) + 1)
            elif event.key in (pygame.K_SPACE, pygame.K_RETURN):
                if self.mode == 'chest':
                    self.transfer_item()
            elif event.key in (pygame.K_BACKSPACE, pygame.K_x):
                self.drop_selected_item()
            return

        if self.mode == 'play':
            # Movement handled in update()
            if event.key in (pygame.K_SPACE,):
                self.use_tool()
            elif event.key in (pygame.K_e, pygame.K_RETURN):
                self.interact()
            elif pygame.K_1 <= event.key <= pygame.K_8:
                self.state.tool_index = event.key - pygame.K_1
            elif event.key == pygame.K_q:
                self.cycle_seed(-1)
            elif event.key == pygame.K_r:
                self.cycle_seed(1)
            elif event.key == pygame.K_t:
                # sleep shortcut
                scene = SCENES[self.state.scene_name]
                if scene.name == 'house' or (scene.name == 'outdoor' and self.state.player_x <= 6 and self.state.player_y <= 6):
                    self.confirm_sleep()
            elif event.key == pygame.K_F5:
                if self.state.save():
                    self.notif("💾 Tersimpan!")
            elif event.key == pygame.K_h:
                self.show_calendar_menu()
            elif event.key == pygame.K_f:
                self.catch_spirit()
            elif event.key == pygame.K_i:
                self.open_inventory()
            elif event.key == pygame.K_ESCAPE:
                self.open_main_menu()

    # ═══════════════════════════════════════════════════
    #  UPDATE
    # ═══════════════════════════════════════════════════
    def update(self, dt):
        self.anim_tick += dt
        self.npc_frame_tick += dt

        if self.notif_timer > 0:
            self.notif_timer -= dt

        # Fade transition
        if self.mode == 'fade':
            self.fade_alpha += self.fade_dir * 12
            if self.fade_dir == 1 and self.fade_alpha >= 255:
                self.fade_alpha = 255
                if self.fade_callback:
                    self.fade_callback()
                    self.fade_callback = None
                self.fade_dir = -1
            elif self.fade_dir == -1 and self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_dir = 0
                self.mode = 'play'
            return

        if self.mode == 'play':
            if self.action_timer > 0:
                self.action_timer -= dt
                if self.action_timer < 0: self.action_timer = 0

            # Advance clock
            active_festival = self.get_active_festival()
            is_festival_day = active_festival is not None

            if not is_festival_day: # Freeze time during festival
                self.state.time_minutes += dt * 0.0016  # 1 hari (16 jam in-game) = 10 menit dunia nyata

            if self.state.time_minutes >= 22*60:
                self.state.time_minutes = 22*60
                self.start_dialog(["Sudah terlalu larut...", "Kamu jatuh pingsan karena kelelahan!"], "🌙 Malam",
                                  callback=lambda: self.sleep_next_day(fainted=True))

            # Movement
            self.handle_movement(dt)

            # --- FITUR V4: LERP (Pixel Interpolation) Player Visual & Camera ---
            lerp_speed = min(1.0, 15.0 * (dt / 1000.0))
            self.px_vis += (self.state.player_x - self.px_vis) * lerp_speed
            self.py_vis += (self.state.player_y - self.py_vis) * lerp_speed
            
            scene = SCENES[self.state.scene_name]
            self.cam_x += (max(0, min(scene.w - VIEW_W, self.px_vis - VIEW_W / 2)) - self.cam_x) * lerp_speed
            self.cam_y += (max(0, min(scene.h - VIEW_H, self.py_vis - VIEW_H / 2)) - self.cam_y) * lerp_speed

            # --- NPC Smooth Movement & Roaming ---
            if getattr(self, 'invuln_timer', 0) > 0:
                self.invuln_timer -= dt

            is_festival_scene = is_festival_day and scene.name == active_festival['scene']

            npc_lerp = min(1.0, 6.0 * (dt / 1000.0))
            is_night = self.state.time_minutes >= 18 * 60
            for npc in scene.npcs[:]:
                if is_festival_scene and npc['id'] in active_festival['locations']:
                    festival_pos = active_festival['locations'][npc['id']]
                    npc['x'], npc['y'] = festival_pos[0], festival_pos[1]
                    npc['px'], npc['py'] = float(npc['x']), float(npc['y'])
                    npc['moving'] = False
                    npc['timer'] = 999999 # Prevent roaming
                    if self.state.player_y > npc['y']: npc['facing'] = 'down'
                    else: npc['facing'] = 'up'

                dist_x = npc['x'] - npc['px']
                dist_y = npc['y'] - npc['py']
                npc['px'] += dist_x * npc_lerp
                npc['py'] += dist_y * npc_lerp
                npc['moving'] = (abs(dist_x) > 0.05 or abs(dist_y) > 0.05)
                
                npc['timer'] -= dt
                npc['attack_timer'] = npc.get('attack_timer', 0) - dt
                
                target_x, target_y = None, None
                is_hostile = npc['id'] in ['banaspati', 'genderuwo', 'kuntilanak']
                
                # AI Mengejar & Menyerang Pemain
                if is_hostile:
                    dist_to_player = math.hypot(self.state.player_x - npc['x'], self.state.player_y - npc['y'])
                    if dist_to_player <= 5:
                        target_x, target_y = self.state.player_x, self.state.player_y
                        npc['timer'] = 0 # Agresif mendekat
                        
                        if dist_to_player <= 1.5 and npc['attack_timer'] <= 0 and getattr(self, 'invuln_timer', 0) <= 0:
                            self.state.hp -= 15
                            self.notif(f"Diserang {npc['id']}! -15 HP")
                            self.play_sfx('panen')
                            self.invuln_timer = 1500
                            npc['attack_timer'] = 2000
                            
                            if self.state.hp <= 0:
                                self.state.hp = 0
                                self.start_dialog(["Kamu terluka parah...", "Pandanganmu menggelap!"], "💫 Tumbang", callback=lambda: self.sleep_next_day(fainted=True))

                if npc['timer'] <= 0:
                    npc['timer'] = random.randint(2000, 5000) if not is_hostile else random.randint(500, 1000)
                    
                    target_x, target_y = None, None
                    if not is_hostile and is_night and npc['id'] not in ['jin', 'kuntilanak', 'genderuwo', 'banaspati', 'betsy']:
                        target_x, target_y = npc['home_x'], npc['home_y']
                        if scene.name == 'outdoor' and npc['id'] == 'arya':
                            target_x, target_y = 22, 5
                    
                    moved = False
                    if target_x is not None and target_y is not None:
                        if int(npc['x']) != target_x or int(npc['y']) != target_y:
                            dx = 1 if target_x > npc['x'] else (-1 if target_x < npc['x'] else 0)
                            dy = 1 if target_y > npc['y'] else (-1 if target_y < npc['y'] else 0)
                            
                            nx, ny = npc['x'], npc['y']
                            if dx != 0 and self.can_walk(npc['x'] + dx, npc['y']): nx = npc['x'] + dx
                            elif dy != 0 and self.can_walk(npc['x'], npc['y'] + dy): ny = npc['y'] + dy
                                
                            if nx != npc['x'] or ny != npc['y']:
                                npc['x'] = nx; npc['y'] = ny
                                moved = True
                                if nx > npc['x']: npc['facing'] = 'right'
                                elif nx < npc['x']: npc['facing'] = 'left'
                                elif ny > npc['y']: npc['facing'] = 'down'
                                elif ny < npc['y']: npc['facing'] = 'up'

                    if not moved and random.random() < 0.4:
                        dx, dy = random.choice([(0,1), (0,-1), (1,0), (-1,0)])
                        nx, ny = npc['x'] + dx, npc['y'] + dy
                        if target_x is not None and (abs(nx - target_x) > 2 or abs(ny - target_y) > 2):
                            continue
                        if self.can_walk(nx, ny) and not (nx == self.state.player_x and ny == self.state.player_y):
                            npc['x'] = nx; npc['y'] = ny
                            if dx > 0: npc['facing'] = 'right'
                            elif dx < 0: npc['facing'] = 'left'
                            elif dy > 0: npc['facing'] = 'down'
                            elif dy < 0: npc['facing'] = 'up'

            # Typewriter advance
            if self.mode == 'dialog':
                pass

        if self.mode == 'dialog':
            if self.typewriter_progress < len(self.dialog_lines[self.dialog_index]):
                self.typewriter_progress += self.typewriter_speed

        # --- Particle Update ---
        if self.mode == 'play':
            scene = SCENES[self.state.scene_name]
            if not scene.indoor:
                is_night = self.state.time_minutes >= 18 * 60 or self.state.time_minutes < 5 * 60
                if is_night and self.state.weather not in ('Hujan', 'Badai'):
                    if random.random() < 0.05:
                        self.particles.append({
                            'x': random.uniform(0, SCREEN_W),
                            'y': random.uniform(0, VIEW_H * TILE),
                            'vx': random.uniform(-0.5, 0.5),
                            'vy': random.uniform(-0.5, 0.5),
                            'life': random.randint(100, 200),
                            'max_life': 200,
                            'type': 'firefly'
                        })
                elif self.state.weather == 'Berangin' or (self.state.season_index in [0, 2] and random.random() < 0.05):
                    self.particles.append({
                        'x': random.uniform(0, SCREEN_W),
                        'y': -10,
                        'vx': random.uniform(1, 4) if self.state.weather == 'Berangin' else random.uniform(-1, 1),
                        'vy': random.uniform(1, 3),
                        'life': random.randint(150, 300),
                        'max_life': 300,
                        'type': 'leaf' if self.state.season_index == 2 else 'petal'
                    })

            for p in reversed(self.particles):
                p['x'] += p['vx']
                p['y'] += p['vy']
                p['life'] -= 1
                if p['type'] == 'firefly':
                    p['vx'] += random.uniform(-0.1, 0.1)
                    p['vy'] += random.uniform(-0.1, 0.1)
                    p['vx'] = max(-1.0, min(1.0, p['vx']))
                    p['vy'] = max(-1.0, min(1.0, p['vy']))
                
                if p['life'] <= 0 or p['y'] > VIEW_H * TILE + 20 or p['x'] < -20 or p['x'] > SCREEN_W + 20:
                    self.particles.remove(p)

    def handle_movement(self, dt):
        if self.action_timer > 0:
            self.moving = False
            return

        keys = pygame.key.get_pressed()
        self.move_cooldown -= dt
        if self.move_cooldown > 0:
            return

        dx = dy = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1; self.state.facing = 'up'
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1; self.state.facing = 'down'
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1; self.state.facing = 'left'
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1; self.state.facing = 'right'
        else:
            self.moving = False
            return

        nx = self.state.player_x + dx
        ny = self.state.player_y + dy
        if self.can_walk(nx, ny):
            self.state.player_x = nx
            self.state.player_y = ny
            self.moving = True
            self.walk_frame = (self.walk_frame + 1) % 2

            # Check portal
            scene = SCENES[self.state.scene_name]
            for portal in scene.portals:
                if portal[0] == nx and portal[1] == ny:
                    active_festival = self.get_active_festival()
                    if active_festival:
                        self.notif("Tidak bisa meninggalkan kota selama festival.")
                        break
                    # Rumah kaca adalah milestone cerita: sebelum diperbaiki,
                    # pintunya menampilkan opsi restorasi alih-alih langsung masuk.
                    if portal[2] == 'greenhouse' and not self.state.greenhouse_open:
                        self.handle_greenhouse_gate(portal)
                    else:
                        self.transition_to(portal[2], portal[3], portal[4])
                    break
        else:
            self.moving = False

        self.move_cooldown = self.move_delay

        # --- Cutscene Trigger Naga ---
        if self.state.scene_name == 'cave' and not getattr(self.state, 'naga_met', False):
            naga_npc = next((n for n in SCENES['cave'].npcs if n['id'] == 'naga'), None)
            if naga_npc and abs(self.state.player_x - naga_npc['x']) <= 3 and abs(self.state.player_y - naga_npc['y']) <= 3:
                self.trigger_naga_cutscene(naga_npc)

    def can_walk(self, x, y):
        scene = SCENES[self.state.scene_name]
        if x < 0 or x >= scene.w or y < 0 or y >= scene.h:
            return False
        t = scene.tiles[y][x]
        # Check blocking furniture
        if t in BLOCKING and t != DR:
            return False
        # Door is walkable (triggers portal)
        return t in WALKABLE or t == DR

    def snap_camera(self):
        self.px_vis = float(self.state.player_x)
        self.py_vis = float(self.state.player_y)
        scene = SCENES[self.state.scene_name]
        self.cam_x = float(max(0, min(scene.w - VIEW_W, self.px_vis - VIEW_W / 2)))
        self.cam_y = float(max(0, min(scene.h - VIEW_H, self.py_vis - VIEW_H / 2)))

    # ═══════════════════════════════════════════════════
    #  TOOLS
    # ═══════════════════════════════════════════════════
    def get_facing_tile(self):
        x, y = self.state.player_x, self.state.player_y
        if self.state.facing == 'up': return (x, y-1)
        if self.state.facing == 'down': return (x, y+1)
        if self.state.facing == 'left': return (x-1, y)
        return (x+1, y)

    def use_tool(self):
        if self.action_timer > 0:
            return
            
        self.action_timer = self.action_duration
        
        tool = TOOLS[self.state.tool_index]
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.state.scene_name]
        
        # --- SISTEM BERTARUNG (COMBAT CHECK) ---
        hit_npc = None
        for npc in scene.npcs:
            if npc['x'] == fx and npc['y'] == fy:
                hit_npc = npc
                break
                
        if hit_npc and hit_npc['id'] in ['banaspati', 'genderuwo', 'kuntilanak']:
            dmg = 0
            if tool == 'Palu': dmg = 2
            elif tool == 'Kapak': dmg = 1
            elif tool == 'Cangkul': dmg = 1
            elif tool == 'Pancing': dmg = 1
            
            if dmg > 0 and self.spend_energy(1):
                hit_npc['hp'] -= dmg
                self.notif(f"Menyerang {hit_npc['id']}! ({dmg} DMG)")
                self.play_sfx('palu')
                
                # Efek Knockback mundur 1 tile
                dx = fx - self.state.player_x
                dy = fy - self.state.player_y
                if self.can_walk(fx + dx, fy + dy):
                    hit_npc['x'] += dx
                    hit_npc['y'] += dy
                    
                if hit_npc['hp'] <= 0:
                    self.notif(f"{hit_npc['id']} dikalahkan!")
                    if hit_npc['id'] == 'banaspati':
                        self.state.inventory['api_magis'] = self.state.inventory.get('api_magis', 0) + 1
                    elif hit_npc['id'] == 'genderuwo':
                        self.state.inventory['taring'] = self.state.inventory.get('taring', 0) + 1
                    elif hit_npc['id'] == 'kuntilanak':
                        self.state.inventory['kain_putih'] = self.state.inventory.get('kain_putih', 0) + 1
                    scene.npcs.remove(hit_npc)
                return

        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h:
            return
        t = scene.tiles[fy][fx]

        if tool == 'Cangkul':
            self.use_hoe(fx, fy, t)
        elif tool == 'Siram':
            self.use_watering(fx, fy)
        elif tool == 'Tanam':
            self.use_plant(fx, fy)
        elif tool == 'Panen':
            self.use_harvest(fx, fy)
        elif tool == 'Kapak':
            self.use_axe(fx, fy, t)
        elif tool == 'Pancing':
            self.use_fishing(fx, fy, t)
        elif tool == 'Hadiah':
            self.give_gift()
        elif tool == 'Palu':
            self.use_hammer(fx, fy, t)

    def use_hoe(self, x, y, tile):
        if tile not in TILLABLE:
            self.notif("Tidak bisa dicangkul!")
            return
        cost = 1 if self.state.upgrades['hoe'] else 3
        if not self.spend_energy(cost):
            return
        key = f"{x},{y},{self.state.scene_name}"
        self.state.soil[key] = {'tilled':True,'watered':False,'crop':None,'age':0}
        self.notif("Tanah dicangkul!")
        self.play_sfx('cangkul')

    def use_watering(self, x, y):
        cost = 1 if self.state.upgrades['water'] else 2
        if not self.spend_energy(cost):
            return
        cells = [(x,y)]
        if self.state.upgrades['water']:
            cells.extend([(x,y-1),(x,y+1)])
        count = 0
        for cx, cy in cells:
            key = f"{cx},{cy},{self.state.scene_name}"
            if key in self.state.soil and self.state.soil[key].get('tilled'):
                self.state.soil[key]['watered'] = True
                if self.state.soil[key].get('crop') == 'lobak':
                    self.state.stats['watered'] += 1
                count += 1
        if count:
            self.notif(f"Menyiram {count} petak!")
            self.play_sfx('siram')
        else:
            self.notif("Tidak ada lahan di sini.")

    def use_plant(self, x, y):
        key = f"{x},{y},{self.state.scene_name}"
        soil = self.state.soil.get(key)
        if not soil or not soil.get('tilled'):
            self.notif("Cangkul dulu!")
            return
        if soil.get('crop'):
            self.notif("Sudah ada tanaman.")
            return
        seed_key = self.state.seed_key + '_seed'
        if self.state.inventory.get(seed_key, 0) <= 0:
            self.notif(f"Benih {CROPS[self.state.seed_key]['name']} habis!")
            return
        crop = CROPS[self.state.seed_key]
        in_greenhouse = self.state.scene_name == 'greenhouse' and self.state.greenhouse_open
        if self.state.get_season() not in crop['seasons'] and not in_greenhouse:
            self.start_dialog([f"{crop['name']} hanya bisa ditanam di musim: {', '.join(crop['seasons'])} atau di rumah kaca."], "🌱")
            return
        if not self.spend_energy(2):
            return
        self.state.inventory[seed_key] -= 1
        if self.state.inventory[seed_key] <= 0:
            del self.state.inventory[seed_key]
        soil['crop'] = self.state.seed_key
        soil['age'] = 0
        if self.state.seed_key == 'lobak':
            self.state.stats['lobak_planted'] += 1
        self.notif(f"Menanam {crop['name']}!")

    def use_harvest(self, x, y):
        scene = SCENES[self.state.scene_name]
        tile = scene.tiles[y][x]
        
        # Fitur cabut ilalang
        if tile == WD:
            if not self.spend_energy(1): return
            scene.tiles[y][x] = D
            self.state.inventory['rumput_liar'] = self.state.inventory.get('rumput_liar', 0) + 1
            self.notif("Mencabut ilalang! +1 Rumput Liar")
            self.play_sfx('panen')
            return
            
        key = f"{x},{y},{self.state.scene_name}"
        soil = self.state.soil.get(key)
        if not soil or not soil.get('crop'):
            self.notif("Tidak ada tanaman atau ilalang.")
            return
        crop = CROPS[soil['crop']]
        if soil.get('age', 0) < crop['days']:
            self.notif(f"{crop['name']} belum matang!")
            return
        if not self.spend_energy(2):
            return
        crop_id = soil['crop']
        self.state.inventory[crop_id] = self.state.inventory.get(crop_id, 0) + 1
        if crop_id == 'lobak':
            self.state.stats['lobak_harvested'] += 1
        if crop_id == 'jagung':
            self.state.stats['corn_harvested'] += 1
        szn = self.state.get_season()
        if szn not in self.state.stats['seasons_harvested']:
            self.state.stats['seasons_harvested'].append(szn)
        soil['crop'] = None
        soil['age'] = 0
        self.notif(f"✨ Panen {crop['name']}!")
        self.play_sfx('panen')
        self.check_quest_progress()

    def use_axe(self, x, y, tile):
        if not self.state.upgrades['axe']:
            self.notif("Butuh kapak! Beli dari Budi.")
            return
            
        if tile == CV:
            self.notif("Tembok bedrock ini tidak bisa dihancurkan!")
            return
            
        if tile == STN:
            # Cegah pemain menghancurkan batu pembatas/pegunungan di Hutan
            if self.state.scene_name == 'forest':
                self.notif("Batu pegunungan ini terlalu keras!")
                return
                
            if not self.spend_energy(2): return
            SCENES[self.state.scene_name].tiles[y][x] = D
            self.state.inventory['batu'] = self.state.inventory.get('batu', 0) + 1
            self.notif("Batu hancur! +1 Batu")
            return
            
        if tile != TR:
            self.notif("Tidak ada pohon atau batu.")
            return
        if not self.spend_energy(4):
            return
        SCENES[self.state.scene_name].tiles[y][x] = G
        self.state.inventory['kayu'] = self.state.inventory.get('kayu', 0) + 3
        self.notif("Pohon ditebang! +3 kayu")
        self.play_sfx('kapak')

    def use_hammer(self, x, y, tile):
        if tile != STN:
            self.notif("Palu hanya bisa menghancurkan batu.")
            return
        if self.state.scene_name == 'forest':
            self.notif("Batu pegunungan ini terlalu keras!")
            return
        if not self.spend_energy(2): return
        SCENES[self.state.scene_name].tiles[y][x] = D
        self.state.inventory['batu'] = self.state.inventory.get('batu', 0) + 1
        self.notif("Batu hancur! +1 Batu")
        self.play_sfx('palu')

    def use_fishing(self, x, y, tile):
        if tile != W:
            self.notif("Hanya bisa memancing di air!")
            return
        if not self.spend_energy(3): return
        if random.random() < 0.4:
            self.state.inventory['ikan'] = self.state.inventory.get('ikan', 0) + 1
            self.notif("🎣 Dapat Ikan!")
        else:
            self.notif("... Ikan lepas.")

    def give_gift(self):
        scene = SCENES[self.state.scene_name]
        px, py = self.state.player_x, self.state.player_y
        for npc in scene.npcs:
            if abs(npc['x'] - px) <= 1 and abs(npc['y'] - py) <= 1:
                npc_id = npc['id']
                npc_data = NPCS[npc_id]
                gift_item = npc_data['gift']
                if self.state.inventory.get(gift_item, 0) <= 0:
                    self.notif(f"Tidak punya {CROPS[gift_item]['name']}!")
                    return
                self.state.inventory[gift_item] -= 1
                if self.state.inventory[gift_item] <= 0:
                    del self.state.inventory[gift_item]
                self.state.npc_hearts[npc_id] = min(10, self.state.npc_hearts.get(npc_id, 0) + 2)
                self.state.stats['gifts'] += 1
                self.start_dialog([npc_data['gift_r']], npc_data['name'])
                self.check_quest_progress()
                return
        self.notif("Tidak ada warga di dekatmu.")
        
    def catch_spirit(self):
        active_festival = self.get_active_festival()
        if active_festival:
            self.notif("Tidak bisa menangkap makhluk halus saat festival.")
            return

        scene = SCENES[self.state.scene_name]
        px, py = self.state.player_x, self.state.player_y
        for npc in scene.npcs:
            if npc['id'] == 'jin' and abs(npc['x'] - px) <= 2 and abs(npc['y'] - py) <= 2:
                self.state.inventory['jin_soul'] = self.state.inventory.get('jin_soul', 0) + 1
                self.notif("✨ Jin Kebun memberimu berkah mistis!")
                return
        self.notif("Tidak ada makhluk mistis di dekatmu yang bisa ditangkap.")

    def spend_energy(self, n):
        # During festivals, actions don't cost energy
        active_festival = self.get_active_festival()
        if active_festival and self.state.scene_name == active_festival['scene']:
            return True

        # Malam hari = di atas jam 20:00 (8 PM)
        is_late_night = self.state.time_minutes >= 20 * 60
        scene = SCENES[self.state.scene_name]
        is_bad_weather = self.state.weather in ('Hujan', 'Badai') and not scene.indoor
        
        # Bekerja di malam hari menguras energi 2x lipat
        cost = n * 2 if is_late_night else n

        # Bekerja di luar ruangan saat hujan menguras ekstra +1 energi
        if is_bad_weather:
            cost += 1

        if self.state.energy < cost:
            if is_late_night:
                self.state.energy = 0
                self.start_dialog([
                    "Pandanganmu mulai kabur...",
                    "Kamu terlalu memaksakan diri bekerja malam hari.",
                    "Kamu jatuh pingsan!"
                ], "💫 Kelelahan", callback=lambda: self.sleep_next_day(fainted=True))
            elif is_bad_weather and self.state.energy >= n:
                self.start_dialog(["Energimu tidak cukup!", "Bekerja di tengah hujan menguras lebih banyak tenaga."], "⚡")
            else:
                self.start_dialog(["Energimu tidak cukup!", "Tidurlah untuk memulihkan."], "⚡")
            return False
            
        self.state.energy -= cost
        
        # Jika setelah bekerja energi habis di malam hari, langsung pingsan
        if self.state.energy <= 0 and is_late_night:
            self.state.energy = 0
            self.start_dialog([
                "Pandanganmu mulai kabur...",
                "Kamu terlalu memaksakan diri bekerja malam hari.",
                "Kamu jatuh pingsan!"
            ], "💫 Kelelahan", callback=lambda: self.sleep_next_day(fainted=True))
            
        return True

    # ═══════════════════════════════════════════════════
    #  INTERACTION
    # ═══════════════════════════════════════════════════
    def interact(self):
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.state.scene_name]
        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h:
            return
        t = scene.tiles[fy][fx]

        # NPC nearby
        for npc in scene.npcs:
            if abs(npc['x'] - self.state.player_x) <= 1 and abs(npc['y'] - self.state.player_y) <= 1:
                self.talk_to_npc(npc['id'])
                if self.state.player_x < npc['x']: npc['facing'] = 'left'
                elif self.state.player_x > npc['x']: npc['facing'] = 'right'
                elif self.state.player_y < npc['y']: npc['facing'] = 'up'
                elif self.state.player_y > npc['y']: npc['facing'] = 'down'
                return

        # Tile interactions
        if t == MB:
            self.read_mail()
        elif t == BD:
            self.confirm_sleep()
        elif t == CH:
            if self.state.scene_name == 'outdoor':
                self.open_shipping_bin()
            else:
                if self.state.scene_name == 'cave':
                    if not self.state.stats.get('got_power_berry'):
                        self.state.stats['got_power_berry'] = True
                        self.state.max_energy += 50
                        self.state.energy = self.state.max_energy
                        self.start_dialog(["Kamu menemukan Buah Karsa (Power-up)!", "Maksimal energi bertambah +50!"], "⭐ Rahasia")
                    else:
                        self.notif("Peti rahasia sudah kosong.")
                else:
                    self.open_chest()
        elif t == ST:
            self.use_stove()
        elif t == BS:
            self.read_bookshelf()
        elif t == MR:
            self.use_mirror()
        elif t == FP:
            self.sit_fireplace()
        elif t == CL:
            self.check_clock()
        elif t == TV:
            self.watch_tv()
        elif t == TB:
            self.rest_at_table()
        elif t == PP:
            self.start_dialog(["🌿 Tanaman hias yang cantik.", "Membuat ruangan hidup."], "🌿")
        elif t == CT:
            # Shop counter
            if self.state.scene_name == 'shop':
                if self.state.shop_unlocked:
                    self.open_shop()
                else:
                    self.start_dialog(["Warung belum menerimamu.","Tunjukkan panen pertamamu!"], "🏪")
            elif self.state.scene_name == 'smith':
                self.open_upgrade_shop()
        else:
            self.notif("Tidak ada yang bisa diinteraksi.")

    def talk_to_npc(self, npc_id):
        active_festival = self.get_active_festival()
        season = self.state.get_season()
        day = self.state.day_in_season
        key = f"{season.lower()}_{day}"

        if active_festival and self.state.scene_name == active_festival['scene'] and npc_id in active_festival['locations']:
            lines = active_festival['dialogs'].get(npc_id, active_festival['dialogs']['default'])
            
            if npc_id == active_festival.get('judge'):
                if self.state.festival_submitted.get(key):
                    self.start_dialog(["Terima kasih atas partisipasinya. Pemenang akan diumumkan sore hari."], NPCS[npc_id]['name'])
                else:
                    self.start_dialog(lines, NPCS[npc_id]['name'], callback=self.open_harvest_contest_menu)
            else:
                self.start_dialog(lines, NPCS[npc_id]['name'])
            return

        npc_data = NPCS[npc_id]
        idx = min(self.state.npc_dialog_index.get(npc_id, 0), len(npc_data['talks'])-1)
        lines = npc_data['talks'][idx]
        self.state.npc_dialog_index[npc_id] = min(idx+1, len(npc_data['talks'])-1)
        # Special: sari & budi open shops after dialog
        callback = None
        if npc_id == 'sari' and self.state.shop_unlocked:
            callback = self.open_shop
        elif npc_id == 'budi':
            callback = self.open_upgrade_shop
        elif npc_id == 'pedagang':
            callback = self.open_pedagang_shop
        self.start_dialog(lines, npc_data['name'], callback)

    def read_mail(self):
        if not self.state.mail_read:
            self.state.mail_read = True
        self.start_dialog([
            "📬 Surat dari Paman Arsa:",
            '"Kalau kamu membaca ini, berarti kamu sudah sampai."',
            '"Kebun ini hanya butuh seseorang yang mau datang setiap hari."',
            '"Mulailah dengan lobak. Warung Bu Sari ada di desa timur."',
            '"Jangan sungkan berkenalan dengan warga." — Paman Arsa',
        ], "📬 Surat", self.check_quest_progress)

    def confirm_sleep(self):
        self.menu_title = "🛏 Tidur?"
        self.menu_items = [
            ("😴 Ya, tidur sekarang", self.sleep_next_day),
            ("🚶 Tidak, lanjut main", self.close_menu),
        ]
        self.menu_selected = 0
        self.mode = 'menu'

    def open_chest(self):
        self.mode = 'chest'
        self.inventory_cursor = 0
        self.chest_active = True
        self.refresh_inventory_lists()

    def open_shipping_bin(self):
        """Kotak pengiriman di area kebun untuk menjual panen tanpa pergi ke toko."""
        total = 0
        details = []
        for crop_id, crop in CROPS.items():
            count = self.state.inventory.get(crop_id, 0)
            if count > 0 and crop['cost'] >= 0: # Termasuk ikan
                subtotal = count * crop['sell']
                total += subtotal
                details.append(f"{crop['name']} x{count} = {subtotal}G")

        if total <= 0:
            self.start_dialog([
                "Kotak pengiriman masih kosong.",
                "Masukkan hasil panen ke sini untuk dijual otomatis."
            ], "📦 Kotak Pengiriman")
            return

        self.menu_title = f"📦 Kotak Pengiriman — {total}G"
        self.menu_items = [
            (f"💰 Kirim semua hasil panen ({total}G)", self.ship_all_harvest),
            ("📋 Lihat rincian", lambda d=details: self.show_shipping_details(d, total)),
            ("❌ Batal", self.close_menu),
        ]
        self.menu_selected = 0
        self.mode = 'menu'

    def show_shipping_details(self, details, total):
        self.close_menu()
        lines = ["Rincian hasil panen yang siap dikirim:"] + details + ["", f"Total: {total}G"]
        self.start_dialog(lines, "📦 Kotak Pengiriman")

    def ship_all_harvest(self):
        total = 0
        for crop_id, crop in CROPS.items():
            count = self.state.inventory.get(crop_id, 0)
            if count > 0:
                total += count * crop['sell']
                del self.state.inventory[crop_id]

        if total > 0:
            self.state.gold += total
            self.state.stats['earned'] += total
            self.check_quest_progress()
            self.state.save()
            self.close_menu()
            self.notif(f"📦 Hasil panen dikirim: +{total}G")
        else:
            self.close_menu()
            self.notif("Tidak ada hasil panen untuk dikirim.")

    def use_stove(self):
        has = any(self.state.inventory.get(c, 0) > 0 for c in ['tomat','jagung','lobak','wortel','bayam'])
        if has:
            self.menu_title = "🍳 Masak?"
            self.menu_items = [
                ("🍲 Masak (+20 energi)", self.cook_food),
                ("🚶 Batal", self.close_menu),
            ]
            self.menu_selected = 0
            self.mode = 'menu'
        else:
            self.start_dialog(["🍳 Dapur.", "Tidak ada bahan untuk dimasak."], "🍳")

    def cook_food(self):
        for c in ['tomat','jagung','lobak','wortel','bayam']:
            if self.state.inventory.get(c, 0) > 0:
                self.state.inventory[c] -= 1
                if self.state.inventory[c] <= 0:
                    del self.state.inventory[c]
                self.state.energy = min(self.state.max_energy, self.state.energy + 20)
                self.close_menu()
                self.notif("+20 energi dari masakan!")
                return

    def read_bookshelf(self):
        tips = [
            "📚 \"Siram tanaman tiap hari agar cepat tumbuh.\"",
            "📚 \"Hujan menyiram semua lahan otomatis.\"",
            "📚 \"Beri hadiah ke warga untuk menambah relasi.\"",
            "📚 \"Upgrade alat di bengkel Budi hemat energi.\"",
            "📚 \"Tiap musim punya tanaman unggulan.\"",
        ]
        self.start_dialog([random.choice(tips), "Petunjuk bertani dari perpustakaan."], "📚")

    def use_mirror(self):
        e = self.state.energy
        comment = ("Terlihat segar!" if e > 70 else
                   "Agak lelah..." if e > 30 else "Sangat kelelahan!")
        self.start_dialog([
            f"🪞 Hari {self.state.day} | Energi {e}/{self.state.max_energy}",
            f"Gold: {self.state.gold}G",
            comment
        ], "🪞 Cermin")

    def sit_fireplace(self):
        self.state.energy = min(self.state.max_energy, self.state.energy + 10)
        self.start_dialog(["🔥 Perapian hangat...", "+10 energi."], "🔥")

    def check_clock(self):
        h = int(self.state.time_minutes // 60)
        comment = ("Masih pagi!" if h < 12 else
                   "Sore menjelang." if h < 18 else "Malam sudah tiba.")
        self.start_dialog([
            f"🕐 {self.state.get_time_str()}",
            f"{self.state.get_season_name()}, hari {self.state.day_in_season}",
            comment
        ], "🕐")
        
    def watch_tv(self):
        weather_icons = {'Cerah': '☀', 'Mendung': '☁', 'Hujan': '🌧', 'Badai': '⛈', 'Berangin': '💨'}
        icon = weather_icons.get(self.state.tomorrow_weather, '')
        self.start_dialog([
            "📺 Saluran Cuaca Lembah Karsa",
            f"Prakiraan cuaca untuk besok adalah: {icon} {self.state.tomorrow_weather}.",
            "Bersiaplah dan semoga harimu menyenangkan!"
        ], "📺 TV")

    def rest_at_table(self):
        self.state.energy = min(self.state.max_energy, self.state.energy + 5)
        self.start_dialog(["🪑 Meja makan.", "Istirahat sejenak. +5 energi."], "🪑")

    # ═══════════════════════════════════════════════════
    #  SCENE TRANSITION
    # ═══════════════════════════════════════════════════
    def transition_to(self, target_scene, tx, ty):
        self.mode = 'fade'
        self.fade_dir = 1
        self.fade_alpha = 0
        def do_switch():
            self.state.scene_name = target_scene
            self.state.player_x = tx
            self.state.player_y = ty
            self.snap_camera()
        self.fade_callback = do_switch

    def handle_greenhouse_gate(self, portal):
        active_festival = self.get_active_festival()
        if active_festival:
            self.notif("Pintu ini terkunci selama festival.")
            return

        """Menahan akses rumah kaca sampai milestone restorasi terpenuhi."""
        if self.state.quest_stage < 7:
            self.start_dialog([
                "Rumah kaca masih terkunci dan beberapa panel kacanya pecah.",
                "Warga desa belum siap membantu memperbaikinya.",
                "Selesaikan dulu pesanan jagung dan bangun hubungan dengan warga."
            ], "🏚 Rumah Kaca")
            return

        if self.state.gold < 400:
            self.start_dialog([
                "Budi sudah menghitung biaya bahan untuk memperbaiki rumah kaca.",
                "Biayanya 400G. Kumpulkan gold lebih dulu, lalu kembali ke sini.",
                f"Gold kamu saat ini: {self.state.gold}G."
            ], "🏚 Rumah Kaca")
            return

        self.menu_title = "🏚 Perbaiki Rumah Kaca?"
        self.menu_items = [
            ("✅ Bayar 400G dan buka rumah kaca", lambda p=portal: self.repair_greenhouse(p)),
            ("❌ Belum sekarang", self.close_menu),
        ]
        self.menu_selected = 0
        self.mode = 'menu'

    def trigger_naga_cutscene(self, naga_npc=None):
        self.state.naga_met = True
        
        nx = naga_npc['x'] if naga_npc else 10
        ny = naga_npc['y'] if naga_npc else 5
        
        # Ubah otomatis arah hadap pemain agar melihat tegak lurus ke arah Naga
        if self.state.player_y < ny:
            self.state.facing = 'down'
        elif self.state.player_y > ny:
            self.state.facing = 'up'
        elif self.state.player_x > nx:
            self.state.facing = 'left'
        elif self.state.player_x < nx:
            self.state.facing = 'right'
            
        dialog = [
            "Bumi bergetar pelan... Air danau beriak dengan kuat.",
            "Sebuah sosok raksasa perlahan bangkit dari tepi air.",
            "NAGA: 'GRRR... Sudah lama sekali tidak ada manusia yang kemari.'",
            "NAGA: 'Aku adalah Naga Sang Hyang, penjaga kuno Lembah Karsa.'",
            "NAGA: 'Apakah kau penerus Arsa? Tunjukkan padaku bakat bertanimu.'",
            "NAGA: 'Bawakan aku Wortel terbaikmu, dan mungkin aku akan membantumu.'"
        ]
        self.start_dialog(dialog, "🐲 Pertemuan Epik", self.state.save)

    def repair_greenhouse(self, portal=None):
        """Membuka rumah kaca sebagai milestone cerita dan gameplay lintas musim."""
        if self.state.greenhouse_open:
            if portal:
                self.transition_to(portal[2], portal[3], portal[4])
            else:
                self.close_menu()
            return

        if self.state.gold < 400:
            self.notif("Gold tidak cukup!")
            self.close_menu()
            return

        self.state.gold -= 400
        self.state.greenhouse_open = True
        self.check_quest_progress()
        self.state.save()
        self.notif("🏚 Rumah kaca berhasil dipulihkan!")
        self.start_dialog([
            "Kaca-kaca baru dipasang, rangka diperkuat, dan bedengan di dalamnya kembali siap dipakai.",
            "Mulai sekarang, kamu bisa membeli benih lintas musim dan menanamnya di rumah kaca.",
            "Lembah Karsa mulai hidup kembali."
        ], "🏚 Rumah Kaca", callback=(lambda p=portal: self.transition_to(p[2], p[3], p[4]) if p else None))

    def descend_mine(self):
        self.state.cave_level = getattr(self.state, 'cave_level', 1) + 1
        SCENES['cave'] = generate_mine_floor(self.state.cave_level)
        self.transition_to('cave', 10, 10) # Muncul di posisi koordinat tangga
        self.close_menu()
        self.notif(f"Memasuki Lantai {self.state.cave_level}")

    def ascend_mine(self):
        self.state.cave_level = getattr(self.state, 'cave_level', 1) - 1
        if self.state.cave_level <= 0:
            self.state.cave_level = 1
            SCENES['cave'] = generate_mine_floor(1)
            self.transition_to('cave_path', 10, 1) # Keluar goa kembali ke permukaan
        else:
            SCENES['cave'] = generate_mine_floor(self.state.cave_level)
            self.transition_to('cave', 10, 10)
        self.close_menu()

    # ═══════════════════════════════════════════════════
    #  SLEEP
    # ═══════════════════════════════════════════════════
    def get_active_festival(self):
        season = self.state.get_season()
        day = self.state.day_in_season
        key = f"{season.lower()}_{day}"
        return FESTIVALS.get(key)

    def sleep_next_day(self, fainted=False):
        self.close_menu()
        # Grow crops
        is_rain = self.state.weather in ('Hujan','Badai')
        for key, soil in self.state.soil.items():
            if is_rain and soil.get('tilled'):
                soil['watered'] = True
            if soil.get('crop') and soil.get('watered'):
                soil['age'] = soil.get('age', 0) + 1
            soil['watered'] = False
            
        # Spawn debris (Ilalang & Batu) di ladang (x: 1-14, y: 1-11)
        scene = SCENES['outdoor']
        for cy in range(1, 12):
            for cx in range(1, 15):
                key = f"{cx},{cy},outdoor"
                is_tilled = self.state.soil.get(key, {}).get('tilled', False)
                if scene.tiles[cy][cx] == D and not is_tilled:
                    if random.random() < 0.05:  # 5% chance per petak tiap hari
                        scene.tiles[cy][cx] = random.choice([WD, STN])
                        
        # Advance day
        self.state.day += 1
        self.state.day_in_season += 1
        if self.state.day_in_season > DAYS_PER_SEASON:
            self.state.day_in_season = 1
            self.state.season_index = (self.state.season_index + 1) % 4
            if self.state.season_index == 0:
                self.state.year += 1
                
        # Pedagang misterius (setiap hari kelipatan 7)
        outdoor_scene = SCENES['outdoor']
        outdoor_scene.npcs = [npc for npc in outdoor_scene.npcs if npc['id'] != 'pedagang']
        if self.state.day % 7 == 0:
            outdoor_scene.npcs.append({
                'id': 'pedagang', 'x': 6, 'y': 8, 'px': 6.0, 'py': 8.0,
                'facing': 'left', 'timer': 999999, 'moving': False, 'hp': 100,
                'home_x': 6, 'home_y': 8, 'attack_timer': 0
            })

        if fainted:
            # Pindahkan pemain ke tempat tidur di rumah
            self.state.scene_name = 'house'
            self.state.player_x = 3
            self.state.player_y = 2
            self.snap_camera()
            
            self.state.time_minutes = 600  # Bangun jam 10:00 (10 AM) karena pingsan
            self.state.energy = self.state.max_energy // 2
            self.state.hp = getattr(self.state, 'max_hp', 100)
            self.state.weather = getattr(self.state, 'tomorrow_weather', 'Cerah')
            self.state.tomorrow_weather = random.choice(['Cerah','Cerah','Mendung','Hujan','Berangin'])
            clinic_fee = min(self.state.gold, 50)
            self.state.gold -= clinic_fee
            self.state.save()
            self.start_dialog([
                f"🌅 Hari {self.state.day} dimulai.",
                "Pak Raka menemukanmu pingsan dan membawamu pulang.",
                f"Biaya pengobatan klinik: -{clinic_fee}G.",
                "Kamu bangun kesiangan dengan tubuh lemas (energi setengah)."
            ], "🏥 Pingsan")
        else:
            active_festival = self.get_active_festival()
            if active_festival:
                self.state.scene_name = active_festival['scene']
                self.state.player_x = 10
                self.state.player_y = 15
                self.snap_camera()
                self.state.time_minutes = 600 # Festival starts at 10:00 AM
                self.state.energy = self.state.max_energy
                self.state.hp = getattr(self.state, 'max_hp', 100)
                self.state.weather = 'Cerah' # Festivals are always sunny
                self.state.tomorrow_weather = random.choice(['Cerah','Cerah','Mendung','Hujan','Berangin'])
                self.state.save()
                self.start_dialog([f"🎉 Hari ini adalah {active_festival['name']}! 🎉", "Semua warga berkumpul di kota. Ayo bergabung!"], "📢 Pengumuman")
                return

            self.state.time_minutes = 360
            self.state.energy = self.state.max_energy
            self.state.hp = getattr(self.state, 'max_hp', 100)
            self.state.weather = getattr(self.state, 'tomorrow_weather', 'Cerah')
            self.state.tomorrow_weather = random.choice(['Cerah','Cerah','Mendung','Hujan','Berangin'])
            self.state.save()
            self.start_dialog([
                f"🌅 Hari {self.state.day} dimulai",
                f"{self.state.get_season_name()}, hari {self.state.day_in_season}",
                f"Cuaca: {self.state.weather}. Energi pulih penuh!",
            ], "🌄 Pagi")
            
        self.check_quest_progress()

    # ═══════════════════════════════════════════════════
    #  SHOP & UPGRADE
    # ═══════════════════════════════════════════════════
    def open_shop(self):
        self.menu_title = f"🏪 Warung — {self.state.gold}G"
        items = []
        szn = self.state.get_season()
        for crop_id, crop in CROPS.items():
            if crop['cost'] > 0 and (szn in crop['seasons'] or self.state.greenhouse_open):
                cost = crop['cost'] * 3
                def mk(k=crop_id, c=cost):
                    return lambda: self.buy_seeds(k, c)
                items.append((f"{crop['name']} x3 benih - {cost}G", mk()))
        items.append(("☕ Minum Jamu Energi (Full HP) - 50G", self.buy_energy_drink))
        items.append(("💰 Jual semua panen", self.sell_all_harvest))
        items.append(("❌ Tutup", self.close_menu))
        self.menu_items = items
        self.menu_selected = 0
        self.mode = 'menu'

    def buy_seeds(self, crop_id, cost):
        if self.state.gold < cost:
            self.notif("Gold tidak cukup!")
            return
        self.state.gold -= cost
        key = crop_id + '_seed'
        self.state.inventory[key] = self.state.inventory.get(key, 0) + 3
        self.notif(f"Beli 3 benih {CROPS[crop_id]['name']}!")
        self.state.save()
        self.open_shop()  # refresh

    def buy_energy_drink(self):
        if self.state.gold < 50:
            self.notif("Gold tidak cukup!")
            return
        if self.state.energy >= self.state.max_energy:
            self.notif("Energimu sudah penuh!")
        if self.state.energy >= self.state.max_energy and self.state.hp >= getattr(self.state, 'max_hp', 100):
            self.notif("Energi dan HP-mu sudah penuh!")
            return
        self.state.gold -= 50
        self.state.energy = self.state.max_energy
        self.notif("Glek.. segar! Energi pulih penuh.")
        self.state.hp = getattr(self.state, 'max_hp', 100)
        self.notif("Glek.. segar! Energi & HP pulih penuh.")
        self.state.save()
        self.open_shop()  # refresh

    def sell_all_harvest(self):
        total = 0
        for crop_id, crop in CROPS.items():
            count = self.state.inventory.get(crop_id, 0)
            if count > 0:
                total += count * crop['sell']
                del self.state.inventory[crop_id]
        if total > 0:
            self.state.gold += total
            self.state.stats['earned'] += total
            self.notif(f"+{total}G dari penjualan!")
            self.check_quest_progress()
            self.state.save()
        else:
            self.notif("Tidak ada yang dijual.")
        self.open_shop()

    def open_pedagang_shop(self):
        self.menu_title = f"🎒 Pedagang — {self.state.gold}G"
        items = []
        rare_items = {
            'jin_soul': 500,
            'api_magis': 400,
            'taring': 300,
            'kain_putih': 250,
            'ikan': 100,
        }
        for item_id, price in rare_items.items():
            if self.state.inventory.get(item_id, 0) > 0:
                count = self.state.inventory[item_id]
                def mk(k=item_id, p=price):
                    return lambda: self.sell_rare_item(k, p)
                name = CROPS.get(item_id, {}).get('name', item_id.replace('_', ' ').title())
                if item_id == 'jin_soul': name = 'Jiwa Jin'
                elif item_id == 'ikan': name = 'Ikan'
                items.append((f"Jual {name} ({count}x) - {price}G", mk()))
        
        if not items:
            items.append(("Tidak ada barang langka untuk dijual.", self.close_menu))
            
        items.append(("❌ Tutup", self.close_menu))
        self.menu_items = items
        self.menu_selected = 0
        self.mode = 'menu'

    def sell_rare_item(self, item_id, price):
        if self.state.inventory.get(item_id, 0) > 0:
            self.state.inventory[item_id] -= 1
            if self.state.inventory[item_id] <= 0:
                del self.state.inventory[item_id]
            self.state.gold += price
            self.state.stats['earned'] += price
            self.notif(f"Terjual seharga {price}G!")
            self.state.save()
            self.open_pedagang_shop()
        else:
            self.notif("Barang tidak ada.")
            self.open_pedagang_shop()

    def open_upgrade_shop(self):
        self.menu_title = f"⚒️ Bengkel Budi — {self.state.gold}G"
        items = []
        upgrades = [
            ('hoe', 80, 'Cangkul Baja (hemat energi)'),
            ('water', 120, 'Penyiram Perunggu (3 petak)'),
            ('bag', 60, 'Tas Besar (energi +20)'),
            ('axe', 50, 'Kapak Besi (tebang pohon)'),
            ('sword', 200, 'Pedang Ksatria (3 DMG)'),
        ]
        for upg_id, cost, label in upgrades:
            if self.state.upgrades.get(upg_id):
                items.append((f"✅ {label}", self.close_menu))
            else:
                def mk(u=upg_id, c=cost):
                    return lambda: self.buy_upgrade(u, c)
                items.append((f"{label} - {cost}G", mk()))

        bag_level = self.state.upgrades.get('bag_level', 1)
        if bag_level == 1:
            items.append(("🎒 Tas Medium (18 Slot) - 150G", lambda: self.buy_bag_upgrade(2, 150)))
        elif bag_level == 2:
            items.append(("🎒 Tas Besar (24 Slot) - 300G", lambda: self.buy_bag_upgrade(3, 300)))
        else:
            items.append(("✅ Tas Maksimal (24 Slot)", self.close_menu))

        items.append(("❌ Tutup", self.close_menu))
        self.menu_items = items
        self.menu_selected = 0
        self.mode = 'menu'

    def buy_upgrade(self, upg_id, cost):
        if self.state.gold < cost:
            self.notif("Gold tidak cukup!")
            return
        self.state.gold -= cost
        self.state.upgrades[upg_id] = True
        if upg_id == 'bag':
            self.state.max_energy += 20
            self.state.energy = min(self.state.energy + 20, self.state.max_energy)
        self.notif("⚒ Upgrade berhasil!")
        self.check_quest_progress()
        self.state.save()
        self.open_upgrade_shop()

    def buy_bag_upgrade(self, target_level, cost):
        if self.state.gold < cost:
            self.notif("Gold tidak cukup!")
            return
        self.state.gold -= cost
        self.state.upgrades['bag_level'] = target_level
        self.notif(f"⚒ Tas diperbarui ke level {target_level}!")
        self.state.save()
        self.open_upgrade_shop()

    def open_harvest_contest_menu(self):
        self.menu_title = "🏆 Kontes Panen 🏆"
        items = []
        
        submittable = []
        for item_id, data in CROPS.items():
            if self.state.inventory.get(item_id, 0) > 0 and data['sell'] > 0:
                submittable.append((item_id, data))

        if not submittable:
            self.start_dialog(["Kamu tidak punya hasil panen untuk diikutkan."], "Pak Arya")
            return

        for item_id, data in submittable:
            def mk(id=item_id):
                return lambda: self.submit_to_contest(id)
            items.append((f"Ikutkan {data['name']} (Nilai: {data['sell']})", mk()))
        
        items.append(("❌ Batal", self.close_menu))
        self.menu_items = items
        self.menu_selected = 0
        self.mode = 'menu'

    def submit_to_contest(self, item_id):
        self.close_menu()
        
        self.state.inventory[item_id] -= 1
        if self.state.inventory[item_id] <= 0:
            del self.state.inventory[item_id]
            
        item_data = CROPS[item_id]
        score = item_data['sell']
        
        if score > 60: prize_text, prize_gold = "Luar biasa! Ini juara pertama! Hadiahnya 1000G!", 1000
        elif score > 40: prize_text, prize_gold = "Kualitas yang bagus! Juara kedua. Hadiahnya 500G.", 500
        elif score > 20: prize_text, prize_gold = "Hasil yang lumayan! Juara ketiga. Hadiahnya 200G.", 200
        else: prize_text, prize_gold = "Terima kasih sudah berpartisipasi. Teruslah berusaha!", 20

        self.state.gold += prize_gold
        
        season = self.state.get_season()
        day = self.state.day_in_season
        key = f"{season.lower()}_{day}"
        self.state.festival_submitted[key] = True
        self.start_dialog([f"Pak Arya memeriksa {item_data['name']} milikmu...", f"Pak Arya: '{prize_text}'"], "🏆 Penjurian")

    # ═══════════════════════════════════════════════════
    #  DIALOG
    # ═══════════════════════════════════════════════════
    def start_dialog(self, lines, speaker, callback=None):
        self.dialog_lines = lines
        self.dialog_index = 0
        self.dialog_speaker = speaker
        self.dialog_callback = callback
        self.typewriter_progress = 0
        self.mode = 'dialog'

    def advance_dialog(self):
        # Skip typewriter
        current = self.dialog_lines[self.dialog_index]
        if self.typewriter_progress < len(current):
            self.typewriter_progress = len(current)
            return
        self.dialog_index += 1
        if self.dialog_index >= len(self.dialog_lines):
            self.mode = 'play'
            cb = self.dialog_callback
            self.dialog_callback = None
            if cb:
                cb()
        else:
            self.typewriter_progress = 0

    # ═══════════════════════════════════════════════════
    #  MENU
    # ═══════════════════════════════════════════════════
    def open_main_menu(self):
        self.menu_title = "☰ Menu Utama"
        self.menu_items = [
            ("🎒 Buka Inventori", self.open_inventory),
            (f"💾 Simpan Game", lambda: (self.state.save(), self.notif("💾 Tersimpan!"), self.close_menu())),
            (f"🌱 Ganti Benih ({CROPS[self.state.seed_key]['name']})", lambda: (self.cycle_seed(1), self.close_menu())),
            ("📋 Lihat Quest", self.show_quest_menu),
            ("📅 Kalender & Tips Musim", self.show_calendar_menu),
            ("👥 Status NPC", self.show_npc_menu),
            ("❌ Tutup", self.close_menu),
        ]
        self.menu_selected = 0
        self.mode = 'menu'

    def show_quest_menu(self):
        stage = QUEST_STAGES[min(self.state.quest_stage, len(QUEST_STAGES)-1)]
        lines = [
            f"📋 {stage['t']}",
            stage['d'],
            "",
            f"Progress:",
            f"Lobak: {self.state.stats['lobak_planted']} tanam / {self.state.stats['lobak_harvested']} panen",
            f"Penghasilan: {self.state.stats['earned']}G",
            f"Hadiah diberikan: {self.state.stats['gifts']}",
        ]
        self.close_menu()
        self.start_dialog(lines, "📋 Quest")

    def show_calendar_menu(self):
        szn = self.state.get_season()
        available = [crop['name'] for crop_id, crop in CROPS.items() if szn in crop['seasons']]
        greenhouse_note = "Rumah kaca sudah aktif: benih semua musim dapat dibeli dan ditanam di sana." if self.state.greenhouse_open else "Rumah kaca belum pulih: tanaman masih mengikuti musim."
        lines = [
            f"📅 Tahun {self.state.year}, {self.state.get_season_name()}, hari {self.state.day_in_season}/{DAYS_PER_SEASON}",
            f"Cuaca hari ini: {self.state.weather}",
            "",
            "Tanaman cocok musim ini:",
            ", ".join(available) if available else "Tidak ada data tanaman musim ini.",
            "",
            greenhouse_note,
            "",
            "Tips: tekan Q/R untuk ganti benih, F5 untuk save, dan H untuk membuka kalender ini lagi."
        ]
        if self.mode == 'menu':
            self.close_menu()
        self.start_dialog(lines, "📅 Kalender")

    def show_npc_menu(self):
        lines = ["💕 Hubungan dengan warga:"]
        for npc_id, data in NPCS.items():
            h = self.state.npc_hearts[npc_id]
            hearts = "❤" * (h // 2) + "♡" * ((10 - h) // 2)
            lines.append(f"{data['name']}: {hearts}")
        self.close_menu()
        self.start_dialog(lines, "👥 Warga")

    def menu_activate(self):
        if 0 <= self.menu_selected < len(self.menu_items):
            _, action = self.menu_items[self.menu_selected]
            if callable(action):
                action()

    def close_menu(self):
        self.mode = 'play'

    def cycle_seed(self, d):
        szn = self.state.get_season()
        available = [k for k, c in CROPS.items()
                     if szn in c['seasons'] or self.state.greenhouse_open
                     or self.state.inventory.get(k+'_seed', 0) > 0]
        if not available:
            return
        try:
            i = available.index(self.state.seed_key)
        except ValueError:
            i = 0
        i = (i + d) % len(available)
        self.state.seed_key = available[i]
        self.notif(f"Benih: {CROPS[self.state.seed_key]['name']}")

    def refresh_inventory_lists(self):
        self.inventory_list = [(k, v) for k, v in self.state.inventory.items() if v > 0]
        if getattr(self.state, 'chest_inventory', None) is None:
            self.state.chest_inventory = {}
        self.chest_list = [(k, v) for k, v in self.state.chest_inventory.items() if v > 0]

    def open_inventory(self):
        self.mode = 'inventory'
        self.inventory_cursor = 0
        self.chest_active = False
        self.refresh_inventory_lists()

    def transfer_item(self):
        is_chest_active = getattr(self, 'chest_active', False)
        source_list = self.chest_list if is_chest_active else self.inventory_list
        source_dict = self.state.chest_inventory if is_chest_active else self.state.inventory
        target_dict = self.state.inventory if is_chest_active else self.state.chest_inventory
        
        bag_level = self.state.upgrades.get('bag_level', 1)
        max_inv_slots = 12 + (bag_level - 1) * 6
        max_chest_slots = 24
        
        if not source_list or self.inventory_cursor >= len(source_list):
            return
            
        item_id, count = source_list[self.inventory_cursor]
        
        # Check target capacity
        target_max = max_inv_slots if is_chest_active else max_chest_slots
        if item_id not in target_dict and len(target_dict) >= target_max:
            self.notif("Kapasitas penyimpanan penuh!")
            return
            
        source_dict[item_id] -= 1
        if source_dict[item_id] <= 0:
            del source_dict[item_id]
            
        target_dict[item_id] = target_dict.get(item_id, 0) + 1
        
        self.refresh_inventory_lists()
        
        new_source_list = self.chest_list if is_chest_active else self.inventory_list
        if self.inventory_cursor >= len(new_source_list):
            self.inventory_cursor = max(0, len(new_source_list) - 1)
            
        _, name = self.get_item_info(item_id)
        action = "Diambil" if is_chest_active else "Disimpan"
        self.notif(f"1 {name} {action}.")

    def drop_selected_item(self):
        is_chest_active = getattr(self, 'chest_active', False)
        source_list = getattr(self, 'chest_list', []) if is_chest_active else getattr(self, 'inventory_list', [])
        source_dict = self.state.chest_inventory if is_chest_active else self.state.inventory
        
        if not source_list or self.inventory_cursor >= len(source_list):
            return
            
        selected_id, _ = source_list[self.inventory_cursor]
        source_dict[selected_id] -= 1
        if source_dict[selected_id] <= 0:
            del source_dict[selected_id]
            
        self.refresh_inventory_lists()
        
        new_source_list = getattr(self, 'chest_list', []) if is_chest_active else getattr(self, 'inventory_list', [])
        if self.inventory_cursor >= len(new_source_list):
            self.inventory_cursor = max(0, len(new_source_list) - 1)
            
        _, name = self.get_item_info(selected_id)
        self.notif(f"1 {name} dibuang.")

    def get_item_info(self, item_id):
        if item_id.endswith('_seed'):
            base_id = item_id.replace('_seed', '')
            if base_id in CROPS:
                return '🌱', f"Benih {CROPS[base_id]['name']}"
        if item_id in CROPS:
            return CROPS[item_id].get('icon', '📦'), CROPS[item_id]['name']
        other_items = {
            'kayu': ('🪵', 'Kayu'), 'batu': ('🪨', 'Batu'), 'ikan': ('🐟', 'Ikan'),
            'rumput_liar': ('🌿', 'Rumput Liar'), 'jin_soul': ('✨', 'Jiwa Jin'),
            'api_magis': ('🔥', 'Api Magis'), 'taring': ('🦷', 'Taring'), 'kain_putih': ('👻', 'Kain Kusam'),
        }
        if item_id in other_items: return other_items[item_id]
        return '📦', item_id

    # ═══════════════════════════════════════════════════
    #  QUEST
    # ═══════════════════════════════════════════════════
    def check_quest_progress(self):
        s = self.state
        stage = s.quest_stage
        if stage == 0 and s.mail_read:
            s.quest_stage = 1
        elif stage == 1 and s.stats['lobak_planted'] >= 3 and s.stats['watered'] >= 3:
            s.quest_stage = 2
        elif stage == 2 and s.stats['lobak_harvested'] >= 3:
            s.quest_stage = 3
            s.shop_unlocked = True
            self.notif("🎉 Warung terbuka!")
        elif stage == 3 and s.stats['earned'] >= 150:
            s.quest_stage = 4
        elif stage == 4 and (s.upgrades['hoe'] or s.upgrades['water']):
            s.quest_stage = 5
        elif stage == 5 and s.stats['corn_harvested'] >= 2:
            s.quest_stage = 6
        elif stage == 6 and s.stats['gifts'] >= 3:
            s.quest_stage = 7
        elif stage == 7 and s.greenhouse_open:
            s.quest_stage = 8
        elif stage == 8 and len(s.stats['seasons_harvested']) >= 4:
            s.quest_stage = 9
        elif stage == 9 and s.day >= DAYS_PER_SEASON * 4:
            s.quest_stage = 10
            self.start_dialog([
                "🌻 SATU TAHUN BERLALU!",
                "Lembah Karsa hidup kembali berkat kerja kerasmu.",
                "Warga desa berterima kasih.",
                "— TAMAT —",
            ], "🌻 Selamat!")

    # ═══════════════════════════════════════════════════
    #  NOTIFICATION
    # ═══════════════════════════════════════════════════
    def notif(self, text):
        self.notif_text = text
        self.notif_timer = 2500

    # ═══════════════════════════════════════════════════
    #  NEW GAME / LOAD
    # ═══════════════════════════════════════════════════
    def start_new_game(self):
        self.state = GameState()
        self.mode = 'play'
        self.snap_camera()
        self.start_dialog([
            "🌅 Kamu tiba di Lembah Karsa.",
            "Kebun Paman Arsa terbentang di depanmu.",
            "Ada kotak pos 📬 di dekat rumah. Bacalah surat Paman.",
            "Gunakan WASD untuk gerak, E untuk interaksi, SPACE untuk pakai alat.",
        ], "🏡 Selamat Datang")

    def try_load_game(self):
        loaded = GameState.load()
        if loaded:
            self.state = loaded
            self.mode = 'play'
            self.snap_camera()
            self.notif("💾 Game dimuat!")
        else:
            self.notif("❌ Tidak ada data simpanan.")

    # ═══════════════════════════════════════════════════
    #  RENDER
    # ═══════════════════════════════════════════════════
    def render(self):
        self.screen.fill(C.ui_bg)

        if self.mode == 'title':
            self.render_title()
            return

        # Render world
        self.render_world()

        # HUD
        self.render_hud()

        # Dialog
        if self.mode == 'dialog':
            self.render_dialog()

        # Menu
        if self.mode == 'menu':
            self.render_menu()
            
        # Inventory / Chest
        if self.mode in ('inventory', 'chest'):
            self.render_inventory()

        # Notification
        if self.notif_timer > 0 and self.notif_text:
            self.render_notification()

        # Fade overlay
        if self.mode == 'fade' or self.fade_alpha > 0:
            overlay = pygame.Surface((SCREEN_W, SCREEN_H))
            overlay.set_alpha(self.fade_alpha)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

    def render_title(self):
        self.screen.fill((20, 10, 35))
        title = self.font_title.render("🌱 LEMBAH KARSA 🌾", True, C.ui_gold)
        sub = self.font.render("Farming RPG — Python Edition", True, C.ui_text)
        start = self.font_big.render("SPACE — Mulai Baru", True, C.ui_green)
        load = self.font_big.render("L — Load Game", True, C.ui_text)
        story = self.font_small.render("Paman Arsa mewariskan kebun untukmu.", True, (150,130,180))
        story2 = self.font_small.render("Hidupkan kembali Lembah Karsa!", True, (150,130,180))

        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 100))
        self.screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 150))
        self.screen.blit(story, (SCREEN_W//2 - story.get_width()//2, 220))
        self.screen.blit(story2, (SCREEN_W//2 - story2.get_width()//2, 240))
        self.screen.blit(start, (SCREEN_W//2 - start.get_width()//2, 320))
        self.screen.blit(load, (SCREEN_W//2 - load.get_width()//2, 360))

        # Animated sprites preview
        frame = (self.anim_tick // 300) % 2
        p = ANIMATED['player']['down'][frame]
        self.screen.blit(p, (SCREEN_W//2 - 16, 270))

    def render_world(self):
        scene = SCENES[self.state.scene_name]
        indoor = scene.indoor
        active_festival = self.get_active_festival()
        is_festival_scene = active_festival and scene.name == active_festival['scene']

        # Background
        bg_color = (40,25,15) if indoor else (80,140,180) if self.state.get_season() == 'Semi' else (100,100,60)
        is_wet = not indoor and self.state.weather in ('Hujan', 'Badai')
        is_night = self.state.time_minutes >= 18 * 60 or self.state.time_minutes < 5 * 60
        if is_wet:
            bg_color = (max(0, bg_color[0]-40), max(0, bg_color[1]-40), max(0, bg_color[2]-20))
        self.screen.fill(bg_color, (0, 0, SCREEN_W, VIEW_H * TILE))

        # --- FITUR V4: Parallax Clouds ---
        if not indoor:
            self.cloud_x = (self.cloud_x + 0.2) % SCREEN_W
            self.screen.blit(self.cloud_surf, (self.cloud_x, 0))
            self.screen.blit(self.cloud_surf, (self.cloud_x - SCREEN_W, 0))

        start_x = max(0, int(self.cam_x) - 1)
        start_y = max(0, int(self.cam_y) - 1)
        end_x = min(scene.w, int(self.cam_x) + VIEW_W + 2)
        end_y = min(scene.h, int(self.cam_y) + VIEW_H + 2)

        # 1. LAYER BAWAH (Hanya Tanah & Air)
        if is_festival_scene:
            # Dekorasi festival
            for x in range(5, 25, 4):
                pygame.draw.rect(self.screen, random.choice([C.cr, C.cy, C.cp]), (x * TILE - self.cam_x * TILE, 6 * TILE - self.cam_y * TILE, TILE, 8))
            title = self.font_big.render(active_festival['name'], True, C.ui_gold)
            self.screen.blit(title, (SCREEN_W/2 - title.get_width()/2, 20))

        for wy in range(start_y, end_y):
            for wx in range(start_x, end_x):
                t = scene.tiles[wy][wx]
                px_ = wx * TILE - self.cam_x * TILE
                py_ = wy * TILE - self.cam_y * TILE
                
                key = f"{wx},{wy},{self.state.scene_name}"
                soil = self.state.soil.get(key)
                if soil and soil.get('tilled'):
                    sprite = SPRITES['tilled_wet'] if soil.get('watered') else SPRITES['tilled_dry']
                    if is_wet and not soil.get('watered'):
                        sprite = get_wet_sprite(sprite)
                    self.screen.blit(sprite, (px_, py_))
                    continue

                # Gambar base tile jika ada tumpukan (seperti batu/ilalang di atas tanah)
                base_t = D if t in [WD, STN] else t
                if base_t in [G, D, P, W, FL]:
                    name = TILE_NAMES.get(base_t)
                    if base_t == W:
                        frame = (self.anim_tick // 300) % 4
                        self.screen.blit(ANIMATED['water'][frame], (px_, py_))
                    elif name and name in SPRITES:
                        sprite = SPRITES[name]
                        if is_wet and base_t in [G, D, P]:
                            sprite = get_wet_sprite(sprite)
                        self.screen.blit(sprite, (px_, py_))
                    else:
                        pygame.draw.rect(self.screen, (60,40,80), (px_, py_, TILE, TILE))

        # Pre-group NPCs by their rounded Y coordinate for faster rendering
        npcs_by_row = {}
        for npc in scene.npcs:
            row_y = int(npc['py'] + 0.5)
            npcs_by_row.setdefault(row_y, []).append(npc)

        # 2. LAYER OBJEK & KARAKTER (Z-Index / Depth Sort berdasarkan Row-Y)
        for wy in range(start_y, end_y):
            # A. Objek Berdiri (Pohon, Rumah, Tanaman, Furniture)
            for wx in range(start_x, end_x):
                t = scene.tiles[wy][wx]
                px_ = wx * TILE - self.cam_x * TILE
                py_ = wy * TILE - self.cam_y * TILE
                
                # Efek angin/badai untuk objek berdiri (pohon, rumput liar/ilalang, tanaman)
                sway = 0
                if not indoor and self.state.weather in ('Badai', 'Berangin'):
                    speed = 2.0 if self.state.weather == 'Badai' else 1.0
                    intensity = 4.0 if self.state.weather == 'Badai' else 2.0
                    sway = math.sin((self.anim_tick * 0.003 * speed) + (wx * 0.5) + (wy * 0.5)) * intensity
                
                key = f"{wx},{wy},{self.state.scene_name}"
                soil = self.state.soil.get(key)
                if soil and soil.get('crop'):
                    stage = min(soil.get('age', 0), 3)
                    crop_id = soil['crop']
                    if crop_id in SPRITES['crops']:
                        sprite = SPRITES['crops'][crop_id][stage]
                        if is_wet:
                            sprite = get_wet_sprite(sprite)
                        self.screen.blit(sprite, (px_ + sway, py_))
                        
                if t not in [G, D, P, W, FL]:
                    name = TILE_NAMES.get(t)
                    if t == H:
                        # Menyatukan grid rumah menjadi satu bangunan besar (Atap + Dinding)
                        s = pygame.Surface((TILE, TILE))
                        h_above = 0
                        cy = wy - 1
                        while cy >= 0 and scene.tiles[cy][wx] == H:
                            h_above += 1
                            cy -= 1
                        if h_above < 2:  # 2 baris teratas jadi atap
                            s.fill(C.r0)
                            pygame.draw.rect(s, C.r1, (0, TILE-4, TILE, 4))
                            if h_above == 0: pygame.draw.rect(s, C.r2, (0, 0, TILE, 8))
                        else:  # Sisanya jadi dinding
                            s.fill(C.b0)
                            pygame.draw.rect(s, C.b1, (0, 0, TILE, TILE), 1)
                            pygame.draw.line(s, C.b1, (0, TILE//2), (TILE, TILE//2), 1)
                        self.screen.blit(s, (px_, py_))
                    elif name and name in SPRITES:
                        sprite = SPRITES[name]
                        if is_wet and t in [TR, WD]:
                            sprite = get_wet_sprite(sprite)
                        obj_sway = sway if t in [TR, WD] else 0
                        self.screen.blit(sprite, (px_ + obj_sway, py_))

                    # Tambahan Visual: Light Glow
                    if t in [FP, ST, TV] and (is_night or indoor):
                        self.screen.blit(self.glow_surf, (px_ + TILE/2 - TILE*2, py_ + TILE/2 - TILE*2), special_flags=pygame.BLEND_RGB_ADD)

            # B. NPCs
            if wy in npcs_by_row:
                for npc in npcs_by_row[wy]:
                        if is_festival_scene and npc['id'] not in active_festival['locations']:
                            continue

                        vx = npc['px'] - self.cam_x
                        vy = npc['py'] - self.cam_y
                        frame = (self.anim_tick // 500) % 2 if npc['moving'] else 0
                        npc_id = npc['id']
                    
                        offset_x = offset_y = 0
                        if npc_id == 'naga':
                            sprite = ANIMATED['npc_naga'][npc['facing']][frame]
                            offset_x = -(sprite.get_width() - TILE) // 2
                            offset_y = -(sprite.get_height() - TILE)
                            self.screen.blit(self.shadow_naga, (vx * TILE + offset_x, vy * TILE + offset_y))
                        else:
                            facing = npc['facing']
                            anim_data = ANIMATED.get(f'npc_{npc_id}')
                            if not anim_data:
                                anim_data = ANIMATED['player']  # Fallback agar tidak crash jika sprite hilang
                            if facing not in anim_data: facing = 'down'
                            sprite = anim_data[facing][frame]
                            shadow = self.shadow_std_small if npc['moving'] and frame == 1 else self.shadow_std
                            self.screen.blit(shadow, (vx * TILE, vy * TILE))
                        
                        self.screen.blit(sprite, (vx * TILE + offset_x, vy * TILE + offset_y))
                        
                        if self.state.npc_hearts.get(npc_id, 0) > 0:
                            heart_count = self.state.npc_hearts.get(npc_id, 0) // 2
                            for i in range(min(heart_count, 5)):
                                pygame.draw.rect(self.screen, C.ui_red, (vx * TILE + 2 + i*5, vy * TILE - 6, 3, 3))

            # C. Player
            if self.state.player_y == wy and not (getattr(self, 'invuln_timer', 0) > 0 and (int(self.invuln_timer) // 150) % 2 == 0):
                pvx = self.px_vis - self.cam_x
                pvy = self.py_vis - self.cam_y
                frame = self.walk_frame if self.moving else 0
                
                # --- ANIMASI ALAT (ACTION) ---
                if self.action_timer > 0:
                    player_sprite = ANIMATED['player'][self.state.facing][0]
                    self.screen.blit(self.shadow_std, (pvx * TILE, pvy * TILE))
                    
                    progress = 1.0 - (self.action_timer / self.action_duration)
                    jump_y = -math.sin(math.pi * progress) * 6
                    
                    tool_sprite = SPRITES['tools'][self.state.tool_index]
                    angle = 0
                    tx, ty = pvx * TILE, pvy * TILE + jump_y
                    
                    if self.state.facing == 'right':
                        angle = 30 - (progress * 120)
                        tx += 5 + (progress * 15); ty -= 10 - (progress * 25)
                    elif self.state.facing == 'left':
                        angle = -30 + (progress * 120)
                        tx -= 5 + (progress * 15); ty -= 10 - (progress * 25)
                        tool_sprite = pygame.transform.flip(tool_sprite, True, False)
                    elif self.state.facing == 'down':
                        angle = 90 + (progress * 90)
                        tx += -10 + (progress * 20); ty += 5 + (progress * 15)
                    elif self.state.facing == 'up':
                        angle = -90 + (progress * 90)
                        tx += 10 - (progress * 20); ty -= 10 + (progress * 10)
                    
                    rotated_tool = pygame.transform.rotate(tool_sprite, angle)
                    tw, th = rotated_tool.get_size()
                    
                    if self.state.facing == 'up':
                        self.screen.blit(rotated_tool, (tx + TILE/2 - tw/2, ty + TILE/2 - th/2))
                        self.screen.blit(player_sprite, (pvx * TILE, pvy * TILE + jump_y))
                    else:
                        self.screen.blit(player_sprite, (pvx * TILE, pvy * TILE + jump_y))
                        self.screen.blit(rotated_tool, (tx + TILE/2 - tw/2, ty + TILE/2 - th/2))
                        
                else:
                    player_sprite = ANIMATED['player'][self.state.facing][frame]
                    shadow = self.shadow_std_small if self.moving and frame == 1 else self.shadow_std
                    self.screen.blit(shadow, (pvx * TILE, pvy * TILE))
                    self.screen.blit(player_sprite, (pvx * TILE, pvy * TILE))
                
                fx, fy = self.get_facing_tile()
                fvx = fx - self.cam_x
                fvy = fy - self.cam_y
                pygame.draw.rect(self.screen, C.ui_gold, (fvx * TILE + 2, fvy * TILE + 2, TILE-4, TILE-4), 1)

        # Weather & Time of Day Overlay
        if not indoor:
            # Time of Day
            time_m = self.state.time_minutes
            overlay = pygame.Surface((SCREEN_W, VIEW_H * TILE), pygame.SRCALPHA)
            
            if 5 * 60 <= time_m < 7 * 60:
                # Fajar (Pagi)
                progress = (time_m - 5 * 60) / 120
                alpha = int(120 * (1 - progress))
                overlay.fill((255, 180, 120, alpha))
                self.screen.blit(overlay, (0, 0))
            elif 16 * 60 <= time_m < 18 * 60:
                # Senja (Sore)
                progress = (time_m - 16 * 60) / 120
                r = int(255 * (1 - progress) + 30 * progress)
                g = int(150 * (1 - progress) + 30 * progress)
                b = int(80 * (1 - progress) + 60 * progress)
                alpha = int(60 + 100 * progress)
                overlay.fill((r, g, b, alpha))
                self.screen.blit(overlay, (0, 0))
            elif time_m >= 18 * 60 or time_m < 5 * 60:
                # Malam
                darkness = 160
                if 18 * 60 <= time_m < 19 * 60:
                    darkness = int(160 * ((time_m - 18 * 60) / 60))
                elif 4 * 60 <= time_m < 5 * 60:
                    darkness = int(160 * (1 - (time_m - 4 * 60) / 60))
                overlay.fill((20, 20, 50, darkness))
                self.screen.blit(overlay, (0, 0))

            # Weather
            if self.state.weather in ('Hujan', 'Badai'):
                speed = 8 if self.state.weather == 'Badai' else 4
                rain_color = (150, 180, 255, 120) if self.state.weather == 'Hujan' else (120, 150, 200, 160)
                for i in range(100 if self.state.weather == 'Badai' else 50):
                    rx = (i * 37 + int(self.anim_tick * 0.5 * speed)) % SCREEN_W
                    ry = (i * 19 + int(self.anim_tick * 0.8 * speed)) % (VIEW_H * TILE)
                    pygame.draw.line(self.screen, rain_color, (rx, ry), (rx - speed * 0.5, ry + speed * 1.5), 2)
                    
            # Particles
            for p in self.particles:
                if p['type'] == 'firefly':
                    alpha = int(255 * math.sin(math.pi * p['life'] / p['max_life']))
                    self.firefly_surf.set_alpha(alpha)
                    self.screen.blit(self.firefly_surf, (int(p['x']) - 6, int(p['y']) - 6))
                elif p['type'] == 'leaf':
                    pygame.draw.rect(self.screen, (200, 100, 30), (int(p['x']), int(p['y']), 4, 4))
                elif p['type'] == 'petal':
                    pygame.draw.rect(self.screen, (255, 180, 200), (int(p['x']), int(p['y']), 4, 4))
                elif p['type'] == 'smoke':
                    alpha = int(100 * (p['life'] / p['max_life']))
                    pygame.draw.circle(self.screen, (100, 100, 100, alpha), (int(p['x']), int(p['y'])), 8)
                    
        else:
            # Indoor Vignette
            self.screen.blit(self.vignette_surf, (0, 0))

    def render_hud(self):
        # HUD at bottom
        hud_y = VIEW_H * TILE
        pygame.draw.rect(self.screen, C.ui_bg, (0, hud_y, SCREEN_W, 80))
        pygame.draw.rect(self.screen, C.ui_border, (0, hud_y, SCREEN_W, 80), 2)

        # Status info
        day_txt = self.font_small.render(
            f"Hari {self.state.day} | {self.state.get_time_str()} | {self.state.get_season_name()}",
            True, C.ui_text)
        self.screen.blit(day_txt, (10, hud_y + 5))

        # Stats
        bar_w = 100
        bar_h = 8

        # --- HP Bar ---
        hp_ratio = self.state.hp / max(1, getattr(self.state, 'max_hp', 100))
        hp_fill_w = int(hp_ratio * bar_w)
        pygame.draw.rect(self.screen, (40, 20, 20), (10, hud_y + 18, bar_w, bar_h), border_radius=4)
        if hp_fill_w > 0:
            pygame.draw.rect(self.screen, (220, 50, 50), (10, hud_y + 18, hp_fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, C.ui_border, (10, hud_y + 18, bar_w, bar_h), 1, border_radius=4)
        hp_txt = self.font_small.render(f"HP: {int(self.state.hp)}/{getattr(self.state, 'max_hp', 100)}", True, C.wt)
        self.screen.blit(hp_txt, (115, hud_y + 16))

        # --- Stamina Bar ---
        bar_w = 100
        bar_h = 8
        ratio = self.state.energy / max(1, self.state.max_energy)
        fill_w = int(ratio * bar_w)
        
        if ratio > 0.5:
            bar_color = (100, 220, 100)
        elif ratio > 0.25:
            bar_color = (220, 200, 50)
        else:
            bar_color = (220, 50, 50)
            
        pygame.draw.rect(self.screen, (40, 20, 20), (10, hud_y + 28, bar_w, bar_h), border_radius=4)
        if fill_w > 0:
            pygame.draw.rect(self.screen, bar_color, (10, hud_y + 28, fill_w, bar_h), border_radius=4)
        pygame.draw.rect(self.screen, C.ui_border, (10, hud_y + 28, bar_w, bar_h), 1, border_radius=4)
        
        energy_txt = self.font_small.render(f"EN: {self.state.energy}/{self.state.max_energy}", True, C.wt)
        self.screen.blit(energy_txt, (115, hud_y + 26))

        gold_txt = self.font_small.render(f"💰 {self.state.gold}G", True, C.ui_gold)
        weather_txt = self.font_small.render(f"🌤 {self.state.weather}", True, (130,200,255))
        self.screen.blit(gold_txt, (200, hud_y + 18))
        self.screen.blit(weather_txt, (280, hud_y + 18))

        # Location
        scene_name = SCENES[self.state.scene_name].display
        loc_txt = self.font_small.render(f"📍 {scene_name}", True, (200,180,255))
        self.screen.blit(loc_txt, (355, hud_y + 22))
        self.screen.blit(loc_txt, (380, hud_y + 24))

        # Tool bar
        for i in range(len(TOOLS)):
            x = 10 + i * 45
            y = hud_y + 42
            selected = (i == self.state.tool_index)
            bg = C.ui_bg2 if selected else (30, 20, 45)
            pygame.draw.rect(self.screen, bg, (x, y, 40, 30), border_radius=6)
            color = C.ui_gold if selected else C.ui_border
            pygame.draw.rect(self.screen, color, (x, y, 40, 30), 2, border_radius=6)
            
            # Gambar icon alat pixel art (berada di tengah kotak)
            self.screen.blit(SPRITES['tools'][i], (x + 6, y + 1))
            
            # Hotkey (1, 2, 3...)
            hotkey_text = self.font_small.render(str(i+1), True, C.wt)
            self.screen.blit(hotkey_text, (x + 3, y + 2))

        # Current tool & seed
        current_tool = self.font_small.render(
            f"Aktif: {TOOLS[self.state.tool_index]} | 🌱 {CROPS[self.state.seed_key]['name']}",
            True, C.ui_text)
        self.screen.blit(current_tool, (290, hud_y + 48))

        # Quest
        quest_stage = QUEST_STAGES[min(self.state.quest_stage, len(QUEST_STAGES)-1)]
        quest_txt = self.font_small.render(
            f"📋 {quest_stage['t']}: {quest_stage['d']}", True, (180,255,180))
        self.screen.blit(quest_txt, (290, hud_y + 62))

    def render_dialog(self):
        # Dialog box at bottom
        box_y = VIEW_H * TILE - 100
        pygame.draw.rect(self.screen, (15, 10, 30), (10, box_y, SCREEN_W - 20, 95), border_radius=12)
        pygame.draw.rect(self.screen, C.ui_border, (10, box_y, SCREEN_W - 20, 95), 2, border_radius=12)

        # Speaker
        if self.dialog_speaker:
            speaker = self.font.render(f"▶ {self.dialog_speaker}", True, C.ui_gold)
            self.screen.blit(speaker, (22, box_y + 10))

        # Typewriter text
        current = self.dialog_lines[self.dialog_index]
        visible = current[:self.typewriter_progress]
        # Word wrap
        words = visible.split(' ')
        line = ''
        y_off = 32
        for word in words:
            test = line + word + ' '
            if self.font.size(test)[0] > SCREEN_W - 20:
                t = self.font.render(line, True, C.ui_text)
                self.screen.blit(t, (22, box_y + y_off))
                y_off += 22
                line = word + ' '
            else:
                line = test
        if line:
            t = self.font.render(line, True, C.ui_text)
            self.screen.blit(t, (22, box_y + y_off))

        # Hint
        if self.typewriter_progress >= len(current):
            hint = self.font_small.render(
                f"▶ SPACE lanjut  ({self.dialog_index+1}/{len(self.dialog_lines)})",
                True, (130, 110, 160))
            self.screen.blit(hint, (SCREEN_W - 190, box_y + 75))
            
    def render_fishing(self):
        # Draw semi-transparent background
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(150)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))
        
        # Draw minigame UI
        bx = SCREEN_W // 2 + 50
        by = SCREEN_H // 2 - 100
        
        # Background bar
        pygame.draw.rect(self.screen, (20, 50, 100), (bx, by, 30, 200))
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, 30, 200), 2)
        
        # Player Catch Bar
        fish_center = self.fishing_fish_y + 5
        bar_center = self.fishing_bar_y + 20
        catch_color = (100, 255, 100) if abs(fish_center - bar_center) <= 25 else (200, 100, 100)
        pygame.draw.rect(self.screen, catch_color, (bx + 2, by + int(self.fishing_bar_y), 26, 40))
        
        # Fish
        fish_y = by + int(self.fishing_fish_y)
        fish_text = self.font.render("🐟", True, C.wt)
        self.screen.blit(fish_text, (bx + 6, fish_y - 2))
        
        # Progress Bar (beside it)
        px = bx + 40
        pygame.draw.rect(self.screen, (50, 20, 20), (px, by, 10, 200))
        fill_h = int(200 * (self.fishing_progress / 100.0))
        pygame.draw.rect(self.screen, (50, 255, 50), (px, by + 200 - fill_h, 10, fill_h))
        pygame.draw.rect(self.screen, C.ui_border, (px, by, 10, 200), 1)
        
        # Instructions
        inst = self.font_big.render("TAHAN SPACE untuk menarik kail!", True, C.wt)
        self.screen.blit(inst, (SCREEN_W // 2 - inst.get_width() // 2, by - 40))

    def render_menu(self):
        # Modal menu
        bw = 400
        if self.menu_items:
            # Dinamis melebarkan UI menu jika ada teks bahan yang panjang
            max_text_w = max(self.font.size(label)[0] for label, _ in self.menu_items)
            bw = max(400, max_text_w + 60)
            
        bh = min(400, 80 + len(self.menu_items) * 32)
        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H // 2 - bh // 2

        # Dim background
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))

        pygame.draw.rect(self.screen, (15, 8, 30), (bx, by, bw, bh), border_radius=12)
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, bw, bh), 3, border_radius=12)

        # Title
        title = self.font_big.render(self.menu_title, True, C.ui_gold)
        self.screen.blit(title, (bx + 20, by + 15))

        # Items
        for i, (label, _) in enumerate(self.menu_items):
            y = by + 60 + i * 32
            if i == self.menu_selected:
                pygame.draw.rect(self.screen, (60, 30, 100), (bx + 10, y - 4, bw - 20, 28), border_radius=6)
                arrow = self.font.render("▶", True, C.ui_gold)
                self.screen.blit(arrow, (bx + 15, y))
            color = C.ui_gold if i == self.menu_selected else C.ui_text
            t = self.font.render(label, True, color)
            self.screen.blit(t, (bx + 35, y))

    def render_inventory(self):
        is_chest = self.mode == 'chest'
        bag_level = self.state.upgrades.get('bag_level', 1)
        inv_rows = 2 + (bag_level - 1)
        inv_slots = inv_rows * 6

        bw = 420
        cols = 6
        cell_size = 48
        gap = 6
        step = cell_size + gap

        if is_chest:
            bh = 110 + (4 * step) + 30 + (inv_rows * step) + 40
        else:
            bh = 100 + (inv_rows * step) + 40

        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H // 2 - bh // 2

        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))

        pygame.draw.rect(self.screen, (25, 15, 40), (bx, by, bw, bh), border_radius=12)
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, bw, bh), 3, border_radius=12)

        title_str = "🎒 Inventori Tas" if not is_chest else "📦 Peti Penyimpanan & Tas"
        title = self.font_big.render(title_str, True, C.ui_gold)
        self.screen.blit(title, (bx + 20, by + 15))

        self.refresh_inventory_lists()
        chest_active = getattr(self, 'chest_active', False)

        margin_x = bx + (bw - (cols * step - gap)) // 2

        if is_chest:
            chest_label = self.font.render("Peti Penyimpanan", True, C.ui_text if not chest_active else C.ui_gold)
            self.screen.blit(chest_label, (bx + 20, by + 50))
            
            margin_y_chest = by + 75
            for i in range(24): # Draw 4 rows for chest
                col = i % cols
                row = i // cols
                cx = margin_x + col * step
                cy = margin_y_chest + row * step
                
                is_selected = chest_active and i == self.inventory_cursor
                bg_color = (60, 40, 80) if is_selected else (40, 25, 60)
                border_color = C.ui_gold if is_selected else C.ui_border
                
                pygame.draw.rect(self.screen, bg_color, (cx, cy, cell_size, cell_size), border_radius=8)
                pygame.draw.rect(self.screen, border_color, (cx, cy, cell_size, cell_size), 2, border_radius=8)
                
                if i < len(self.chest_list):
                    item_id, count = self.chest_list[i]
                    icon, name = self.get_item_info(item_id)
                    icon_txt = self.font_big.render(icon, True, C.wt)
                    self.screen.blit(icon_txt, (cx + cell_size//2 - icon_txt.get_width()//2, cy + 6))
                    count_txt = self.font_small.render(str(count), True, C.wt)
                    self.screen.blit(count_txt, (cx + cell_size - count_txt.get_width() - 4, cy + cell_size - 14))
                    
        inv_start_y = by + 75 + (4 * step) + 20 if is_chest else by + 60
        if is_chest:
            inv_label = self.font.render("Tas Pemain", True, C.ui_gold if not chest_active else C.ui_text)
            self.screen.blit(inv_label, (bx + 20, inv_start_y - 20))
            
        for i in range(inv_slots):
            col = i % cols
            row = i // cols
            cx = margin_x + col * step
            cy = inv_start_y + row * step

            is_selected = (not chest_active) and i == self.inventory_cursor
            bg_color = (60, 40, 80) if is_selected else (40, 25, 60)
            border_color = C.ui_gold if is_selected else C.ui_border
            
            pygame.draw.rect(self.screen, bg_color, (cx, cy, cell_size, cell_size), border_radius=8)
            pygame.draw.rect(self.screen, border_color, (cx, cy, cell_size, cell_size), 2, border_radius=8)

            if i < len(self.inventory_list):
                item_id, count = self.inventory_list[i]
                icon, name = self.get_item_info(item_id)
                icon_txt = self.font_big.render(icon, True, C.wt)
                self.screen.blit(icon_txt, (cx + cell_size//2 - icon_txt.get_width()//2, cy + 6))
                count_txt = self.font_small.render(str(count), True, C.wt)
                self.screen.blit(count_txt, (cx + cell_size - count_txt.get_width() - 4, cy + cell_size - 14))

        active_list = self.chest_list if chest_active else self.inventory_list
        if active_list and self.inventory_cursor < len(active_list):
            selected_id, count = active_list[self.inventory_cursor]
            _, name = self.get_item_info(selected_id)
            desc = self.font.render(f"▶ {name} (Total: {count})", True, C.ui_text)
            self.screen.blit(desc, (bx + 20, by + bh - 35))
            hint_str = "ESC/I: Tutup | X: Buang" if not is_chest else "ESC/E: Tutup | TAB/SPACE: Pindah"
            hint = self.font_small.render(hint_str, True, (150, 150, 150))
            self.screen.blit(hint, (bx + bw - hint.get_width() - 20, by + bh - 25))

    def render_notification(self):
        # Toast at top
        text = self.font.render(self.notif_text, True, C.ui_gold)
        tw = text.get_width() + 40
        tx = SCREEN_W // 2 - tw // 2
        ty = 15
        pygame.draw.rect(self.screen, (15, 10, 30), (tx, ty, tw, 36), border_radius=18)
        pygame.draw.rect(self.screen, C.ui_border, (tx, ty, tw, 36), 2, border_radius=18)
        self.screen.blit(text, (tx + 20, ty + 9))


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()
