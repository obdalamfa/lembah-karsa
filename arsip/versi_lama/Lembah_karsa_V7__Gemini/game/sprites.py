"""
sprites.py — Procedural HD-2D Pixel Art Generator
"""
import pygame
import random
import math
from .config import TILE

SPRITES = {}
ANIMATED = {}

def make_surface(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)

def make_grass():
    s = make_surface(TILE, TILE)
    s.fill((85, 140, 70))
    for _ in range(15):
        x, y = random.randint(0, TILE-2), random.randint(0, TILE-2)
        c = random.choice([(100, 160, 80), (70, 120, 60)])
        pygame.draw.line(s, c, (x, y+2), (x+1, y)) # Helai rumput
    return s

def make_dirt():
    s = make_surface(TILE, TILE)
    s.fill((120, 85, 60))
    for _ in range(20):
        x, y = random.randint(0, TILE-1), random.randint(0, TILE-1)
        pygame.draw.rect(s, (100, 70, 50), (x, y, 2, 1)) # Tekstur kerikil/tanah
    return s

def make_tree():
    s = make_surface(TILE, int(TILE * 1.5))
    # Batang Kayu bergradasi
    pygame.draw.rect(s, (60, 40, 25), (12, 20, 8, 28))
    pygame.draw.rect(s, (80, 55, 35), (12, 20, 3, 28)) # Highlight cahaya
    # Daun rimbun (Layered Circles)
    pygame.draw.circle(s, (30, 80, 30), (16, 20), 16)
    pygame.draw.circle(s, (40, 100, 40), (16, 14), 14)
    pygame.draw.circle(s, (55, 130, 55), (16, 8), 10)
    return s

def make_house():
    s = make_surface(TILE*2, TILE*2)
    # Tembok bata krem
    pygame.draw.rect(s, (220, 200, 180), (4, 24, 56, 40))
    pygame.draw.rect(s, (190, 170, 150), (4, 24, 56, 40), 2)
    # Pintu kayu
    pygame.draw.rect(s, (100, 60, 40), (24, 40, 16, 24))
    pygame.draw.circle(s, (200, 180, 50), (36, 52), 2) # Gagang pintu
    # Jendela
    pygame.draw.rect(s, (100, 150, 200), (8, 32, 12, 12))
    pygame.draw.rect(s, (100, 150, 200), (44, 32, 12, 12))
    # Atap genteng merah
    pygame.draw.polygon(s, (160, 50, 50), [(2, 24), (32, 0), (62, 24)])
    pygame.draw.polygon(s, (130, 40, 40), [(2, 24), (32, 0), (62, 24)], 3)
    return s

def make_shadow():
    s = make_surface(TILE, TILE)
    pygame.draw.ellipse(s, (0, 0, 0, 90), (4, TILE - 10, 24, 8))
    return s

def make_cloud():
    s = make_surface(250, 150)
    pygame.draw.ellipse(s, (255, 255, 255, 40), (0, 40, 180, 80))
    pygame.draw.ellipse(s, (255, 255, 255, 40), (60, 0, 150, 100))
    pygame.draw.ellipse(s, (255, 255, 255, 40), (100, 50, 150, 90))
    return s

def make_char(hair_c, shirt_c, pants_c):
    s = make_surface(TILE, TILE)
    # Kaki/Celana
    pygame.draw.rect(s, pants_c, (10, 22, 12, 10))
    # Baju
    pygame.draw.rect(s, shirt_c, (8, 12, 16, 12))
    pygame.draw.rect(s, (max(0, shirt_c[0]-30), max(0, shirt_c[1]-30), max(0, shirt_c[2]-30)), (8, 12, 16, 12), 2)
    # Kepala (Kulit)
    pygame.draw.rect(s, (255, 220, 190), (10, 4, 12, 10))
    # Rambut/Topi
    pygame.draw.rect(s, hair_c, (8, 2, 16, 6))
    # Mata
    pygame.draw.rect(s, (50, 50, 50), (12, 8, 2, 2))
    pygame.draw.rect(s, (50, 50, 50), (18, 8, 2, 2))
    return s

def init_sprites():
    SPRITES['grass'] = make_grass()
    SPRITES['dirt'] = make_dirt()
    
    # Path/Jalan (Krem bertekstur)
    path = make_surface(TILE, TILE)
    path.fill((180, 160, 130))
    pygame.draw.rect(path, (150, 130, 100), (0,0,TILE,TILE), 2)
    SPRITES['path'] = path

    # Air bergradasi
    w_surf = make_surface(TILE, TILE)
    w_surf.fill((60, 140, 210))
    pygame.draw.line(w_surf, (100, 180, 240), (4, 4), (20, 4), 2)
    SPRITES['water'] = w_surf
    ANIMATED['water'] = [w_surf] * 4 # Placeholder animasi air

    SPRITES['tree'] = make_tree()
    SPRITES['dead_tree'] = make_tree() # Bisa diubah nanti warnanya
    SPRITES['house'] = make_house()
    SPRITES['shadow'] = make_shadow()
    SPRITES['cloud'] = make_cloud()

    # Warna fallback untuk objek mati
    dummy = make_surface(TILE, TILE)
    dummy.fill((100, 100, 100))
    pygame.draw.rect(dummy, (50, 50, 50), (0,0,TILE,TILE), 2)
    for name in ['tilled_dry', 'tilled_wet', 'mailbox', 'door', 'fence', 'gate', 
                 'bed', 'stove', 'table', 'bookshelf', 'mirror', 'fireplace', 
                 'clock', 'plant_pot', 'chest', 'counter', 'shelf_store', 'grave', 
                 'lantern', 'cave_wall', 'cave_floor', 'pen_post', 'straw']:
        if name not in SPRITES:
            SPRITES[name] = dummy

    # Karakter (Animasi 1 frame dulu untuk kestabilan)
    player_surf = make_char((40, 30, 20), (50, 150, 200), (40, 50, 80))
    ANIMATED['player'] = {'up':[player_surf]*3, 'down':[player_surf]*3, 'left':[player_surf]*3, 'right':[player_surf]*3}
    
    # NPC Unik dengan warna berbeda
    ANIMATED['npc_arya'] = {'down': [make_char((50,50,50), (100, 180, 100), (50,40,30))]}
    ANIMATED['npc_sari'] = {'down': [make_char((150,80,80), (220, 100, 150), (200,200,200))]}
    ANIMATED['npc_raka'] = {'down': [make_char((200,200,200), (255, 255, 255), (100,100,150))]}
    ANIMATED['npc_maya'] = {'down': [make_char((255,150,50), (200, 200, 50), (80,80,80))]}
    ANIMATED['npc_budi'] = {'down': [make_char((0,0,0), (150, 80, 50), (50,50,50))]}
    
    # Makhluk
    ANIMATED['npc_sapi'] = {'down': [make_char((255,255,255), (255, 255, 255), (50,50,50))]}
    ANIMATED['npc_ayam'] = {'down': [make_char((255,0,0), (255, 200, 0), (255,150,0))]}
    ANIMATED['npc_tuyul'] = {'down': [make_char((200,255,200), (200, 255, 200), (255,255,255))]}
    ANIMATED['npc_jin'] = {'down': [make_char((100,0,200), (150, 50, 255), (50,0,100))]}
    ANIMATED['npc_naga'] = {'down': [make_char((50,200,100), (50, 200, 100), (20,100,50))]}
