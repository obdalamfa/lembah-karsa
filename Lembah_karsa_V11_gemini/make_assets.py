import pygame
import os
import random

pygame.init()
TILE = 32

# 1. PERSIAPAN FOLDER SUPER LENGKAP
folders = [
    "assets/tiles", "assets/objects",
    "assets/chars/player", "assets/chars/npc_arya", "assets/chars/npc_sari",
    "assets/chars/npc_raka", "assets/chars/npc_maya", "assets/chars/npc_budi",
    "assets/chars/npc_sapi", "assets/chars/npc_ayam", "assets/chars/npc_tuyul",
    "assets/chars/npc_jin", "assets/chars/npc_naga"
]
for f in folders: os.makedirs(f, exist_ok=True)

def save_img(surf, path):
    pygame.image.save(surf, path)

def make_surf(w=TILE, h=TILE):
    return pygame.Surface((w, h), pygame.SRCALPHA)

# =========================================================================
#  2. MENGHANCURKAN KOTAK ABU-ABU (FURNITUR, GUA, & ALAM MATI)
# =========================================================================
print("🛠️ Membangun Interior, Gua, dan Pertanian...")

# A. Tekstur Gua (Cave)
cave_w = make_surf()
cave_w.fill((50, 40, 40)) # Dinding gua gelap
pygame.draw.rect(cave_w, (30, 20, 20), (0,0,TILE,TILE), 2)
pygame.draw.polygon(cave_w, (70, 60, 60), [(5,30), (15,10), (25,30)]) # Stalagmit
save_img(cave_w, "assets/objects/cave_wall.png")

cave_f = make_surf()
cave_f.fill((40, 35, 35)) # Lantai gua
for _ in range(10): pygame.draw.rect(cave_f, (20,15,15), (random.randint(0,28), random.randint(0,28), 4, 4))
save_img(cave_f, "assets/objects/cave_floor.png")

# B. Furnitur Interior Rumah
furnitures = {
    'bed': [(100,50,50), (10,10,22,22)], # Kasur merah
    'stove': [(80,80,80), (5,5,27,27)], # Kompor besi
    'table': [(130,90,50), (2,10,28,20)], # Meja kayu
    'bookshelf': [(100,60,40), (2,2,28,30)], # Rak buku
    'chest': [(200,150,50), (4,10,24,20)], # Peti emas/kayu
    'mirror': [(150,200,250), (8,4,16,24)], # Cermin biru
    'fireplace': [(150,50,0), (4,15,24,17)], # Perapian (api)
    'clock': [(255,255,255), (8,8,16,16)], # Jam bundar putih
    'plant_pot': [(40,150,40), (10,5,12,15)], # Tanaman pot
    'counter': [(160,120,80), (0,15,32,17)], # Meja kasir
    'shelf_store': [(120,80,50), (0,0,32,15)], # Rak warung
    'grave': [(100,100,110), (8,5,16,25)], # Batu nisan
    'lantern': [(255,200,50), (12,12,8,15)], # Lentera menyala
    'mailbox': [(200,50,50), (10,10,12,15)], # Kotak pos
    'fence': [(120,80,50), (0,12,32,8)], # Pagar horizontal
    'gate': [(100,60,40), (0,12,10,8)], # Gerbang
    'dead_tree': [(80,70,60), (12,5,8,27)], # Pohon mati
    'door': [(100,60,30), (4,0,24,32)],
    'straw': [(200,200,100), (4,15,24,15)], # Jerami
    'pen_post': [(100,50,20), (12,12,8,8)] # Tiang ternak
}

for name, data in furnitures.items():
    s = make_surf()
    s.fill((60, 40, 30)) # Warna dasar kayu/bayangan
    pygame.draw.rect(s, data[0], data[1]) # Bentuk utama
    pygame.draw.rect(s, (0,0,0), (0,0,TILE,TILE), 1) # Outline batas
    save_img(s, f"assets/objects/{name}.png")

# C. Sayuran (Crops) - 4 Fase
crops = {'lobak': (255,50,100), 'wortel': (255,150,0), 'jagung': (255,255,0), 'tomat': (255,0,0), 'stroberi': (255,50,150)}
for c_name, color in crops.items():
    for stage in range(4):
        s = make_surf()
        # Tanah bawah
        pygame.draw.ellipse(s, (80,50,30), (4, 20, 24, 10))
        if stage == 0: pygame.draw.rect(s, (100,200,100), (14, 18, 4, 6)) # Bibit
        elif stage == 1: pygame.draw.rect(s, (100,200,100), (12, 14, 8, 10)) # Tunas
        elif stage == 2: 
            pygame.draw.rect(s, (80,180,80), (10, 10, 12, 14)) # Rimbun
            pygame.draw.circle(s, color, (16, 16), 4) # Buah kecil
        elif stage == 3:
            pygame.draw.rect(s, (60,160,60), (6, 6, 20, 18)) # Panen
            pygame.draw.circle(s, color, (16, 14), 8) # Buah besar!
        save_img(s, f"assets/objects/{c_name}_{stage}.png")

# =========================================================================
#  3. MEMBANGUN NPC YANG BERBEDA-BEDA WUJUDNYA
# =========================================================================
print("🛠️ Melahirkan Warga dan Makhluk Lembah...")

def draw_char(color_shirt, color_hair, color_pants, is_tuyul=False):
    s = make_surf(TILE, int(TILE * 1.5))
    if is_tuyul:
        pygame.draw.rect(s, (100,200,100), (8, 16, 16, 20), border_radius=5) # Badan tuyul hijau
        pygame.draw.circle(s, (100,200,100), (16, 12), 10) # Kepala botak
        pygame.draw.circle(s, (0,0,0), (12, 10), 2); pygame.draw.circle(s, (0,0,0), (20, 10), 2) # Mata belo
    else:
        pygame.draw.rect(s, color_pants, (10, 30, 12, 16)) # Celana
        pygame.draw.rect(s, color_shirt, (8, 16, 16, 14), border_radius=3) # Baju
        pygame.draw.rect(s, (255, 220, 190), (10, 4, 12, 12), border_radius=4) # Kepala
        pygame.draw.rect(s, color_hair, (8, 2, 16, 8), border_radius=4) # Rambut
        pygame.draw.rect(s, (0,0,0), (12, 10, 2, 2)); pygame.draw.rect(s, (0,0,0), (18, 10, 2, 2)) # Mata
    return s

npc_data = {
    'player': [(50,100,200), (50,30,20), (50,50,50)],   # Baju Biru
    'npc_arya': [(100,180,100), (200,150,50), (80,60,40)],# Baju Hijau, Rambut Pirang
    'npc_sari': [(220,100,150), (100,50,50), (200,200,200)],# Baju Pink, Rambut Merah
    'npc_raka': [(200,200,200), (50,50,50), (50,50,150)], # Baju Putih, Celana Biru
    'npc_maya': [(255,150,50), (80,40,20), (100,100,100)],# Baju Oranye
    'npc_budi': [(100,50,50), (200,200,200), (50,40,30)], # Baju Merah Tua, Ubanan
    'npc_tuyul': [(0,0,0), (0,0,0), (0,0,0)] # Khusus Tuyul
}

for name, colors in npc_data.items():
    base = draw_char(colors[0], colors[1], colors[2], is_tuyul=(name=='npc_tuyul'))
    for d in ['up', 'down', 'left', 'right']:
        for f in range(3):
            frame = base.copy()
            if d == 'up': pygame.draw.rect(frame, colors[1] if name!='npc_tuyul' else (100,200,100), (10, 4, 12, 12)) # Tutup muka
            elif d == 'left': frame = pygame.transform.flip(frame, True, False)
            save_img(frame, f"assets/chars/{name}/{d}_{f}.png")

# =========================================================================
#  4. NAGA RAKSASA (BOSS SIZE - 3x3 TILE!)
# =========================================================================
print("🐉 Membangkitkan Naga Raksasa...")
# Ukuran naga sekarang 96x96 pixel!
def draw_big_dragon():
    s = make_surf(TILE*3, TILE*3)
    # Ekor besar melingkar
    pygame.draw.ellipse(s, (20, 120, 50), (10, 50, 76, 40)) 
    # Badan gempal
    pygame.draw.ellipse(s, (50, 200, 100), (20, 30, 56, 50))
    # Perut terang
    pygame.draw.ellipse(s, (150, 255, 150), (32, 40, 32, 36))
    # Kepala Naga Besar
    pygame.draw.rect(s, (50, 200, 100), (32, 10, 32, 26), border_radius=8)
    pygame.draw.rect(s, (20, 100, 40), (28, 14, 40, 10), border_radius=4) # Moncong
    # Mata menyala merah
    pygame.draw.circle(s, (255, 0, 0), (40, 18), 4); pygame.draw.circle(s, (255, 0, 0), (56, 18), 4)
    # Tanduk
    pygame.draw.polygon(s, (220, 220, 220), [(32, 10), (20, 0), (40, 10)])
    pygame.draw.polygon(s, (220, 220, 220), [(64, 10), (76, 0), (56, 10)])
    # Sayap kecil (Mengepak)
    pygame.draw.polygon(s, (30, 150, 70), [(20, 40), (0, 10), (30, 30)])
    pygame.draw.polygon(s, (30, 150, 70), [(76, 40), (96, 10), (66, 30)])
    return s

base_naga = draw_big_dragon()
for d in ['up', 'down', 'left', 'right']:
    for f in range(3):
        # Sedikit ayunan pernapasan untuk animasi
        frame = make_surf(TILE*3, TILE*3)
        y_bounce = -2 if f == 1 else (2 if f == 2 else 0)
        frame.blit(base_naga, (0, y_bounce))
        save_img(frame, f"assets/chars/npc_naga/{d}_{f}.png")

print("✨ SELESAI! Kotak abu-abu musnah, Naga Raksasa bangkit. Jalankan `python main.py`!")
pygame.quit()
