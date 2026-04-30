"""
entities.py — Logic untuk wild entities dan NPC AI (termasuk State Machine).
"""
import random
import math
from .config import G
from .scenes import SCENES
from .data import all_npcs, SCHEDULES, ANIMAL_NPCS, SUPERNATURAL_NPCS

def spawn_wild_entities(state):
    if state.wild_entities: return
    rng = random.Random(state.day * 7)

    for _ in range(3):
        x, y = rng.randint(0, 29), rng.randint(4, 24)
        state.wild_entities.append({'kind': 'mandrake', 'x': x, 'y': y, 'scene': 'mountain', 'moving': False})

    for scene in ['mountain', 'farm']:
        for _ in range(3):
            x, y = rng.randint(5, 20), rng.randint(5, 15)
            state.wild_entities.append({'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': scene, 'moving': True})

    for scene in ['farm', 'town']:
        for _ in range(5):
            x, y = rng.randint(5, 20), rng.randint(5, 15)
            state.wild_entities.append({'kind': 'firefly', 'x': x, 'y': y, 'scene': scene, 'moving': True, 'night_only': True})

    for _ in range(15):
        x, y = rng.randint(0, 29), rng.randint(4, 24)
        state.wild_entities.append({'kind': rng.choice(['wild_herb', 'wild_berry']), 'x': x, 'y': y, 'scene': 'mountain', 'moving': False})

def respawn_wild_at_morning(state):
    rng = random.Random()
    for scene in ['farm', 'mountain']:
        for _ in range(rng.randint(2, 4)):
            x, y = rng.randint(0, 20), rng.randint(5, 15)
            state.wild_entities.append({'kind': rng.choice(['wild_herb', 'wild_berry']), 'x': x, 'y': y, 'scene': scene, 'moving': False})

def find_wild_at(state, x, y, scene):
    for w in state.wild_entities:
        if w['scene'] == scene and w['x'] == x and w['y'] == y: return w
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
            if can_walk_at(nx, ny, w['scene']):
                w['x'] = nx; w['y'] = ny
        elif w['kind'] == 'firefly':
            dx, dy = rng.choice([-1, 0, 1]), rng.choice([-1, 0, 1])
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, w['scene']):
                w['x'] = nx; w['y'] = ny

def can_walk_at(x, y, scene_name):
    from .config import WALKABLE
    sc = SCENES.get(scene_name)
    if not sc: return False
    if x < 0 or x >= sc.w or y < 0 or y >= sc.h: return False
    return sc.tiles[y][x] in WALKABLE

def update_all_npc_positions(state):
    hour = state.get_hour()
    for npc_id in all_npcs():
        sched = SCHEDULES.get(npc_id, [])
        if not sched: continue
        
        # Biarkan AI yang mengatur X dan Y untuk hewan & makhluk halus
        if npc_id in ANIMAL_NPCS or npc_id in SUPERNATURAL_NPCS:
            if npc_id in state.npc_positions:
                current = sched[0]
                for entry in sched:
                    if entry[0] <= hour: current = entry
                    else: break
                state.npc_positions[npc_id]['scene'] = current[3]
                continue
            
        current = sched[0]
        for entry in sched:
            if entry[0] <= hour: current = entry
            else: break
        state.npc_positions[npc_id] = {'scene': current[3], 'x': current[1], 'y': current[2], 'activity': current[4]}

# Batas Kandang
ANIMAL_PEN_BOUNDS = {
    'sapi_betsy':     (15, 2, 21, 7),
    'ayam_kuning':    (15, 2, 21, 7),
    'kambing_jenggot':(15, 2, 21, 7),
}

def update_dynamic_ai(state, dt_ms):
    """State Machine AI untuk Makhluk Halus, Hewan, dan NPC."""
    import random as _random
    rng = _random.Random()
    px, py = state.get_player_tile()

    for npc_id, pos in state.npc_positions.items():
        if pos['scene'] != state.scene_name: continue

        if 'target_x' not in pos:
            pos['target_x'] = pos['x']
            pos['target_y'] = pos['y']

        tx, ty = pos['target_x'], pos['target_y']
        dist_to_player = math.hypot(pos['x'] - px, pos['y'] - py)
        speed = 1.5 / 1000.0
        is_moving = abs(pos['x'] - tx) > 0.01 or abs(pos['y'] - ty) > 0.01

        # ─── AI: TUYUL PENCURI ───
        if npc_id == 'tuyul_pencuri':
            if dist_to_player < 4.0:
                pos['activity'] = 'Panik Kabur!'
                speed = 4.5 / 1000.0 # Lari ngebut
                if not is_moving:
                    dx = 1 if pos['x'] > px else -1
                    dy = 1 if pos['y'] > py else -1
                    nx = int(pos['x']) + dx * rng.randint(2, 4)
                    ny = int(pos['y']) + dy * rng.randint(2, 4)
                    if can_walk_at(nx, ny, state.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)
            else:
                pos['activity'] = 'Mengintai Lahan'
                speed = 1.2 / 1000.0
                if not is_moving and rng.random() < 0.02:
                    nx = int(pos['x']) + rng.choice([-1, 0, 1])
                    ny = int(pos['y']) + rng.choice([-1, 0, 1])
                    if can_walk_at(nx, ny, state.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── AI: HEWAN TERNAK ───
        elif npc_id in ANIMAL_NPCS:
            if state.is_night():
                pos['activity'] = 'Tidur 💤'
                pos['target_x'] = pos['x']
                continue
            else:
                pos['activity'] = 'Makan Rumput'
                if not is_moving and rng.random() < 0.02:
                    bounds = ANIMAL_PEN_BOUNDS.get(npc_id, (15, 2, 21, 7))
                    nx = int(pos['x']) + rng.choice([-1, 0, 0, 1])
                    ny = int(pos['y']) + rng.choice([-1, 0, 0, 1])
                    nx = max(bounds[0], min(bounds[2], nx))
                    ny = max(bounds[1], min(bounds[3], ny))
                    if can_walk_at(nx, ny, state.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── AI: JIN KEBUN ───
        elif npc_id == 'jin_kebun':
            pos['activity'] = 'Melayang Misterius'
            speed = 0.8 / 1000.0
            if not is_moving and rng.random() < 0.01:
                nx = int(pos['x']) + rng.choice([-2, 0, 2])
                ny = int(pos['y']) + rng.choice([-2, 0, 2])
                if can_walk_at(nx, ny, state.scene_name):
                    pos['target_x'], pos['target_y'] = float(nx), float(ny)

        # ─── EKSEKUSI LERP MOVEMENT ───
        if abs(pos['x'] - tx) > 0.01 or abs(pos['y'] - ty) > 0.01:
            dx, dy = tx - pos['x'], ty - pos['y']
            dist = math.hypot(dx, dy)
            move_dist = speed * dt_ms
            if dist <= move_dist:
                pos['x'], pos['y'] = float(tx), float(ty)
            else:
                pos['x'] += (dx / dist) * move_dist
                pos['y'] += (dy / dist) * move_dist

def init_npc_data(state):
    for npc_id in all_npcs():
        if npc_id not in state.npc_hearts: state.npc_hearts[npc_id] = 0
        if npc_id not in state.npc_dialog_index: state.npc_dialog_index[npc_id] = 0
