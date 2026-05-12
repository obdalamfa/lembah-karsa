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
from PIL import Image
from ursina import Entity, Vec3, color, destroy, Texture
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
        try:
            img = Image.open(p)
            t = Texture(img)
            t.filtering = False
            _TEX_CACHE[name] = t
            return t
        except Exception:
            pass
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


# Checkerboard outdoor — vivid green pastel (Animal Crossing style)
_CB_LIGHT = color.rgb(162, 225, 120)
_CB_DARK  = color.rgb(138, 205, 98)

# Checkerboard indoor — warm honey wood
_FL_LIGHT = color.rgb(228, 200, 148)
_FL_DARK  = color.rgb(200, 170, 115)

# Cave floor — cool purple-grey
_CV_LIGHT = color.rgb(132, 118, 152)
_CV_DARK  = color.rgb(108, 95, 128)

def _cb(tx, ty):
    return _CB_DARK if (tx + ty) % 2 == 1 else _CB_LIGHT

def _cb_floor(tx, ty):
    return _FL_DARK if (tx + ty) % 2 == 1 else _FL_LIGHT

def _cb_cave(tx, ty):
    return _CV_DARK if (tx + ty) % 2 == 1 else _CV_LIGHT


# ─── TERRAIN NOISE (dari filosofi Panda3D Terrain + Ursina minecraft_clone) ──
# Multi-frequency smooth noise (mirip Perlin stacking dari StephenLujan repo)
def _noise_val(tx, ty):
    """Smooth deterministic noise [0..1] dari posisi tile.
    Menggabungkan 3 frekuensi sin seperti stacked Perlin noise di terrain repos."""
    s = (math.sin(tx * 1.7  + ty * 3.1 ) * 0.50 +
         math.sin(tx * 2.9  + ty * 1.3 ) * 0.30 +
         math.sin(tx * 0.7  + ty * 4.1 ) * 0.20)
    return (s + 1.0) * 0.5   # → [0.0, 1.0]

def _noise2(tx, ty):
    """Noise sekunder untuk dekorasi (frekuensi berbeda)."""
    s = (math.sin(tx * 5.3  + ty * 2.7 ) * 0.60 +
         math.sin(tx * 11.1 + ty * 7.9 ) * 0.40)
    return (s + 1.0) * 0.5

# Terrain step height per level (dari Craig-Macomber: tile height caching)
_STEP_H = 0.22   # tinggi satu "step" voxel, sesuai proporsi GROUND_H


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
    WL:  _c(118, 105, 138),
    TR:  _c(95, 200, 65),    # vivid green
    H:   _c(248, 235, 200),  # cream warm
    MB:  _c(88, 128, 228),   # bright blue mailbox
    DR:  _c(168, 112, 62),
    FN:  _c(178, 148, 95),   # warmer fence
    GT:  _c(168, 130, 72),
    BD:  _c(238, 205, 162),  # warm bed
    ST:  _c(145, 115, 95),
    TB:  _c(205, 168, 112),  # warm table
    BS:  _c(162, 118, 72),
    MR:  _c(165, 225, 255),  # brighter mirror
    FP:  _c(255, 148, 55),   # vivid fireplace
    CL:  _c(105, 85, 68),
    PP:  _c(88, 215, 88),    # vivid plant
    CH:  _c(185, 138, 82),
    CT:  _c(198, 158, 105),
    SH:  _c(185, 145, 95),
    GR:  _c(148, 132, 165),  # softer grave
    LN:  _c(255, 248, 120),  # bright lantern
    DT:  _c(112, 85, 55),
    CV_W:_c(88, 75, 108),
    PEN: _c(155, 115, 65),
    BOT: _c(215, 165, 102),
    CRYS:_c(208, 168, 255),  # soft purple crystal
    ORE_TBG:_c(215, 138, 72),
    ORE_BSI:_c(165, 168, 195),
    ORE_EMS:_c(255, 238, 95),
    ORE_KRS:_c(198, 158, 255),
    ORE_MTH:_c(165, 245, 255),
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
        self.dungeon_level      = state.dungeon_level
        self._tile_ents: list   = []   # ground tiles
        self._obj_ents:  list   = []   # blocking objects
        self._soil_ents: dict   = {}   # key → Entity
        self._crop_ents: dict   = {}   # key → Entity
        self._water_ents: list  = []   # untuk animasi warna
        self._water_t    = 0.0
        # Craig-Macomber pattern: cache tinggi surface per tile (tx,ty) → float
        self._tile_heights: dict = {}

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

    def get_surface_height(self, tx: int, ty: int) -> float:
        """Return Y offset permukaan tile (tx,ty) — digunakan player untuk terrain following."""
        return self._tile_heights.get((tx, ty), 0.0)

    def _is_outdoor(self) -> bool:
        return (self.scene_name not in ('dungeon',) and
                not getattr(self.scene_obj, 'indoor', False))

    def get_tile(self, tx: int, ty: int) -> int:
        sc = self.scene_obj
        if sc:
            if self.scene_name == 'dungeon' and self.state.dungeon_tiles:
                if 0 <= ty < len(self.state.dungeon_tiles) and 0 <= tx < len(self.state.dungeon_tiles[0]):
                    return self.state.dungeon_tiles[ty][tx]
            if 0 <= tx < sc.w and 0 <= ty < sc.h:
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
        self._tile_heights.clear()

    # ─── INTERNAL: BUILD TILES ───────────────────────────
    def _build_tiles(self):
        sc = self.scene_obj
        is_dungeon = (self.scene_name == 'dungeon' and self.state.dungeon_tiles)
        default_tex = 'cave_floor' if is_dungeon else ('floor_wood' if sc.indoor else 'grass')

        tiles_to_build = self.state.dungeon_tiles if is_dungeon else sc.tiles
        h = len(tiles_to_build)
        w = len(tiles_to_build[0]) if h > 0 else 0

        for ty in range(h):
            for tx in range(w):
                tid = tiles_to_build[ty][tx]
                wx, wz = tx * TS, ty * TS
                self._make_tile(tid, wx, wz, default_tex, tx, ty)

    def _make_tile(self, tid, wx, wz, default_tex, tx=0, ty=0):
        # Pick tint based on tile type so indoor rooms aren't all white
        if tid == FL or (tid in BLOCKING and default_tex == 'floor_wood'):
            tint = _cb_floor(tx, ty)
        elif tid == CV_F or (tid in BLOCKING and default_tex == 'cave_floor'):
            tint = _cb_cave(tx, ty)
        else:
            tint = _cb(tx, ty)

        if tid in BLOCKING or tid == MB:
            ge = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), default_tex, tint)
            self._tile_ents.append(ge)
            self._make_blocking_obj(tid, wx, wz)

        elif tid == G:
            # ── Minecraft-style voxel height-stepping (dari Ursina minecraft_clone + Panda3D terrain repos) ──
            # Noise menentukan jumlah step: 0, 1, atau 2 lapisan tambahan
            nv = _noise_val(tx, ty) if self._is_outdoor() else 0.0
            step = 2 if nv > 0.74 else (1 if nv > 0.48 else 0)
            step_h = step * _STEP_H

            # Base dirt cube (selalu ada)
            base = _e('cube', (wx, GROUND_H / 2, wz), (TS, GROUND_H, TS), 'dirt', tint)
            self._tile_ents.append(base)

            # Tambahan lapisan untuk step 1 dan 2 — makin tinggi, sedikit lebih sempit
            for s in range(1, step + 1):
                layer_y = GROUND_H + (s - 0.5) * _STEP_H
                shrink  = s * 0.03
                layer   = _e('cube', (wx, layer_y, wz),
                             (TS * (1 - shrink), _STEP_H, TS * (1 - shrink)), 'dirt', tint)
                self._tile_ents.append(layer)

            # Grass cap di atas step tertinggi
            cap_y = GROUND_H + step_h + 0.04
            cap   = _e('cube', (wx, cap_y, wz), (TS * 1.005, 0.08, TS * 1.005), 'grass')
            self._tile_ents.append(cap)

            # Cache tinggi surface untuk player terrain-following
            self._tile_heights[(tx, ty)] = step_h

            # Dekorasi organik: batu kecil / rumput tinggi / bunga liar (30% tile)
            if nv < 0.30:
                self._add_outdoor_deco(wx, wz, GROUND_H + step_h, tx, ty, nv)

        elif tid == W:
            we = _e('cube', (wx, 0.05, wz), (TS, 0.10, TS), 'water',
                    color.rgb(88, 210, 218))  # teal turquoise
            self._tile_ents.append(we)
            self._water_ents.append(we)

        elif tid == STAIRS_DOWN:
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'stairs_down', tint)
            self._tile_ents.append(base)

        elif tid == STAIRS_UP:
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'stairs_up', tint)
            self._tile_ents.append(base)

        elif tid == P and self._is_outdoor():
            # Path tile: batu dasar + butiran kerikil kecil (dari filosofi tile-detail Panda3D terrain)
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'path_stone', tint)
            self._tile_ents.append(base)
            nv2 = _noise2(tx, ty)
            if nv2 > 0.55:
                ox = math.sin(tx * 53.7 + ty * 89.1) * 0.38
                oz = math.cos(tx * 73.2 + ty * 47.5) * 0.38
                pebble = _e('cube', (wx + ox, GROUND_H + 0.04, wz + oz),
                            (0.18, 0.09, 0.16), 'path_stone', _c(140, 128, 112))
                self._tile_ents.append(pebble)

        elif tid == CV_F:
            base = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), 'cave_floor', _cb_cave(tx, ty))
            self._tile_ents.append(base)
            nv2 = _noise2(tx, ty)
            if nv2 > 0.70:
                ox = math.sin(tx * 41.3 + ty * 97.7) * 0.28
                oz = math.cos(tx * 63.9 + ty * 31.1) * 0.28
                h_stala = 0.22 + nv2 * 0.18
                stala = _e('cube', (wx + ox, WALL_H + GROUND_H - h_stala * 0.5, wz + oz),
                           (0.10, h_stala, 0.10), 'wall_cave', _c(65, 55, 75))
                self._tile_ents.append(stala)

        else:
            tex = TILE_TEX.get(tid, default_tex)
            ge = _e('cube', (wx, GROUND_H/2, wz), (TS, GROUND_H, TS), tex, tint)
            self._tile_ents.append(ge)

    # ─── INTERNAL: OUTDOOR DECORATION ───────────────────────
    def _add_outdoor_deco(self, wx, wz, surface_y, tx, ty, nv):
        """Dekorasi organik berbasis noise: batu, rumput tinggi, bunga liar.
        Terinspirasi dari Craig-Macomber placement system + Ursina voxel tile detail."""
        ox = math.sin(tx * 53.7 + ty * 89.1) * 0.42
        oz = math.cos(tx * 73.2 + ty * 47.5) * 0.42
        dtype = int(abs(math.sin(tx * 200.3 + ty * 150.7)) * 3)

        if dtype == 0:   # Batu kecil — rounded look
            rock = _e('sphere', (wx + ox, surface_y + 0.08, wz + oz),
                      (0.24, 0.16, 0.22), 'path_stone', _c(178, 165, 145))
            self._tile_ents.append(rock)

        elif dtype == 1:  # Rumput tinggi / semak — vivid green
            tuft = _e('cube', (wx + ox, surface_y + 0.20, wz + oz),
                      (0.10, 0.38, 0.08), 'cloth_green', _c(72, 198, 58))
            # Semak kecil sampingan
            tuft2 = _e('cube', (wx + ox + 0.12, surface_y + 0.14, wz + oz),
                       (0.08, 0.26, 0.07), 'cloth_green', _c(88, 215, 70))
            self._tile_ents.extend([tuft, tuft2])

        else:             # Bunga warna-warni (Animal Crossing style)
            stem = _e('cylinder', (wx + ox, surface_y + 0.14, wz + oz),
                      (0.05, 0.26, 0.05), 'cloth_green', _c(68, 185, 52))
            fc_idx = int(abs(math.sin(tx * 100 + ty * 70)) * 5)
            fc = [_c(255, 88, 140), _c(255, 215, 55), _c(148, 88, 255),
                  _c(255, 148, 55), _c(88, 215, 255)][fc_idx]
            flower = _e('sphere', (wx + ox, surface_y + 0.30, wz + oz),
                        (0.18, 0.16, 0.18), 'lamp_glow', fc)
            # Daun bunga kecil di sisi
            leaf = _e('sphere', (wx + ox + 0.08, surface_y + 0.22, wz + oz),
                      (0.10, 0.10, 0.08), 'cloth_green', _c(72, 198, 58))
            self._tile_ents.extend([stem, flower, leaf])

    def _make_blocking_obj(self, tid, wx, wz):
        if tid == TR:
            # Animal Crossing style: batang gemuk bulat + kanopi pom-pom multi-sphere
            trunk = _e('cylinder', (wx, TREE_H * 0.26, wz),
                       (TS * 0.35, TREE_H * 0.52, TS * 0.35), 'tree_trunk',
                       _c(145, 100, 58))
            # Kanopi tengah besar (hijau terang)
            canopy = _e('sphere', (wx, TREE_H * 0.84, wz),
                        (TS * 1.08, TREE_H * 0.82, TS * 1.08), 'tree_leaf',
                        _c(95, 200, 65))
            # 6 puff mengelilingi + sedikit bawah → tampilan lebih bulat & lebat
            puff_offsets = [(0,60),(1,120),(0,180),(1,240),(0,300),(1,0)]
            for side, ang_deg in puff_offsets:
                rad = math.radians(ang_deg)
                dist = TS * (0.46 + side * 0.04)
                cx = wx + math.sin(rad) * dist
                cz = wz + math.cos(rad) * dist
                cy = TREE_H * (0.74 - side * 0.06)
                sc_xy = TS * (0.58 + side * 0.04)
                g = _c(78 + side*12, 185 + side*10, 52 + side*8)
                cluster = _e('sphere', (cx, cy, cz), (sc_xy, TREE_H*0.48, sc_xy), 'tree_leaf', g)
                self._obj_ents.append(cluster)
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
            # Rumah gaya Animal Crossing: tembok krem hangat, atap merah terakota
            body = _e('cube', (wx, HOUSE_H * 0.40 + GROUND_H, wz),
                      (TS * 0.94, HOUSE_H * 0.80, TS * 0.94), 'house_wall',
                      _c(248, 235, 200))
            roof = _e('cube', (wx, HOUSE_H * 0.97 + GROUND_H, wz),
                      (TS * 1.12, HOUSE_H * 0.30, TS * 1.12), 'roof_red',
                      _c(215, 88, 68), rotation=(0, 45, 0))
            # Jendela biru lembut
            for wx_off in (-0.26, 0.26):
                win = Entity(model='cube',
                             position=(wx + wx_off * TS, HOUSE_H * 0.44 + GROUND_H, wz - TS * 0.47),
                             scale=(TS * 0.26, TS * 0.26, 0.07),
                             color=color.rgb(160, 215, 255))
                win2 = Entity(model='cube',
                              position=(wx + wx_off * TS, HOUSE_H * 0.44 + GROUND_H, wz - TS * 0.48),
                              scale=(TS * 0.28, TS * 0.28, 0.05),
                              color=color.rgb(245, 240, 215))
                self._obj_ents.extend([win2, win])
            # Pintu kecil tengah
            door = Entity(model='cube',
                          position=(wx, HOUSE_H * 0.28 + GROUND_H, wz - TS * 0.47),
                          scale=(TS * 0.24, HOUSE_H * 0.55, 0.07),
                          color=color.rgb(138, 92, 52))
            chimney = _e('cube', (wx + TS * 0.26, HOUSE_H * 1.10 + GROUND_H, wz - TS * 0.18),
                         (TS * 0.16, HOUSE_H * 0.32, TS * 0.16), 'wall_stone', _c(155, 138, 122))
            self._obj_ents.extend([body, roof, door, chimney])

        elif tid == FP:
            base = _e('cube', (wx, OBJ_H * 0.5 + GROUND_H, wz),
                      (TS * 0.85, OBJ_H, TS * 0.85), 'wall_stone',
                      _c(90, 80, 75))
            flame = _e('sphere', (wx, OBJ_H + GROUND_H + 0.22, wz),
                       (TS * 0.40, 0.42, TS * 0.40), 'fire_orange')
            self._obj_ents.extend([base, flame])

        elif tid == GR:
            vert  = _e('cube', (wx, OBJ_H * 0.50 + GROUND_H, wz),
                       (TS * 0.16, OBJ_H * 0.90, TS * 0.14), 'grave_stone', _c(112, 100, 122))
            horiz = _e('cube', (wx, OBJ_H * 0.68 + GROUND_H, wz),
                       (TS * 0.52, TS * 0.14, TS * 0.12), 'grave_stone', _c(112, 100, 122))
            self._obj_ents.extend([vert, horiz])

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
