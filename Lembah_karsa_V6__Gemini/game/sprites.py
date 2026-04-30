"""
sprites.py — Generator sprite pixel-art.
Semua sprite digenerate runtime via pygame.Surface agar ringan.
"""
import pygame
import math
import random
from .config import C, TILE, SPRITE

# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def make_surface(w=SPRITE, h=SPRITE, fill=None):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if fill: s.fill(fill)
    return s

def pp(s, x, y, c):
    """Set pixel dengan bounds check."""
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), c)

def rect(s, x1, y1, x2, y2, c):
    for y in range(y1, y2+1):
        for x in range(x1, x2+1): pp(s, x, y, c)

def hline(s, y, x1, x2, c):
    for x in range(x1, x2+1): pp(s, x, y, c)

def vline(s, x, y1, y2, c):
    for y in range(y1, y2+1): pp(s, x, y, c)

# ══════════════════════════════════════════════════════
#  TILE GENERATORS
# ══════════════════════════════════════════════════════
def make_grass():
    s = make_surface(fill=(85, 140, 70))
    for _ in range(8):
        pp(s, random.randint(0,15), random.randint(0,15), (100, 160, 80))
    return pygame.transform.scale(s, (TILE, TILE))

def make_dirt():
    s = make_surface(fill=(110, 80, 60))
    for _ in range(12):
        pp(s, random.randint(0,15), random.randint(0,15), (90, 65, 50))
    return pygame.transform.scale(s, (TILE, TILE))

def make_path():
    s = make_surface(fill=(160, 140, 110))
    rect(s, 0, 0, 15, 0, (140, 120, 90))
    rect(s, 0, 0, 0, 15, (140, 120, 90))
    return pygame.transform.scale(s, (TILE, TILE))

def make_tilled(wet=False):
    c = (70, 45, 30) if wet else (95, 65, 45)
    s = make_surface(fill=c)
    line_c = (50, 30, 20) if wet else (75, 50, 35)
    hline(s, 4, 2, 13, line_c)
    hline(s, 10, 2, 13, line_c)
    return pygame.transform.scale(s, (TILE, TILE))

def make_water(frame=0):
    c = (60, 120, 200)
    s = make_surface(fill=c)
    offset = frame * 4
    for i in range(2):
        hline(s, (4+i*8+offset)%16, 2, 13, (100, 150, 230))
    return pygame.transform.scale(s, (TILE, TILE))

def make_tree():
    s = make_surface(16, 24)
    # Batang
    rect(s, 6, 16, 9, 23, (80, 50, 30))
    # Daun
    rect(s, 2, 4, 13, 15, (40, 100, 40))
    rect(s, 4, 0, 11, 3, (50, 120, 50))
    return pygame.transform.scale(s, (TILE, TILE*1.5))

def make_house():
    s = make_surface(32, 32)
    rect(s, 2, 10, 29, 31, (180, 160, 140)) # Tembok
    rect(s, 0, 0, 31, 12, (120, 40, 40))    # Atap
    rect(s, 12, 20, 19, 31, (80, 50, 30))   # Pintu
    return pygame.transform.scale(s, (TILE*2, TILE*2))

# ══════════════════════════════════════════════════════
#  NEW EFFECTS (FIX KEYERROR: 'SHADOW')
# ══════════════════════════════════════════════════════
def make_shadow():
    """Bayangan berbentuk elips di bawah karakter/objek."""
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    # Elips transparan hitam
    pygame.draw.ellipse(s, (0, 0, 0, 90), (4, TILE - 10, 24, 8))
    return s

def make_cloud():
    """Bayangan awan transparan untuk efek Parallax."""
    # Ukuran besar untuk menutupi sebagian layar
    s = pygame.Surface((250, 150), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 30), (0, 40, 180, 80))
    pygame.draw.ellipse(s, (0, 0, 0, 30), (60, 0, 150, 100))
    pygame.draw.ellipse(s, (0, 0, 0, 30), (100, 50, 150, 90))
    return s

# ══════════════════════════════════════════════════════
#  CHARACTER GENERATORS
# ══════════════════════════════════════════════════════
def make_char(direction='down', frame=0, hair_c=(50,30,20), shirt_c=(200,50,50), pants_c=(50,50,150), blink=False):
    s = make_surface(16, 16)
    # Tubuh
    rect(s, 4, 8, 11, 14, shirt_c) # Baju
    rect(s, 5, 14, 10, 15, pants_c) # Celana/Kaki
    # Kepala
    rect(s, 4, 2, 11, 8, (240, 200, 180)) # Kulit
    rect(s, 4, 1, 11, 4, hair_c) # Rambut
    # Mata
    if not blink:
        if direction == 'down':
            pp(s, 6, 5, (20,20,80)); pp(s, 9, 5, (20,20,80))
        elif direction == 'right':
            pp(s, 10, 5, (20,20,80))
    return s

def build_char_anim(hair=(50,30,20), shirt=(200,50,50), pants=(50,50,150)):
    out = {}
    for d in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(3): # 0:idle, 1:walk1, 2:walk2
            real_d = 'right' if d == 'left' else d
            surf = make_char(real_d, f, hair, shirt, pants)
            scaled = pygame.transform.scale(surf, (TILE, TILE))
            if d == 'left': scaled = pygame.transform.flip(scaled, True, False)
            frames.append(scaled)
        out[d] = frames
    return out

# ══════════════════════════════════════════════════════
#  INITIALIZATION
# ══════════════════════════════════════════════════════
SPRITES = {}
ANIMATED = {}

def init_sprites():
    # Tiles
    SPRITES['grass'] = make_grass()
    SPRITES['dirt'] = make_dirt()
    SPRITES['path'] = make_path()
    SPRITES['tilled_dry'] = make_tilled(False)
    SPRITES['tilled_wet'] = make_tilled(True)
    SPRITES['tree'] = make_tree()
    SPRITES['dead_tree'] = make_tree() # Bisa dimodifikasi warnanya nanti
    SPRITES['house'] = make_house()
    
    # UI & Effects
    SPRITES['shadow'] = make_shadow()
    SPRITES['cloud'] = make_cloud()
    
    # Placeholder untuk item lainnya agar tidak KeyError
    dummy = make_surface(TILE, TILE, (200, 0, 200))
    for name in ['mailbox', 'door', 'fence', 'gate', 'bed', 'stove', 'table', 
                 'bookshelf', 'mirror', 'fireplace', 'clock', 'plant_pot', 
                 'chest', 'counter', 'shelf_store', 'grave', 'lantern',
                 'mandrake', 'running_mushroom', 'firefly', 'wild_herb', 'wild_berry']:
        SPRITES[name] = dummy

    # Animated
    ANIMATED['water'] = [make_water(0), make_water(1), make_water(0), make_water(1)]
    ANIMATED['player'] = build_char_anim()
    
    # NPC Anims (Sederhana, menggunakan warna berbeda)
    ANIMATED['npc_human'] = build_char_anim(shirt=(50, 150, 50))
    ANIMATED['npc_sapi'] = build_char_anim(shirt=(255, 255, 255), hair=(50, 50, 50))
    ANIMATED['npc_ayam'] = build_char_anim(shirt=(255, 200, 0))
    ANIMATED['npc_tuyul'] = build_char_anim(shirt=(100, 100, 100), hair=(0,0,0))
    ANIMATED['npc_jin'] = build_char_anim(shirt=(100, 50, 150), hair=(200, 200, 255))
    
    # Khusus untuk pendaftaran NPC ID unik
    ANIMATED['npc_arya'] = ANIMATED['npc_human']
    ANIMATED['npc_sari'] = build_char_anim(shirt=(200, 100, 150))
    ANIMATED['npc_raka'] = build_char_anim(shirt=(100, 100, 255))
    ANIMATED['npc_maya'] = build_char_anim(shirt=(255, 150, 50))
    ANIMATED['npc_budi'] = build_char_anim(shirt=(150, 100, 50))

    # Crop Sprites (Placeholder)
    SPRITES['crops'] = {
        'lobak': [dummy, dummy, dummy, dummy],
        'wortel': [dummy, dummy, dummy, dummy],
        'stroberi': [dummy, dummy, dummy, dummy],
        'jagung': [dummy, dummy, dummy, dummy],
        'tomat': [dummy, dummy, dummy, dummy],
    }
