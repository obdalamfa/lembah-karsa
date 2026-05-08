"""
world.py — 3D world renderer untuk Ursina Engine.
Mengkonversi tile map 2D (dari scenes.py) menjadi entitas 3D.

Koordinat mapping:
  Tile (tx, ty)  →  World Vec3(tx * TS, 0, ty * TS)
  TS = TILE_SIZE = 2.0 world-units per tile

Struktur Y (vertikal):
  y = 0          → bawah ground
  y = GROUND_H/2 → center ground tile (top face = GROUND_H)
  y > GROUND_H   → objek berdiri di atas tanah
"""
import math, os
from pathlib import Path
from ursina import Entity, Vec3, color, destroy, load_texture
from ursina.models.procedural.cylinder import Cylinder

from .config import (TILE_SIZE, GROUND_H, WALL_H, TREE_H, HOUSE_H, OBJ_H, SMALL_OBJ_H,
                     WALKABLE, BLOCKING, MINEABLE, TILLABLE,
                     G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS,
                     MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR_T,
                     DCK, BOT, LLY, CRYS, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH,
                     STAIRS_DOWN, STAIRS_UP, MINED)
from .scenes import SCENES
from .data import CROPS

TS = TILE_SIZE

# ─── TEXTURE HELPERS ─────────────────────────────────────
_ASSET_DIR = Path(__file__).resolve().parent.parent / 'assets'
_TEX_CACHE: dict = {}

def _tex(name: str):
    """Load & cache tekstur via Path (bypass Ursina string-search)."""
    if not name:
        return None
    if name in _TEX_CACHE:
        return _TEX_CACHE[name]
    p = _ASSET_DIR / f'{name}.png'
    if p.exists():
        t = load_texture(str(p))
        _TEX_CACHE[name] = t
        return t
    return None

def _e(model, pos, scale, tex_name, tint=color.white, **kw):
    """Buat Entity dengan tekstur + tint opsional."""
    if model == 'cylinder':
        model = Cylinder()
    t = _tex(tex_name)
    if t:
        return Entity(model=model, position=pos, scale=scale,
                      texture=t, color=tint, **kw)
    return Entity(model=model, position=pos, scale=scale,
                  color=tint, **kw)


def _c(r, g_, b):
    return color.rgb(r, g_, b)


# Warna checkerboard untuk tint ringan (tak terlalu gelap)
_CB_LIGHT = color.white
_CB_DARK  = color.rgb(220, 220, 220)

def _cb(tx, ty):
    return _CB_DARK if (tx + ty) % 2 == 1 else _CB_LIGHT


# ─── PETA TEKSTUR TILE ───────────────────────────────────
TILE_TEX = {
    G:          'grass',
    D:          'dirt',
    P:          'path_stone',
    W:          'water',
    FL:         'floor_wood',
    CV_F:       'cave_floor',
    STR_T:      'straw',
    DCK:        'dock',
    LLY:        'lily',
    MINED:      'mined',
    STAIRS_DOWN:'stairs_down',
    STAIRS_UP:  'stairs_up',
}

# Tekstur untuk objek/dinding
OBJ_TEX = {
    WL:      'wall_stone',
    CV_W:    'wall_cave',
    H:       'house_wall',
    TR:      'tree_leaf',
    DT:      'tree_trunk',
    FP:      'fire_orange',
    LN:      'lamp_glow',
    CRYS:    'crystal',
    ORE_TBG: 'ore_copper',
    ORE_BSI: 'ore_iron',
    ORE_EMS: 'ore_gold',
    ORE_KRS: 'ore_crystal',
    ORE_MTH: 'ore_mithril',
    CH:      'chest_wood',
    BOT:     'boat_wood',
    BD:      'wood_plank',
    TB:      'wood_plank',
    BS:      'wood_plank',
    CT:      'wood_plank',
    SH:      'wood_plank',
    ST:      'metal_grey',
    MR:      'mirror_blue',
    GR:      'grave_stone',
    FN:      'wood_plank',
    GT:      'wood_plank',
    PEN:     'wood_plank',
    DR:      'house_wall',
    PP:      'cloth_green',
    MB:      'cloth_blue',
    CL:      'metal_grey',
}

# Fallback warna untuk objek tanpa tekstur
OBJ_COLORS = {
    WL:  _c(102, 90, 118),
    TR:  _c(52, 155, 40),
    H:   _c(185, 128, 80),
    MB:  _c(72, 72, 228),
    DR:  _c(155, 100, 55),
    FN:  _c(130, 92, 50),
    GT:  _c(140, 100, 55),
    BD:  _c(222, 185, 142),
    ST:  _c(108, 85, 75),
    TB:  _c(182, 148, 102),
    BS:  _c(142, 102, 62),
    MR:  _c(185, 215, 240),
    FP:  _c(205, 92, 48),
    CL:  _c(85, 68, 58),
    PP:  _c(62, 185, 65),
    CH:  _c(152, 112, 68),
    CT:  _c(175, 135, 92),
    SH:  _c(162, 125, 80),
    GR:  _c(112, 100, 122),
    LN:  _c(255, 238, 88),
    DT:  _c(85, 65, 45),
    CV_W:_c(75, 65, 92),
    PEN: _c(130, 92, 50),
    BOT: _c(192, 145, 90),
    CRYS:_c(188, 148, 245),
    ORE_TBG:_c(198, 122, 62),
    ORE_BSI:_c(148, 150, 175),
    ORE_EMS:_c(255, 228, 85),
    ORE_KRS:_c(188, 148, 245),
    ORE_MTH:_c(148, 232, 255),
}

CROP_TEX = {
    'lobak':    'crop_lobak',
    'wortel':   'crop_wortel',
    'stroberi': 'crop_stroberi',
    'jagung':   'crop_jagung',
    'tomat':    'crop_tomat',
    'labu':     'crop_labu',
    'bayam':    'crop_bayam',
    'jamur':    'crop_jamur',
}


class World3D:
    """Mengelola semua 3D entity untuk scene yang sedang aktif."""

    def __init__(self, state):
        self.state              = state
        self.scene_name         = None
        self.scene_obj          = None
        self._tile_ents: list   = []   # ground tiles
        self._obj_ents:  list   = []   # blocking objects
        self._soil_ents: dict   = {}   # key → Entity
        self._crop_ents: dict   = {}   # key → Entity
        self._water_ents: list  = []   # untuk animasi warna
        self._water_t    = 0.0

    # ─── PUBLIC API ──────────────────────────────────────
    def load_scene(self, name: str):
        self._clear()
        self.scene_name = name
        self.scene_obj  = SCENES[name]
        self._build_tiles()
        self._build_all_crops()

    def tile_to_world(self, tx: int, ty: int) -> Vec3:
        return Vec3(tx * TS, 0, ty * TS)

    def world_to_tile(self, wx: float, wz: float):
        return int(round(wx / TS)), int(round(wz / TS))

    def get_tile(self, tx: int, ty: int) -> int:
        sc = self.scene_obj
        if sc and 0 <= tx < sc.w and 0 <= ty < sc.h:
            return sc.tiles[ty][tx]
        return WL  # out-of-bounds = blocking

    def is_walkable(self, tx: int, ty: int) -> bool:
        return self.get_tile(tx, ty) in WALKABLE

    def refresh_tile(self, tx: int, ty: int, soil_key: str):
        """Update visual tanah/tanaman di satu tile."""
        soil = self.state.soil.get(soil_key, {})
        self._update_soil(soil_key, tx, ty, soil)
        if soil.get('crop'):
            self._update_crop(soil_key, tx, ty, soil)
        else:
            self._destroy_crop(soil_key)

    def update(self, dt: float):
        """Animasi air — tint shimmer perlahan di atas tekstur water."""
        if not self._water_ents:
            return
        self._water_t += dt
        # Tint terang agar tekstur water tetap terlihat (nilai 200-255)
        r  = 195 + int(abs(math.sin(self._water_t * 1.5)) * 30)
        g_ = 220 + int(abs(math.sin(self._water_t * 1.0)) * 20)
        b  = 245 + int(abs(math.sin(self._water_t * 2.0)) * 10)
        col = color.rgb(min(255, r), min(255, g_), min(255, b))
        for e in self._water_ents:
            e.color = col

    # ─── INTERNAL: CLEAR ─────────────────────────────────
    def _clear(self):
        for e in self._tile_ents + self._obj_ents:
            destroy(e)
        for e in self._soil_ents.values():
            destroy(e)
        for e in self._crop_ents.values():
            destroy(e)
        self._tile_ents.clear()
        self._obj_ents.clear()
        self._soil_ents.clear()
        self._crop_ents.clear()
        self._water_ents.clear()

    # ─── INTERNAL: BUILD TILES ───────────────────────────
    def _build_tiles(self):
        sc = self.scene_obj
        default_tex = 'floor_wood' if sc.indoor else 'grass'

        for ty in range(sc.h):
            for tx in range(sc.w):
                tid = sc.tiles[ty][tx]
                wx, wz = tx * TS, ty * TS
                self._make_tile(tid, wx, wz, default_tex, tx, ty)

    def _make_tile(self, tid, wx, wz, default_tex, tx=0, ty=0):
        tint = _cb(tx, ty)

        if tid in BLOCKING or tid == MB:
            ge = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), default_tex, tint)
            self._tile_ents.append(ge)
            self._make_blocking_obj(tid, wx, wz)

        elif tid == W:
            we = _e('cube', (wx, 0.05, wz), (TS, 0.10, TS), 'water', tint)
            self._tile_ents.append(we)
            self._water_ents.append(we)

        elif tid == STAIRS_DOWN:
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'stairs_down', tint)
            self._tile_ents.append(base)

        elif tid == STAIRS_UP:
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'stairs_up', tint)
            self._tile_ents.append(base)

        else:
            tex = TILE_TEX.get(tid, default_tex)
            ge = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), tex, tint)
            self._tile_ents.append(ge)

    def _make_blocking_obj(self, tid, wx, wz):
        if tid == TR:
            trunk = _e('cylinder', (wx, TREE_H * 0.28, wz),
                       (TS * 0.28, TREE_H * 0.55, TS * 0.28), 'tree_trunk')
            canopy = _e('sphere', (wx, TREE_H * 0.80, wz),
                        (TS * 0.92, TREE_H * 0.72, TS * 0.92), 'tree_leaf')
            self._obj_ents.extend([trunk, canopy])

        elif tid == DT:
            trunk = _e('cylinder', (wx, TREE_H * 0.40, wz),
                       (TS * 0.22, TREE_H * 0.80, TS * 0.22), 'tree_trunk',
                       _c(68, 50, 30))
            self._obj_ents.append(trunk)

        elif tid == LN:
            pole = _e('cylinder', (wx, OBJ_H * 0.45, wz),
                      (TS * 0.08, OBJ_H * 0.90, TS * 0.08), 'wood_plank')
            lamp = _e('cube', (wx, OBJ_H * 0.95, wz),
                      (TS * 0.38, 0.40, TS * 0.38), 'lamp_glow')
            self._obj_ents.extend([pole, lamp])

        elif tid in (ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, CRYS, CV_W):
            if tid == CV_W:
                e = _e('cube', (wx, WALL_H / 2 + GROUND_H, wz),
                       (TS * 0.98, WALL_H, TS * 0.98), 'wall_cave')
                self._obj_ents.append(e)
            else:
                ore_tex = OBJ_TEX.get(tid, 'crystal')
                base = _e('cube', (wx, WALL_H / 2 + GROUND_H, wz),
                          (TS * 0.98, WALL_H, TS * 0.98), 'wall_cave')
                gem  = _e('cube',
                          (wx, WALL_H + GROUND_H + SMALL_OBJ_H * 0.4, wz),
                          (TS * 0.45, SMALL_OBJ_H * 0.7, TS * 0.45),
                          ore_tex, rotation=(30, 45, 15))
                self._obj_ents.extend([base, gem])

        elif tid == H:
            body = _e('cube', (wx, HOUSE_H * 0.40 + GROUND_H, wz),
                      (TS * 0.94, HOUSE_H * 0.80, TS * 0.94), 'house_wall')
            roof = _e('cube', (wx, HOUSE_H * 0.95 + GROUND_H, wz),
                      (TS * 1.08, HOUSE_H * 0.28, TS * 1.08), 'roof_red',
                      rotation=(0, 45, 0))
            self._obj_ents.extend([body, roof])

        elif tid == FP:
            base = _e('cube', (wx, OBJ_H * 0.5 + GROUND_H, wz),
                      (TS * 0.85, OBJ_H, TS * 0.85), 'wall_stone',
                      _c(90, 80, 75))
            flame = _e('sphere', (wx, OBJ_H + GROUND_H + 0.22, wz),
                       (TS * 0.40, 0.42, TS * 0.40), 'fire_orange')
            self._obj_ents.extend([base, flame])

        else:
            oh = {WL: WALL_H, FN: OBJ_H * 0.75, GT: OBJ_H, PEN: OBJ_H * 0.95,
                  BD: 0.62, TB: 0.82, BS: OBJ_H * 1.4, MR: OBJ_H * 1.2,
                  CL: OBJ_H * 1.35, PP: 0.70, CH: 0.80, CT: 0.90, SH: OBJ_H * 1.5,
                  GR: OBJ_H * 0.90, BOT: 0.60, MB: 0.85, ST: 0.95,
                  DR: WALL_H}.get(tid, OBJ_H)
            tex = OBJ_TEX.get(tid, None)
            col = OBJ_COLORS.get(tid, _c(130, 130, 130))
            sc = 0.88
            if tex:
                e = _e('cube', (wx, oh / 2 + GROUND_H, wz),
                       (TS * sc, oh, TS * sc), tex, col)
            else:
                e = Entity(model='cube', position=(wx, oh / 2 + GROUND_H, wz),
                           scale=(TS * sc, oh, TS * sc), color=col)
            self._obj_ents.append(e)

    # ─── INTERNAL: SOIL / CROP ───────────────────────────
    def _build_all_crops(self):
        sc_name = self.scene_name
        for key, soil in self.state.soil.items():
            parts = key.split(',')
            if len(parts) != 3 or parts[2] != sc_name:
                continue
            tx, ty = int(parts[0]), int(parts[1])
            if soil.get('tilled'):
                self._update_soil(key, tx, ty, soil)
            if soil.get('crop'):
                self._update_crop(key, tx, ty, soil)

    def _update_soil(self, key, tx, ty, soil):
        if key in self._soil_ents:
            destroy(self._soil_ents.pop(key))
        if not soil.get('tilled'):
            return
        wx, wz = tx * TS, ty * TS
        soil_tex = 'soil_wet' if soil.get('watered') else 'soil_dry'
        e = _e('cube', (wx, GROUND_H + 0.06, wz),
               (TS * 0.92, 0.10, TS * 0.92), soil_tex)
        self._soil_ents[key] = e

    def _update_crop(self, key, tx, ty, soil):
        self._destroy_crop(key)
        crop_id = soil.get('crop')
        if not crop_id:
            return
        crop_data = CROPS.get(crop_id, {})
        days  = crop_data.get('days', 4)
        age   = soil.get('age', 0)
        stage = min(3, int(age / max(days, 1) * 4))

        wx, wz = tx * TS, ty * TS
        scale_y = 0.30 + stage * 0.25
        cy = GROUND_H + 0.16 + scale_y / 2

        if stage == 0:
            crop_tex = 'crop_seed'
        elif stage == 1:
            crop_tex = 'crop_sprout'
        else:
            crop_tex = CROP_TEX.get(crop_id, 'crop_lobak')

        e = _e('sphere', (wx, cy, wz),
               (TS * 0.40, scale_y, TS * 0.40), crop_tex)
        stem_h = scale_y * 0.55
        stem = _e('cylinder',
                  (wx, GROUND_H + 0.12 + stem_h / 2, wz),
                  (TS * 0.08, stem_h, TS * 0.08),
                  'cloth_green')
        self._crop_ents[key] = e
        self._crop_ents[key + '_stem'] = stem

    def _destroy_crop(self, key):
        for k in (key, key + '_stem'):
            if k in self._crop_ents:
                destroy(self._crop_ents.pop(k))
