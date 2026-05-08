import pygame
import os
import random

pygame.init()
TILE = 32
SCALE = 2

# =========================================================================
# 1. PERSIAPAN FOLDER TOTAL
# =========================================================================
folders = [
    "assets/tiles", "assets/objects",
    "assets/chars/player", "assets/chars/npc_arya", "assets/chars/npc_sari",
    "assets/chars/npc_raka", "assets/chars/npc_maya", "assets/chars/npc_budi",
    "assets/chars/npc_sapi", "assets/chars/npc_ayam", "assets/chars/npc_tuyul",
    "assets/chars/npc_jin", "assets/chars/npc_naga", "assets/chars/running_mushroom"
]
for f in folders: os.makedirs(f, exist_ok=True)

def save_img(surf, path):
    pygame.image.save(surf, path)

def make_surf(w=TILE, h=TILE):
    return pygame.Surface((w, h), pygame.SRCALPHA)

# =========================================================================
# 2. BLUEPRINT MATRIKS (16x16 & 32x32)
# =========================================================================
# Cetakan Manusia (B = Baju, C = Celana, R = Rambut, K = Kulit, M = Mata)
bp_human = [
    "......RRRR......",
    ".....RRRRRR.....",
    ".....KMMKKM.....",
    ".....KKKKKK.....",
    "......KKKK......",
    ".....BBBBBB.....",
    "....BBlBBlBB....",
    "...BB.BBBB.BB...",
    "...B..BBBB..B...",
    "......BBBB......",
    "......CCCC......",
    "......CCCC......",
    "......C..C......",
    "......C..C......",
    ".....CC..CC.....",
    "................"
]

# Cetakan Ayam
bp_chicken = [
    "................",
    "......RR........",
    ".....RWW........",
    "....YWWW........",
    "....WWWWWW......",
    ".....WWWWWW.....",
    "......WWWW......",
    ".......YY.......",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................",
    "................"
]

# Cetakan Tuyul/Jin (B = Badan, G = Gelap, M = Mata)
bp_tuyul = [
    "......BBBB......",
    ".....BBBBBB.....",
    "....BBMmBBMm....",
    "....BBBBBBBB....",
    ".....BGBBGB.....",
    "......BBBB......",
    ".....BBBBBB.....",
    "....BGBBBBBGB...",
    "...BB.BBBB.BB...",
    "...B..BBBB..B...",
    "......BBBB......",
    "......GGGG......",
    "......B..B......",
    ".....BB..BB.....",
    "................",
    "................"
]

# Cetakan Naga Raksasa 32x32
bp_naga = [
    "................................",
    "..........DDDDDD................",
    ".........DGGGGGGD...............",
    "........DGGGGGGGGD..............",
    ".......DGMMGGGGMMGD.............",
    ".......DGGGGGGGGGGD.............",
    "........DGGdGGdGGD..............",
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
    "........DGGGGGGGGGD.............",
    ".......DGGGD...DGGGD............",
    ".......DGGD.....DGGD............",
    "......DGGGD.....DGGGD...........",
    "......DDDGD.....DDDGD...........",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................",
    "................................"
]

def draw_matrix(blueprint, cmap, scale=SCALE):
    w, h = len(blueprint[0]), len(blueprint)
    s = make_surf(w*scale, h*scale)
    for y, row in enumerate(blueprint):
        for x, char in enumerate(row):
            if char in cmap:
                pygame.draw.rect(s, cmap[char], (x*scale, y*scale, scale, scale))
    return s

# =========================================================================
# 3. GENERATOR LINGKUNGAN & ALAM (DENGAN NOISE)
# =========================================================================
print("🌱 Menumbuhkan Alam dan Gua...")

def make_noisy_tile(base_color, noise_colors, is_path=False):
    s = pygame.Surface((TILE, TILE))
    s.fill(base_color)
    for _ in range(40):
        x, y = random.randint(0, 31), random.randint(0, 31)
        pygame.draw.rect(s, random.choice(noise_colors), (x, y, random.randint(1,2), random.randint(1,2)))
    if is_path: pygame.draw.rect(s, (120,100,80), (0,0,32,32), 2)
    return s

save_img(make_noisy_tile((85,140,70), [(70,115,55), (100,160,80)]), "assets/tiles/grass.png")
save_img(make_noisy_tile((120,85,60), [(100,70,50), (90,60,40)]), "assets/tiles/dirt.png")
save_img(make_noisy_tile((160,140,110), [(140,120,90), (120,100,80)], True), "assets/tiles/path.png")

# Tilled Soil
dry = make_noisy_tile((100,70,50), [(90,60,40)])
pygame.draw.line(dry, (80,50,30), (8,0), (8,32), 2); pygame.draw.line(dry, (80,50,30), (24,0), (24,32), 2)
save_img(dry, "assets/tiles/tilled_dry.png")

wet = make_noisy_tile((70,45,30), [(60,35,20)])
pygame.draw.line(wet, (50,30,20), (8,0), (8,32), 2); pygame.draw.line(wet, (50,30,20), (24,0), (24,32), 2)
save_img(wet, "assets/tiles/tilled_wet.png")

# Gua
save_img(make_noisy_tile((50,40,40), [(40,30,30), (60,50,50)]), "assets/objects/cave_wall.png")
save_img(make_noisy_tile((40,35,35), [(30,25,25)]), "assets/objects/cave_floor.png")

# Air Dinamis
for i in range(4):
    w = pygame.Surface((TILE, TILE)); w.fill((60,140,210))
    for y in range(0, 32, 8):
        pygame.draw.line(w, (100,180,240), (((i*4)+y)%32, y+4), ((((i*4)+y)%32)+8, y+4), 2)
    save_img(w, f"assets/tiles/water_{i}.png")

# =========================================================================
# 4. GENERATOR INTERIOR & TANAMAN KELENGKAPAN V3
# =========================================================================
print("🏠 Melengkapi Perabotan dan Pertanian...")

def make_obj(c_base, c_detail, is_bed=False):
    s = make_surf()
    pygame.draw.rect(s, c_base, (2,2,28,28), border_radius=4)
    pygame.draw.rect(s, (0,0,0,100), (2,2,28,28), 2, border_radius=4)
    if is_bed:
        pygame.draw.rect(s, (255,255,255), (4,4,24,8), border_radius=2) 
        pygame.draw.rect(s, c_detail, (4,14,24,14), border_radius=2) 
    else:
        pygame.draw.rect(s, c_detail, (8,8,16,16), border_radius=2)
    return s

items = {
    'bed': ((120,80,50), (50,100,200)), 'chest': ((150,100,50), (200,180,50)),
    'stove': ((80,80,80), (200,100,50)), 'table': ((130,90,50), (100,60,30)),
    'bookshelf': ((100,60,40), (200,200,200)), 'mirror': ((100,60,40), (150,200,250)),
    'fireplace': ((100,100,100), (255,100,0)), 'clock': ((130,90,50), (255,255,255)),
    'plant_pot': ((150,100,50), (40,150,40)), 'counter': ((160,120,80), (100,60,30)),
    'shelf_store': ((120,80,50), (200,150,100)), 'grave': ((100,100,110), (80,80,90)),
    'lantern': ((50,50,50), (255,255,100)), 'mailbox': ((200,50,50), (255,255,255)),
    'fence': ((120,80,50), (100,60,30)), 'gate': ((100,60,40), (80,40,20)),
    'door': ((100,60,30), (200,150,50)), 'straw': ((200,200,100), (180,180,80)),
    'pen_post': ((100,50,20), (80,40,20)), 'dead_tree': ((80,70,60), (60,50,40))
}
for name, colors in items.items():
    save_img(make_obj(colors[0], colors[1], is_bed=(name=='bed')), f"assets/objects/{name}.png")

# Pohon Epik V4
tree = make_surf(64, 96)
pygame.draw.rect(tree, (60,40,25), (24, 48, 16, 48)) # Batang
pygame.draw.circle(tree, (30,80,30), (32, 40), 32)
pygame.draw.circle(tree, (40,100,40), (32, 24), 24)
save_img(tree, "assets/objects/tree.png")

# Tanaman (4 Fase)
crops = {'lobak': (255,50,100), 'wortel': (255,150,0), 'jagung': (255,255,0), 'tomat': (255,0,0), 'stroberi': (255,50,150)}
for c_name, c_color in crops.items():
    for stg in range(4):
        s = make_surf()
        pygame.draw.ellipse(s, (80,50,30), (4, 20, 24, 10)) # Gundukan
        if stg == 0: pygame.draw.rect(s, (100,200,100), (14, 18, 4, 6))
        elif stg == 1: pygame.draw.rect(s, (100,200,100), (12, 14, 8, 10))
        elif stg == 2: 
            pygame.draw.rect(s, (80,180,80), (10, 10, 12, 14))
            pygame.draw.circle(s, c_color, (16, 16), 4)
        elif stg == 3:
            pygame.draw.rect(s, (60,160,60), (6, 6, 20, 18))
            pygame.draw.circle(s, c_color, (16, 14), 8)
        save_img(s, f"assets/objects/{c_name}_{stg}.png")

# =========================================================================
# 5. PEMBUATAN KARAKTER MULTI-WARNA (COLOR MAPPING)
# =========================================================================
print("🧙‍♂️ Menempa Karakter dan Monster Epik...")

char_palettes = {
    'player':    {'K':(255,220,190), 'M':(0,0,0), 'R':(50,30,20),  'B':(50,100,200), 'C':(50,50,50),  'l':(80,130,220)},
    'npc_arya':  {'K':(255,220,190), 'M':(0,0,0), 'R':(220,180,50),'B':(100,180,100),'C':(80,60,40),  'l':(130,200,130)},
    'npc_sari':  {'K':(255,220,190), 'M':(0,0,0), 'R':(200,50,50), 'B':(220,100,150),'C':(200,200,200),'l':(240,130,180)},
    'npc_raka':  {'K':(240,200,180), 'M':(0,0,0), 'R':(50,50,50),  'B':(200,200,200),'C':(50,50,150), 'l':(255,255,255)},
    'npc_maya':  {'K':(230,190,170), 'M':(0,0,0), 'R':(80,40,20),  'B':(255,150,50), 'C':(100,100,100),'l':(255,180,80)},
    'npc_budi':  {'K':(220,180,160), 'M':(0,0,0), 'R':(180,180,180),'B':(150,50,50), 'C':(60,50,40),  'l':(180,80,80)},
    'npc_tuyul': {'B':(100,200,100), 'G':(60,150,60), 'M':(0,0,0), 'm':(255,255,255)},
    'npc_jin':   {'B':(150,50,200),  'G':(100,30,150),'M':(255,255,0),'m':(255,0,0)},
    'npc_ayam':  {'W':(255,255,255), 'R':(255,0,0), 'Y':(255,200,0)},
}

def build_anim(name, base_surf, is_huge=False):
    w, h = base_surf.get_width(), base_surf.get_height()
    for d in ['up', 'down', 'left', 'right']:
        for f in range(3):
            frame = make_surf(w, h + (4 if not is_huge else 12))
            art = base_surf.copy()
            if d == 'left': art = pygame.transform.flip(art, True, False)
            
            # --- BARIS YANG DIPERBAIKI (Aman dari Sapi & Jamur) ---
            elif d == 'up' and not is_huge and name in char_palettes and 'R' in char_palettes[name]:
                pygame.draw.rect(art, char_palettes[name]['R'], (8*SCALE, 4*SCALE, 6*SCALE, 6*SCALE))
            # --------------------------------------------------------

            y_bounce = -SCALE if f != 0 else 0
            if is_huge: y_bounce = -SCALE*2 if f != 0 else 0
            
            frame.blit(art, (0, (4 if not is_huge else 12) + y_bounce))
            
            # Shadow
            shadow_y = h + (2 if not is_huge else 8)
            shadow_w = w - (8 * SCALE)
            pygame.draw.ellipse(frame, (0,0,0,60), ((w-shadow_w)//2, shadow_y, shadow_w, SCALE*2))
            save_img(frame, f"assets/chars/{name}/{d}_{f}.png")

# Generate Manusia, Tuyul, Jin, Ayam
for name, pmap in char_palettes.items():
    if name in ['npc_tuyul', 'npc_jin']: bp = bp_tuyul
    elif name == 'npc_ayam': bp = bp_chicken
    else: bp = bp_human
    build_anim(name, draw_matrix(bp, pmap))

# Generate Naga Raksasa (Scale 3x = 96x96 px)
naga_map = {'D':(30,100,50), 'G':(50,200,100), 'M':(255,0,0), 'd':(150,255,150)}
build_anim('npc_naga', draw_matrix(bp_naga, naga_map, scale=3), is_huge=True)

# Generate Sapi (Khusus)
sapi = make_surf(32, 32)
pygame.draw.rect(sapi, (150,100,50), (4,12,24,16), border_radius=4)
pygame.draw.rect(sapi, (255,255,255), (10,14,10,10)) # Bercak
pygame.draw.rect(sapi, (100,60,30), (22,8,8,10), border_radius=2) # Kepala
build_anim('npc_sapi', sapi)

# Generate Jamur (Khusus)
jamur = make_surf(32, 32)
pygame.draw.ellipse(jamur, (200,50,50), (4, 8, 24, 16))
pygame.draw.ellipse(jamur, (255,255,255), (8, 10, 6, 6))
pygame.draw.rect(jamur, (255,220,190), (12, 20, 8, 10))
build_anim('running_mushroom', jamur)

print("🔥 EKSEKUSI SELESAI! Mahakarya V5 telah siap. Langsung jalankan `python main.py`!")
pygame.quit()
