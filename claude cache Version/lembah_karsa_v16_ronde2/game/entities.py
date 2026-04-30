"""
entities.py — Logic untuk wild entities (mandrake, jamur lari, kunang)
dan NPC AI (schedule + animal roaming).

v5: support multi-scene untuk wild entities (tidak cuma 'outdoor').
"""
import random
from .config import G, WALKABLE
from .scenes import SCENES
from .data import all_npcs, SCHEDULES


# ═══════════════════════════════════════════════════
#  WILD ENTITIES
# ═══════════════════════════════════════════════════
def _has_wild_at(state, scene, x, y):
    for w in state.wild_entities:
        if w['scene'] == scene and w['x'] == x and w['y'] == y:
            return True
    return False


def spawn_wild_entities(state):
    """Spawn awal — dipanggil saat new game."""
    if state.wild_entities:
        return
    rng = random.Random(state.day * 7)
    outdoor = SCENES['outdoor']

    # Mandrake — 3 di hutan dalam outdoor (rare, langka)
    for _ in range(3):
        for _ in range(20):
            x, y = rng.randint(0, 11), rng.randint(22, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'mandrake', 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Mandrake bonus di cemetery_z3 (zona terdalam, sangat rare)
    cz3 = SCENES['cemetery_z3']
    for _ in range(2):
        for _ in range(15):
            x, y = rng.randint(2, cz3.w - 3), rng.randint(2, cz3.h - 3)
            if cz3.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'mandrake', 'x': x, 'y': y, 'scene': 'cemetery_z3',
                    'spooked': False, 'night_only': False,
                })
                break

    # Running mushroom — 5 di hutan outdoor
    for _ in range(5):
        for _ in range(20):
            x, y = rng.randint(0, 17), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': 'outdoor',
                    'moving': True, 'spooked': False, 'night_only': False,
                })
                break

    # Mushroom di bat_cave (dalam gelap)
    bc = SCENES['bat_cave']
    for _ in range(3):
        for _ in range(15):
            x, y = rng.randint(2, bc.w - 3), rng.randint(2, bc.h - 3)
            from .config import CV_F, BAT_D
            if bc.tiles[y][x] in (CV_F, BAT_D):
                state.wild_entities.append({
                    'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': 'bat_cave',
                    'moving': True, 'spooked': False, 'night_only': False,
                })
                break

    # Firefly — 8 di outdoor (malam)
    for _ in range(8):
        for _ in range(20):
            x = rng.randint(0, 49)
            y = rng.randint(15, 33)
            if 0 <= x < outdoor.w and 0 <= y < outdoor.h:
                if outdoor.tiles[y][x] == G:
                    state.wild_entities.append({
                        'kind': 'firefly', 'x': x, 'y': y, 'scene': 'outdoor',
                        'moving': True, 'spooked': False, 'night_only': True,
                    })
                    break

    # Firefly bonus di lake (estetika malam danau)
    lake = SCENES['lake']
    for _ in range(5):
        for _ in range(15):
            x, y = rng.randint(2, lake.w - 3), rng.randint(2, lake.h - 3)
            if lake.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'firefly', 'x': x, 'y': y, 'scene': 'lake',
                    'moving': True, 'spooked': False, 'night_only': True,
                })
                break

    # Wild herb — 15 di outdoor
    for _ in range(15):
        for _ in range(20):
            x, y = rng.randint(0, 49), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'wild_herb', 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Wild berry — 10 di outdoor
    for _ in range(10):
        for _ in range(20):
            x, y = rng.randint(0, 49), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'wild_berry', 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break


def respawn_wild_at_morning(state):
    """Spawn herbs/berries baru di pagi hari + isi mushroom kalau kurang."""
    rng = random.Random()
    outdoor = SCENES['outdoor']

    # 2-4 herb/berry baru di outdoor
    for _ in range(rng.randint(2, 4)):
        for _ in range(15):
            x, y = rng.randint(0, 49), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G and not _has_wild_at(state, 'outdoor', x, y):
                kind = rng.choice(['wild_herb', 'wild_berry'])
                state.wild_entities.append({
                    'kind': kind, 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Top up mushroom di outdoor
    mushrooms_out = [w for w in state.wild_entities
                     if w['kind'] == 'running_mushroom' and w['scene'] == 'outdoor']
    if len(mushrooms_out) < 5:
        for _ in range(5 - len(mushrooms_out)):
            for _ in range(15):
                x, y = rng.randint(0, 17), rng.randint(15, 33)
                if outdoor.tiles[y][x] == G and not _has_wild_at(state, 'outdoor', x, y):
                    state.wild_entities.append({
                        'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': 'outdoor',
                        'moving': True, 'spooked': False, 'night_only': False,
                    })
                    break


def find_wild_at(state, x, y, scene='outdoor'):
    for w in state.wild_entities:
        if w['scene'] == scene and w['x'] == x and w['y'] == y:
            return w
    return None


def update_wild_entities(state, dt_ms):
    """Update gerakan wild entities (jamur lari, kunang melayang)."""
    is_night = state.is_night()
    rng = random.Random()
    px, py = state.get_player_tile()

    for w in list(state.wild_entities):
        # Hanya entitas di scene yang sama dengan player yang bergerak
        if w['scene'] != state.scene_name:
            continue
        if w.get('night_only', False) and not is_night:
            continue
        if not w.get('moving', False):
            continue

        dist = abs(w['x'] - px) + abs(w['y'] - py)

        if w['kind'] == 'running_mushroom' and dist <= 3:
            dx = 1 if w['x'] > px else (-1 if w['x'] < px else rng.choice([-1, 1]))
            dy = 1 if w['y'] > py else (-1 if w['y'] < py else 0)
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, w['scene']):
                w['x'] = nx; w['y'] = ny
        elif w['kind'] == 'firefly':
            dx = rng.choice([-1, 0, 1])
            dy = rng.choice([-1, 0, 1])
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, w['scene']):
                w['x'] = nx; w['y'] = ny


def can_walk_at(x, y, scene_name):
    sc = SCENES.get(scene_name)
    if not sc:
        return False
    # Cast ke int — pos NPC bisa float (smooth movement)
    x = int(round(x))
    y = int(round(y))
    if x < 0 or x >= sc.w or y < 0 or y >= sc.h:
        return False
    return sc.tiles[y][x] in WALKABLE


# ═══════════════════════════════════════════════════
#  NPC SCHEDULE UPDATE
# ═══════════════════════════════════════════════════
NPC_WALK_SPEED_TILES_PER_SEC = 1.5  # NPC jalan lebih lambat dari player


def update_all_npc_positions(state):
    """Set TARGET position NPC sesuai schedule & jam.
    NPC akan smooth-walk ke target tiap frame via update_npc_smooth_movement().
    """
    hour = state.get_hour()
    from .data import ANIMAL_NPCS

    for npc_id in all_npcs():
        sched = SCHEDULES.get(npc_id, [])
        if not sched:
            continue

        # Cari entry schedule aktif (jam terbesar yang ≤ hour saat ini)
        current = sched[0]
        for entry in sched:
            if entry[0] <= hour:
                current = entry
            else:
                break

        target_scene = current[3]
        target_x = current[1]
        target_y = current[2]
        activity = current[4]

        # Hewan ternak: hanya update activity & scene, biarkan x,y free-roam
        if npc_id in ANIMAL_NPCS and npc_id in state.npc_positions:
            existing = state.npc_positions[npc_id]
            existing['scene'] = target_scene
            existing['activity'] = activity
            # Hewan tidak punya target — animal_roaming yang gerakkan
            existing['target_x'] = existing.get('x', target_x)
            existing['target_y'] = existing.get('y', target_y)
            continue

        # Cek apakah NPC sudah ada (continuing) atau baru spawn
        if npc_id not in state.npc_positions:
            # First time — teleport ke target
            state.npc_positions[npc_id] = {
                'scene': target_scene,
                'x': float(target_x),
                'y': float(target_y),
                'target_x': float(target_x),
                'target_y': float(target_y),
                'activity': activity,
                'facing': 'down',
            }
        else:
            existing = state.npc_positions[npc_id]
            # Jika scene berubah (NPC pindah ruang), teleport (jangan smooth-walk lintas-scene)
            if existing.get('scene') != target_scene:
                existing['scene'] = target_scene
                existing['x'] = float(target_x)
                existing['y'] = float(target_y)
            # Set target baru (smooth walk akan interpolasi)
            existing['target_x'] = float(target_x)
            existing['target_y'] = float(target_y)
            existing['activity'] = activity


def update_npc_smooth_movement(state, dt_ms):
    """Tiap frame, gerakkan NPC ke target_x/y dengan kecepatan smooth.
    Update juga 'facing' agar arah sprite mengikuti gerakan."""
    from .data import ANIMAL_NPCS
    speed_per_ms = NPC_WALK_SPEED_TILES_PER_SEC / 1000.0
    delta = speed_per_ms * dt_ms

    for npc_id, pos in state.npc_positions.items():
        # Hewan ternak handled di update_animal_roaming
        if npc_id in ANIMAL_NPCS:
            continue
        if 'target_x' not in pos:
            continue
        # Hanya smooth-walk NPC di scene yang aktif (hemat CPU)
        # Tapi NPC di scene lain pun harus pelan-pelan sampai ke target
        # (kalau player masuk scene itu, NPC sudah di posisi). Jadi tetap update.
        cx = pos['x']
        cy = pos['y']
        tx = pos['target_x']
        ty = pos['target_y']
        dx = tx - cx
        dy = ty - cy
        dist = (dx * dx + dy * dy) ** 0.5
        if dist < 0.05:
            pos['x'] = tx
            pos['y'] = ty
            continue
        # Pilih facing
        if abs(dx) > abs(dy):
            pos['facing'] = 'right' if dx > 0 else 'left'
        else:
            pos['facing'] = 'down' if dy > 0 else 'up'
        # Move
        if dist < delta:
            pos['x'] = tx
            pos['y'] = ty
        else:
            pos['x'] = cx + (dx / dist) * delta
            pos['y'] = cy + (dy / dist) * delta


# Pen boundary untuk hewan ternak (x_min, y_min, x_max, y_max) di outdoor
ANIMAL_PEN_BOUNDS = {
    'sapi_betsy':     (3, 10, 7, 11),
    'ayam_kuning':    (3, 10, 7, 11),
    'kambing_jenggot':(3, 10, 7, 11),
    'domba_woolly':   (3, 10, 7, 11),
    'kuda_pegasus':   (3, 10, 7, 11),
    # Bebek di danau (outdoor sungai kecil & lake)
    'bebek_donald':   (6, 19, 11, 21),
}


def update_animal_roaming(state, dt_ms):
    """Free-roam AI untuk hewan ternak. Random walk dalam pen."""
    from .data import ANIMAL_NPCS
    import random as _random

    if not hasattr(update_animal_roaming, '_timer'):
        update_animal_roaming._timer = 0
    update_animal_roaming._timer += dt_ms
    if update_animal_roaming._timer < 1500:
        return
    update_animal_roaming._timer = 0

    rng = _random.Random()
    for npc_id in ANIMAL_NPCS:
        if npc_id not in state.npc_positions:
            continue
        pos = state.npc_positions[npc_id]
        if pos['scene'] != 'outdoor':
            continue
        if rng.random() < 0.4:
            continue

        bounds = ANIMAL_PEN_BOUNDS.get(npc_id, (3, 10, 7, 11))
        x_min, y_min, x_max, y_max = bounds

        # Hewan walk grid-based (tidak smooth) — pakai int posisi
        cur_x = int(round(pos['x']))
        cur_y = int(round(pos['y']))
        dx = rng.choice([-1, 0, 0, 1])
        dy = rng.choice([-1, 0, 0, 1])
        nx = cur_x + dx
        ny = cur_y + dy
        nx = max(x_min, min(x_max, nx))
        ny = max(y_min, min(y_max, ny))

        npc_data = ANIMAL_NPCS.get(npc_id, {})
        if npc_data.get('type') == 'bebek':
            # Bebek bisa di air
            if 0 <= nx < SCENES['outdoor'].w and 0 <= ny < SCENES['outdoor'].h:
                pos['x'] = float(nx)
                pos['y'] = float(ny)
        else:
            if can_walk_at(nx, ny, 'outdoor'):
                pos['x'] = float(nx)
                pos['y'] = float(ny)


def init_npc_data(state):
    """Pastikan semua NPC punya entry di hearts/dialog_index."""
    for npc_id in all_npcs():
        if npc_id not in state.npc_hearts:
            state.npc_hearts[npc_id] = 0
        if npc_id not in state.npc_dialog_index:
            state.npc_dialog_index[npc_id] = 0
    update_all_npc_positions(state)
