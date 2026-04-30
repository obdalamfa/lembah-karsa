"""
sprites.py — Asset Loader & Procedural Fallback.
Membaca file .png dari folder assets/. Jika tidak ada, pakai kotak warna.
"""
import pygame
import os
import math
import random
from .config import TILE

SPRITES = {}
ANIMATED = {}

# ══════════════════════════════════════════════════════
#  SMART ASSET LOADER
# ══════════════════════════════════════════════════════
def load_img(path, w=TILE, h=TILE, fallback_color=(255, 0, 255)):
    """Mencari file PNG. Jika gagal, buat kotak warna sebagai pengganti."""
    if os.path.exists(path):
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (w, h))
    
    # Fallback jika gambar belum ada
    s = pygame.Surface((w, h))
    s.fill(fallback_color)
    pygame.draw.rect(s, (0,0,0), (0,0,w,h), 1) # Beri garis tepi agar jelas
    return s

def load_char_anim(char_name, fallback_color):
    """Load animasi karakter 4 arah (up, down, left, right). Masing-masing 3 frame."""
    anim = {}
    base_path = f"assets/chars/{char_name}"
    
    for d in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(3):
            # Contoh nama file yang dicari: assets/chars/player/down_0.png
            file_path = f"{base_path}/{d}_{f}.png"
            if os.path.exists(file_path):
                img = pygame.image.load(file_path).convert_alpha()
                # Proporsi Octopath (karakter lebih tinggi dari ubin)
                frames.append(pygame.transform.scale(img, (TILE, int(TILE * 1.5)))) 
            else:
                # Fallback jika belum ada gambar
                s = pygame.Surface((TILE, int(TILE * 1.5)))
                s.fill(fallback_color)
                # Tandai bagian depan (muka) dengan warna gelap
                if d == 'down': pygame.draw.rect(s, (50,50,50), (10, 5, 12, 6))
                frames.append(s)
        anim[d] = frames
    return anim

# ══════════════════════════════════════════════════════
#  SPECIAL PROCEDURAL EFFECTS (Shadows & Clouds)
# ══════════════════════════════════════════════════════
def make_shadow():
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, 100), (4, TILE - 10, 24, 8))
    return s

def make_cloud():
    s = pygame.Surface((300, 200), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (255, 255, 255, 30), (0, 50, 200, 100))
    pygame.draw.ellipse(s, (255, 255, 255, 30), (80, 0, 180, 120))
    return s

# ══════════════════════════════════════════════════════
#  INITIALIZATION
# ══════════════════════════════════════════════════════
def init_sprites():
    # 1. Load Lingkungan / Tiles
    SPRITES['grass'] = load_img("assets/tiles/grass.png", TILE, TILE, (85, 140, 70))
    SPRITES['dirt']  = load_img("assets/tiles/dirt.png", TILE, TILE, (120, 85, 60))
    SPRITES['path']  = load_img("assets/tiles/path.png", TILE, TILE, (180, 160, 130))
    
    # Animasi Air (Baca 4 frame: water_0.png sampai water_3.png)
    w_frames = []
    for i in range(4):
        p = f"assets/tiles/water_{i}.png"
        if os.path.exists(p):
            w_frames.append(pygame.transform.scale(pygame.image.load(p).convert_alpha(), (TILE, TILE)))
        else:
            s = pygame.Surface((TILE, TILE)); s.fill((60, 140, 210))
            w_frames.append(s)
    ANIMATED['water'] = w_frames

    # Lahan Tani
    SPRITES['tilled_dry'] = load_img("assets/tiles/tilled_dry.png", TILE, TILE, (100, 70, 45))
    SPRITES['tilled_wet'] = load_img("assets/tiles/tilled_wet.png", TILE, TILE, (70, 45, 30))

    # 2. Load Objek / Bangunan
    SPRITES['tree'] = load_img("assets/objects/tree.png", TILE * 2, TILE * 3, (40, 100, 40))
    SPRITES['house'] = load_img("assets/objects/house.png", TILE * 3, TILE * 3, (180, 150, 120))
    
    # Objek yang belum punya gambar akan pakai warna fallback ini
    for name in ['mailbox', 'door', 'fence', 'gate', 'bed', 'stove', 'table', 
                 'bookshelf', 'mirror', 'fireplace', 'clock', 'plant_pot', 
                 'chest', 'counter', 'shelf_store', 'grave', 'lantern', 'dead_tree', 
                 'cave_wall', 'cave_floor', 'pen_post', 'straw']:
        SPRITES[name] = load_img(f"assets/objects/{name}.png", TILE, TILE, (150, 150, 150))

    # Efek Khusus (Tidak perlu PNG, tetap pakai kode karena transparan)
    SPRITES['shadow'] = make_shadow()
    SPRITES['cloud'] = make_cloud()

    # 3. Load Karakter & NPC
    # Pastikan folder ada, misal: assets/chars/player/down_0.png
    ANIMATED['player'] = load_char_anim('player', (50, 150, 200))
    ANIMATED['npc_arya'] = load_char_anim('npc_arya', (100, 180, 100))
    ANIMATED['npc_sari'] = load_char_anim('npc_sari', (220, 100, 150))
    ANIMATED['npc_raka'] = load_char_anim('npc_raka', (200, 200, 200))
    ANIMATED['npc_maya'] = load_char_anim('npc_maya', (255, 150, 50))
    ANIMATED['npc_budi'] = load_char_anim('npc_budi', (150, 80, 50))
    
    # Makhluk
    ANIMATED['npc_sapi'] = load_char_anim('sapi', (255, 255, 255))
    ANIMATED['npc_ayam'] = load_char_anim('ayam', (255, 200, 0))
    ANIMATED['npc_tuyul'] = load_char_anim('tuyul', (200, 255, 200))
    ANIMATED['npc_jin'] = load_char_anim('jin', (150, 50, 255))
    ANIMATED['npc_naga'] = load_char_anim('naga', (50, 200, 100))

    # Crops (Tanaman)
    SPRITES['crops'] = {}
    for c_name in ['lobak', 'wortel', 'stroberi', 'jagung', 'tomat']:
        SPRITES['crops'][c_name] = []
        for stage in range(4): # 4 fase tumbuh
            SPRITES['crops'][c_name].append(load_img(f"assets/objects/{c_name}_{stage}.png", TILE, TILE, (0, 200, 0)))
