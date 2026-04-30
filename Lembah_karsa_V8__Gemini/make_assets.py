import pygame
import os

# Inisialisasi
pygame.init()
TILE = 32

# Buat struktur folder
folders = [
    "assets/tiles",
    "assets/objects",
    "assets/chars/player",
    "assets/chars/sapi",
    "assets/chars/tuyul"
]
for f in folders:
    os.makedirs(f, exist_ok=True)

def save_img(surface, path):
    pygame.image.save(surface, path)
    print(f"✅ Dibuat: {path}")

def make_surface(w, h):
    return pygame.Surface((w, h), pygame.SRCALPHA)

print("Membuat Aset Lingkungan...")
# 1. Tiles (Rumput, Tanah, Air)
grass = make_surface(TILE, TILE)
grass.fill((85, 140, 70))
pygame.draw.rect(grass, (100, 160, 80), (4, 4, 8, 8)) # Tekstur
save_img(grass, "assets/tiles/grass.png")

dirt = make_surface(TILE, TILE)
dirt.fill((120, 85, 60))
pygame.draw.rect(dirt, (100, 70, 50), (10, 10, 6, 4))
save_img(dirt, "assets/tiles/dirt.png")

path = make_surface(TILE, TILE)
path.fill((180, 160, 130))
pygame.draw.rect(path, (150, 130, 100), (0, 0, TILE, TILE), 2)
save_img(path, "assets/tiles/path.png")

for i in range(4):
    water = make_surface(TILE, TILE)
    water.fill((60, 140, 210))
    pygame.draw.line(water, (100, 180, 240), (i*4, 5), (i*4 + 10, 5), 2)
    save_img(water, f"assets/tiles/water_{i}.png")

print("Membuat Objek Besar...")
# 2. Objek (Pohon & Rumah)
tree = make_surface(TILE * 2, TILE * 3)
pygame.draw.rect(tree, (60, 40, 25), (TILE//2 + 8, TILE, TILE-16, TILE*2)) # Batang
pygame.draw.circle(tree, (30, 80, 30), (TILE, TILE), TILE) # Daun
pygame.draw.circle(tree, (40, 100, 40), (TILE, TILE-10), int(TILE*0.8))
save_img(tree, "assets/objects/tree.png")

house = make_surface(TILE * 3, TILE * 3)
pygame.draw.rect(house, (220, 200, 180), (10, TILE+10, TILE*3-20, TILE*2-10)) # Tembok
pygame.draw.rect(house, (100, 60, 40), (TILE*1.5 - 16, TILE*2+10, 32, TILE)) # Pintu
pygame.draw.polygon(house, (160, 50, 50), [(0, TILE+10), (TILE*1.5, 0), (TILE*3, TILE+10)]) # Atap
save_img(house, "assets/objects/house.png")

print("Membuat Karakter (4 Arah)...")
# 3. Karakter (Player)
dirs = ['up', 'down', 'left', 'right']
for d in dirs:
    for f in range(3):
        char = make_surface(TILE, int(TILE * 1.5))
        pygame.draw.rect(char, (50, 50, 150), (10, 30, 12, 18)) # Celana
        pygame.draw.rect(char, (200, 50, 50), (8, 16, 16, 14)) # Baju
        pygame.draw.rect(char, (255, 220, 190), (10, 4, 12, 12)) # Kepala
        pygame.draw.rect(char, (50, 30, 20), (8, 2, 16, 8)) # Rambut
        
        # Mata (hanya kalau hadap depan/kiri/kanan)
        if d == 'down':
            pygame.draw.rect(char, (0, 0, 0), (12, 10, 2, 2))
            pygame.draw.rect(char, (0, 0, 0), (18, 10, 2, 2))
        elif d == 'right':
            pygame.draw.rect(char, (0, 0, 0), (18, 10, 2, 2))
        elif d == 'left':
            pygame.draw.rect(char, (0, 0, 0), (12, 10, 2, 2))
            
        save_img(char, f"assets/chars/player/{d}_{f}.png")

print("🎉 Selesai! Semua file .png berhasil dibuat di dalam folder assets/!")
pygame.quit()
