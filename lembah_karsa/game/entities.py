"""
entities.py — Logic untuk wild entities (mandrake, jamur lari, kunang) dan NPC AI.
"""
import random
from .config import G
from .scenes import SCENES
from .data import all_npcs, SCHEDULES


# ═══════════════════════════════════════════════════
#  WILD ENTITIES
# ═══════════════════════════════════════════════════
def spawn_wild_entities(state):
    """Spawn awal — dipanggil saat new game."""
    if state.wild_entities:
        return
    rng = random.Random(state.day * 7)
    outdoor = SCENES['outdoor']

    # Mandrake — 3 di hutan dalam (rare)
    for _ in range(3):
        for _ in range(20):
            x, y = rng.randint(0, 11), rng.randint(22, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'mandrake', 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Running mushroom — 5 di hutan
    for _ in range(5):
        for _ in range(20):
            x, y = rng.randint(0, 17), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'running_mushroom', 'x': x, 'y': y, 'scene': 'outdoor',
                    'moving': True, 'spooked': False, 'night_only': False,
                })
                break

    # Firefly — 8, malam saja
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

    # Wild herb — 15
    for _ in range(15):
        for _ in range(20):
            x, y = rng.randint(0, 49), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G:
                state.wild_entities.append({
                    'kind': 'wild_herb', 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Wild berry — 10
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
    """Spawn baru di pagi hari."""
    rng = random.Random()
    outdoor = SCENES['outdoor']

    def has_wild_at(x, y):
        for w in state.wild_entities:
            if w['scene'] == 'outdoor' and w['x'] == x and w['y'] == y:
                return True
        return False

    # 2-4 herb/berry baru
    for _ in range(rng.randint(2, 4)):
        for _ in range(15):
            x, y = rng.randint(0, 49), rng.randint(15, 33)
            if outdoor.tiles[y][x] == G and not has_wild_at(x, y):
                kind = rng.choice(['wild_herb', 'wild_berry'])
                state.wild_entities.append({
                    'kind': kind, 'x': x, 'y': y, 'scene': 'outdoor',
                    'spooked': False, 'night_only': False,
                })
                break

    # Mushroom kalau kurang
    mushrooms = [w for w in state.wild_entities if w['kind'] == 'running_mushroom']
    if len(mushrooms) < 5:
        for _ in range(2):
            for _ in range(15):
                x, y = rng.randint(0, 17), rng.randint(15, 33)
                if outdoor.tiles[y][x] == G and not has_wild_at(x, y):
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
        if w['scene'] != 'outdoor':
            continue
        if w.get('night_only', False) and not is_night:
            continue
        if not w.get('moving', False):
            continue

        dist = abs(w['x'] - px) + abs(w['y'] - py)

        if w['kind'] == 'running_mushroom' and dist <= 3:
            # Lari menjauhi player
            dx = 1 if w['x'] > px else (-1 if w['x'] < px else rng.choice([-1, 1]))
            dy = 1 if w['y'] > py else (-1 if w['y'] < py else 0)
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, 'outdoor'):
                w['x'] = nx; w['y'] = ny
        elif w['kind'] == 'firefly':
            dx = rng.choice([-1, 0, 1])
            dy = rng.choice([-1, 0, 1])
            nx, ny = w['x'] + dx, w['y'] + dy
            if can_walk_at(nx, ny, 'outdoor'):
                w['x'] = nx; w['y'] = ny


def can_walk_at(x, y, scene_name):
    from .config import WALKABLE
    sc = SCENES.get(scene_name)
    if not sc: return False
    if x < 0 or x >= sc.w or y < 0 or y >= sc.h: return False
    return sc.tiles[y][x] in WALKABLE


# ═══════════════════════════════════════════════════
#  NPC SCHEDULE UPDATE
# ═══════════════════════════════════════════════════
def update_all_npc_positions(state):
    """Refresh posisi semua NPC sesuai schedule & jam."""
    hour = state.get_hour()
    for npc_id in all_npcs():
        sched = SCHEDULES.get(npc_id, [])
        if not sched: continue
        current = sched[0]
        for entry in sched:
            if entry[0] <= hour:
                current = entry
            else:
                break
        state.npc_positions[npc_id] = {
            'scene': current[3],
            'x': current[1],
            'y': current[2],
            'activity': current[4],
        }


def init_npc_data(state):
    """Pastikan semua NPC punya entry di hearts/dialog_index."""
    for npc_id in all_npcs():
        if npc_id not in state.npc_hearts:
            state.npc_hearts[npc_id] = 0
        if npc_id not in state.npc_dialog_index:
            state.npc_dialog_index[npc_id] = 0
    update_all_npc_positions(state)
