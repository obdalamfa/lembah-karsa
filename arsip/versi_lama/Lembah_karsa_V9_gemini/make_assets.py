import pygame
import os
import random

# Initial Setup
pygame.init()
TILE = 32 # Base tile size

# Define a smarter folder list from your asset guide
folders = [
    "assets/tiles",
    "assets/objects",
    "assets/chars/player",
    "assets/chars/arya",
    "assets/chars/sapi",
    "assets/chars/tuyul",
    "assets/chars/jin",
    "assets/chars/naga"
]
for f in folders:
    os.makedirs(f, exist_ok=True)

# Helper for drawing pixel-art outlines
def pp(s, x, y, c):
    """Set pixel with bound checking."""
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), c)

def rect_pp(s, x1, y1, x2, y2, c):
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1): pp(s, x, y, c)

def hline_pp(s, y, x1, x2, c):
    for x in range(x1, x2 + 1): pp(s, x, y, c)

def vline_pp(s, x, y1, y2, c):
    for y in range(y1, y2 + 1): pp(s, x, y, c)

def save_img(surface, path):
    pygame.image.save(surface, path)
    print(f"✅ Created Detailed Asset: {path}")

def make_surface(w, h=TILE):
    return pygame.Surface((w, h), pygame.SRCALPHA)

# Colour Palette
class C:
    grass = (85, 140, 70); grass_dk = (70, 115, 55); grass_lt = (100, 160, 80)
    dirt = (110, 80, 60); dirt_dk = (90, 65, 50)
    path = (160, 140, 110); path_dk = (140, 120, 90)
    soil = (95, 65, 45); soil_dk = (75, 50, 35)
    water = (60, 120, 200); water_lt = (100, 150, 230)
    wood = (80, 50, 30); wood_dk = (60, 40, 25); wood_lt = (110, 75, 50)
    stone = (120, 120, 130); stone_dk = (90, 90, 100)
    char_skin = (240, 200, 180); char_shirt = (200, 50, 50); char_pants = (50, 50, 150)
    cow_base = (140, 80, 60); cow_spot = (255, 255, 255)
    goblin = (100, 160, 80); gold = (220, 180, 50)

# =========================================================================
#  TILES
# =========================================================================
print("Creating Detailed Environment Tiles...")

# 1. Grass
surf = make_surface(TILE)
surf.fill(C.grass)
rect_pp(surf, 4, 4, 8, 8, C.grass_dk)
rect_pp(surf, 20, 6, 24, 10, C.grass_dk)
pp(surf, 2, 2, C.grass_lt); pp(surf, 16, 12, C.grass_lt)
pp(surf, 30, 26, C.grass_lt); pp(surf, 26, 18, C.grass_lt)
pp(surf, 10, 30, C.grass_dk)
save_img(surf, "assets/tiles/grass.png")

# 2. Dirt
surf = make_surface(TILE)
surf.fill(C.dirt)
for _ in range(12):
    x, y = random.randint(0, 31), random.randint(0, 31)
    shape_type = random.randint(0, 1)
    if shape_type == 0: rect_pp(surf, x, y, min(x+2, 31), min(y+1, 31), C.dirt_dk)
    else: hline_pp(surf, y, max(0, x-1), min(x+2, 31), C.dirt_dk)
save_img(surf, "assets/tiles/dirt.png")

# 3. Path
surf = make_surface(TILE)
surf.fill(C.path)
rect_pp(surf, 0, 0, 31, 0, C.path_dk) 
rect_pp(surf, 0, 0, 0, 31, C.path_dk)
rect_pp(surf, 8, 8, 15, 15, C.stone) 
rect_pp(surf, 24, 8, 31, 15, C.stone) 
pp(surf, 16, 24, C.path_dk) 
save_img(surf, "assets/tiles/path.png")

# 4. Tilled Soil
surf = make_surface(TILE); surf.fill(C.soil)
hline_pp(surf, 6, 4, 27, C.soil_dk); hline_pp(surf, 12, 4, 27, C.soil_dk)
vline_pp(surf, 4, 6, 12, C.soil_dk); vline_pp(surf, 27, 6, 12, C.soil_dk)
save_img(surf, "assets/tiles/tilled_dry.png")

surf = make_surface(TILE); surf.fill((70, 45, 30))
hline_pp(surf, 6, 4, 27, (50, 30, 20)); hline_pp(surf, 12, 4, 27, (50, 30, 20))
save_img(surf, "assets/tiles/tilled_wet.png")

# 5. Water
for i in range(4):
    surf = make_surface(TILE)
    surf.fill(C.water)
    y_start = (i * 8) % TILE
    for y in range(y_start, TILE + y_start, 12):
        hline_pp(surf, y % TILE, 8, 23, C.water_lt)
    save_img(surf, f"assets/tiles/water_{i}.png")

# =========================================================================
#  OBJECTS
# =========================================================================
print("Creating Large Detailed Objects...")

# 6. Tree
surf = make_surface(TILE * 2, TILE * 3)
rect_pp(surf, 16, 32, 23, 71, C.wood) 
pygame.draw.circle(surf, (30, 80, 30), (32, 24), 32) 
pygame.draw.circle(surf, (40, 100, 40), (32, 20), 28) 
pygame.draw.circle(surf, (30, 80, 30), (16, 12), 16); pygame.draw.circle(surf, (30, 80, 30), (48, 12), 16)
pp(surf, 32, 4, C.wood_lt); pp(surf, 16, 16, C.wood_lt) 
save_img(surf, "assets/objects/tree.png")

# 7. House
surf = make_surface(TILE * 3, TILE * 3)
rect_pp(surf, 8, 20, 87, 83, C.wood)
pygame.draw.rect(surf, C.wood_dk, (8, 20, 80, 64), 2) # Wall texture
pygame.draw.polygon(surf, (160, 50, 50), [(0, 30), (48, 0), (96, 30)])
pygame.draw.polygon(surf, (130, 40, 40), [(0, 30), (48, 0), (96, 30)], 3) 
rect_pp(surf, 40, 50, 55, 83, C.wood_dk); pp(surf, 52, 65, C.gold)
rect_pp(surf, 16, 40, 27, 51, (80, 150, 220))
vline_pp(surf, 21, 40, 51, C.wood_dk); hline_pp(surf, 45, 16, 27, C.wood_dk)

# Stone deck floor
rect_pp(surf, 10, 83, 85, 95, C.stone)
pygame.draw.rect(surf, C.stone_dk, (10, 83, 76, 13), 2) # Stone outline
save_img(surf, "assets/objects/house.png")

# =========================================================================
#  FURNITURE & CROP ICONS 
# =========================================================================
print("Creating Furniture & Crop Icons...")
def make_icon(c1, c2=None):
    s = make_surface(TILE, TILE)
    rect_pp(s, 2, 2, 29, 29, c1)
    pygame.draw.rect(s, (0, 0, 0, 50), (0, 0, TILE, TILE), 2) # Icon outline
    if c2: rect_pp(s, 8, 8, 23, 23, c2)
    return s

save_img(make_icon(C.char_pants, (80, 180, 250)), "assets/objects/bed.png")
save_img(make_icon(C.wood, (200, 160, 100)), "assets/objects/chest.png")
save_img(make_icon((80,80,80), (250,150,100)), "assets/objects/stove.png")
save_img(make_icon(C.wood_dk, (255,255,100)), "assets/objects/lantern.png")

# =========================================================================
#  CHARACTER & ANIMAL SPRITES
# =========================================================================
print("Creating Detailed Animated Characters...")

def draw_humanoid(s, shirt_c, pants_c, hair_c=(50,30,20)):
    rect_pp(s, 10, TILE, 11, TILE+10, pants_c); rect_pp(s, 18, TILE, 19, TILE+10, pants_c)
    rect_pp(s, 10, 4, 21, 15, C.char_skin)
    pp(s, 14, 10, (50,50,50)); pp(s, 18, 10, (50,50,50)) 
    rect_pp(s, 8, 16, 23, TILE, shirt_c)
    rect_pp(s, 8, 2, 23, 8, hair_c)

def draw_cow(s):
    rect_pp(s, 4, 10, 27, 27, C.cow_base)
    rect_pp(s, 4, 24, 7, 31, C.wood); rect_pp(s, 24, 24, 27, 31, C.wood) 
    rect_pp(s, 16, 2, 27, 10, C.cow_spot)
    pp(s, 22, 6, (0,0,0)) 
    pp(s, 18, 4, (100,100,100)); pp(s, 20, 4, (100,100,100)) 
    
def draw_goblin(s):
    rect_pp(s, 10, 10, 21, 27, C.goblin); rect_pp(s, 10, 27, 21, 31, (60, 60, 60)) 
    rect_pp(s, 8, 2, 23, 14, C.goblin)
    pp(s, 12, 10, (0, 0, 0)); pp(s, 18, 10, (0, 0, 0))
    rect_pp(s, 8, 2, 23, 6, (80, 140, 60)) 

h_char = int(TILE * 1.5)
dirs = ['up', 'down', 'left', 'right']

def make_12_frame_sheet(name, draw_func, colors_tuple=None):
    for d in dirs:
        for f in range(3):
            s = make_surface(TILE, h_char)
            if colors_tuple: draw_func(s, colors_tuple[0], colors_tuple[1], colors_tuple[2])
            else: draw_func(s)
            
            if f == 1: pygame.draw.rect(s, (0,0,0,50), (4, h_char-4, TILE-8, 4), border_radius=2)
            elif f == 2: pygame.draw.rect(s, (0,0,0,50), (TILE-4, h_char-4, -TILE+8, 4), border_radius=2)
            
            if d == 'left' and f > 0: s = pygame.transform.flip(s, True, False)

            folder_path = f"assets/chars/{name}"
            save_img(s, f"{folder_path}/{d}_{f}.png")

make_12_frame_sheet('player', draw_humanoid, (C.char_shirt, C.char_pants, (50, 30, 20)))
make_12_frame_sheet('arya', draw_humanoid, ((100, 180, 100), (50, 40, 30), (50, 50, 50)))
make_12_frame_sheet('sapi', draw_cow)
make_12_frame_sheet('tuyul', draw_goblin)

for name in ['jin', 'naga']:
    for d in dirs:
        for f in range(3):
            s = make_surface(TILE, TILE)
            c = C.goblin if name == 'jin' else (50, 200, 100)
            rect_pp(s, 8, 8, 23, 23, c)
            save_img(s, f"assets/chars/{name}/{d}_{f}.png")

print("🎉 Finished Generating Detailed Pixel Art Assets! No errors.")
pygame.quit()
