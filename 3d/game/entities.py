"""
entities.py — 3D NPC, wild entity, dan mob AI untuk Ursina Engine.

Setiap NPC/mob adalah Ursina Entity dengan model blocky sederhana.
AI logic diadaptasi dari v17 entities.py (berjalan di bidang XZ).

Koordinat:
  state.npc_positions[id]['x'/'y'] = tile koordinat (2D)
  → 3D pos: Vec3(tx*TS, GROUND_H, tz*TS)
"""
import math, os, random
from pathlib import Path
from PIL import Image

from ursina import Entity, Vec3, color, destroy, Text, Texture
from ursina.models.procedural.cylinder import Cylinder

from .config import (TILE_SIZE, GROUND_H, NPC_SPEED, WALKABLE, INVULN_AFTER_HIT_MS,
                     PLAYER_ATTACK_RANGE)
from .data import (HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS, SCHEDULES,
                   WILD_ITEMS, MOB_TEMPLATES, all_npcs)
from .scenes import SCENES

TS = TILE_SIZE

# ─── TEXTURE HELPER ──────────────────────────────────────
_ASSET_DIR = Path(__file__).resolve().parent.parent / 'assets'
_TEX_CACHE: dict = {}

def _tex(name: str):
    if not name:
        return None
    if name in _TEX_CACHE:
        return _TEX_CACHE[name]
    p = _ASSET_DIR / f'{name}.png'
    if p.exists():
        try:
            img = Image.open(p)
            t = Texture(img)
            t.filtering = False
            _TEX_CACHE[name] = t
            return t
        except Exception:
            pass
    return None

def _resolve_model(model):
    if model == 'cylinder':
        return Cylinder()
    return model

def _ent(model, pos, scale, tex_name, tint=color.white, **kw):
    model = _resolve_model(model)
    t = _tex(tex_name)
    if t:
        return Entity(model=model, position=pos, scale=scale, texture=t, color=tint, **kw)
    return Entity(model=model, position=pos, scale=scale, color=tint, **kw)

def _child(parent, model, pos, scale, tex_name, tint=color.white, **kw):
    return _ent(model, pos, scale, tex_name, tint, parent=parent, **kw)


# ─── WARNA NPC ────────────────────────────────────────────
NPC_COLORS = {
    'arya':          color.rgb(80, 160, 80),
    'sari':          color.rgb(220, 120, 160),
    'raka':          color.rgb(80, 180, 200),
    'maya':          color.rgb(160, 80, 200),
    'budi':          color.rgb(200, 120, 60),
    'joko':          color.rgb(60, 100, 200),
    'cici':          color.rgb(240, 200, 80),
    'bowo':          color.rgb(100, 200, 80),
    'ningsih':       color.rgb(200, 80, 160),
    'pak_guru':      color.rgb(60, 160, 180),
    'mbok_jum':      color.rgb(160, 120, 80),
    'jaka_ronda':    color.rgb(80, 80, 100),
    # Supernatural — warna supranatural/creepy
    'naga_bijak':    color.rgb(220, 180, 40),
    'jin_kebun':     color.rgb(80, 220, 220),
    'demit_tua':     color.rgb(140, 140, 160),
    'tuyul_pencuri': color.rgb(200, 60, 200),
    'kuntilanak':    color.rgb(240, 240, 255),
    'pocong':        color.rgb(230, 230, 220),
    'genderuwo':     color.rgb(80, 60, 80),
    'wewe_gombel':   color.rgb(120, 80, 60),
    'banaspati':     color.rgb(255, 140, 20),
    'leak_bali':     color.rgb(200, 40, 40),
    # Hewan
    'sapi_betsy':    color.rgb(240, 240, 240),
    'ayam_kuning':   color.rgb(240, 220, 60),
    'kambing_jenggot':color.rgb(180, 180, 160),
    'bebek_donald':  color.rgb(240, 220, 80),
    'domba_woolly':  color.rgb(240, 240, 235),
    'kuda_pegasus':  color.rgb(220, 220, 220),
    'kucing_oren':   color.rgb(230, 130, 60),
    'rubah_hutan':   color.rgb(210, 100, 40),
    'kelinci_putih': color.rgb(250, 248, 248),
}

MOB_COLORS = {
    'kelelawar':  color.rgb(100, 80, 120),
    'tikus_gua':  color.rgb(120, 90, 70),
    'genderuwo':  color.rgb(75, 55, 75),
    'banaspati':  color.rgb(255, 130, 20),
    'kuntilanak': color.rgb(230, 230, 248),
    'leak':       color.rgb(200, 38, 38),
    'pocong':     color.rgb(220, 220, 210),
    'naga_boss':  color.rgb(220, 175, 38),
}

SKIN = color.rgb(230, 188, 148)

# Tekstur baju per NPC
NPC_CLOTH_TEX = {
    'arya': 'cloth_green',  'sari': 'cloth_red',    'raka': 'cloth_blue',
    'maya': 'cloth_purple', 'budi': 'cloth_orange', 'joko': 'cloth_blue',
    'cici': 'cloth_yellow', 'bowo': 'cloth_green',  'ningsih': 'cloth_red',
    'pak_guru': 'cloth_blue', 'mbok_jum': 'cloth_orange', 'jaka_ronda': 'metal_grey',
    'naga_bijak': 'mob_naga',    'jin_kebun': 'cloth_green',
    'demit_tua':  'cloth_white', 'tuyul_pencuri': 'cloth_purple',
    'kuntilanak': 'mob_ghost',   'pocong': 'cloth_white',
    'genderuwo':  'wall_cave',   'wewe_gombel': 'wood_plank',
    'banaspati':  'mob_fire',    'leak_bali': 'cloth_red',
    'sapi_betsy': 'cloth_white', 'ayam_kuning': 'cloth_yellow',
    'kambing_jenggot': 'cloth_white', 'bebek_donald': 'cloth_yellow',
    'domba_woolly': 'cloth_white', 'kuda_pegasus': 'cloth_white',
    'kucing_oren': 'cloth_orange', 'rubah_hutan': 'cloth_orange',
    'kelinci_putih': 'cloth_white',
}

WILD_COLORS = {
    'mandrake':         color.rgb(80, 160, 80),
    'running_mushroom': color.rgb(200, 140, 80),
    'firefly':          color.rgb(240, 240, 80),
    'wild_herb':        color.rgb(60, 200, 80),
    'wild_berry':       color.rgb(200, 60, 120),
}


# ─── HELPER: CAN WALK ─────────────────────────────────────
def _can_walk(tx, ty, scene_name, dungeon_tiles=None):
    tx, ty = int(round(tx)), int(round(ty))
    if scene_name == 'dungeon' and dungeon_tiles:
        if ty < 0 or ty >= len(dungeon_tiles): return False
        if tx < 0 or tx >= len(dungeon_tiles[0]): return False
        return dungeon_tiles[ty][tx] in WALKABLE
    sc = SCENES.get(scene_name)
    if not sc: return False
    if tx < 0 or tx >= sc.w or ty < 0 or ty >= sc.h: return False
    return sc.tiles[ty][tx] in WALKABLE


# ─── NPC ENTITY (visual) ──────────────────────────────────
def _make_npc_entity(npc_id, tx, ty, col):
    root = Entity()
    root.x = tx * TS;  root.y = 0;  root.z = ty * TS

    is_animal = npc_id in ANIMAL_NPCS
    is_super  = npc_id in SUPERNATURAL_NPCS
    cloth = NPC_CLOTH_TEX.get(npc_id, 'cloth_blue')

    if is_animal:
        body_h, body_w, body_d = 0.65, 0.70, 1.10
        by = GROUND_H + 0.22 + body_h / 2
        _child(root, 'cube', (0, by, 0), (body_w, body_h, body_d), cloth, col)
        _child(root, 'cube', (0, by + body_h * 0.18, -body_d * 0.55),
               (0.42, 0.38, 0.40), cloth, col)
        for lx in (-0.22, 0.22):
            for lz in (-0.30, 0.30):
                _child(root, 'cube', (lx, GROUND_H + 0.18, lz),
                       (0.15, 0.36, 0.15), 'shoe_dark')
    else:
        # Chibi proportions — kepala besar (0.74) > badan (0.60), badan kompak
        leg_h = 0.38
        leg_y = GROUND_H + leg_h / 2
        body_h, body_w, body_d, head_sc = 0.90, 0.60, 0.46, 0.74
        by = GROUND_H + leg_h + body_h / 2
        hy = GROUND_H + leg_h + body_h + head_sc / 2

        # Simpan ref kaki & tangan untuk animasi berjalan
        root._leg_l = _child(root, 'cube', (-0.15, leg_y, 0), (0.22, leg_h, 0.26), 'pants_dark')
        root._leg_r = _child(root, 'cube', ( 0.15, leg_y, 0), (0.22, leg_h, 0.26), 'pants_dark')
        for lx in (-0.15, 0.15):
            _child(root, 'cube', (lx, GROUND_H + 0.06, 0.06), (0.22, 0.13, 0.34), 'shoe_dark')
        _child(root, 'cube', (0, by, 0), (body_w, body_h, body_d), cloth)
        _child(root, 'cube', (0, by - body_h * 0.44, 0),
               (body_w + 0.02, 0.09, body_d + 0.02), 'pants_dark')
        root._arm_l = _child(root, 'cube', (-0.40, by + 0.04, 0), (0.20, 0.82, 0.20), cloth)
        root._arm_r = _child(root, 'cube', ( 0.40, by + 0.04, 0), (0.20, 0.82, 0.20), cloth)
        # Sphere hands (lebih lucu)
        for arm_x in (-0.40, 0.40):
            _child(root, 'sphere', (arm_x, by - body_h * 0.46, 0),
                   (0.24, 0.24, 0.24), 'skin', SKIN)
        # Neck
        _child(root, 'cube', (0, hy - head_sc * 0.58, 0), (0.24, 0.16, 0.24), 'skin', SKIN)
        # Big chibi head
        _child(root, 'cube', (0, hy, 0), (head_sc, head_sc * 0.95, head_sc), 'skin', SKIN)
        # Cute eyes
        for ex in (-0.18, 0.18):
            _child(root, 'cube', (ex, hy + 0.08, -head_sc * 0.50),
                   (0.10, 0.12, 0.05), '', color.rgb(45, 30, 18))
        root._walk_t = 0.0

        if is_super:
            glow_c = color.rgb(255, 200, 60) if npc_id == 'banaspati' else color.rgb(180, 240, 255)
            _child(root, 'sphere', (0, hy + 0.18, -0.14), (0.24, 0.24, 0.24), 'lamp_glow', glow_c)

    root._npc_id = npc_id
    return root


# ─── ENTITIES MANAGER ─────────────────────────────────────
class EntitiesManager:
    """Mengelola semua NPC, wild entity, dan mob 3D di scene aktif."""

    def __init__(self, state):
        self.state        = state
        self.scene_name   = None
        self._npc_ents:  dict  = {}   # npc_id → (root Entity, label Text)
        self._wild_ents: dict  = {}   # idx → Entity
        self._mob_ents:  dict  = {}   # idx → (root Entity, hp_bar Entity)
        self._npc_update_t = 0.0
        self._wild_update_t= 0.0
        self._npc_sched_t  = 0.0

        self._init_npc_data()
        self._spawn_wild()

    # ─── PUBLIC: LOAD SCENE ──────────────────────────────
    def load_scene(self, scene_name: str):
        self._clear_all()
        self.scene_name = scene_name
        self._spawn_npcs_for_scene()
        self._spawn_wild_for_scene()
        self._spawn_mobs_for_scene()

    def spawn_mobs(self, mob_specs: list):
        """Spawn mob baru (dipanggil setelah dungeon di-generate)."""
        for ent in self._mob_ents.values():
            for e in ent: destroy(e)
        self._mob_ents.clear()
        self.state.mobs = mob_specs
        self._spawn_mobs_for_scene()

    # ─── PUBLIC: UPDATE ──────────────────────────────────
    def update(self, dt: float):
        s     = self.state
        dt_ms = dt * 1000.0

        # NPC AI (dipanggil setiap kali update dipanggil dari app.py ≈ tiap 0.05s)
        self._update_npc_ai(dt_ms)

        # Schedule update tiap 30 detik
        self._npc_sched_t += dt
        if self._npc_sched_t >= 30:
            self._npc_sched_t = 0
            self._update_npc_schedules()

        # Sync NPC visuals
        self._sync_npc_visuals(dt)

        # Wild update tiap 0.8s
        self._wild_update_t += dt
        if self._wild_update_t >= 0.8:
            self._wild_update_t = 0
            self._update_wild_ai()
        self._sync_wild_visuals()

        # Mob AI + visuals
        self._update_mob_ai(dt)
        self._sync_mob_visuals()

    # ─── PUBLIC: QUERY ───────────────────────────────────
    def get_nearest_npc(self, tx: int, ty: int, max_dist_tiles: float = 3.0):
        """Return {'id': ..., 'name': ...} NPC terdekat atau None."""
        s = self.state
        best_d, best_id = max_dist_tiles + 1, None
        for npc_id, pos in s.npc_positions.items():
            if pos.get('scene') != s.scene_name: continue
            if pos.get('x', -1) < 0: continue
            d = math.hypot(pos['x'] - tx, pos['y'] - ty)
            if d < best_d:
                best_d, best_id = d, npc_id
        if best_id is None:
            return None
        return {'id': best_id}

    def attack_mobs(self, tx: int, ty: int, attack_range: float, damage: int) -> int:
        """Serang semua mob dalam range (world-units). Return jumlah kill."""
        s = self.state
        if s.scene_name != 'dungeon': return 0
        killed = 0
        wx, wz = tx * TS, ty * TS
        for mob in list(s.mobs):
            mx, mz = mob['x'] * TS, mob['y'] * TS
            dist = math.sqrt((wx-mx)**2 + (wz-mz)**2)
            if dist <= attack_range:
                mob['hp'] -= damage
                mob['dmg_flash_ms'] = 200
                if mob['hp'] <= 0:
                    # Loot
                    for item, n in mob.get('drops', {}).items():
                        s.inventory[item] = s.inventory.get(item, 0) + n
                    if mob.get('is_boss'):
                        s.naga_defeated = True
                    killed += 1
                    s.mobs.remove(mob)
        return killed

    def try_capture_wild(self, tx: int, ty: int, state) -> tuple | None:
        """Coba tangkap wild entity di sekitar player. Return (name, sell) atau None."""
        import random as rng_mod
        sc = state.scene_name
        px, pz = tx * TS, ty * TS
        for w in list(state.wild_entities):
            if w['scene'] != sc: continue
            wx, wz = w['x'] * TS, w['y'] * TS
            if math.sqrt((px-wx)**2 + (pz-wz)**2) > 3.0: continue
            kind = w['kind']
            rates = {'running_mushroom': 0.60, 'firefly': 0.70,
                     'mandrake': 0.30, 'wild_herb': 0.90, 'wild_berry': 0.90}
            if rng_mod.random() < rates.get(kind, 0.5):
                state.wild_entities.remove(w)
                item = WILD_ITEMS.get(kind, {})
                return kind, item.get('sell', 10)
        return None

    # ─── PRIVATE: INIT ───────────────────────────────────
    def _init_npc_data(self):
        s = self.state
        for npc_id in all_npcs():
            if npc_id not in s.npc_hearts:       s.npc_hearts[npc_id] = 0
            if npc_id not in s.npc_dialog_index:  s.npc_dialog_index[npc_id] = 0
        self._update_npc_schedules()

    def _update_npc_schedules(self):
        s    = self.state
        hour = s.get_hour()
        for npc_id in all_npcs():
            sched = SCHEDULES.get(npc_id, [])
            if not sched: continue
            current = sched[0]
            for entry in sched:
                if entry[0] <= hour: current = entry
                else: break
            target_scene = current[3]
            tx, ty       = float(current[1]), float(current[2])

            if npc_id not in s.npc_positions:
                s.npc_positions[npc_id] = {
                    'scene': target_scene, 'x': tx, 'y': ty,
                    'target_x': tx, 'target_y': ty,
                    'activity': current[4], 'facing': 'down',
                }
            else:
                pos = s.npc_positions[npc_id]
                if pos['scene'] != target_scene:
                    pos['scene']    = target_scene
                    pos['x']        = tx
                    pos['y']        = ty
                pos['target_x']  = tx
                pos['target_y']  = ty
                pos['activity']  = current[4]

    def _spawn_wild(self):
        s = self.state
        if s.wild_entities: return
        rng = random.Random(s.day * 7)
        for _ in range(3):
            x, y = rng.randint(2, 28), rng.randint(5, 22)
            s.wild_entities.append({'kind':'mandrake','x':x,'y':y,'scene':'mountain','moving':False})
        for scene in ['farm','mountain']:
            for _ in range(3):
                x, y = rng.randint(5, 20), rng.randint(5, 15)
                s.wild_entities.append({'kind':'running_mushroom','x':x,'y':y,'scene':scene,'moving':True})
        for scene in ['farm','town','lake']:
            for _ in range(5):
                x, y = rng.randint(3, 15), rng.randint(3, 12)
                s.wild_entities.append({'kind':'firefly','x':x,'y':y,'scene':scene,'moving':True,'night_only':True})
        for _ in range(15):
            x, y = rng.randint(2, 28), rng.randint(5, 22)
            s.wild_entities.append({
                'kind': rng.choice(['wild_herb','wild_berry']),
                'x':x,'y':y,'scene':'mountain','moving':False,
            })

    # ─── PRIVATE: SPAWN PER SCENE ────────────────────────
    def _spawn_npcs_for_scene(self):
        s = self.state
        for npc_id, pos in s.npc_positions.items():
            if pos.get('scene') != s.scene_name: continue
            if pos.get('x', -1) < 0: continue
            col = NPC_COLORS.get(npc_id, color.white)
            ent = _make_npc_entity(npc_id, pos['x'], pos['y'], col)
            # Label nama
            from .data import HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS
            all_d = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}
            name  = all_d.get(npc_id, {}).get('name', npc_id)
            lbl   = Text(name, parent=ent, billboard=True,
                         position=(0, GROUND_H + 2.7, 0),
                         scale=5, color=color.rgb(255, 240, 160),
                         background=True)
            self._npc_ents[npc_id] = (ent, lbl)

    def _spawn_wild_for_scene(self):
        s = self.state
        for i, w in enumerate(s.wild_entities):
            if w['scene'] != s.scene_name: continue
            if w.get('night_only') and not s.is_night(): continue
            self._wild_ents[i] = self._make_wild_entity(w)

    def _make_wild_entity(self, w):
        kind = w['kind']
        px, py = w['x'] * TS, w['y'] * TS
        if kind == 'mandrake':
            root = Entity()
            root.x, root.z = px, py
            _child(root, 'cube', (0, GROUND_H + 0.18, 0), (0.38, 0.35, 0.38), 'cloth_green')
            _child(root, 'sphere', (0, GROUND_H + 0.42, 0), (0.22, 0.28, 0.22), 'skin')
            return root
        elif kind == 'running_mushroom':
            root = Entity()
            root.x, root.z = px, py
            _child(root, 'cylinder', (0, GROUND_H + 0.18, 0), (0.14, 0.38, 0.14), 'skin')
            _child(root, 'sphere',   (0, GROUND_H + 0.50, 0), (0.42, 0.24, 0.42), 'fire_orange')
            return root
        elif kind == 'firefly':
            return _ent('sphere', (px, GROUND_H + 0.55, py), (0.18, 0.18, 0.18), 'lamp_glow')
        elif kind == 'wild_herb':
            return _ent('cylinder', (px, GROUND_H + 0.22, py), (0.20, 0.42, 0.20), 'cloth_green')
        elif kind == 'wild_berry':
            return _ent('sphere', (px, GROUND_H + 0.22, py), (0.30, 0.30, 0.30), 'crop_stroberi')
        else:
            return _ent('sphere', (px, GROUND_H + 0.25, py), (0.35, 0.35, 0.35), 'crop_lobak')

    def _spawn_mobs_for_scene(self):
        s = self.state
        if s.scene_name != 'dungeon': return
        for i, mob in enumerate(s.mobs):
            self._create_mob_entity(i, mob)

    def _create_mob_entity(self, idx, mob):
        kind    = mob['kind']
        is_boss = mob.get('is_boss', False)
        sc      = 1.4 if is_boss else 1.0

        root = Entity()
        root.x = mob['x'] * TS;  root.y = 0;  root.z = mob['y'] * TS

        builders = {
            'kelelawar':  self._mob_bat,
            'tikus_gua':  self._mob_rat,
            'genderuwo':  self._mob_genderuwo,
            'banaspati':  self._mob_banaspati,
            'kuntilanak': self._mob_kuntilanak,
            'leak':       self._mob_leak,
            'pocong':     self._mob_pocong,
            'naga_boss':  self._mob_naga,
        }
        fn = builders.get(kind)
        if fn:
            body_ref = fn(root, sc)
        else:
            body_ref = Entity(parent=root, model='cube',
                              position=(0, GROUND_H + 0.6*sc, 0),
                              scale=(0.8*sc, 1.0*sc, 0.6*sc),
                              color=MOB_COLORS.get(kind, color.red))
            Entity(parent=root, model='cube',
                   position=(0, GROUND_H + 1.25*sc, 0),
                   scale=(0.55*sc, 0.55*sc, 0.55*sc),
                   color=MOB_COLORS.get(kind, color.red))

        hp_y = GROUND_H + (3.5 if is_boss else 2.4) * sc
        Entity(parent=root, model='cube',
               position=(0, hp_y, 0),
               scale=(0.9*sc, 0.10, 0.10),
               color=color.rgb(45, 45, 45))
        hp_bar = Entity(parent=root, model='cube',
                        position=(0, hp_y, -0.02),
                        scale=(0.9*sc, 0.08, 0.08),
                        color=color.rgb(225, 48, 48))

        self._mob_ents[idx] = (root, hp_bar, body_ref)

    # ── Mob builders ─────────────────────────────────────
    def _mob_bat(self, root, sc):
        body = _child(root, 'cube', (0, GROUND_H + 0.90*sc, 0),
                      (0.32*sc, 0.30*sc, 0.22*sc), 'mob_bat')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.46*sc, GROUND_H + 0.84*sc, 0),
                   (0.55*sc, 0.10*sc, 0.38*sc), 'mob_bat',
                   rotation=(0, 0, side*-18))
        for side in (-1, 1):
            _child(root, 'sphere',
                   (side*0.08*sc, GROUND_H + 0.98*sc, -0.14*sc),
                   (0.07*sc, 0.07*sc, 0.07*sc), 'cloth_red')
        return body

    def _mob_rat(self, root, sc):
        body = _child(root, 'cube',
                      (0, GROUND_H + 0.28*sc, 0),
                      (0.55*sc, 0.36*sc, 0.88*sc), 'mob_rat')
        _child(root, 'sphere',
               (0, GROUND_H + 0.42*sc, -0.50*sc),
               (0.35*sc, 0.30*sc, 0.35*sc), 'mob_rat')
        for side in (-1, 1):
            _child(root, 'sphere',
                   (side*0.13*sc, GROUND_H + 0.62*sc, -0.46*sc),
                   (0.12*sc, 0.15*sc, 0.08*sc), 'skin')
        _child(root, 'cylinder',
               (0, GROUND_H + 0.20*sc, 0.56*sc),
               (0.06*sc, 0.62*sc, 0.06*sc), 'skin',
               rotation=(90, 0, 0))
        return body

    def _mob_genderuwo(self, root, sc):
        g = sc * 1.5
        body = _child(root, 'cube',
                      (0, GROUND_H + 0.85*g, 0),
                      (1.15*g, 1.35*g, 0.72*g), 'wall_cave')
        _child(root, 'cube',
               (0, GROUND_H + 1.92*g, 0),
               (0.82*g, 0.78*g, 0.68*g), 'wall_cave')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.78*g, GROUND_H + 0.55*g, 0),
                   (0.30*g, 1.45*g, 0.28*g), 'wall_cave')
        for side in (-1, 1):
            _child(root, 'sphere',
                   (side*0.22*g, GROUND_H + 2.02*g, -0.36*g),
                   (0.13*g, 0.13*g, 0.10*g), 'cloth_red')
        return body

    def _mob_banaspati(self, root, sc):
        hover = GROUND_H + 1.2*sc
        body = _child(root, 'sphere',
                      (0, hover, 0),
                      (0.52*sc, 0.52*sc, 0.52*sc), 'mob_fire')
        _child(root, 'sphere',
               (0, hover, 0),
               (0.76*sc, 0.76*sc, 0.76*sc), 'lamp_glow')
        for ang in (0, 90, 180, 270):
            rad = math.radians(ang)
            ox, oz = math.sin(rad)*0.56*sc, math.cos(rad)*0.56*sc
            _child(root, 'cube',
                   (ox, hover, oz),
                   (0.11*sc, 0.42*sc, 0.11*sc), 'fire_orange',
                   rotation=(0, ang, 28))
        return body

    def _mob_kuntilanak(self, root, sc):
        hover = GROUND_H + 0.18*sc
        body = _child(root, 'cube',
                      (0, hover + 0.88*sc, 0),
                      (0.50*sc, 1.55*sc, 0.34*sc), 'mob_ghost')
        _child(root, 'cube',
               (0, hover + 1.92*sc, 0),
               (0.44*sc, 0.50*sc, 0.40*sc), 'cloth_white')
        for ox in (-0.16*sc, 0.0, 0.16*sc):
            _child(root, 'cube',
                   (ox, hover + 0.80*sc, -0.20*sc),
                   (0.10*sc, 1.65*sc, 0.09*sc), 'mob_bat')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.42*sc, hover + 0.50*sc, 0),
                   (0.17*sc, 0.88*sc, 0.17*sc), 'mob_ghost',
                   rotation=(0, 0, side*-30))
        return body

    def _mob_leak(self, root, sc):
        hover = GROUND_H + 1.5*sc
        body = _child(root, 'sphere',
                      (0, hover, 0),
                      (0.72*sc, 0.72*sc, 0.68*sc), 'cloth_red')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.28*sc, hover + 0.52*sc, 0),
                   (0.12*sc, 0.46*sc, 0.12*sc), 'cloth_red',
                   rotation=(0, 0, side*-18))
        for side in (-1, 1):
            _child(root, 'sphere',
                   (side*0.20*sc, hover + 0.12*sc, -0.36*sc),
                   (0.13*sc, 0.13*sc, 0.10*sc), 'lamp_glow')
        for ox in (-0.18*sc, 0.0, 0.18*sc):
            _child(root, 'cube',
                   (ox, hover - 0.52*sc, 0),
                   (0.10*sc, 0.42*sc, 0.10*sc), 'cloth_red')
        return body

    def _mob_pocong(self, root, sc):
        hover = GROUND_H + 0.08*sc
        body = _child(root, 'cube',
                      (0, hover + 0.88*sc, 0),
                      (0.54*sc, 1.72*sc, 0.46*sc), 'cloth_white')
        _child(root, 'sphere',
               (0, hover + 1.88*sc, 0),
               (0.30*sc, 0.24*sc, 0.28*sc), 'cloth_white')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.12*sc, hover + 1.35*sc, -0.24*sc),
                   (0.12*sc, 0.10*sc, 0.05*sc), 'mob_bat')
        _child(root, 'cube',
               (0, hover + 0.14*sc, 0),
               (0.36*sc, 0.30*sc, 0.33*sc), 'cloth_white')
        return body

    def _mob_naga(self, root, sc):
        body = _child(root, 'cube',
                      (0, GROUND_H + 2.2*sc, 0),
                      (1.20*sc, 1.00*sc, 1.30*sc), 'mob_naga')
        for side in (-1, 1):
            _child(root, 'cube',
                   (side*0.40*sc, GROUND_H + 3.10*sc, 0),
                   (0.20*sc, 0.85*sc, 0.20*sc), 'ore_gold',
                   rotation=(0, 0, side*-15))
        for side in (-1, 1):
            _child(root, 'sphere',
                   (side*0.38*sc, GROUND_H + 2.38*sc, -0.62*sc),
                   (0.20*sc, 0.20*sc, 0.16*sc), 'cloth_red')
        for i, (zy, ysz) in enumerate([(0.90*sc, 1.1), (1.80*sc, 0.95), (2.60*sc, 0.80)]):
            _child(root, 'sphere',
                   (0, GROUND_H + (1.2 - i*0.22)*sc, zy),
                   (ysz*sc, ysz*0.85*sc, ysz*sc), 'mob_naga')
        _child(root, 'cylinder',
               (0, GROUND_H + 0.45*sc, 3.5*sc),
               (0.28*sc, 0.70*sc, 0.28*sc), 'mob_naga',
               rotation=(90, 0, 0))
        return body

    # ─── PRIVATE: AI UPDATE ──────────────────────────────
    def _update_npc_ai(self, dt_ms):
        s   = self.state
        rng = random.Random()
        px, py = s.player_x, s.player_y

        ANIMAL_PEN = {
            'sapi_betsy':(15,2,21,7), 'ayam_kuning':(15,2,21,7),
            'kambing_jenggot':(15,2,21,7), 'domba_woolly':(15,2,21,7),
            'kuda_pegasus':(15,2,21,7), 'kucing_oren':(3,8,9,12),
            'rubah_hutan':(1,5,28,24), 'kelinci_putih':(1,5,28,24),
            'bebek_donald':(3,4,14,11),
        }

        for npc_id, pos in s.npc_positions.items():
            if pos.get('scene') != s.scene_name: continue
            if pos.get('x', -1) < 0: continue

            tx_, ty_ = pos.get('target_x', pos['x']), pos.get('target_y', pos['y'])
            dist_p   = math.hypot(pos['x'] - px, pos['y'] - py)
            speed    = NPC_SPEED / (TS * 20)  # tile/dt_ms
            is_moving= abs(pos['x']-tx_)>0.02 or abs(pos['y']-ty_)>0.02

            if npc_id == 'tuyul_pencuri':
                if dist_p < 4:
                    speed *= 3.0
                    if not is_moving:
                        dx_ = 1 if pos['x']>px else -1
                        dy_ = 1 if pos['y']>py else -1
                        nx_ = int(pos['x']) + dx_*rng.randint(2,4)
                        ny_ = int(pos['y']) + dy_*rng.randint(2,4)
                        if _can_walk(nx_, ny_, s.scene_name):
                            pos['target_x'], pos['target_y'] = float(nx_), float(ny_)
                elif not is_moving and rng.random() < 0.015:
                    nx_ = int(pos['x'])+rng.choice([-1,0,1])
                    ny_ = int(pos['y'])+rng.choice([-1,0,1])
                    if _can_walk(nx_, ny_, s.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx_), float(ny_)

            elif npc_id in ANIMAL_NPCS:
                if s.is_night():
                    pos['target_x'] = pos['x'];  pos['target_y'] = pos['y'];  continue
                if not is_moving and rng.random() < 0.015:
                    bounds = ANIMAL_PEN.get(npc_id, (3,3,22,12))
                    nx_ = max(bounds[0], min(bounds[2], int(pos['x'])+rng.choice([-1,0,0,1])))
                    ny_ = max(bounds[1], min(bounds[3], int(pos['y'])+rng.choice([-1,0,0,1])))
                    if _can_walk(nx_, ny_, s.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx_), float(ny_)

            elif npc_id in SUPERNATURAL_NPCS:
                speed *= 0.5
                if not is_moving and rng.random() < 0.008:
                    nx_ = int(pos['x'])+rng.choice([-1,0,1])
                    ny_ = int(pos['y'])+rng.choice([-1,0,1])
                    if _can_walk(nx_, ny_, s.scene_name):
                        pos['target_x'], pos['target_y'] = float(nx_), float(ny_)

            # Lerp movement
            dx_ = tx_ - pos['x'];  dy_ = ty_ - pos['y']
            dist= math.hypot(dx_, dy_)
            move= speed * dt_ms
            if dist <= move:
                pos['x'], pos['y'] = float(tx_), float(ty_)
            elif dist > 0:
                pos['x'] += (dx_/dist)*move
                pos['y'] += (dy_/dist)*move

    def _update_wild_ai(self):
        s   = self.state
        rng = random.Random()
        px, py = s.player_x, s.player_y
        for w in s.wild_entities:
            if w['scene'] != s.scene_name: continue
            if w.get('night_only') and not s.is_night(): continue
            if not w.get('moving'): continue
            dist = math.hypot(w['x']-px, w['y']-py)
            if w['kind'] == 'running_mushroom' and dist <= 3:
                dx_ = 1 if w['x']>px else (-1 if w['x']<px else rng.choice([-1,1]))
                dy_ = 1 if w['y']>py else 0
                nx_, ny_ = w['x']+dx_, w['y']+dy_
                if _can_walk(nx_, ny_, s.scene_name):
                    w['x'], w['y'] = nx_, ny_
            elif w['kind'] == 'firefly':
                dx_, dy_ = rng.choice([-1,0,1]), rng.choice([-1,0,1])
                nx_, ny_ = w['x']+dx_, w['y']+dy_
                if _can_walk(nx_, ny_, s.scene_name):
                    w['x'], w['y'] = nx_, ny_

    def _update_mob_ai(self, dt: float):
        s  = self.state
        if s.scene_name != 'dungeon': return
        px, pz = s.player_x, s.player_y
        _rng = __import__('random')

        for mob in list(s.mobs):
            if mob.get('dmg_flash_ms', 0) > 0:
                mob['dmg_flash_ms'] = max(0, mob['dmg_flash_ms'] - dt*1000)
            if mob.get('attack_cooldown_ms', 0) > 0:
                mob['attack_cooldown_ms'] = max(0, mob['attack_cooldown_ms'] - dt*1000)

            if mob['hp'] <= 0:
                if mob.get('is_boss'): s.naga_defeated = True
                if mob in s.mobs:
                    s.mobs.remove(mob)
                continue

            is_boss  = mob.get('is_boss', False)
            alert_r  = 10.0 if is_boss else 5.0
            chase_r  = 14.0 if is_boss else 8.0
            atk_r    = 1.5  if is_boss else 1.0
            dist     = math.hypot(mob['x']-px, mob['y']-pz)

            # ── state transitions ──────────────────────────
            ai_state = mob.get('ai_state', 'patrol')
            if dist <= alert_r:
                ai_state = 'chase'
            elif dist <= chase_r:
                if ai_state == 'patrol':
                    ai_state = 'alert'
            else:
                ai_state = 'patrol'
            mob['ai_state'] = ai_state

            # ── PATROL: random wander ──────────────────────
            if ai_state == 'patrol':
                mob['patrol_t'] = mob.get('patrol_t', 0.0) + dt
                interval = mob.get('patrol_interval', _rng.uniform(1.5, 3.5))
                mob['patrol_interval'] = interval
                if mob['patrol_t'] >= interval:
                    mob['patrol_t'] = 0.0
                    mob['patrol_interval'] = _rng.uniform(1.5, 3.5)
                    mob['patrol_dx'] = _rng.choice([-1, 0, 0, 1])
                    mob['patrol_dy'] = _rng.choice([-1, 0, 0, 1])
                pdx = mob.get('patrol_dx', 0)
                pdy = mob.get('patrol_dy', 0)
                if pdx != 0 or pdy != 0:
                    spd = mob['speed'] * 0.4 / TS * dt
                    nx_ = mob['x'] + pdx * spd
                    ny_ = mob['y'] + pdy * spd
                    if _can_walk(nx_, mob['y'], 'dungeon', s.dungeon_tiles): mob['x'] = nx_
                    if _can_walk(mob['x'], ny_, 'dungeon', s.dungeon_tiles): mob['y'] = ny_

            # ── ALERT: speed-burst toward player ──────────
            elif ai_state == 'alert':
                if dist > 0.3:
                    spd  = mob['speed'] * 1.6 / TS * dt
                    dx_  = (px - mob['x']) / dist
                    dy_  = (pz - mob['y']) / dist
                    nx_  = mob['x'] + dx_ * spd
                    ny_  = mob['y'] + dy_ * spd
                    if _can_walk(nx_, mob['y'], 'dungeon', s.dungeon_tiles): mob['x'] = nx_
                    if _can_walk(mob['x'], ny_, 'dungeon', s.dungeon_tiles): mob['y'] = ny_

            # ── CHASE: normal pursuit ──────────────────────
            elif ai_state == 'chase':
                if dist > 0.3:
                    spd  = mob['speed'] / TS * dt
                    dx_  = (px - mob['x']) / dist
                    dy_  = (pz - mob['y']) / dist
                    nx_  = mob['x'] + dx_ * spd
                    ny_  = mob['y'] + dy_ * spd
                    if _can_walk(nx_, mob['y'], 'dungeon', s.dungeon_tiles): mob['x'] = nx_
                    if _can_walk(mob['x'], ny_, 'dungeon', s.dungeon_tiles): mob['y'] = ny_

            # ── ATTACK ────────────────────────────────────
            if dist <= atk_r and mob.get('attack_cooldown_ms', 0) <= 0:
                if s.invuln_timer_ms <= 0:
                    s.hp = max(0, s.hp - mob['damage'])
                    s.invuln_timer_ms = INVULN_AFTER_HIT_MS
                mob['attack_cooldown_ms'] = 1000

    # ─── PRIVATE: SYNC VISUALS ───────────────────────────
    def _sync_npc_visuals(self, dt):
        s    = self.state
        # Dynamic spawn/despawn — handles NPCs entering/leaving scene mid-session
        from .data import HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS as _AN
        _all_d = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **_AN}
        for npc_id, pos in list(s.npc_positions.items()):
            in_scene = pos.get('scene') == s.scene_name and pos.get('x', -1) >= 0
            has_ent  = npc_id in self._npc_ents
            if in_scene and not has_ent:
                col = NPC_COLORS.get(npc_id, color.white)
                ent = _make_npc_entity(npc_id, pos['x'], pos['y'], col)
                nm  = _all_d.get(npc_id, {}).get('name', npc_id)
                lbl = Text(nm, parent=ent, billboard=True,
                           position=(0, GROUND_H + 2.7, 0),
                           scale=5, color=color.rgb(255, 240, 160),
                           background=True)
                self._npc_ents[npc_id] = (ent, lbl)
            elif not in_scene and has_ent:
                ent, lbl = self._npc_ents.pop(npc_id)
                destroy(ent); destroy(lbl)

        lf   = min(1.0, dt * 8)
        for npc_id, (ent, lbl) in self._npc_ents.items():
            pos = s.npc_positions.get(npc_id)
            if not pos: continue
            wx  = pos['x'] * TS
            wz  = pos['y'] * TS
            dx  = wx - ent.x
            dz  = wz - ent.z
            ent.x += dx * lf
            ent.z += dz * lf

            # Animasi berjalan / idle untuk NPC humanoid
            if not hasattr(ent, '_leg_l'):
                continue
            moving = abs(dx) > 0.015 or abs(dz) > 0.015
            if moving:
                # Hadap arah gerak
                if abs(dx) > abs(dz):
                    ent.rotation_y = 90 if dx > 0 else -90
                else:
                    ent.rotation_y = 0 if dz > 0 else 180

                ent._walk_t += dt * 9.0
                swing = math.sin(ent._walk_t) * 24.0
                ent._leg_l.rotation_x =  swing
                ent._leg_r.rotation_x = -swing
                ent._arm_l.rotation_x = -swing * 0.55
                ent._arm_r.rotation_x =  swing * 0.55
            else:
                # Idle bob — napas halus
                ent._walk_t += dt * 1.8
                bob = math.sin(ent._walk_t) * 3.0
                ent._leg_l.rotation_x = ent._leg_l.rotation_x * 0.80
                ent._leg_r.rotation_x = ent._leg_r.rotation_x * 0.80
                ent._arm_l.rotation_x = bob * 0.4
                ent._arm_r.rotation_x = -bob * 0.4

    def _sync_wild_visuals(self):
        s = self.state
        for i, w in enumerate(s.wild_entities):
            if i not in self._wild_ents: continue
            e = self._wild_ents[i]
            e.x = w['x']*TS;  e.z = w['y']*TS
            if w.get('night_only'):
                e.enabled = s.is_night()

    def _sync_mob_visuals(self):
        s = self.state
        for i, mob in enumerate(s.mobs):
            if i not in self._mob_ents: continue
            root, hp_bar, body = self._mob_ents[i]
            root.x = mob['x']*TS;  root.z = mob['y']*TS
            # HP bar scale
            ratio = max(0, mob['hp'] / max(mob.get('max_hp', 1), 1))
            is_boss = mob.get('is_boss', False)
            sc = 1.4 if is_boss else 1.0
            hp_bar.scale_x = 0.9 * sc * ratio
            # Damage flash
            if mob.get('dmg_flash_ms', 0) > 0:
                body.color = color.white
            else:
                body.color = MOB_COLORS.get(mob['kind'], color.red)

        # Hapus entity mob yang sudah mati
        alive_idx = set(range(len(s.mobs)))
        dead_idx  = set(self._mob_ents.keys()) - alive_idx
        for i in dead_idx:
            for e in self._mob_ents.pop(i):
                destroy(e)

    # ─── PRIVATE: CLEAR ──────────────────────────────────
    def _clear_all(self):
        for ent, lbl in self._npc_ents.values():
            destroy(ent);  destroy(lbl)
        self._npc_ents.clear()
        for e in self._wild_ents.values():
            destroy(e)
        self._wild_ents.clear()
        for tup in self._mob_ents.values():
            for e in tup: destroy(e)
        self._mob_ents.clear()


def respawn_wild_at_morning(state):
    rng = random.Random()
    for scene in ['farm', 'mountain']:
        for _ in range(rng.randint(2, 4)):
            x, y = rng.randint(2, 20), rng.randint(5, 15)
            state.wild_entities.append({
                'kind': rng.choice(['wild_herb', 'wild_berry']),
                'x': x, 'y': y, 'scene': scene, 'moving': False,
            })
