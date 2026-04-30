import pygame
import os
import random

pygame.init()
TILE = 32

folders = [
    "assets/tiles", "assets/objects",
    "assets/chars/player", "assets/chars/npc_arya", "assets/chars/npc_budi",
    "assets/chars/npc_sapi", "assets/chars/npc_ayam", "assets/chars/npc_tuyul",
    "assets/chars/npc_naga", "assets/chars/running_mushroom"
]
for f in folders: os.makedirs(f, exist_ok=True)

# =========================================================================
# PALET WARNA LENGKAP
# =========================================================================
P = {
    '.': (0,0,0,0),      'X': (0,0,0),        'W': (255,255,255),
    'S': (255,220,190),  's': (220,180,150),  # Skin
    'H': (70,40,30),     'h': (50,30,20),     # Hair/Brown
    'R': (200,50,50),    'r': (150,30,30),    # Red
    'B': (50,100,200),   'b': (30,60,150),    # Blue
    'G': (80,200,80),    'g': (40,150,40),    # Green (Tuyul/Dragon)
    'D': (40,100,40),    'd': (20,60,20),     # Dark Green (Dragon Scales)
    'Y': (250,200,50),   'y': (200,150,30),   # Yellow/Gold
    'C': (180,120,80),   'c': (140,90,60),    # Cow/Wood
    'M': (150,150,150),  'm': (100,100,100),  # Grey/Stone
}

# =========================================================================
# BLUEPRINT MATRIKS (Seni Piksel via Teks)
# =========================================================================

# Player (16x16) - Versi yang kamu suka!
bp_player = [
    "......HHHH......",
    ".....HHHHHH.....",
    ".....SXXSSX.....",
    ".....SSSSSS.....",
    "......SSSS......",
    ".....RRRRRR.....",
    "....RRrRRrRR....",
    "...RR.RRRR.RR...",
    "...R..RRRR..R...",
    "......RRRR......",
    "......BBBB......",
    "......BBBB......",
    "......B..B......",
    "......B..B......",
    ".....BB..BB.....",
    "................"
]

# Jamur Lari (16x16)
bp_jamur = [
    ".......rr.......",
    ".....RRRRRR.....",
    "....RWRRRRWR....",
    "...RRRRRRRRRR...",
    "..RRWRRRRRRWRR..",
    "..RRRRRWRRRRRR..",
    "...RRRRRRRRRR...",
    "....rrrrrrrr....",
    "......SSSS......",
    ".....SXXSXXS....",
    "......SSSS......",
    ".......SS.......",
    "......S..S......",
    ".....SS..SS.....",
    "................",
    "................"
]

# Tuyul (16x16)
bp_tuyul = [
    "......GGGG......",
    ".....GGGGGG.....",
    "....GGXXGGXX....",
    "....GGGGGGGG....",
    ".....GgGGgG.....",
    "......GGGG......",
    ".....GGGGGG.....",
    "....GgGGGGgG....",
    "...GG.GGGG.GG...",
    "...G..GGGG..G...",
    "......GGGG......",
    "......XXXX......",
    "......G..G......",
    ".....GG..GG.....",
    "................",
    "................"
]

# Naga Epik (32x32) - MATRIKS RAKSASA!
bp_naga = [
    "................................",
    "................................",
    "..........DDDDDD................",
    ".........DGGGGGGD...............",
    "........DGGGGGGGGD..............",
    ".......DGXXGGGGXXGD.............",
    ".......DGGGGGGGGGGD.............",
    "........DGGgGGgGGD..............",
    "........DGGGGGGGGD......DD......",
    ".........DDGGGGDD......DGGD.....",
    "........DGGGGGGGGD....DGGGGD....",
    ".......DGGGGGGGGGGD...DGGGGD....",
    "......DGGGDGGGGGDGGD.DGGGGGGD...",
    ".....DGGGD.DGGGD.DGGDDGGGGGGD...",
    "....DGGGD..DGGGD..DGGGGGGGGGD...",
    "...DGGGD...DGGGD...DGGGGGGGGD...",
    "..DGGGD....DGGGD....DGGGGGGGD...",
    "..DGGD.....DGGGD.....DDGGGDD....",
    "...DD......DGGGD.......DDD......",
    "...........DGGGD................",
    "..........DGGGGGD...............",
    ".........DGGGGGGGD..............",
    ".........DGGGGGGGD..............",
    "........DGGGGGGGGGD.............",
    "........DGGGGGGGGGD.............",
    ".......DGGGD...DGGGD............",
    ".......DGGD.....DGGD............",
    "......DGGGD.....DGGGD...........",
    "......DDDGD.....DDDGD...........",
    "................................",
    "................................",
    "................................"
]

def draw_matrix(blueprint, scale):
    width = len(blueprint[0])
    height = len(blueprint)
    surf = pygame.Surface((width * scale, height * scale), pygame.SRCALPHA)
    for y, row in enumerate(blueprint):
        for x, char in enumerate(row):
            if char in P and char != '.':
                pygame.draw.rect(surf, P[char], (x * scale, y * scale, scale, scale))
    return surf

def save_img(surf, path):
    pygame.image.save(surf, path)
    print(f"✅ Created: {path}")

# =========================================================================
# 1. GENERATE LINGKUNGAN (Procedural Noise)
# =========================================================================
print("🌱 Menumbuhkan Alam Lembah Karsa...")

def make_noisy_tile(base_color, noise_colors, is_path=False):
    s = pygame.Surface((TILE, TILE))
    s.fill(base_color)
    # Bikin bintik-bintik alami
    for _ in range(40):
        x, y = random.randint(0, 31), random.randint(0, 31)
        c = random.choice(noise_colors)
        pygame.draw.rect(s, c, (x, y, random.randint(1,2), random.randint(1,2)))
    if is_path:
        pygame.draw.rect(s, (120,100,80), (0,0,32,32), 2) # Garis tepi jalan
    return s

save_img(make_noisy_tile((85,140,70), [(70,115,55), (100,160,80)]), "assets/tiles/grass.png")
save_img(make_noisy_tile((120,85,60), [(100,70,50), (90,60,40)]), "assets/tiles/dirt.png")
save_img(make_noisy_tile((160,140,110), [(140,120,90), (120,100,80)], True), "assets/tiles/path.png")

# Animasi Air 
for i in range(4):
    w = pygame.Surface((TILE, TILE))
    w.fill((60,140,210))
    offset = i * 4
    for y in range(0, 32, 8):
        pygame.draw.line(w, (100,180,240), ((offset+y)%32, y+4), (((offset+y)%32)+8, y+4), 2)
    save_img(w, f"assets/tiles/water_{i}.png")

# =========================================================================
# 2. GENERATE KARAKTER 12-FRAME
# =========================================================================
print("🧙‍♂️ Menempa Karakter dan Monster...")

def build_chars(name, blueprint, matrix_size=16, scale=2, is_huge=False):
    base_art = draw_matrix(blueprint, scale)
    w_out = matrix_size * scale
    h_out = matrix_size * scale
    
    for d in ['up', 'down', 'left', 'right']:
        for f in range(3):
            # Kanvas akhir (Diberi ruang untuk animasi jalan)
            frame = pygame.Surface((w_out, h_out + (4 if not is_huge else 8)), pygame.SRCALPHA)
            
            # Copy art dasar
            art = base_art.copy()
            if d == 'left': art = pygame.transform.flip(art, True, False)
            elif d == 'up' and not is_huge: 
                # Tutup muka kalau hadap belakang (sederhana)
                pygame.draw.rect(art, P['H'], (8*scale, 4*scale, 6*scale, 6*scale))

            # Animasi naik turun saat jalan (f = 1 atau 2)
            y_bounce = -scale if f != 0 else 0
            if is_huge: y_bounce = -scale*2 if f != 0 else 0
            
            frame.blit(art, (0, (4 if not is_huge else 8) + y_bounce))
            
            # Bayangan oval di bawah kaki biar menapak di tanah
            shadow_y = h_out + (2 if not is_huge else 4)
            shadow_w = w_out - (8 * scale)
            pygame.draw.ellipse(frame, (0,0,0,70), ((w_out-shadow_w)//2, shadow_y, shadow_w, scale*2))

            save_img(frame, f"assets/chars/{name}/{d}_{f}.png")

build_chars('player', bp_player)
build_chars('npc_arya', bp_player) # Pakai wujud player sementara
build_chars('running_mushroom', bp_jamur)
build_chars('npc_tuyul', bp_tuyul)

# Sang Naga Raksasa! Matriks 32x32 di-scale 3x (Jadinya 96x96 pixel / 3x3 Tile!)
build_chars('npc_naga', bp_naga, matrix_size=32, scale=3, is_huge=True)

# =========================================================================
# 3. INTERIOR RAPI & BENDA MATI
# =========================================================================
print("🏠 Mendekorasi Ulang Interior...")

def make_obj(c_base, c_detail, is_bed=False):
    s = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
    pygame.draw.rect(s, c_base, (2,2,28,28), border_radius=4)
    pygame.draw.rect(s, (0,0,0,100), (2,2,28,28), 2, border_radius=4)
    if is_bed:
        pygame.draw.rect(s, (255,255,255), (4,4,24,8), border_radius=2) # Bantal
        pygame.draw.rect(s, c_detail, (4,14,24,14), border_radius=2) # Selimut
    else:
        pygame.draw.rect(s, c_detail, (8,8,16,16), border_radius=2)
    return s

save_img(make_obj((120,80,50), (50,100,200), True), "assets/objects/bed.png")
save_img(make_obj((150,100,50), (200,180,50)), "assets/objects/chest.png")
save_img(make_obj((80,80,80), (200,100,50)), "assets/objects/stove.png")

# Pohon lebih bagus
tree = draw_matrix([
    "......GGGG......",
    "....GGGGGgGG....",
    "...GGgGGGGGGg...",
    "..GGGGGGgGGGGG..",
    ".GGgGGGGGGGGgGG.",
    ".GGGGgGGGGgGGGG.",
    "..GGGGGGGGGGGG..",
    "...GGgGGgGGGG...",
    "......cccc......",
    "......cccc......",
    "......cccc......",
    "......cccc......",
    ".....cccccc.....",
    "................",
    "................",
    "................"
], 4) # Scale 4 = 64x64 pixel (2x2 Tile)
save_img(tree, "assets/objects/tree.png")

print("🔥 EKSEKUSI SELESAI! Aset Ultimate berhasil dibuat. Langsung test `python main.py`!")
pygame.quit()
