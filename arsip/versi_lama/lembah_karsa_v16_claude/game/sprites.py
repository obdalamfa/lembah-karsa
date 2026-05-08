"""
sprites.py — Asset Loader dengan fallback warna.

Strategi V15: load PNG dari assets/ jika ada, fallback ke kotak warna jika tidak.
Hasilnya: game tetap jalan walau make_assets.py belum dijalankan.

Keys SPRITES & ANIMATED dijaga kompatibel dengan render_world v4:
  SPRITES['grass'..'cave_wall'..'water_lily']  — tile & object
  SPRITES['mandrake'..'wild_berry']            — wild items
  SPRITES['shadow_small','shadow_med','shadow_large','cloud_shadow']
  SPRITES['crops'][crop_id][0..3]              — tanaman 4 fase
  ANIMATED['water'][0..3]                      — air mengalir
  ANIMATED['fireplace'][0..1], ['lantern'][0..1]
  ANIMATED['running_mushroom'][0..1], ['firefly'][0..2]
  ANIMATED['player'/'npc_xxx'][direction][frame]  — 4 arah × 3 frame
"""
import pygame
import os
import math
import random
from .config import C, TILE


SPRITES = {}
ANIMATED = {}

# Path asset relatif ke working dir (saat main.py dijalankan)
ASSETS_DIR = "assets"


# ═══════════════════════════════════════════════════
#  PROCEDURAL HELPERS (untuk fallback & efek transparan)
# ═══════════════════════════════════════════════════
def _surf(w, h, fill=None):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if fill is not None:
        s.fill(fill)
    return s


def make_shadow(width=20, height=8):
    """Bayangan oval transparan."""
    s = _surf(TILE, TILE)
    pygame.draw.ellipse(s, (0, 0, 0, 110),
                        ((TILE - width) // 2, TILE - height - 2, width, height))
    return s


def make_shadow_large(width=60, height=18):
    """Bayangan untuk naga (sprite besar)."""
    s = _surf(96, 64)
    pygame.draw.ellipse(s, (0, 0, 0, 110),
                        ((96 - width) // 2, 64 - height - 2, width, height))
    return s


def make_cloud_shadow(width=160, height=100):
    """Bayangan awan untuk parallax."""
    s = _surf(width, height)
    # Dua oval transparan agar terkesan awan
    pygame.draw.ellipse(s, (40, 50, 80, 35), (0, height // 4, width * 3 // 4, height // 2))
    pygame.draw.ellipse(s, (40, 50, 80, 30), (width // 4, 0, width * 3 // 4, height * 3 // 4))
    return s


# ═══════════════════════════════════════════════════
#  FALLBACK TILE GENERATORS (warna sederhana + noise)
# ═══════════════════════════════════════════════════
def _noisy_tile(base, noise_colors, seed=42, n=20):
    """Tile dasar warna + noise untuk variasi visual."""
    s = pygame.Surface((TILE, TILE))
    s.fill(base)
    rng = random.Random(seed)
    for _ in range(n):
        x = rng.randint(0, TILE - 1)
        y = rng.randint(0, TILE - 1)
        c = rng.choice(noise_colors)
        sz = rng.randint(1, 2)
        pygame.draw.rect(s, c, (x, y, sz, sz))
    return s


def _solid_tile(color):
    s = pygame.Surface((TILE, TILE))
    s.fill(color)
    return s


def _crystal_tile(seed=99):
    """Kristal cluster — warna gradient ungu-pink-biru."""
    s = _surf(TILE, TILE)
    s.fill(C.cave_floor)
    # Cluster geometris
    pygame.draw.polygon(s, C.crystal_purple, [(8, 28), (4, 14), (12, 6), (16, 18)])
    pygame.draw.polygon(s, C.crystal_blue, [(16, 28), (14, 12), (22, 8), (24, 22)])
    pygame.draw.polygon(s, C.crystal_pink, [(20, 30), (22, 18), (28, 14), (28, 28)])
    # Highlight
    pygame.draw.line(s, C.crystal_glow, (10, 18), (12, 10), 1)
    pygame.draw.line(s, C.crystal_glow, (18, 18), (20, 12), 1)
    return s


def _waterfall_tile(frame=0):
    """Air terjun — pita putih+biru bergerak."""
    s = pygame.Surface((TILE, TILE))
    s.fill(C.waterfall_blue)
    off = (frame * 4) % 8
    for y in range(0, TILE, 4):
        pygame.draw.line(s, C.waterfall_white, (4 + ((y + off) % 6), y),
                         (28 - ((y + off) % 6), y), 2)
    return s


def _dock_tile():
    """Dermaga kayu."""
    s = pygame.Surface((TILE, TILE))
    s.fill(C.dock_wood)
    # Papan kayu horizontal
    for y in [4, 14, 24]:
        pygame.draw.line(s, C.dock_wood_dk, (0, y), (TILE, y), 1)
    # Knot kayu
    pygame.draw.circle(s, C.dock_wood_dk, (8, 8), 2)
    pygame.draw.circle(s, C.dock_wood_dk, (24, 18), 2)
    return s


def _boat_tile():
    """Perahu kecil — view dari atas."""
    s = _surf(TILE, TILE)
    s.fill(C.water_light if hasattr(C, 'water_light') else (60, 140, 210))
    # Hull oval
    pygame.draw.ellipse(s, C.boat_wood, (4, 8, 24, 18))
    pygame.draw.ellipse(s, C.boat_wood_dk, (4, 8, 24, 18), 2)
    # Bangku tengah
    pygame.draw.rect(s, C.boat_wood_dk, (10, 14, 12, 3))
    return s


def _water_lily_tile():
    """Eceng gondok — daun + bunga ungu."""
    s = _surf(TILE, TILE)
    # Latar air biar nyambung
    s.fill((60, 140, 210))
    # Daun
    pygame.draw.circle(s, C.lily_green, (10, 18), 7)
    pygame.draw.circle(s, C.lily_green, (22, 14), 6)
    # Bunga
    pygame.draw.circle(s, C.lily_purple, (16, 12), 3)
    pygame.draw.circle(s, (240, 220, 100), (16, 12), 1)
    return s


def _bat_dropping_tile():
    """Lantai gua dengan kotoran kelelawar (bat dropping)."""
    s = pygame.Surface((TILE, TILE))
    s.fill(C.cave_floor)
    rng = random.Random(77)
    for _ in range(8):
        x = rng.randint(2, TILE - 4)
        y = rng.randint(2, TILE - 4)
        pygame.draw.ellipse(s, C.bat_dropping, (x, y, 3, 2))
    return s


def _crypt_floor_tile():
    s = pygame.Surface((TILE, TILE))
    s.fill(C.crypt_floor)
    # Pola batu
    pygame.draw.rect(s, C.crypt_stone_dk, (0, 15, TILE, 1))
    pygame.draw.rect(s, C.crypt_stone_dk, (15, 0, 1, TILE))
    return s


def _crypt_wall_tile():
    s = pygame.Surface((TILE, TILE))
    s.fill(C.crypt_stone)
    rng = random.Random(55)
    for _ in range(15):
        x = rng.randint(0, TILE - 2)
        y = rng.randint(0, TILE - 2)
        pygame.draw.rect(s, C.crypt_stone_dk, (x, y, 2, 1))
    return s


# ═══════════════════════════════════════════════════
#  ASSET LOADER — Smart loader dengan fallback
# ═══════════════════════════════════════════════════
def load_img(rel_path, w=TILE, h=TILE, fallback_func=None, fallback_color=(255, 0, 255)):
    """Coba load PNG; jika gagal panggil fallback_func() atau kotak warna."""
    full_path = os.path.join(ASSETS_DIR, rel_path)
    if os.path.exists(full_path):
        try:
            img = pygame.image.load(full_path).convert_alpha()
            return pygame.transform.scale(img, (w, h))
        except Exception as e:
            print(f"⚠️  Gagal load {full_path}: {e}")

    if fallback_func is not None:
        s = fallback_func()
        if s.get_size() != (w, h):
            s = pygame.transform.scale(s, (w, h))
        return s

    # Fallback paling sederhana: kotak warna + border hitam
    s = pygame.Surface((w, h))
    s.fill(fallback_color)
    pygame.draw.rect(s, (0, 0, 0), (0, 0, w, h), 1)
    return s


def load_char_anim(char_name, fallback_color=(150, 150, 150), is_huge=False):
    """Load animasi karakter 4 arah × 3 frame.
    Layout file: assets/chars/<name>/<dir>_<frame>.png
    Sprite size: TILE × TILE*1.5 (lebih tinggi dari ubin) atau 96×64 (huge/naga).
    """
    target_w = 96 if is_huge else TILE
    target_h = 64 if is_huge else int(TILE * 1.5)
    base = f"chars/{char_name}"
    anim = {}
    for d in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(3):
            file_path = os.path.join(ASSETS_DIR, f"{base}/{d}_{f}.png")
            if os.path.exists(file_path):
                try:
                    img = pygame.image.load(file_path).convert_alpha()
                    frames.append(pygame.transform.scale(img, (target_w, target_h)))
                    continue
                except Exception:
                    pass
            # Fallback: kotak warna + petunjuk arah
            s = _surf(target_w, target_h, fallback_color)
            if d == 'down':
                pygame.draw.rect(s, (40, 30, 40), (target_w // 4, 4, target_w // 2, 4))
            elif d == 'up':
                pygame.draw.rect(s, (40, 30, 40), (target_w // 4, target_h - 8, target_w // 2, 4))
            else:
                pygame.draw.rect(s, (40, 30, 40), (4 if d == 'left' else target_w - 8, 8, 4, 4))
            pygame.draw.rect(s, (0, 0, 0), (0, 0, target_w, target_h), 1)
            frames.append(s)
        anim[d] = frames
    return anim


# ═══════════════════════════════════════════════════
#  INIT — populate SPRITES + ANIMATED
# ═══════════════════════════════════════════════════
def init_sprites():
    """Generate/load semua sprite & cache."""
    # ─── TILES DASAR ───
    SPRITES['grass'] = load_img("tiles/grass.png",
        fallback_func=lambda: _noisy_tile(C.g0, [C.g1, C.g2, C.g3], seed=42))
    SPRITES['dirt'] = load_img("tiles/dirt.png",
        fallback_func=lambda: _noisy_tile(C.d1, [C.d0, C.d2, C.d3], seed=43))
    SPRITES['path'] = load_img("tiles/path.png",
        fallback_func=lambda: _noisy_tile(C.p1, [C.p0, C.p2], seed=44))
    SPRITES['floor'] = load_img("tiles/floor.png",
        fallback_func=lambda: _noisy_tile(C.fl, [C.fl2, C.fl3], seed=45))
    SPRITES['wall'] = load_img("tiles/wall.png",
        fallback_func=lambda: _noisy_tile(C.wl, [C.wl2], seed=46, n=8))
    SPRITES['tilled_dry'] = load_img("tiles/tilled_dry.png",
        fallback_func=lambda: _noisy_tile(C.d3, [C.d0], seed=47))
    SPRITES['tilled_wet'] = load_img("tiles/tilled_wet.png",
        fallback_func=lambda: _noisy_tile((50, 30, 15), [(40, 25, 10)], seed=48))
    SPRITES['cave_wall'] = load_img("tiles/cave_wall.png",
        fallback_func=lambda: _noisy_tile(C.cave_stone, [C.cave_stone_dk, C.cave_stone_lt], seed=49, n=30))
    SPRITES['cave_floor'] = load_img("tiles/cave_floor.png",
        fallback_func=lambda: _noisy_tile(C.cave_floor, [C.cave_stone_dk], seed=50))
    SPRITES['straw'] = load_img("tiles/straw.png",
        fallback_func=lambda: _noisy_tile(C.pen_floor, [(120, 90, 50), (160, 120, 70)], seed=51))
    # Tile baru v5
    SPRITES['crypt_wall'] = load_img("tiles/crypt_wall.png", fallback_func=_crypt_wall_tile)
    SPRITES['crypt_floor'] = load_img("tiles/crypt_floor.png", fallback_func=_crypt_floor_tile)
    SPRITES['crystal'] = load_img("tiles/crystal.png", fallback_func=_crystal_tile)
    SPRITES['bat_dropping'] = load_img("tiles/bat_dropping.png", fallback_func=_bat_dropping_tile)
    SPRITES['dock'] = load_img("tiles/dock.png", fallback_func=_dock_tile)
    SPRITES['boat'] = load_img("tiles/boat.png", fallback_func=_boat_tile)
    SPRITES['water_lily'] = load_img("tiles/water_lily.png", fallback_func=_water_lily_tile)

    # ─── ANIMATED TILES ───
    # Air (4 frame)
    ANIMATED['water'] = []
    for i in range(4):
        spr = load_img(f"tiles/water_{i}.png",
            fallback_func=lambda fi=i: _noisy_tile(
                (60, 140, 210),
                [(80, 160, 230), (100, 180, 240)],
                seed=60 + fi))
        ANIMATED['water'].append(spr)
    # Waterfall (4 frame)
    ANIMATED['waterfall'] = []
    for i in range(4):
        spr = load_img(f"tiles/waterfall_{i}.png",
            fallback_func=lambda fi=i: _waterfall_tile(fi))
        ANIMATED['waterfall'].append(spr)
    # Untuk akses by-tile-name di render_world: gunakan frame 0 sebagai default
    SPRITES['waterfall'] = ANIMATED['waterfall'][0]

    # Fireplace (2 frame)
    ANIMATED['fireplace'] = []
    for i in range(2):
        spr = load_img(f"objects/fireplace_{i}.png",
            fallback_func=lambda fi=i: _make_fireplace_fallback(fi))
        ANIMATED['fireplace'].append(spr)
    # Lantern (2 frame)
    ANIMATED['lantern'] = []
    for i in range(2):
        spr = load_img(f"objects/lantern_{i}.png",
            fallback_func=lambda fi=i: _make_lantern_fallback(fi))
        ANIMATED['lantern'].append(spr)

    # ─── OBJECTS ───
    obj_fallbacks = {
        'tree': lambda: _make_tree_fallback(),
        'dead_tree': lambda: _solid_tile(C.fn2),
        'fence': lambda: _make_fence_fallback(),
        'gate': lambda: _make_gate_fallback(),
        'mailbox': lambda: _solid_tile((220, 60, 60)),
        'door': lambda: _make_door_fallback(),
        'chest': lambda: _solid_tile((180, 130, 60)),
        'bed': lambda: _make_bed_fallback(),
        'stove': lambda: _solid_tile((80, 80, 80)),
        'table': lambda: _solid_tile(C.fn),
        'bookshelf': lambda: _solid_tile((100, 60, 40)),
        'mirror': lambda: _solid_tile((150, 200, 240)),
        'clock': lambda: _solid_tile((150, 100, 60)),
        'plant_pot': lambda: _solid_tile((140, 90, 50)),
        'counter': lambda: _solid_tile(C.fn3),
        'shelf_store': lambda: _solid_tile((140, 100, 60)),
        'grave': lambda: _make_grave_fallback(),
        'pen_post': lambda: _solid_tile(C.fn2),
        # 'house' diurus inline di render_world v4 (composite)
    }
    for name, fb in obj_fallbacks.items():
        SPRITES[name] = load_img(f"objects/{name}.png", fallback_func=fb)

    # ─── WILD ITEMS ───
    SPRITES['mandrake'] = load_img("objects/mandrake.png",
        fallback_func=lambda: _solid_tile(C.mandrake_skin))
    SPRITES['wild_herb'] = load_img("objects/wild_herb.png",
        fallback_func=lambda: _solid_tile((80, 160, 80)))
    SPRITES['wild_berry'] = load_img("objects/wild_berry.png",
        fallback_func=lambda: _solid_tile((180, 50, 80)))

    # Running mushroom (2 frame)
    ANIMATED['running_mushroom'] = []
    for i in range(2):
        spr = load_img(f"objects/running_mushroom_{i}.png",
            fallback_func=lambda fi=i: _make_mushroom_fallback(fi))
        ANIMATED['running_mushroom'].append(spr)
    # Firefly (3 frame)
    ANIMATED['firefly'] = []
    for i in range(3):
        spr = load_img(f"objects/firefly_{i}.png",
            fallback_func=lambda fi=i: _make_firefly_fallback(fi))
        ANIMATED['firefly'].append(spr)

    # ─── CROPS (4 fase) ───
    SPRITES['crops'] = {}
    crop_colors = {
        'lobak': (C.cg, C.cg2),
        'wortel': (C.co, C.d1),
        'stroberi': (C.cr, C.cg),
        'jagung': (C.cy, C.cg),
        'tomat': (C.cr, (255, 80, 80)),
        'labu': (C.co, C.fn),
        'bayam': (C.g2, C.g0),
        'jamur': ((212, 164, 116), C.fn2),
    }
    for crop_id, (c1, c2) in crop_colors.items():
        SPRITES['crops'][crop_id] = []
        for stage in range(4):
            spr = load_img(f"objects/{crop_id}_{stage}.png",
                fallback_func=lambda c1=c1, c2=c2, s=stage: _make_crop_fallback(s, c1, c2))
            SPRITES['crops'][crop_id].append(spr)

    # ─── SHADOWS & CLOUD ───
    SPRITES['shadow_small'] = make_shadow(20, 8)
    SPRITES['shadow_med'] = make_shadow(28, 10)
    SPRITES['shadow_large'] = make_shadow_large(60, 18)
    SPRITES['cloud_shadow'] = make_cloud_shadow(160, 100)

    # ─── KARAKTER (player + 12 manusia + 10 makhluk halus + 9 hewan = 32) ───
    # Manusia
    ANIMATED['player'] = load_char_anim('player', (50, 100, 200))
    ANIMATED['npc_arya'] = load_char_anim('npc_arya', (100, 180, 100))
    ANIMATED['npc_sari'] = load_char_anim('npc_sari', C.nc_sari)
    ANIMATED['npc_raka'] = load_char_anim('npc_raka', C.nc_raka)
    ANIMATED['npc_maya'] = load_char_anim('npc_maya', C.nc_maya)
    ANIMATED['npc_budi'] = load_char_anim('npc_budi', C.nc_budi)
    ANIMATED['npc_joko'] = load_char_anim('npc_joko', C.nc_joko)
    ANIMATED['npc_cici'] = load_char_anim('npc_cici', C.nc_cici)
    ANIMATED['npc_bowo'] = load_char_anim('npc_bowo', C.nc_bowo)
    ANIMATED['npc_ningsih'] = load_char_anim('npc_ningsih', C.nc_ningsih)
    ANIMATED['npc_pak_guru'] = load_char_anim('npc_pak_guru', C.nc_guru)
    ANIMATED['npc_mbok_jum'] = load_char_anim('npc_mbok_jum', C.nc_mbokjum)
    ANIMATED['npc_jaka_ronda'] = load_char_anim('npc_jaka_ronda', C.nc_jaka)

    # Makhluk halus (di-key by type, bukan by id, mengikuti pattern v4)
    ANIMATED['npc_jin'] = load_char_anim('npc_jin', C.jin_aura)
    ANIMATED['npc_demit'] = load_char_anim('npc_demit', C.demit_dark)
    ANIMATED['npc_tuyul'] = load_char_anim('npc_tuyul', C.tuyul_skin)
    ANIMATED['npc_kuntilanak'] = load_char_anim('npc_kuntilanak', C.kunti_white)
    ANIMATED['npc_pocong'] = load_char_anim('npc_pocong', C.pocong_white)
    ANIMATED['npc_genderuwo'] = load_char_anim('npc_genderuwo', C.genderuwo_brown)
    ANIMATED['npc_wewe'] = load_char_anim('npc_wewe', C.wewe_dark)
    ANIMATED['npc_banaspati'] = load_char_anim('npc_banaspati', (255, 100, 0))
    ANIMATED['npc_leak'] = load_char_anim('npc_leak', (180, 60, 120))
    # Naga = sprite besar 96×64
    ANIMATED['npc_naga'] = load_char_anim('npc_naga', C.naga_body, is_huge=True)

    # Hewan (di-key by type)
    ANIMATED['npc_sapi'] = load_char_anim('npc_sapi', C.sapi_white)
    ANIMATED['npc_ayam'] = load_char_anim('npc_ayam', C.ayam_white)
    ANIMATED['npc_kambing'] = load_char_anim('npc_kambing', C.kambing_grey)
    ANIMATED['npc_bebek'] = load_char_anim('npc_bebek', C.bebek_white)
    ANIMATED['npc_domba'] = load_char_anim('npc_domba', C.domba_white)
    ANIMATED['npc_kuda'] = load_char_anim('npc_kuda', C.kuda_brown)
    ANIMATED['npc_kucing'] = load_char_anim('npc_kucing', C.kucing_oren)
    ANIMATED['npc_rubah'] = load_char_anim('npc_rubah', C.rubah_orange)
    ANIMATED['npc_kelinci'] = load_char_anim('npc_kelinci', C.kelinci_white)


# ═══════════════════════════════════════════════════
#  FALLBACK PARTICULAR FUNCTIONS
# ═══════════════════════════════════════════════════
def _make_fireplace_fallback(frame):
    s = _surf(TILE, TILE, (60, 50, 50))
    pygame.draw.rect(s, (40, 30, 30), (4, 6, 24, 22), border_radius=2)
    flame_h = 12 if frame == 0 else 10
    pygame.draw.polygon(s, C.fire1, [(8, 22), (12, 22 - flame_h), (16, 22), (14, 24)])
    pygame.draw.polygon(s, C.fire2, [(16, 22), (20, 22 - flame_h + 2), (24, 22), (22, 24)])
    pygame.draw.polygon(s, C.fire3, [(12, 22), (14, 22 - flame_h + 4), (18, 22)])
    return s


def _make_lantern_fallback(frame):
    s = _surf(TILE, TILE)
    # Tiang
    pygame.draw.rect(s, C.fn2, (14, 8, 4, 22))
    # Kepala lampu
    pygame.draw.rect(s, (50, 40, 30), (10, 4, 12, 10), border_radius=2)
    glow = (255, 230, 100) if frame == 0 else (255, 200, 60)
    pygame.draw.rect(s, glow, (12, 6, 8, 6))
    return s


def _make_tree_fallback():
    s = _surf(TILE, TILE)
    # Daun
    pygame.draw.circle(s, C.g3, (16, 12), 13)
    pygame.draw.circle(s, C.g0, (16, 10), 10)
    # Batang
    pygame.draw.rect(s, C.fn2, (13, 18, 6, 12))
    return s


def _make_fence_fallback():
    s = _surf(TILE, TILE)
    pygame.draw.rect(s, C.fn2, (0, 12, TILE, 4))
    pygame.draw.rect(s, C.fn2, (0, 22, TILE, 4))
    for x in [4, 14, 24]:
        pygame.draw.rect(s, C.fn, (x, 6, 4, 22))
    return s


def _make_gate_fallback():
    s = _surf(TILE, TILE)
    pygame.draw.rect(s, C.fn3, (0, 12, TILE, 4))
    pygame.draw.rect(s, C.fn3, (0, 22, TILE, 4))
    for x in [4, 14, 24]:
        pygame.draw.rect(s, C.fn, (x, 6, 4, 22))
    pygame.draw.rect(s, C.ui_gold, (14, 14, 4, 8))  # gembok emas
    return s


def _make_door_fallback():
    s = _surf(TILE, TILE, C.fn2)
    pygame.draw.rect(s, C.fn, (4, 4, 24, 26), border_radius=3)
    pygame.draw.circle(s, C.ui_gold, (24, 18), 2)
    return s


def _make_bed_fallback():
    s = _surf(TILE, TILE)
    pygame.draw.rect(s, C.fn3, (2, 8, 28, 20), border_radius=3)
    pygame.draw.rect(s, (200, 200, 240), (4, 10, 24, 8))
    pygame.draw.rect(s, (180, 80, 80), (4, 18, 24, 8))
    return s


def _make_grave_fallback():
    s = _surf(TILE, TILE)
    pygame.draw.rect(s, (110, 100, 100), (8, 6, 16, 22))
    pygame.draw.arc(s, (110, 100, 100), (8, 4, 16, 8), 0, 3.14, 0)
    pygame.draw.rect(s, (60, 50, 50), (12, 12, 8, 2))  # tulisan
    pygame.draw.rect(s, (60, 50, 50), (12, 16, 8, 2))
    return s


def _make_mushroom_fallback(frame):
    s = _surf(TILE, TILE)
    bounce = 0 if frame == 0 else -2
    # Topi merah
    pygame.draw.ellipse(s, C.mushroom_red, (4, 10 + bounce, 24, 14))
    # Bintik putih
    pygame.draw.circle(s, C.mushroom_white, (10, 14 + bounce), 2)
    pygame.draw.circle(s, C.mushroom_white, (20, 13 + bounce), 2)
    # Batang
    pygame.draw.rect(s, C.sk3, (13, 20 + bounce, 6, 8))
    return s


def _make_firefly_fallback(frame):
    s = _surf(TILE, TILE)
    glow_radius = [4, 6, 5][frame]
    glow_alpha = [180, 220, 200][frame]
    # Aura halo
    halo = _surf(TILE, TILE)
    pygame.draw.circle(halo, (*C.firefly_glow, glow_alpha // 3), (16, 16), glow_radius + 4)
    s.blit(halo, (0, 0))
    pygame.draw.circle(s, C.firefly_glow, (16, 16), glow_radius)
    pygame.draw.circle(s, (255, 255, 220), (16, 16), max(1, glow_radius - 2))
    return s


def _make_crop_fallback(stage, c1, c2):
    s = _surf(TILE, TILE)
    # Gundukan tanah dasar
    pygame.draw.ellipse(s, C.d1, (4, 22, 24, 8))
    if stage == 0:
        pygame.draw.rect(s, c2, (14, 20, 4, 6))
    elif stage == 1:
        pygame.draw.rect(s, c2, (12, 14, 8, 12))
    elif stage == 2:
        pygame.draw.rect(s, c2, (10, 8, 12, 18))
        pygame.draw.circle(s, c1, (16, 16), 4)
    elif stage == 3:
        pygame.draw.rect(s, c2, (6, 4, 20, 22))
        pygame.draw.circle(s, c1, (16, 12), 8)
        pygame.draw.circle(s, c1, (10, 18), 4)
        pygame.draw.circle(s, c1, (22, 18), 4)
    return s
