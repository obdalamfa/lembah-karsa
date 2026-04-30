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
    1-6                - Pilih alat (cangkul, siram, tanam, panen, kapak, hadiah)
    Q / R              - Ganti jenis benih
    T                  - Tidur (dekat rumah)
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
TILE = 32                      # ukuran tile di layar (pixel)
SPRITE = 16                    # ukuran sprite asli (pixel art 16x16)
SCALE = TILE // SPRITE         # faktor scaling (2x)
VIEW_W = 20                    # viewport lebar (tile)
VIEW_H = 13                    # viewport tinggi (tile)
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
    # Trunk
    rect(s, 6, 11, 9, 15, C.wo0)
    rect(s, 7, 11, 8, 15, C.wo1)
    # Crown layers
    layers = [
        (5,9,10,10,C.g0), (4,7,11,9,C.g1), (3,5,12,7,C.g0),
        (4,3,11,5,C.g1), (5,2,10,4,C.g0), (6,1,9,3,C.g1),
    ]
    for x1,y1,x2,y2,c in layers:
        rect(s, x1, y1, x2, y2, c)
    # Highlight
    rect(s, 6, 1, 8, 3, C.g2)
    return s

def make_fence():
    s = make_surface()
    rect(s, 0, 5, 15, 8, C.wo0)
    hline(s, 5, 0, 15, C.wo2)
    hline(s, 8, 0, 15, C.wo1)
    vline(s, 7, 0, 15, C.wo1)
    vline(s, 8, 0, 15, C.wo1)
    return s

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
def make_char(direction, frame, hair=C.h0, shirt=C.s0, pants=C.pn):
    s = make_surface()
    # Topi
    rect(s, 5, 1, 10, 2, C.ht)
    rect(s, 4, 2, 11, 3, C.ht2)
    # Kepala
    rect(s, 4, 3, 11, 7, C.sk)
    # Rambut samping
    for xi in [4,5,10,11]:
        for yi in [3,4]:
            px(s, xi, yi, hair)
    # Mata & mulut
    if direction != "up":
        px(s, 5, 5, C.bk)
        px(s, 9, 5, C.bk)
        px(s, 7, 6, (224,128,128))
        px(s, 8, 6, (224,128,128))
    else:
        rect(s, 4, 3, 11, 5, hair)
    # Badan
    rect(s, 4, 8, 11, 12, shirt)
    # Tangan
    if direction in ("left","right"):
        off = 1 if frame else 0
        px(s, 3, 8, C.sk)
        px(s, 3, 9+off, C.sk)
        px(s, 12, 8+(1-off), C.sk)
        px(s, 12, 9, C.sk)
    else:
        px(s, 3, 8, C.sk); px(s, 3, 9, C.sk)
        px(s, 12, 8, C.sk); px(s, 12, 9, C.sk)
    # Celana
    rect(s, 4, 12, 11, 15, pants)
    vline(s, 8, 12, 15, C.pn2)
    # Sepatu
    rect(s, 4, 15, 5, 15, C.h2)
    rect(s, 10, 15, 11, 15, C.h2)
    # Walk animation
    if frame and direction in ("left","right"):
        px(s, 4, 14, pants)
        px(s, 11, 15, C.h2)
    return s

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
    return s

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
#  SPRITE REGISTRY (lazy init after pygame.init)
# ══════════════════════════════════════════════════════════════
SPRITES = {}
ANIMATED = {}

def init_sprites():
    """Generate & cache semua sprite."""
    global SPRITES, ANIMATED

    # Terrain
    SPRITES['grass'] = pygame.transform.scale(make_grass_tile(), (TILE, TILE))
    SPRITES['dirt'] = pygame.transform.scale(make_dirt_tile(), (TILE, TILE))
    SPRITES['tilled_dry'] = pygame.transform.scale(make_tilled_dry(), (TILE, TILE))
    SPRITES['tilled_wet'] = pygame.transform.scale(make_tilled_wet(), (TILE, TILE))
    SPRITES['path'] = pygame.transform.scale(make_path_tile(), (TILE, TILE))
    SPRITES['floor'] = pygame.transform.scale(make_floor_tile(), (TILE, TILE))
    SPRITES['wall'] = pygame.transform.scale(make_wall_tile(), (TILE, TILE))

    # Objects
    SPRITES['tree'] = pygame.transform.scale(make_tree(), (TILE, TILE))
    SPRITES['fence'] = pygame.transform.scale(make_fence(), (TILE, TILE))
    SPRITES['mailbox'] = pygame.transform.scale(make_mailbox(), (TILE, TILE))
    SPRITES['door'] = pygame.transform.scale(make_door(), (TILE, TILE))
    SPRITES['chest'] = pygame.transform.scale(make_chest(), (TILE, TILE))

    # Furniture
    SPRITES['bed'] = pygame.transform.scale(make_bed(), (TILE, TILE))
    SPRITES['stove'] = pygame.transform.scale(make_stove(), (TILE, TILE))
    SPRITES['table'] = pygame.transform.scale(make_table(), (TILE, TILE))
    SPRITES['bookshelf'] = pygame.transform.scale(make_bookshelf(), (TILE, TILE))
    SPRITES['mirror'] = pygame.transform.scale(make_mirror(), (TILE, TILE))
    SPRITES['fireplace'] = pygame.transform.scale(make_fireplace(), (TILE, TILE))
    SPRITES['clock'] = pygame.transform.scale(make_clock(), (TILE, TILE))
    SPRITES['plant_pot'] = pygame.transform.scale(make_plant_pot(), (TILE, TILE))
    SPRITES['counter'] = pygame.transform.scale(make_counter(), (TILE, TILE))
    SPRITES['shelf_store'] = pygame.transform.scale(make_shelf_store(), (TILE, TILE))

    # Water animated (4 frames)
    ANIMATED['water'] = [
        pygame.transform.scale(make_water_tile(i*4), (TILE, TILE))
        for i in range(4)
    ]

    # Player animations — 4 directions × 2 frames
    ANIMATED['player'] = {}
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(2):
            dir_for_sprite = direction
            flip = False
            if direction == 'left':
                dir_for_sprite = 'right'
                flip = True
            surf = make_char(dir_for_sprite, f)
            surf = pygame.transform.scale(surf, (TILE, TILE))
            if flip:
                surf = pygame.transform.flip(surf, True, False)
            frames.append(surf)
        ANIMATED['player'][direction] = frames

    # NPC animations
    npc_configs = {
        'arya': (C.ng, C.g1, C.pn),
        'sari': (C.cr, C.nc_sari, C.pn),
        'raka': (C.ng, C.nc_raka, C.s0),
        'maya': (C.gl, C.nc_maya, C.pn),
        'budi': (C.ng, C.nc_budi, C.p2),
    }
    for npc_id, (hair, shirt, pants) in npc_configs.items():
        ANIMATED[f'npc_{npc_id}'] = {}
        for direction in ['up', 'down', 'left', 'right']:
            frames = []
            for f in range(2):
                dir_for_sprite = direction
                flip = False
                if direction == 'left':
                    dir_for_sprite = 'right'
                    flip = True
                surf = make_char(dir_for_sprite, f, hair, shirt, pants)
                surf = pygame.transform.scale(surf, (TILE, TILE))
                if flip:
                    surf = pygame.transform.flip(surf, True, False)
                frames.append(surf)
            ANIMATED[f'npc_{npc_id}'][direction] = frames

    # Crops
    SPRITES['crops'] = {}
    CROP_COLORS = {
        'lobak': (C.cg, C.cg2),
        'wortel': (C.co, C.d1),
        'stroberi': (C.cr, C.cg),
        'jagung': (C.cy, C.cg),
        'tomat': (C.cr, (255,80,80)),
        'labu': (C.co, C.fn),
        'bayam': (C.g2, C.g0),
        'jamur': ((212,164,116), C.fn2),
    }
    for crop_id, (c1, c2) in CROP_COLORS.items():
        SPRITES['crops'][crop_id] = [
            pygame.transform.scale(make_crop_sprite(stage, c1, c2), (TILE, TILE))
            for stage in range(4)
        ]

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
}

SEASONS = ['Semi','Panas','Gugur','Dingin']
SEASON_NAMES = {'Semi':'Musim Semi','Panas':'Musim Panas','Gugur':'Musim Gugur','Dingin':'Musim Dingin'}
DAYS_PER_SEASON = 28

TOOLS = ['Cangkul', 'Siram', 'Tanam', 'Panen', 'Kapak', 'Hadiah']
TOOL_ICONS = ['⛏', '💧', '🌱', '🌾', '🪓', '🎁']

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

# ══════════════════════════════════════════════════════════════
#  TILE TYPES
# ══════════════════════════════════════════════════════════════
# Simple tile IDs
G, D, P, W, FL, WL, TR, H, MB, DR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH = range(22)

TILE_NAMES = {
    G: 'grass', D: 'dirt', P: 'path', W: 'water', FL: 'floor', WL: 'wall',
    TR: 'tree', H: 'house', MB: 'mailbox', DR: 'door', FN: 'fence',
    BD: 'bed', ST: 'stove', TB: 'table', BS: 'bookshelf', MR: 'mirror',
    FP: 'fireplace', CL: 'clock', PP: 'plant_pot', CH: 'chest',
    CT: 'counter', SH: 'shelf_store',
}

WALKABLE = {G, D, P, FL}  # tile yang bisa diinjak
TILLABLE = {G, D}          # tile yang bisa dicangkul
BLOCKING = {W, WL, TR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH}

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
        self.npcs = npcs or []        # [(npc_id,x,y)]
        self.indoor = indoor

def build_outdoor():
    W_, H_ = 40, 25
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

    # Main paths
    hline_(13, 0, W_-1, P)
    vline_(18, 0, H_-1, P)

    # River
    rect_fill(19, 0, 4, 5, W)
    rect_fill(22, 4, 3, 4, W)
    # Bridge
    m[13][19] = P; m[13][20] = P; m[13][21] = P

    # Village — shops (using H for buildings)
    rect_fill(20, 1, 5, 4, H); m[4][22] = DR   # shop
    rect_fill(27, 1, 5, 4, H); m[4][29] = DR   # clinic
    rect_fill(34, 1, 5, 4, H); m[4][36] = DR   # studio
    rect_fill(20, 7, 5, 4, H); m[10][22] = DR  # smith
    rect_fill(27, 7, 5, 4, H); m[10][29] = DR  # greenhouse

    # Trees in village
    for x,y in [(25,2),(26,5),(33,2),(33,7),(38,3),(39,7)]:
        if m[y][x] == G: m[y][x] = TR

    # Southern forest (random trees)
    rng = random.Random(1)
    for y in range(15, H_):
        for x in range(0, 18):
            if m[y][x] == G and rng.random() < 0.2:
                m[y][x] = TR

    # Fishing lake
    rect_fill(5, 18, 8, 5, W)

    return Scene('outdoor', 'Lembah Karsa', m,
        portals=[
            (3,4,'house',7,9),
            (22,4,'shop',7,9),
            (29,4,'clinic',7,9),
            (36,4,'studio',7,9),
            (22,10,'smith',7,9),
            (29,10,'greenhouse',7,9),
        ],
        npcs=[('arya',11,8)])

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
        portals=[(7,11,'outdoor',22,5)],
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
        portals=[(7,11,'outdoor',29,5)],
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
        portals=[(7,11,'outdoor',36,5)],
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
        portals=[(7,11,'outdoor',22,11)],
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
        portals=[(7,11,'outdoor',29,11)],
        indoor=True)

SCENES = {
    'outdoor': build_outdoor(),
    'house': build_house(),
    'shop': build_shop(),
    'clinic': build_clinic(),
    'studio': build_studio(),
    'smith': build_smith(),
    'greenhouse': build_greenhouse(),
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

    # Time
    day: int = 1
    year: int = 1
    day_in_season: int = 1
    season_index: int = 0
    time_minutes: float = 360.0  # 6:00 AM
    weather: str = 'Cerah'

    # Stats
    energy: int = 100
    max_energy: int = 100
    gold: int = 100
    tool_index: int = 0
    seed_key: str = 'lobak'

    # Inventory
    inventory: dict = field(default_factory=lambda: {'lobak_seed': 3})

    # Soil: key "x,y,scene" -> dict
    soil: dict = field(default_factory=dict)

    # NPC
    npc_hearts: dict = field(default_factory=lambda: {n:0 for n in NPCS})
    npc_dialog_index: dict = field(default_factory=lambda: {n:0 for n in NPCS})

    # Upgrades
    upgrades: dict = field(default_factory=lambda: {'hoe':False,'water':False,'bag':False,'axe':False})

    # Quest
    quest_stage: int = 0
    mail_read: bool = False
    shop_unlocked: bool = False
    greenhouse_open: bool = False

    # Stats
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
            'time_minutes': self.time_minutes, 'weather': self.weather,
            'energy': self.energy, 'max_energy': self.max_energy, 'gold': self.gold,
            'tool_index': self.tool_index, 'seed_key': self.seed_key,
            'inventory': self.inventory, 'soil': self.soil,
            'npc_hearts': self.npc_hearts, 'npc_dialog_index': self.npc_dialog_index,
            'upgrades': self.upgrades, 'quest_stage': self.quest_stage,
            'mail_read': self.mail_read, 'shop_unlocked': self.shop_unlocked,
            'greenhouse_open': self.greenhouse_open, 'stats': self.stats,
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

        # NPC positions (for wandering)
        self.npc_frame_tick = 0

        # Input cooldowns
        self.move_cooldown = 0
        self.move_delay = 140  # ms between moves

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

        if self.mode == 'play':
            # Movement handled in update()
            if event.key in (pygame.K_SPACE,):
                self.use_tool()
            elif event.key in (pygame.K_e, pygame.K_RETURN):
                self.interact()
            elif pygame.K_1 <= event.key <= pygame.K_6:
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
            # Advance clock
            self.state.time_minutes += dt * 0.016  # 1 in-game minute per ~1s
            if self.state.time_minutes >= 22*60:
                self.state.time_minutes = 22*60
                self.start_dialog(["Sudah larut malam...", "Kamu tertidur kelelahan."], "🌙 Malam",
                                  callback=self.sleep_next_day)

            # Movement
            self.handle_movement(dt)

            # Typewriter advance
            if self.mode == 'dialog':
                pass

        if self.mode == 'dialog':
            if self.typewriter_progress < len(self.dialog_lines[self.dialog_index]):
                self.typewriter_progress += self.typewriter_speed

    def handle_movement(self, dt):
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
                    # Rumah kaca adalah milestone cerita: sebelum diperbaiki,
                    # pintunya menampilkan opsi restorasi alih-alih langsung masuk.
                    if portal[2] == 'greenhouse' and not self.state.greenhouse_open:
                        self.handle_greenhouse_gate(portal)
                    else:
                        self.transition_to(portal[2], portal[3], portal[4])
                    break

        self.update_camera()
        self.move_cooldown = self.move_delay

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

    def update_camera(self):
        scene = SCENES[self.state.scene_name]
        self.cam_x = max(0, min(scene.w - VIEW_W, self.state.player_x - VIEW_W // 2))
        self.cam_y = max(0, min(scene.h - VIEW_H, self.state.player_y - VIEW_H // 2))

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
        tool = TOOLS[self.state.tool_index]
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.state.scene_name]
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
        elif tool == 'Hadiah':
            self.give_gift()

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
        key = f"{x},{y},{self.state.scene_name}"
        soil = self.state.soil.get(key)
        if not soil or not soil.get('crop'):
            self.notif("Tidak ada tanaman.")
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
        self.check_quest_progress()

    def use_axe(self, x, y, tile):
        if not self.state.upgrades['axe']:
            self.notif("Butuh kapak! Beli dari Budi.")
            return
        if tile != TR:
            self.notif("Tidak ada pohon.")
            return
        if not self.spend_energy(4):
            return
        SCENES[self.state.scene_name].tiles[y][x] = G
        self.state.inventory['kayu'] = self.state.inventory.get('kayu', 0) + 3
        self.notif("Pohon ditebang! +3 kayu")

    def give_gift(self):
        scene = SCENES[self.state.scene_name]
        px, py = self.state.player_x, self.state.player_y
        for npc_id, nx, ny in scene.npcs:
            if abs(nx - px) <= 1 and abs(ny - py) <= 1:
                npc_data = NPCS[npc_id]
                gift_item = npc_data['gift']
                if self.state.inventory.get(gift_item, 0) <= 0:
                    self.notif(f"Tidak punya {CROPS[gift_item]['name']}!")
                    return
                self.state.inventory[gift_item] -= 1
                if self.state.inventory[gift_item] <= 0:
                    del self.state.inventory[gift_item]
                self.state.npc_hearts[npc_id] = min(10, self.state.npc_hearts[npc_id] + 2)
                self.state.stats['gifts'] += 1
                self.start_dialog([npc_data['gift_r']], npc_data['name'])
                self.check_quest_progress()
                return
        self.notif("Tidak ada warga di dekatmu.")

    def spend_energy(self, n):
        if self.state.energy < n:
            self.start_dialog(["Energimu tidak cukup!", "Tidurlah untuk memulihkan."], "⚡")
            return False
        self.state.energy -= n
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
        for npc_id, nx, ny in scene.npcs:
            if abs(nx - self.state.player_x) <= 1 and abs(ny - self.state.player_y) <= 1:
                self.talk_to_npc(npc_id)
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
        npc_data = NPCS[npc_id]
        idx = min(self.state.npc_dialog_index[npc_id], len(npc_data['talks'])-1)
        lines = npc_data['talks'][idx]
        self.state.npc_dialog_index[npc_id] = min(idx+1, len(npc_data['talks'])-1)
        # Special: sari & budi open shops after dialog
        callback = None
        if npc_id == 'sari' and self.state.shop_unlocked:
            callback = self.open_shop
        elif npc_id == 'budi':
            callback = self.open_upgrade_shop
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
        inv = self.state.inventory
        lines = ["📦 Peti penyimpanan:"]
        has_items = False
        for k, v in inv.items():
            if v > 0:
                lines.append(f"  {k}: {v}")
                has_items = True
        if not has_items:
            lines.append("  (Kosong)")
        self.start_dialog(lines, "📦 Peti")

    def open_shipping_bin(self):
        """Kotak pengiriman di area kebun untuk menjual panen tanpa pergi ke toko."""
        total = 0
        details = []
        for crop_id, crop in CROPS.items():
            count = self.state.inventory.get(crop_id, 0)
            if count > 0:
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
            self.update_camera()
        self.fade_callback = do_switch

    def handle_greenhouse_gate(self, portal):
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

    # ═══════════════════════════════════════════════════
    #  SLEEP
    # ═══════════════════════════════════════════════════
    def sleep_next_day(self):
        self.close_menu()
        # Grow crops
        is_rain = self.state.weather in ('Hujan','Badai')
        for key, soil in self.state.soil.items():
            if is_rain and soil.get('tilled'):
                soil['watered'] = True
            if soil.get('crop') and soil.get('watered'):
                soil['age'] = soil.get('age', 0) + 1
            soil['watered'] = False
        # Advance day
        self.state.day += 1
        self.state.day_in_season += 1
        if self.state.day_in_season > DAYS_PER_SEASON:
            self.state.day_in_season = 1
            self.state.season_index = (self.state.season_index + 1) % 4
            if self.state.season_index == 0:
                self.state.year += 1
        self.state.time_minutes = 360
        self.state.energy = self.state.max_energy
        self.state.weather = random.choice(['Cerah','Cerah','Mendung','Hujan','Berangin'])
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
            if szn in crop['seasons'] or self.state.greenhouse_open:
                cost = crop['cost'] * 3
                def mk(k=crop_id, c=cost):
                    return lambda: self.buy_seeds(k, c)
                items.append((f"{crop['name']} x3 benih - {cost}G", mk()))
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

    def open_upgrade_shop(self):
        self.menu_title = f"⚒️ Bengkel Budi — {self.state.gold}G"
        items = []
        upgrades = [
            ('hoe', 80, 'Cangkul Baja (hemat energi)'),
            ('water', 120, 'Penyiram Perunggu (3 petak)'),
            ('bag', 60, 'Tas Besar (energi +20)'),
            ('axe', 50, 'Kapak Besi (tebang pohon)'),
        ]
        for upg_id, cost, label in upgrades:
            if self.state.upgrades[upg_id]:
                items.append((f"✅ {label}", self.close_menu))
            else:
                def mk(u=upg_id, c=cost):
                    return lambda: self.buy_upgrade(u, c)
                items.append((f"{label} - {cost}G", mk()))
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
        self.update_camera()
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
            self.update_camera()
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

        # Background
        bg_color = (40,25,15) if indoor else (80,140,180) if self.state.get_season() == 'Semi' else (100,100,60)
        self.screen.fill(bg_color, (0, 0, SCREEN_W, VIEW_H * TILE))

        # Draw tiles
        for vy in range(VH := VIEW_H):
            for vx in range(VIEW_W):
                wx = vx + self.cam_x
                wy = vy + self.cam_y
                if wx < 0 or wx >= scene.w or wy < 0 or wy >= scene.h:
                    continue
                t = scene.tiles[wy][wx]
                px_ = vx * TILE
                py_ = vy * TILE
                # Base ground
                key = f"{wx},{wy},{self.state.scene_name}"
                soil = self.state.soil.get(key)
                if soil and soil.get('tilled'):
                    sprite = SPRITES['tilled_wet'] if soil.get('watered') else SPRITES['tilled_dry']
                    self.screen.blit(sprite, (px_, py_))
                    if soil.get('crop'):
                        stage = min(soil.get('age', 0), 3)
                        crop_id = soil['crop']
                        if crop_id in SPRITES['crops']:
                            self.screen.blit(SPRITES['crops'][crop_id][stage], (px_, py_))
                    continue

                # Normal tile
                name = TILE_NAMES.get(t)
                if t == W:
                    # Animated water
                    frame = (self.anim_tick // 300) % 4
                    self.screen.blit(ANIMATED['water'][frame], (px_, py_))
                elif t == H:
                    # Draw house (combine grass + tree-like for now)
                    # Use a red-tinted rectangle
                    s = pygame.Surface((TILE, TILE))
                    s.fill(C.r0)
                    pygame.draw.rect(s, C.r1, (0,0,TILE,8))
                    pygame.draw.rect(s, C.b0, (0,8,TILE,TILE-8))
                    self.screen.blit(s, (px_, py_))
                elif name and name in SPRITES:
                    self.screen.blit(SPRITES[name], (px_, py_))
                else:
                    # Fallback
                    pygame.draw.rect(self.screen, (60,40,80), (px_, py_, TILE, TILE))

        # Draw NPCs
        for npc_id, nx, ny in scene.npcs:
            vx = nx - self.cam_x
            vy = ny - self.cam_y
            if 0 <= vx < VIEW_W and 0 <= vy < VIEW_H:
                frame = (self.anim_tick // 500) % 2
                sprite = ANIMATED[f'npc_{npc_id}']['down'][frame]
                self.screen.blit(sprite, (vx * TILE, vy * TILE))
                # Heart above if relationship > 0
                if self.state.npc_hearts[npc_id] > 0:
                    heart_count = self.state.npc_hearts[npc_id] // 2
                    for i in range(min(heart_count, 5)):
                        pygame.draw.rect(self.screen, C.ui_red,
                                       (vx * TILE + 2 + i*5, vy * TILE - 6, 3, 3))

        # Draw player
        pvx = self.state.player_x - self.cam_x
        pvy = self.state.player_y - self.cam_y
        if 0 <= pvx < VIEW_W and 0 <= pvy < VIEW_H:
            frame = self.walk_frame if self.moving else 0
            player_sprite = ANIMATED['player'][self.state.facing][frame]
            self.screen.blit(player_sprite, (pvx * TILE, pvy * TILE))
            # Facing indicator
            fx, fy = self.get_facing_tile()
            fvx = fx - self.cam_x
            fvy = fy - self.cam_y
            if 0 <= fvx < VIEW_W and 0 <= fvy < VIEW_H:
                pygame.draw.rect(self.screen, C.ui_gold,
                               (fvx * TILE + 2, fvy * TILE + 2, TILE-4, TILE-4), 1)

        # Weather overlay
        if self.state.weather == 'Hujan' and not indoor:
            for i in range(50):
                rx = (i * 37 + int(self.anim_tick * 0.3)) % SCREEN_W
                ry = (i * 19 + int(self.anim_tick * 0.4)) % (VIEW_H * TILE)
                pygame.draw.line(self.screen, (120,180,255,128),
                               (rx, ry), (rx, ry+6))

        # Night overlay
        if self.state.time_minutes >= 19*60 and not indoor:
            darkness = min(100, int((self.state.time_minutes - 19*60) * 0.3))
            dark = pygame.Surface((SCREEN_W, VIEW_H * TILE))
            dark.set_alpha(darkness)
            dark.fill((0, 0, 30))
            self.screen.blit(dark, (0, 0))

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
        energy_txt = self.font_small.render(f"⚡ {self.state.energy}/{self.state.max_energy}", True, C.ui_green)
        gold_txt = self.font_small.render(f"💰 {self.state.gold}G", True, C.ui_gold)
        weather_txt = self.font_small.render(f"🌤 {self.state.weather}", True, (130,200,255))
        self.screen.blit(energy_txt, (10, hud_y + 22))
        self.screen.blit(gold_txt, (130, hud_y + 22))
        self.screen.blit(weather_txt, (230, hud_y + 22))

        # Location
        scene_name = SCENES[self.state.scene_name].display
        loc_txt = self.font_small.render(f"📍 {scene_name}", True, (200,180,255))
        self.screen.blit(loc_txt, (350, hud_y + 22))

        # Tool bar
        for i in range(6):
            x = 10 + i * 45
            y = hud_y + 42
            selected = (i == self.state.tool_index)
            bg = C.ui_bg2 if selected else (30, 20, 45)
            pygame.draw.rect(self.screen, bg, (x, y, 40, 30))
            color = C.ui_gold if selected else C.ui_border
            pygame.draw.rect(self.screen, color, (x, y, 40, 30), 2)
            icon = self.font.render(f"{i+1}", True, C.ui_gold)
            self.screen.blit(icon, (x + 4, y + 4))
            name = self.font_small.render(TOOLS[i][:3], True, C.ui_text)
            self.screen.blit(name, (x + 10, y + 18))

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
        box_y = VIEW_H * TILE - 90
        pygame.draw.rect(self.screen, (10, 5, 25), (0, box_y, SCREEN_W, 90))
        pygame.draw.rect(self.screen, C.ui_border, (0, box_y, SCREEN_W, 90), 2)

        # Speaker
        if self.dialog_speaker:
            speaker = self.font.render(f"▶ {self.dialog_speaker}", True, C.ui_gold)
            self.screen.blit(speaker, (12, box_y + 8))

        # Typewriter text
        current = self.dialog_lines[self.dialog_index]
        visible = current[:self.typewriter_progress]
        # Word wrap
        words = visible.split(' ')
        line = ''
        y_off = 30
        for word in words:
            test = line + word + ' '
            if self.font.size(test)[0] > SCREEN_W - 20:
                t = self.font.render(line, True, C.ui_text)
                self.screen.blit(t, (12, box_y + y_off))
                y_off += 22
                line = word + ' '
            else:
                line = test
        if line:
            t = self.font.render(line, True, C.ui_text)
            self.screen.blit(t, (12, box_y + y_off))

        # Hint
        if self.typewriter_progress >= len(current):
            hint = self.font_small.render(
                f"▶ SPACE lanjut  ({self.dialog_index+1}/{len(self.dialog_lines)})",
                True, (130, 110, 160))
            self.screen.blit(hint, (SCREEN_W - 180, box_y + 72))

    def render_menu(self):
        # Modal menu
        bw = 400
        bh = min(400, 80 + len(self.menu_items) * 32)
        bx = SCREEN_W // 2 - bw // 2
        by = SCREEN_H // 2 - bh // 2

        # Dim background
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))

        pygame.draw.rect(self.screen, (15, 8, 30), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, bw, bh), 3)

        # Title
        title = self.font_big.render(self.menu_title, True, C.ui_gold)
        self.screen.blit(title, (bx + 20, by + 15))

        # Items
        for i, (label, _) in enumerate(self.menu_items):
            y = by + 60 + i * 32
            if i == self.menu_selected:
                pygame.draw.rect(self.screen, (60, 30, 100), (bx + 10, y - 4, bw - 20, 28))
                arrow = self.font.render("▶", True, C.ui_gold)
                self.screen.blit(arrow, (bx + 15, y))
            color = C.ui_gold if i == self.menu_selected else C.ui_text
            t = self.font.render(label, True, color)
            self.screen.blit(t, (bx + 35, y))

    def render_notification(self):
        # Toast at top
        text = self.font.render(self.notif_text, True, C.ui_gold)
        tw = text.get_width() + 20
        tx = SCREEN_W // 2 - tw // 2
        ty = 10
        pygame.draw.rect(self.screen, (10, 5, 25), (tx, ty, tw, 30))
        pygame.draw.rect(self.screen, C.ui_border, (tx, ty, tw, 30), 2)
        self.screen.blit(text, (tx + 10, ty + 6))


# ══════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════
if __name__ == "__main__":
    game = Game()
    game.run()
