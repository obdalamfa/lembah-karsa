import pygame
import os

pygame.init()
TILE = 32
SCALE = 2 # Menggambar di grid 16x16 lalu diperbesar ke 32x32

folders = [
    "assets/tiles", "assets/objects",
    "assets/chars/player", "assets/chars/arya",
    "assets/chars/sapi", "assets/chars/tuyul",
    "assets/chars/naga", "assets/chars/running_mushroom"
]
for f in folders: os.makedirs(f, exist_ok=True)

# Palet Warna
PALETTE = {
    'G': (85, 140, 70),  'g': (70, 115, 55),  # Grass
    'D': (120, 85, 60),  'd': (100, 70, 50),  # Dirt
    'W': (60, 140, 210), 'w': (100, 180, 240),# Water
    'T': (80, 50, 30),   't': (60, 40, 25),   # Wood
    'L': (40, 100, 40),  'l': (30, 80, 30),   # Leaves
    'S': (240, 200, 180),                     # Skin
    'R': (200, 50, 50),  'r': (150, 30, 30),  # Red Shirt/Mushroom
    'B': (50, 50, 150),                       # Blue Pants
    'H': (50, 30, 20),                        # Hair
    'C': (180, 110, 70), 'c': (255, 255, 255),# Cow Brown / White Spots
    'Y': (100, 160, 80), 'y': (60, 100, 50),  # Tuyul Green
    'N': (50, 200, 100), 'n': (20, 120, 50),  # Naga Emerald
    'X': (0, 0, 0),                           # Black/Eyes
    'M': (220, 220, 220),                     # Gray/Horns
    '.': (0, 0, 0, 0)                         # Transparent
}

def draw_matrix(matrix, width=16, height=16):
    surf = pygame.Surface((width * SCALE, height * SCALE), pygame.SRCALPHA)
    for y, row in enumerate(matrix):
        for x, char in enumerate(row):
            if char in PALETTE and char != '.':
                pygame.draw.rect(surf, PALETTE[char], (x*SCALE, y*SCALE, SCALE, SCALE))
    return surf

def save_img(surf, path):
    pygame.image.save(surf, path)
    print(f"✅ Dibuat: {path}")

# =========================================================================
#  1. BLUEPRINT MATRIKS (16x16)
# =========================================================================

# Naga (Dragon) - Epik dan imut
blueprint_naga = [
    "......NNNN......",
    ".....NMXXMN.....",
    "....NNNNNNNN....",
    "...NNnNNNNnNN...",
    "..N..NNNNNN..N..",
    ".N...NNNNNN...N.",
    "N....NNNNNN....N",
    "N....NNNNNN....N",
    ".....nNNNNn.....",
    ".....nNNNNn.....",
    "......nnnn......",
    "......nnnn......",
    ".....N....N.....",
    "....NN....NN....",
    "....NN....NN....",
    "................"
]

# Tuyul - Botak, hijau, kecil
blueprint_tuyul = [
    "................",
    "......YYYY......",
    ".....YYYYYY.....",
    ".....YXXYYX.....",
    ".....YYYYYY.....",
    "......yYYy......",
    "......YYYY......",
    ".....YYYYYY.....",
    "....YYyYYyYY....",
    "...YY.YYYY.YY...",
    "...Y..YYYY..Y...",
    "......YYYY......",
    "......yyyy......",
    "......Y..Y......",
    ".....YY..YY.....",
    "................"
]

# Jamur Lari (Running Mushroom)
blueprint_jamur = [
    "................",
    "......RRRR......",
    "....RRcRRRRR....",
    "...RRRRRRcRRR...",
    "..RRRcRRRRRRRR..",
    "..RRRRRRRcRRRR..",
    "...RRcRRRRRRR...",
    "....RRRRcRRR....",
    "......SSSS......",
    ".....SXSSXS.....",
    "......SSSS......",
    ".......SS.......",
    "......S..S......",
    ".....SS..SS.....",
    "....SS....SS....",
    "................"
]

# Sapi (Cow) - Cokelat bercak putih
blueprint_sapi = [
    "................",
    "................",
    "....MM....MM....",
    "...CCCC..CCCC...",
    "...CXXC..CXXC...",
    "....CCCCCCCC....",
    "..CCCCCCCCCCCC..",
    ".CCcCCCCCCCCcCC.",
    ".CCCCCCCCCCCCCC.",
    ".CCcCCCCCCCCcCC.",
    ".CCCCCCCCCCCCCC.",
    "..CC..CC..CC..CC",
    "..cc..cc..cc..cc",
    "..CC..CC..CC..CC",
    "..CC..CC..CC..CC",
    "................"
]

# Player / NPC Base
blueprint_human = [
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

# Rumput, Tanah & Pohon
blueprint_grass = [
    "GGGGGGgGGGGGGGGG",
    "GGgGGGGGGGGGGgGG",
    "GGGGgGGGGGGGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGGGGGgGGGGGGG",
    "GgGGGGGGGGGGGGGG",
    "GGGGGGGGGGGGgGGG",
    "GGGGgGGGGGGGGGGG",
    "GGGGGGGGGGgGGGGG",
    "GGGGGGgGGGGGGGGG",
    "GGGGGGGGGGGGGGgG",
    "gGGGGGGGGgGGGGGG",
    "GGGGGGGGGGGGGGGG",
    "GGGGgGGGGGGGGGGG",
    "GGGGGGGGGGgGGGGG",
    "GGGGGGGGGGGGGGGG"
]

blueprint_tree = [
    ".......ll.......",
    ".....llllll.....",
    "...llllllllll...",
    "..llllLlllllLl..",
    ".llllllllllllll.",
    ".llllLllllLllll.",
    ".llllllllllllll.",
    "..llllLlllllLl..",
    "...llllllllll...",
    ".......TT.......",
    ".......tT.......",
    ".......TT.......",
    ".......tT.......",
    ".......TT.......",
    "......tTTt......",
    "................"
]

# =========================================================================
#  2. GENERATOR ASET
# =========================================================================
print("🛠️ Membangun Tile & Objek Matriks...")
save_img(draw_matrix(blueprint_grass), "assets/tiles/grass.png")
save_img(draw_matrix(blueprint_tree), "assets/objects/tree.png")

# Bikin variasi air animasi
for i in range(4):
    surf = pygame.Surface((32, 32))
    surf.fill(PALETTE['W'])
    pygame.draw.line(surf, PALETTE['w'], (0, (i*4)%32), (32, (i*4)%32), 4)
    save_img(surf, f"assets/tiles/water_{i}.png")

print("🛠️ Membangun Karakter Animasi (12-Frame)...")

def generate_character(name, blueprint, is_animal=False):
    base_surf = draw_matrix(blueprint)
    
    # 4 Arah (Atas, Bawah, Kiri, Kanan)
    for d in ['up', 'down', 'left', 'right']:
        for f in range(3):
            # Frame dasar
            frame = base_surf.copy()
            
            # Modifikasi tampilan berdasarkan arah (Sederhana)
            if d == 'up': 
                # Tutup mata pakai warna rambut/kulit
                pygame.draw.rect(frame, PALETTE['H'] if not is_animal else PALETTE['C'], (8, 4, 16, 12))
            elif d == 'left':
                frame = pygame.transform.flip(frame, True, False)
            
            # Simulasi Animasi Berjalan (mengangkat gambar sedikit ke atas)
            anim_surf = pygame.Surface((32, 48), pygame.SRCALPHA)
            y_offset = -4 if f != 0 else 0 
            anim_surf.blit(frame, (0, 16 + y_offset))
            
            # Tambah bayangan kaki
            pygame.draw.ellipse(anim_surf, (0,0,0,80), (8, 40, 16, 6))
            
            save_img(anim_surf, f"assets/chars/{name}/{d}_{f}.png")

generate_character('player', blueprint_human)
generate_character('arya', blueprint_human) # Bisa diubah warnanya nanti
generate_character('sapi', blueprint_sapi, is_animal=True)
generate_character('tuyul', blueprint_tuyul)
generate_character('naga', blueprint_naga, is_animal=True)
generate_character('running_mushroom', blueprint_jamur, is_animal=True)

print("\n🚀 SELESAI! Seni Piksel V2 berhasil dibuat. Silakan jalankan `python main.py`!")
pygame.quit()
