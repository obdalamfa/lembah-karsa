"""
entities.py — Wild entities, NPC AI smooth, Mob combat AI.
Berbasis V15 update_dynamic_ai. Tambah:
  - Mob AI: chase player, attack saat dekat, take damage
  - Mob spawn dari dungeon.generate_dungeon_level
"""
import random
import math
from .config import (G, WALKABLE, BLOCKING, MINEABLE, INVULN_AFTER_HIT_MS,
                     CV_F, MINED, STAIRS_UP, STAIRS_DOWN)
from .scenes import SCENES
from .data import all_npcs, SCHEDULES, ANIMAL_NPCS, SUPERNATURAL_NPCS, MOB_TEMPLATES


def can_walk_at(x, y, scene_name, dungeon_tiles=None):
    """Cek tile walkable. Cast int defensive."""
    x = int(round(x))
    y = int(round(y))
    if scene_name == 'dungeon' and dungeon_tiles:
        if y < 0 or y >= len(dungeon_tiles): return False
        if x < 0 or x >= len(dungeon_tiles[0]): return False
        return dungeon_tiles[y][x] in WALKABLE
    sc = SCENES.get(scene_name)
    if not sc: return False
    if x < 0 or x >= sc.w or y < 0 or y >= sc.h: return False
    return sc.tiles[y][x] in WALKABLE


def get_scene_tiles(state):
    """Return tile array for current scene (dungeon vs static)."""
    if state.scene_name == 'dungeon':
        return state.dungeon_tiles
    return SCENES[state.scene_name].tiles


# ═══════════════════════════════════════════════════════
#  WILD ENTITIES (mandrake, mushroom, firefly, herbs)
# ═══════════════════════════════════════════════════════
def spawn_wild_entities(state):
    if state.wild_entities: return
    rng = random.Random(state.day * 7)

    # 3 mandrake di mountain
    for _ in range(3):
        x, y = rng.randint(2, 28), rng.randint(5, 22)
        state.wild_entities.append({
            'kind': 'mandrake', 'x': x, 'y': y, 'scene': 'mountain', 'moving': False,
        })

    # Running mushrooms di farm + mountain
    for scene in ['farm', 'mountain']:
        for _ in range(3):
            x, y = rng.randint(5, 20), rng.randint(5, 15)
            state.wild_entities.append({
                'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': scene, 'moving': True,
            })

    # Fireflies di farm + town + lake (malam)
    for scene in ['farm', 'town', 'lake']:
        for _ in range(5):
            x, y = rng.randint(3, 20), rng.randint(3, 15)
            state.wild_entities.append({
                'kind': 'firefly', 'x': x, 'y': y, 'scene': scene,
                'moving': True, 'night_only': True,
            })

    # Wild herb/berry di mountain
    for _ in range(15):
        x, y = rng.randint(2, 28), rng.randint(5, 22)
        state.wild_entities.append({
            'kind': rng.choice(['wild_herb', 'wild_berry']),
            'x': x, 'y': y, 'scene': 'mountain', 'moving': False,
        })


def respawn_wild_at_morning(state):
    rng = random.Random()
    for scene in ['farm', 'mountain']:
        for _ in range(rng.randint(2, 4)):
            x, y = rng.randint(2, 20), rng.randint(5, 15)
            state.wild_entities.append({
                'kind': rng.choice(['wild_herb', 'wild_berry']),
                'x': x, 'y': y, 'scene': scene, 'moving': False,
            })


def find_wild_at(state, x, y, scene):
    for w in state.wild_entities:
        if w['scene'] == scene and int(w['x']) == int(x) and int(w['y']) == int(y):
            return w
    return None


def update_wild_entities(state, dt_ms):
    is_night = state.is_night()
    rng = random.Random()
    px, py = state.get_player_tile()

    for w in list(state.wild_entities):
        if w['scene'] != state.scene_name: continue
        if w.get('night_only', False) and not is_night: continue
        if not w.get('moving', False): continue

        dist = abs(w['x'] - px) + abs(w['y'] - py)
        if w['kind'] == 'running_mushroom' and dist <= 3:
            dx = 1 if w['x'] > px else (-1 if w['x'] < px else rng.choice([-1, 1]))
            dy = 1 if w['y'] > py else (-1 if w['y'] < py else 0)
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, w['scene'], state.dungeon_tiles if w['scene']=='dungeon' else None):
                w['x'] = nx; w['y'] = ny
        elif w['kind'] == 'firefly':
            dx, dy = rng.choice([-1, 0, 1]), rng.choice([-1, 0, 1])
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, w['scene']):
                w['x'] = nx; w['y'] = ny


# ═══════════════════════════════════════════════════════
#  NPC SCHEDULE — set scene/x/y target dari schedule
# ═══════════════════════════════════════════════════════
def update_all_npc_positions(state):
    """Refresh scene & target_x/y NPC sesuai schedule jam."""
    hour = state.get_hour()
    for npc_id in all_npcs():
        sched = SCHEDULES.get(npc_id, [])
        if not sched: continue

        # Pilih entry yang aktif (terbesar yang ≤ hour)
        current = sched[0]
        for entry in sched:
            if entry[0] <= hour: current = entry
            else: break
        target_scene = current[3]
        tx, ty = current[1], current[2]

        # Hewan & makhluk halus: AI yang gerakkan, tapi scene ikut schedule
        if npc_id in ANIMAL_NPCS or npc_id in SUPERNATURAL_NPCS:
            if npc_id in state.npc_positions:
                pos = state.npc_positions[npc_id]
                # Scene berubah → teleport
                if pos['scene'] != target_scene:
                    pos['scene'] = target_scene
                    pos['x'] = float(tx) if tx >= 0 else 0.0
                    pos['y'] = float(ty) if ty >= 0 else 0.0
                    pos['target_x'] = pos['x']
                    pos['target_y'] = pos['y']
                pos['activity'] = current[4]
                continue
            # First time spawn
        # Manusia: langsung set target ke schedule
        if npc_id not in state.npc_positions:
            state.npc_positions[npc_id] = {
                'scene': target_scene,
                'x': float(tx), 'y': float(ty),
                'target_x': float(tx), 'target_y': float(ty),
                'activity': current[4],
                'facing': 'down',
            }
        else:
            pos = state.npc_positions[npc_id]
            if pos['scene'] != target_scene:
                pos['scene'] = target_scene
                pos['x'] = float(tx)
                pos['y'] = float(ty)
            pos['target_x'] = float(tx)
            pos['target_y'] = float(ty)
            pos['activity'] = current[4]


# Pen bounds untuk hewan (di farm)
ANIMAL_PEN_BOUNDS = {
    'sapi_betsy':      (15, 2, 21, 7),
    'ayam_kuning':     (15, 2, 21, 7),
    'kambing_jenggot': (15, 2, 21, 7),
    'domba_woolly':    (15, 2, 21, 7),
    'kuda_pegasus':    (15, 2, 21, 7),
    'kucing_oren':     (3, 8, 9, 12),  # halaman
    'rubah_hutan':     (1, 5, 28, 24),  # mountain
    'kelinci_putih':   (1, 5, 28, 24),
    'bebek_donald':    (3, 4, 14, 11),  # lake
}


def update_dynamic_ai(state, dt_ms):
    """V15-style state machine AI: tuyul kabur, hewan tidur malam, jin melayang.
    Smooth lerp movement ke target_x/y. Update facing.
    """
    rng = random.Random()
    px, py = state.get_player_tile()

    for npc_id, pos in state.npc_positions.items():
        if pos['scene'] != state.scene_name: continue
        if pos.get('x', 0) < 0: continue  # hidden

        # Pastikan target_x/y ada
        if 'target_x' not in pos:
            pos['target_x'] = pos['x']
            pos['target_y'] = pos['y']

        tx, ty = pos['target_x'], pos['target_y']
        dist_to_player = math.hypot(pos['x'] - px, pos['y'] - py)
        speed = 1.5 / 1000.0
        is_moving = abs(pos['x'] - tx) > 0.01 or abs(pos['y'] - ty) > 0.01

        # ─── AI: TUYUL PENCURI (kabur kalau dikejar) ───
        if npc_id == 'tuyul_pencuri':
            if dist_to_player < 4.0:
                pos['activity'] = 'Panik Kabur!'
                speed = 4.5 / 1000.0
                if not is_moving:
                    dx = 1 if pos['x'] > px else -1
                    dy = 1 if pos['y'] > py else -1
                    nx = int(pos['x']) + dx * rng.randint(2, 4)
                    ny = int(pos['y']) + dy * rng.randint(2, 4)
                    if can_walk_at(nx, ny, state.scene_name, state.dungeon_tiles):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)
            else:
                pos['activity'] = 'Mengintai'
                speed = 1.2 / 1000.0
                if not is_moving and rng.random() < 0.02:
                    nx = int(pos['x']) + rng.choice([-1, 0, 1])
                    ny = int(pos['y']) + rng.choice([-1, 0, 1])
                    if can_walk_at(nx, ny, state.scene_name, state.dungeon_tiles):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── AI: HEWAN TERNAK (tidur malam, makan rumput siang) ───
        elif npc_id in ANIMAL_NPCS:
            if state.is_night():
                pos['activity'] = 'Tidur 💤'
                pos['target_x'] = pos['x']
                pos['target_y'] = pos['y']
                continue
            else:
                pos['activity'] = 'Makan Rumput'
                if not is_moving and rng.random() < 0.02:
                    bounds = ANIMAL_PEN_BOUNDS.get(npc_id, (3, 3, 22, 12))
                    nx = int(pos['x']) + rng.choice([-1, 0, 0, 1])
                    ny = int(pos['y']) + rng.choice([-1, 0, 0, 1])
                    nx = max(bounds[0], min(bounds[2], nx))
                    ny = max(bounds[1], min(bounds[3], ny))
                    if can_walk_at(nx, ny, state.scene_name, state.dungeon_tiles):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── AI: JIN KEBUN (melayang misterius) ───
        elif npc_id == 'jin_kebun':
            pos['activity'] = 'Melayang Misterius'
            speed = 0.8 / 1000.0
            if not is_moving and rng.random() < 0.01:
                nx = int(pos['x']) + rng.choice([-2, 0, 2])
                ny = int(pos['y']) + rng.choice([-2, 0, 2])
                if can_walk_at(nx, ny, state.scene_name, state.dungeon_tiles):
                    pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── AI: SUPERNATURAL LAIN (drift pelan) ───
        elif npc_id in SUPERNATURAL_NPCS:
            speed = 0.7 / 1000.0
            if not is_moving and rng.random() < 0.008:
                nx = int(pos['x']) + rng.choice([-1, 0, 1])
                ny = int(pos['y']) + rng.choice([-1, 0, 1])
                if can_walk_at(nx, ny, state.scene_name, state.dungeon_tiles):
                    pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── EKSEKUSI LERP MOVEMENT (smooth) ───
        if abs(pos['x'] - tx) > 0.01 or abs(pos['y'] - ty) > 0.01:
            dx, dy = tx - pos['x'], ty - pos['y']
            dist = math.hypot(dx, dy)
            move_dist = speed * dt_ms
            if dist <= move_dist:
                pos['x'], pos['y'] = float(tx), float(ty)
            else:
                pos['x'] += (dx / dist) * move_dist
                pos['y'] += (dy / dist) * move_dist
            # Update facing
            if abs(dx) > abs(dy):
                pos['facing'] = 'right' if dx > 0 else 'left'
            else:
                pos['facing'] = 'down' if dy > 0 else 'up'


def init_npc_data(state):
    for npc_id in all_npcs():
        if npc_id not in state.npc_hearts: state.npc_hearts[npc_id] = 0
        if npc_id not in state.npc_dialog_index: state.npc_dialog_index[npc_id] = 0
    update_all_npc_positions(state)


# ═══════════════════════════════════════════════════════
#  MOB AI — Combat di dungeon
# ═══════════════════════════════════════════════════════
def update_mobs(state, dt_ms):
    """Update semua mob:
    - Chase player jika dalam range
    - Attack player jika kontak
    - Apply damage flash timer
    - Track death (drops + xp)
    """
    if state.scene_name != 'dungeon': return
    if not state.mobs: return

    px, py = state.player_x, state.player_y

    for mob in list(state.mobs):
        # Damage flash decay
        if mob.get('dmg_flash_ms', 0) > 0:
            mob['dmg_flash_ms'] = max(0, mob['dmg_flash_ms'] - dt_ms)
        if mob.get('attack_cooldown_ms', 0) > 0:
            mob['attack_cooldown_ms'] = max(0, mob['attack_cooldown_ms'] - dt_ms)

        dist = math.hypot(mob['x'] - px, mob['y'] - py)

        # Mati?
        if mob['hp'] <= 0:
            # Drop loot ke inventory
            for item, n in mob.get('drops', {}).items():
                state.inventory[item] = state.inventory.get(item, 0) + n
            state.stats['mobs_killed'] = state.stats.get('mobs_killed', 0) + 1
            # Naga boss?
            if mob.get('is_boss'):
                state.naga_defeated = True
            state.mobs.remove(mob)
            continue

        # Chase logic
        chase_range = 8.0 if mob.get('is_boss') else 6.0
        if dist <= chase_range:
            # Move toward player (simple direct chase)
            speed_per_ms = mob['speed'] / 1000.0
            move = speed_per_ms * dt_ms
            if dist > 0.3:
                dx = (px - mob['x']) / dist
                dy = (py - mob['y']) / dist
                new_x = mob['x'] + dx * move
                new_y = mob['y'] + dy * move
                # Cek collision dengan dinding
                if can_walk_at(new_x, mob['y'], 'dungeon', state.dungeon_tiles):
                    mob['x'] = new_x
                if can_walk_at(mob['x'], new_y, 'dungeon', state.dungeon_tiles):
                    mob['y'] = new_y
                # Update facing
                if abs(dx) > abs(dy):
                    mob['facing'] = 'right' if dx > 0 else 'left'
                else:
                    mob['facing'] = 'down' if dy > 0 else 'up'

        # Attack player jika kontak
        attack_range = 1.5 if mob.get('is_boss') else 1.0
        if dist <= attack_range and mob.get('attack_cooldown_ms', 0) <= 0:
            if state.invuln_timer_ms <= 0:
                state.hp = max(0, state.hp - mob['damage'])
                state.invuln_timer_ms = INVULN_AFTER_HIT_MS
                mob['attack_cooldown_ms'] = 1000  # mob attack tiap 1 detik


def damage_mob(state, mob, damage):
    """Apply damage ke mob, set flash timer. Tidak remove di sini (update_mobs handle)."""
    mob['hp'] -= damage
    mob['dmg_flash_ms'] = 200
