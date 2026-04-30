"""
dungeon.py — Random roguelike dungeon generator.

Setiap kali player turun (STAIRS_DOWN), generate ulang layout level berikutnya:
  - Goa berbentuk cellular automata (organic shape)
  - Spawn ore tile berdasarkan level (deeper = better minerals)
  - Spawn mob berdasarkan level
  - 1 tangga ke bawah (STAIRS_DOWN) di lokasi random
  - 1 tangga ke atas (STAIRS_UP) tempat player muncul
  - Boss naga di level 15: arena khusus + 1 tangga keluar

Player bisa turun dengan:
  1. Berdiri di STAIRS_DOWN → otomatis turun
  2. Cangkul tile dirt random → 30% chance muncul tangga (Spelunky style)

Player naik dengan STAIRS_UP.
"""
import random
from .config import (CV_W, CV_F, MINED, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH,
                     STAIRS_DOWN, STAIRS_UP, CRYS, D)
from .data import MOB_TEMPLATES, NAGA_BOSS, DUNGEON_MAX_LEVEL


# Tile probability table per level (spawn rate untuk ore tiles)
ORE_SPAWN_TABLE = {
    # level: [(tile, weight), ...]
    1: [(ORE_TBG, 8), (CV_W, 92)],
    2: [(ORE_TBG, 10), (CV_W, 90)],
    3: [(ORE_TBG, 8), (ORE_BSI, 4), (CV_W, 88)],
    4: [(ORE_TBG, 6), (ORE_BSI, 6), (ORE_KRS, 2), (CV_W, 86)],
    5: [(ORE_TBG, 5), (ORE_BSI, 8), (ORE_KRS, 3), (CV_W, 84)],
    6: [(ORE_BSI, 8), (ORE_EMS, 3), (ORE_KRS, 4), (CV_W, 85)],
    7: [(ORE_BSI, 7), (ORE_EMS, 4), (ORE_KRS, 5), (CV_W, 84)],
    8: [(ORE_BSI, 5), (ORE_EMS, 6), (ORE_KRS, 5), (CV_W, 84)],
    9: [(ORE_EMS, 7), (ORE_KRS, 6), (ORE_BSI, 3), (CV_W, 84)],
    10: [(ORE_EMS, 6), (ORE_MTH, 2), (ORE_KRS, 5), (CV_W, 87)],
    11: [(ORE_EMS, 5), (ORE_MTH, 4), (ORE_KRS, 5), (CV_W, 86)],
    12: [(ORE_EMS, 4), (ORE_MTH, 6), (CRYS, 4), (CV_W, 86)],
    13: [(ORE_MTH, 8), (ORE_EMS, 3), (CRYS, 5), (CV_W, 84)],
    14: [(ORE_MTH, 10), (CRYS, 8), (ORE_EMS, 2), (CV_W, 80)],
    15: [(CRYS, 15), (ORE_MTH, 8), (CV_W, 77)],  # level naga: kristal khas
}


def _weighted_choice(rng, options):
    """options: [(item, weight), ...]"""
    total = sum(w for _, w in options)
    r = rng.random() * total
    cum = 0
    for item, w in options:
        cum += w
        if r <= cum:
            return item
    return options[-1][0]


def _cellular_automata_step(grid, w, h):
    """Cellular automata: tile jadi wall jika ≥5 tetangga wall."""
    new_grid = [row[:] for row in grid]
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            wall_count = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if grid[y + dy][x + dx] == CV_W:
                        wall_count += 1
            new_grid[y][x] = CV_W if wall_count >= 5 else CV_F
    return new_grid


def generate_dungeon_level(level, seed=None):
    """Generate satu level dungeon. Return (tiles, spawn_x, spawn_y, mob_specs).
    
    mob_specs: list of dict {kind, x, y, hp, damage, speed, drops, xp}
    """
    if seed is None:
        seed = random.randint(0, 999999)
    rng = random.Random(seed)
    w, h = 24, 18

    # ─── PHASE 1: Random fill ───
    # Initial: 45% wall, 55% floor (cellular automata default)
    grid = [[CV_W if rng.random() < 0.45 else CV_F for _ in range(w)]
            for _ in range(h)]
    # Border = wall
    for x in range(w):
        grid[0][x] = CV_W
        grid[h - 1][x] = CV_W
    for y in range(h):
        grid[y][0] = CV_W
        grid[y][w - 1] = CV_W

    # ─── PHASE 2: 4 step cellular automata (smooth) ───
    for _ in range(4):
        grid = _cellular_automata_step(grid, w, h)

    # ─── PHASE 3: Replace some CV_W with ore tiles ───
    spawn_table = ORE_SPAWN_TABLE.get(level, ORE_SPAWN_TABLE[1])
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if grid[y][x] == CV_W:
                # Replace dengan weighted random choice
                grid[y][x] = _weighted_choice(rng, spawn_table)

    # ─── PHASE 4: Pastikan ada ruang spawn (flood fill biggest room) ───
    # Cari semua sel CV_F yang reachable dari titik tengah
    floor_cells = []
    for y in range(1, h - 1):
        for x in range(1, w - 1):
            if grid[y][x] == CV_F:
                floor_cells.append((x, y))

    if not floor_cells:
        # Edge case: tidak ada floor, paksa buat
        cx, cy = w // 2, h // 2
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                grid[cy + dy][cx + dx] = CV_F
        floor_cells = [(cx + dx, cy + dy) for dy in range(-2, 3) for dx in range(-2, 3)]

    # ─── PHASE 5: Tempatkan STAIRS_UP (spawn point player) ───
    spawn_x, spawn_y = rng.choice(floor_cells)
    grid[spawn_y][spawn_x] = STAIRS_UP
    # Pastikan spawn aman (3x3 cleared)
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            nx, ny = spawn_x + dx, spawn_y + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1:
                if grid[ny][nx] == CV_W or grid[ny][nx] in [ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH]:
                    grid[ny][nx] = CV_F
    grid[spawn_y][spawn_x] = STAIRS_UP

    # ─── PHASE 6: Tempatkan STAIRS_DOWN (kecuali level 15 = boss) ───
    if level < DUNGEON_MAX_LEVEL:
        # Cari spot floor jauh dari spawn
        far_cells = [c for c in floor_cells
                     if abs(c[0] - spawn_x) + abs(c[1] - spawn_y) >= 8]
        if far_cells:
            dx_, dy_ = rng.choice(far_cells)
            grid[dy_][dx_] = STAIRS_DOWN
        else:
            dx_, dy_ = rng.choice(floor_cells)
            grid[dy_][dx_] = STAIRS_DOWN

    # ─── PHASE 7: Spawn mobs ───
    mob_specs = []
    if level == DUNGEON_MAX_LEVEL:
        # Boss arena: hanya naga, jauh dari spawn
        far_cells = [c for c in floor_cells if (c[0], c[1]) != (spawn_x, spawn_y)
                     and abs(c[0] - spawn_x) + abs(c[1] - spawn_y) >= 6]
        if far_cells:
            bx, by = rng.choice(far_cells)
            mob_specs.append({
                'kind': 'naga_boss',
                'x': float(bx), 'y': float(by),
                'hp': NAGA_BOSS['hp'],
                'max_hp': NAGA_BOSS['hp'],
                'damage': NAGA_BOSS['damage'],
                'speed': NAGA_BOSS['speed'],
                'drops': dict(NAGA_BOSS['drops']),
                'xp': 200,
                'is_boss': True,
                'target_x': float(bx),
                'target_y': float(by),
                'dmg_flash_ms': 0,
                'attack_cooldown_ms': 0,
            })
    else:
        # Mob normal: pilih spesies yang sesuai level
        eligible = [k for k, m in MOB_TEMPLATES.items()
                    if m['min_lvl'] <= level <= m['max_lvl']]
        n_mobs = min(3 + level // 2, 8)
        avail_cells = [c for c in floor_cells
                       if (c[0], c[1]) != (spawn_x, spawn_y)
                       and abs(c[0] - spawn_x) + abs(c[1] - spawn_y) >= 4]
        rng.shuffle(avail_cells)
        for i in range(min(n_mobs, len(avail_cells))):
            mx, my = avail_cells[i]
            kind = rng.choice(eligible)
            tmpl = MOB_TEMPLATES[kind]
            mob_specs.append({
                'kind': kind,
                'x': float(mx), 'y': float(my),
                'hp': tmpl['hp'],
                'max_hp': tmpl['hp'],
                'damage': tmpl['damage'],
                'speed': tmpl['speed'],
                'drops': dict(tmpl['drops']),
                'xp': tmpl['xp'],
                'is_boss': False,
                'target_x': float(mx),
                'target_y': float(my),
                'dmg_flash_ms': 0,
                'attack_cooldown_ms': 0,
            })

    return grid, spawn_x, spawn_y, mob_specs


def random_stairs_chance(level, rng=None):
    """Cangkul tanah → 30% chance muncul tangga (Spelunky style).
    Lebih dalam = chance lebih tinggi (memudahkan eksplorasi lower levels)."""
    if rng is None:
        rng = random
    if level >= DUNGEON_MAX_LEVEL:
        return False  # tidak ada tangga di level boss
    chance = 0.30 + min(0.20, level * 0.02)  # max 50% di level 10+
    return rng.random() < chance
