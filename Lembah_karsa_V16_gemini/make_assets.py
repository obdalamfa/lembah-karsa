import pygame
import os
import random
import math

# Inisiasi Pygame dalam mode tersembunyi (hanya untuk merender gambar)
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

# =========================================================================
# 1. KAMUS WARNA SUPER LENGKAP
# =========================================================================
class C:
    # Alam & Lingkungan
    g1 = (85, 140, 70)       # Rumput utama
    g2 = (60, 100, 40)       # Rumput gelap/daun
    dirt = (120, 85, 60)     # Tanah
    water = (60, 140, 210)   # Air
    wood = (139, 69, 19)     # Kayu gelap
    wood_light = (160, 82, 45) # Kayu terang
    hay = (218, 165, 32)     # Jerami
    stone = (150, 150, 150)  # Batu
    tilled_dry = (100, 70, 45) # Tanah garapan kering
    tilled_wet = (70, 45, 30)  # Tanah garapan basah
    
    # Karakter & Hewan
    skin = (255, 220, 190)
    eye = (0, 0, 0)
    white = (255, 255, 255)
    black = (0, 0, 0)
    pink = (255, 182, 193)
    red = (220, 50, 50)
    blue = (50, 100, 200)

# =========================================================================
# 2. FUNGSI BANTUAN (SAVE & MAKER)
# =========================================================================
def _save(surface, path):
    """Fungsi ajaib untuk memastikan folder ada dan menyimpan PNG"""
    full_path = os.path.join("assets", path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    pygame.image.save(surface, full_path)
    print(f"✅ Tersimpan: {full_path}")

# =========================================================================
# 3. MESIN PELUKIS LINGKUNGAN (TILES & OBJEK)
# =========================================================================
def make_grass_tile():
    surf = pygame.Surface((32, 32))
    surf.fill(C.g1)
    # Tambah detail titik rumput acak
    for _ in range(5):
        x, y = random.randint(0, 30), random.randint(0, 30)
        pygame.draw.rect(surf, C.g2, (x, y, 2, 4))
    return surf

def make_dirt_tile():
    surf = pygame.Surface((32, 32))
    surf.fill(C.dirt)
    for _ in range(8):
        x, y = random.randint(0, 30), random.randint(0, 30)
        pygame.draw.rect(surf, (100, 70, 50), (x, y, 4, 2))
    return surf

def make_kandang():
    """Kandang besar modern dengan sudut melengkung"""
    surf = pygame.Surface((96, 96), pygame.SRCALPHA)
    pygame.draw.rect(surf, C.dirt, (0, 0, 96, 96)) # Lantai tanah
    
    # Jerami
    for _ in range(15):
        x, y = random.randint(10, 80), random.randint(10, 80)
        pygame.draw.line(surf, C.hay, (x, y), (x+8, y+4), 2)
        pygame.draw.line(surf, C.hay, (x+8, y+4), (x+4, y+8), 2)

    # Pagar Kayu Halus
    pygame.draw.rect(surf, C.wood, (0, 0, 96, 8), border_radius=4)  # Atas
    pygame.draw.rect(surf, C.wood, (0, 88, 96, 8), border_radius=4) # Bawah
    pygame.draw.rect(surf, C.wood, (0, 0, 8, 96), border_radius=4)  # Kiri
    pygame.draw.rect(surf, C.wood, (88, 0, 8, 96), border_radius=4) # Kanan
    return surf

def make_house():
    """Rumah dengan atap halus"""
    surf = pygame.Surface((96, 96), pygame.SRCALPHA)
    pygame.draw.rect(surf, (220, 200, 180), (16, 40, 64, 50)) # Tembok
    pygame.draw.polygon(surf, C.red, [(48, 10), (10, 40), (86, 40)]) # Atap
    pygame.draw.rect(surf, C.wood, (40, 60, 16, 30)) # Pintu
    return surf

# =========================================================================
# 4. MESIN PELUKIS KARAKTER & HEWAN (GEOMETRIS MULUS)
# =========================================================================
def make_smooth_character(hair_col, shirt_col, pants_col, direction, is_moving=False):
    """Karakter dinamis yang mulus (Rounded Indie Style)"""
    surf = pygame.Surface((32, 48), pygame.SRCALPHA)
    
    # Efek jalan (badan naik turun)
    bounce = -2 if is_moving else 0

    # Kaki / Celana
    pygame.draw.rect(surf, pants_col, (8, 30, 16, 16), border_radius=4)
    if direction == 'down' or direction == 'up':
        pygame.draw.line(surf, C.black, (16, 36), (16, 46), 2) # Belahan kaki

    # Badan / Baju
    pygame.draw.rect(surf, shirt_col, (6, 16 + bounce, 20, 18), border_radius=6)

    # Kepala (Lingkaran)
    pygame.draw.circle(surf, C.skin, (16, 12 + bounce), 10)

    # Detail Wajah & Rambut
    if direction == 'down':
        pygame.draw.circle(surf, C.eye, (12, 12 + bounce), 2) # Mata kiri
        pygame.draw.circle(surf, C.eye, (20, 12 + bounce), 2) # Mata kanan
        pygame.draw.arc(surf, hair_col, (4, bounce, 24, 20), 0, 3.14, 6) # Poni
    
    elif direction == 'up':
        pygame.draw.circle(surf, hair_col, (16, 12 + bounce), 10) # Rambut full belakang
        
    elif direction == 'left':
        pygame.draw.circle(surf, C.eye, (10, 12 + bounce), 2)
        pygame.draw.arc(surf, hair_col, (6, 2 + bounce, 20, 20), 0, 3.14, 5)
        
    elif direction == 'right':
        pygame.draw.circle(surf, C.eye, (22, 12 + bounce), 2)
        pygame.draw.arc(surf, hair_col, (6, 2 + bounce, 20, 20), 0, 3.14, 5)

    return surf

def make_sapi():
    surf = pygame.Surface((64, 48), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, C.white, (4, 10, 56, 30)) # Badan
    pygame.draw.ellipse(surf, C.black, (15, 15, 15, 12)) # Bercak 1
    pygame.draw.ellipse(surf, C.black, (40, 20, 12, 15)) # Bercak 2
    pygame.draw.circle(surf, C.white, (12, 20), 12) # Kepala
    pygame.draw.ellipse(surf, C.pink, (4, 22, 12, 8)) # Moncong
    pygame.draw.circle(surf, C.eye, (10, 16), 2) # Mata
    return surf

def make_ayam():
    surf = pygame.Surface((32, 32), pygame.SRCALPHA)
    pygame.draw.ellipse(surf, C.white, (8, 12, 20, 16)) # Badan
    pygame.draw.circle(surf, C.red, (12, 10), 3) # Jengger
    pygame.draw.polygon(surf, C.hay, [(4, 14), (8, 12), (8, 16)]) # Paruh
    pygame.draw.circle(surf, C.eye, (12, 14), 1) # Mata
    return surf

# =========================================================================
# 5. GENERATOR UTAMA (Menjalankan semua fungsi di atas)
# =========================================================================
def generate_all():
    print("🚀 MEMULAI PABRIK ASET LEMBAH KARSA (V5 MODERN EDITION)...")
    
    # 1. Generate Tiles
    _save(make_grass_tile(), "tiles/grass.png")
    _save(make_dirt_tile(), "tiles/dirt.png")
    
    # 2. Generate Objek / Bangunan
    _save(make_kandang(), "objects/kandang.png")
    _save(make_house(), "objects/house.png")

    # 3. Generate Hewan
    for d in ['down', 'up', 'left', 'right']:
        for i in range(3):
            _save(make_sapi(), f"chars/sapi/{d}_{i}.png")
            _save(make_ayam(), f"chars/ayam/{d}_{i}.png")

    # 4. Generate Karakter (Player & NPC)
    chars = {
        'player':   {'hair': (50,30,20),   'shirt': C.blue,         'pants': (100,100,100)},
        'npc_arya': {'hair': (220,180,50), 'shirt': (100,180,100),  'pants': (80,60,40)},
        'npc_sari': {'hair': (200,50,50),  'shirt': (220,100,150),  'pants': (200,200,200)}
    }

    directions = ['down', 'up', 'left', 'right']
    for name, colors in chars.items():
        for d in directions:
            # Frame 0: Berdiri Diam
            _save(make_smooth_character(colors['hair'], colors['shirt'], colors['pants'], d, False), f"chars/{name}/{d}_0.png")
            # Frame 1 & 2: Bergerak (Badan memantul / bounce)
            _save(make_smooth_character(colors['hair'], colors['shirt'], colors['pants'], d, True),  f"chars/{name}/{d}_1.png")
            _save(make_smooth_character(colors['hair'], colors['shirt'], colors['pants'], d, True),  f"chars/{name}/{d}_2.png")

    print("🎉 SEMUA ASET BERHASIL DICETAK! SILAKAN JALANKAN GAME!")

# Jalankan skrip
if __name__ == "__main__":
    generate_all()
    pygame.quit()
