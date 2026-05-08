"""
HARVEST MOON 2.0 → LEMBAH KARSA  ASSET EXTRACTOR
==================================================
Potong dan salin sprite dari Harvest Moon 2.0 ke folder assets/ game.

Cara pakai:
    python extract_hm_assets.py

Semua output masuk ke:  lembah_karsa/assets/
Semua fallback tetap bekerja jika file tidak ditemukan.
"""

import pygame
import os
import shutil

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

# ── PATH ─────────────────────────────────────────────────────────
HM = r"E:\Download\Harvest-Moon-2.0-1.0\Harvest-Moon-2.0-1.0\Harvest Moon 2.0"
OUT = "assets"          # relatif ke folder game (jalankan dari sana)
TILE = 48               # ukuran tile game kita

def p(rel):             # HM absolute path
    return os.path.join(HM, rel)

def out(*parts):        # output path
    return os.path.join(OUT, *parts)

# ── HELPER ───────────────────────────────────────────────────────
def load(rel_path):
    full = p(rel_path)
    if not os.path.exists(full):
        print(f"  [SKIP] tidak ditemukan: {rel_path}")
        return None
    try:
        surf = pygame.image.load(full)
        try:
            return surf.convert_alpha()
        except Exception:
            return surf.convert()
    except Exception as e:
        print(f"  [ERROR] {rel_path}: {e}")
        return None

def crop(surf, x, y, w, h):
    """Potong rect dari surface."""
    x, y = max(0, x), max(0, y)
    w = min(w, surf.get_width() - x)
    h = min(h, surf.get_height() - y)
    r = pygame.Rect(x, y, w, h)
    return surf.subsurface(r).copy()

def save(surf, *path_parts):
    """Scale ke TILE×TILE dan simpan."""
    dst = out(*path_parts)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    scaled = pygame.transform.scale(surf, (TILE, TILE))
    pygame.image.save(scaled, dst)
    print(f"  -> {dst}")

def save_raw(surf, w, h, *path_parts):
    """Scale ke ukuran khusus dan simpan."""
    dst = out(*path_parts)
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    scaled = pygame.transform.scale(surf, (w, h))
    pygame.image.save(scaled, dst)
    print(f"  -> {dst}  ({w}×{h})")

def copy_file(src_rel, *dst_parts):
    """Salin file langsung (scale otomatis di game)."""
    src = p(src_rel)
    dst = out(*dst_parts)
    if not os.path.exists(src):
        print(f"  [SKIP] tidak ditemukan: {src_rel}")
        return False
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    shutil.copy2(src, dst)
    print(f"  copy -> {dst}")
    return True

# ═══════════════════════════════════════════════════════════════
#  1. TERRAIN TILES
# ═══════════════════════════════════════════════════════════════
print("\n[1] TERRAIN TILES")

# Grass dari Pokemon tiles (48×48 tiles)
pokemon = load("tilesets/Pokemon tiles.png")
if pokemon:
    # GrassMiddleCenter dari backgroundTiles.tres
    grass = crop(pokemon, 256, 240, 48, 48)
    save(grass, "tiles", "grass.png")

    # Mud1 sebagai dirt
    dirt = crop(pokemon, 400, 240, 48, 48)
    save(dirt, "tiles", "dirt.png")

    # Town tile sebagai path
    path_t = crop(pokemon, 544, 240, 48, 48)
    save(path_t, "tiles", "path.png")

# Terrain.png: tilled_dry, tilled_wet, dirt (32×32)
terrain = load("tilesets/terrain.png")
if terrain:
    tilled_dry = crop(terrain, 0, 22, 32, 32)
    save(tilled_dry, "tiles", "tilled_dry.png")

    normal_dirt = crop(terrain, 32, 22, 32, 32)
    # Jika dirt dari pokemon terlalu terang, bisa uncomment baris berikut:
    # save(normal_dirt, "tiles", "dirt.png")

    tilled_wet = crop(terrain, 64, 22, 32, 32)
    save(tilled_wet, "tiles", "tilled_wet.png")

# Water dari houseTiles (32×32) – diambil satu tile, dibuat 4 variasi
house = load("tilesets/houseTiles.png")
if house:
    water_base = crop(house, 96, 672, 32, 32)
    for i in range(4):
        # Variasi: shift warna sedikit untuk animasi
        w_var = water_base.copy()
        if i > 0:
            # Buat efek shimmer sederhana
            tint = pygame.Surface(w_var.get_size(), pygame.SRCALPHA)
            tint.fill((0, 20 * i, 40 * i, 30))
            w_var.blit(tint, (0, 0))
        save(w_var, "tiles", f"water_{i}.png")

# ═══════════════════════════════════════════════════════════════
#  2. OBJEK & FURNITURE
# ═══════════════════════════════════════════════════════════════
print("\n[2] OBJEK & FURNITURE")

if house:
    # Tree: gabung Tree1 (top) + Tree3 (bottom) menjadi 1 tile
    tree_top = crop(house, 0, 384, 32, 32)
    tree_bot = crop(house, 0, 416, 32, 32)
    tree_surf = pygame.Surface((32, 64), pygame.SRCALPHA)
    tree_surf.blit(tree_top, (0, 0))
    tree_surf.blit(tree_bot, (0, 32))
    tree_scaled = pygame.transform.scale(tree_surf, (TILE, TILE * 2))
    # Simpan sebagai TILE×TILE (crop setengah bawah untuk 1 tile)
    save(tree_top, "objects", "tree.png")

    # Bush sebagai weed
    bush = crop(house, 96, 352, 32, 32)
    save(bush, "objects", "weed.png")

    # BigBush
    bigbush = crop(house, 64, 384, 32, 32)
    save(bigbush, "objects", "stone.png")

# Interior stove.png (31×44)
stove_surf = load("tilesets/interior/stove.png")
if stove_surf:
    save(stove_surf, "objects", "stove.png")

# Interior shelf
shelf = load("tilesets/interior/shelf_full.png")
if shelf:
    save(shelf, "objects", "bookshelf.png")
    save(shelf, "objects", "shelf_store.png")

# ═══════════════════════════════════════════════════════════════
#  3. CROP STAGES  (Crops.png = 192×160, tile 16×16)
# ═══════════════════════════════════════════════════════════════
print("\n[3] CROP STAGES")

crops_sheet = load("tilesets/Crops.png")
if crops_sheet:
    # Format: setiap baris = 1 jenis tanaman, 6 tahap dari kanan ke kiri
    # tahap 0 (benih): x=0  tahap 3 (panen): x=80
    # Stages mapping: [seed_x, early_x, mid_x, harvest_x] dari Crops.png
    CROP_MAP = {
        # name         seed   early  mid    harvest   y
        "lobak":    [(0,    0), (32,  0), (64,  0), (80,  0)],  # Turnip row y=0
        "tomat":    [(0,   33), (32, 32), (64, 33), (80, 33)],  # Tomato row y=32
        "bayam":    [(0,   47), (32, 48), (64, 48), (80, 48)],  # Eggplant y=47
        "labu":     [(95,  32), (128,32), (160,32), (176,32)],  # Melon   y=32
        "jagung":   [(95,  64), (128,63), (160,64), (176,64)],  # Wheat   y=64
        "stroberi": [(0,   96), (32, 96), (64, 96), (80,  96)], # Strawberry y=96
        "wortel":   [(0,  112), (32,112), (64,112), (80, 112)], # Potato  y=112
    }
    for crop_id, stages in CROP_MAP.items():
        for stage_num, (cx, cy) in enumerate(stages):
            tile = crop(crops_sheet, cx, max(0, cy), 16, 16)
            save(tile, "crops", f"{crop_id}_{stage_num}.png")
            print(f"     {crop_id} stage {stage_num} @ ({cx},{cy})")

# ═══════════════════════════════════════════════════════════════
#  4. PLAYER SPRITES (Walking animations)
# ═══════════════════════════════════════════════════════════════
print("\n[4] PLAYER SPRITES")

# Walking Down (5 frames tersedia, kita pakai 1 dan 3 untuk 2-frame anim)
# Idle Down = frame idle (berdiri diam)
idle_down = load("player/animations/idle/Idle Down.png")
idle_up   = load("player/animations/idle/Idle Up.png")
idle_left = load("player/animations/idle/Idle Left.png")

walk_down  = [load(f"player/animations/walking/Down{i}.png") for i in range(1, 6)]
walk_up    = [load(f"player/animations/walking/Up{i}.png")   for i in range(1, 3)]
walk_left  = [load(f"player/animations/walking/left{i}.png") for i in range(1, 3)]

def player_frame(surf, direction, frame_num):
    """Simpan frame player dan mirror untuk 'right' dari 'left'."""
    if surf is None:
        return
    save(surf, "chars", "player", f"player_{direction}_{frame_num}.png")
    if direction == "left":
        mirrored = pygame.transform.flip(surf, True, False)
        save(mirrored, "chars", "player", f"player_right_{frame_num}.png")

# Frame 0 = idle, Frame 1 = mid-walk
if idle_down:  player_frame(idle_down, "down", 0)
if walk_down and walk_down[1]:  player_frame(walk_down[1], "down", 1)

if idle_up:    player_frame(idle_up, "up", 0)
if walk_up and walk_up[0]:     player_frame(walk_up[0], "up", 1)

if idle_left:  player_frame(idle_left, "left", 0)
if walk_left and walk_left[0]: player_frame(walk_left[0], "left", 1)

# Extra walk frames ke 2 (untuk masa depan jika game diperluas ke 3-frame)
if walk_down and len(walk_down) >= 3 and walk_down[2]:
    player_frame(walk_down[2], "down", 2)
if walk_up and len(walk_up) >= 2 and walk_up[1]:
    player_frame(walk_up[1], "up", 2)

# ═══════════════════════════════════════════════════════════════
#  5. TOOL ICONS  (100×100 → 28×28)
# ═══════════════════════════════════════════════════════════════
print("\n[5] TOOL ICONS")

TOOL_MAP = {
    "cangkul":  "ui/inventory/tools and items/Hoe.png",
    "siram":    "ui/inventory/tools and items/Watering Can.png",
    "panen":    "ui/inventory/tools and items/Sickle.png",
    "kapak":    "ui/inventory/tools and items/Axe.png",
}
# tanam & pancing tidak ada di HM2, pakai procedural fallback

for out_name, src_rel in TOOL_MAP.items():
    surf = load(src_rel)
    if surf:
        save_raw(surf, 28, 28, "items", f"{out_name}.png")

# Bonus: item icons (untuk inventory visual masa depan)
ITEM_MAP = {
    "stroberi_item": "ui/inventory/tools and items/Strawberry.png",
    "lobak_item":    "ui/inventory/tools and items/Turnip.png",
    "gold_icon":     "ui/inventory/tools and items/Gold.png",
}
for out_name, src_rel in ITEM_MAP.items():
    surf = load(src_rel)
    if surf:
        save_raw(surf, 24, 24, "items", f"{out_name}.png")

# ═══════════════════════════════════════════════════════════════
#  6. WEATHER ICONS (untuk HUD)
# ═══════════════════════════════════════════════════════════════
print("\n[6] WEATHER ICONS")

WEATHER_MAP = {
    "Cerah":   "ui/dashboard/weather/Sunny.png",
    "Mendung": "ui/dashboard/weather/Cloudy.png",
    "Hujan":   "ui/dashboard/weather/Raining.png",
    "Badai":   "ui/dashboard/weather/Raining.png",
    "Berangin":"ui/dashboard/weather/Cloudy.png",
}
for weather_name, src_rel in WEATHER_MAP.items():
    surf = load(src_rel)
    if surf:
        save_raw(surf, 24, 24, "ui", "weather", f"{weather_name}.png")

# ═══════════════════════════════════════════════════════════════
#  7. UI ELEMENTS
# ═══════════════════════════════════════════════════════════════
print("\n[7] UI ELEMENTS")

# Hotbar background
hotbar = load("ui/hotbar/Hotbar.png")
if hotbar:
    # Ambil satu slot (1200×162 → 162×162 per slot, ada beberapa slot)
    slot_w = hotbar.get_height()  # slot = square seukuran tinggi hotbar
    slot = crop(hotbar, 0, 0, slot_w, hotbar.get_height())
    save_raw(slot, 40, 30, "ui", "hotbar_slot.png")

# Energy bar
energy_bg = load("ui/energy/Energy Bar Background.png")
energy_fg = load("ui/energy/Energy Bar Filled.png")
if energy_bg:
    save_raw(energy_bg, 20, 100, "ui", "energy_bg.png")
if energy_fg:
    save_raw(energy_fg, 20, 100, "ui", "energy_fg.png")

# Dashboard window
dashboard = load("ui/dashboard/Window.png")
if dashboard:
    save_raw(dashboard, 202, 60, "ui", "dashboard.png")

# ═══════════════════════════════════════════════════════════════
print("\n" + "="*52)
print("  SELESAI! Semua aset diekstrak ke folder assets/")
print("="*52)
print("""
Selanjutnya:
  - Jalankan game: python lembah_karsa_revisi.py
  - Sprite PNG akan otomatis dipakai (fallback ke procedural jika gagal)
  - Weather icons tersimpan di: assets/ui/weather/
  - Tool icons tersimpan di:    assets/items/
  - Crop stages di:             assets/crops/
  - Player di:                  assets/chars/player/
""")

pygame.quit()
