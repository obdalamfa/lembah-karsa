"""
sprites.py — Generator sprite pixel-art.
Semua sprite digenerate runtime via pygame.Surface.
Style: Harvest Moon Back to Nature inspired
- Outline gelap di tepi
- 3-tone shading (highlight + base + shadow)
- Mata ekspresif
- Animasi 4 frame untuk karakter
"""
import pygame
import math
import random
from .config import C, TILE, SPRITE


# ══════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════
def make_surface(w=SPRITE, h=SPRITE, fill=None):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    if fill: s.fill(fill)
    return s

def pp(s, x, y, c):
    """Set pixel dengan bounds check."""
    if 0 <= x < s.get_width() and 0 <= y < s.get_height():
        s.set_at((x, y), c)

def rect(s, x1, y1, x2, y2, c):
    for y in range(y1, y2+1):
        for x in range(x1, x2+1):
            pp(s, x, y, c)

def hline(s, y, x1, x2, c):
    for x in range(x1, x2+1): pp(s, x, y, c)

def vline(s, x, y1, y2, c):
    for y in range(y1, y2+1): pp(s, x, y, c)

def darker(c, amt=40):
    """Buat warna lebih gelap untuk shading."""
    return tuple(max(0, ch - amt) for ch in c[:3])

def lighter(c, amt=30):
    """Buat warna lebih terang untuk highlight."""
    return tuple(min(255, ch + amt) for ch in c[:3])

def outline_sprite(s, color=(20, 10, 20)):
    """Tambahkan outline 1 pixel di tepi non-transparan."""
    w, h = s.get_size()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(s, (0, 0))
    for y in range(h):
        for x in range(w):
            if s.get_at((x, y))[3] == 0:  # transparent
                # Cek tetangga
                for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        if s.get_at((nx, ny))[3] > 0:
                            out.set_at((x, y), color)
                            break
    return out


# ══════════════════════════════════════════════════════
#  TERRAIN TILES
# ══════════════════════════════════════════════════════
def make_grass_tile(seed=42):
    rng = random.Random(seed)
    s = make_surface(fill=C.g1)
    # Variasi rumput
    for _ in range(18):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([C.g0, C.g2, C.g3]))
    # Beberapa tuft kecil
    for _ in range(3):
        bx, by = rng.randint(2, 13), rng.randint(2, 13)
        pp(s, bx, by, C.g3)
        pp(s, bx, by-1, C.g2)
        pp(s, bx+1, by, C.g0)
    return s

def make_dirt_tile(seed=43):
    rng = random.Random(seed)
    s = make_surface(fill=C.d1)
    for _ in range(14):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([C.d0, C.d2, C.d3]))
    return s

def make_tilled_dry():
    s = make_surface(fill=C.d0)
    for y in range(16):
        for x in range(16):
            if y % 4 == 0: pp(s, x, y, C.d2)
            elif y % 4 == 1: pp(s, x, y, C.d1)
            elif y % 4 == 3: pp(s, x, y, C.d3)
    return s

def make_tilled_wet():
    s = make_surface(fill=C.d3)
    for y in range(16):
        for x in range(16):
            if y % 4 == 0: pp(s, x, y, C.w0)
            elif y % 4 == 1: pp(s, x, y, C.d3)
            elif y % 4 == 3: pp(s, x, y, C.d2)
    return s

def make_water_tile(frame=0):
    s = make_surface(fill=C.w0)
    for y in range(16):
        for x in range(16):
            wave = math.sin((x + y*2 + frame*0.5) * 0.7)
            if wave > 0.4: pp(s, x, y, C.w2)
            elif wave > 0: pp(s, x, y, C.w1)
            elif (x + y) % 3 == 0: pp(s, x, y, C.w1)
    # Sparkle
    if frame % 8 < 4:
        pp(s, 4 + (frame % 4), 6, (255, 255, 255))
    return s

def make_path_tile(seed=44):
    rng = random.Random(seed)
    s = make_surface(fill=C.p0)
    for _ in range(16):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([C.p1, C.p2]))
    for x in range(0, 16, 5):
        vline(s, x, 0, 15, C.p2)
    return s

def make_floor_tile():
    s = make_surface(fill=C.fl)
    for y in range(16):
        for x in range(16):
            if x % 8 == 0 or y % 8 == 0: pp(s, x, y, C.fl2)
            elif (x + y) % 16 == 7: pp(s, x, y, C.fl3)
    return s

def make_wall_tile():
    s = make_surface(fill=C.wl)
    for y in range(16):
        if y % 5 == 0: hline(s, y, 0, 15, C.wl2)
        elif y % 5 == 2:
            step = 4 if y < 8 else 0
            for x in range(step, 16, 8):
                pp(s, x, y, C.wl2)
    return s

def make_tree():
    """Pohon dengan outline & shading 3-tone (HM:BTN style)."""
    s = make_surface()
    # Trunk dengan shading
    rect(s, 6, 11, 9, 15, C.wo0)
    rect(s, 7, 11, 8, 15, C.wo1)
    pp(s, 6, 11, darker(C.wo0))
    pp(s, 9, 11, darker(C.wo0))
    # Crown - layered & shaded
    layers = [
        (5, 9, 10, 10, C.g0),
        (4, 7, 11, 9, C.g1),
        (3, 5, 12, 7, C.g0),
        (4, 3, 11, 5, C.g1),
        (5, 2, 10, 4, C.g0),
        (6, 1, 9, 3, C.g1),
    ]
    for x1, y1, x2, y2, c in layers:
        rect(s, x1, y1, x2, y2, c)
    # Highlight
    rect(s, 6, 1, 8, 3, C.g2)
    pp(s, 5, 4, C.g2)
    pp(s, 9, 6, C.g2)
    # Shadow side (kanan bawah)
    pp(s, 11, 8, darker(C.g0))
    pp(s, 12, 7, darker(C.g0))
    return s

def make_dead_tree():
    s = make_surface()
    rect(s, 6, 8, 9, 15, (60, 40, 30))
    rect(s, 7, 8, 8, 15, (40, 25, 20))
    branches = [(5,7),(4,6),(3,5),(10,7),(11,6),(12,5),(7,4),(8,3)]
    for x, y in branches:
        pp(s, x, y, (60, 40, 30))
    return s

def make_fence():
    s = make_surface()
    rect(s, 0, 5, 15, 8, C.wo0)
    hline(s, 5, 0, 15, C.wo2)
    hline(s, 8, 0, 15, C.wo1)
    vline(s, 7, 0, 15, C.wo1)
    vline(s, 8, 0, 15, C.wo1)
    return s

def make_gate():
    s = make_surface()
    vline(s, 0, 0, 15, C.wo1)
    vline(s, 15, 0, 15, C.wo1)
    hline(s, 3, 0, 15, C.wo0)
    hline(s, 12, 0, 15, C.wo0)
    for i in range(10):
        pp(s, 3+i, 5+i, C.wo2)
        pp(s, 12-i, 5+i, C.wo2)
    pp(s, 7, 8, C.gl)
    pp(s, 8, 8, C.gl)
    return s

def make_mailbox():
    s = make_surface()
    rect(s, 3, 3, 12, 9, C.gl)
    rect(s, 4, 4, 11, 8, C.ht2)
    rect(s, 4, 4, 11, 5, C.ht)
    rect(s, 5, 6, 10, 7, C.bk)
    vline(s, 7, 9, 15, C.p0)
    vline(s, 8, 9, 15, C.p1)
    return s

def make_door():
    s = make_surface()
    rect(s, 2, 0, 13, 15, C.wo0)
    hline(s, 0, 2, 13, C.wo2)
    vline(s, 2, 0, 15, C.wo1)
    vline(s, 13, 0, 15, C.wo1)
    rect(s, 4, 2, 11, 7, C.wo2)
    rect(s, 4, 9, 11, 14, C.wo2)
    rect(s, 11, 7, 12, 9, C.gl)
    return s


# ══════════════════════════════════════════════════════
#  CROP SPRITES (4 stages)
# ══════════════════════════════════════════════════════
def make_crop_sprite(stage, c1, c2):
    s = make_surface()
    if stage == 0:
        pp(s, 7, 13, C.cg2); pp(s, 7, 12, C.cg)
        pp(s, 6, 12, C.cg2); pp(s, 8, 12, C.cg2)
    elif stage == 1:
        vline(s, 7, 9, 15, C.cg); vline(s, 8, 9, 15, C.cg)
        hline(s, 10, 5, 10, C.cg)
        hline(s, 9, 6, 9, c2)
    elif stage == 2:
        vline(s, 7, 10, 15, C.g0); vline(s, 8, 10, 15, C.g0)
        rect(s, 3, 5, 12, 9, c1)
        rect(s, 4, 4, 11, 8, c2)
        rect(s, 5, 3, 10, 7, c1)
        for y in range(6, 10):
            pp(s, 2, y, c2); pp(s, 13, y, c2)
    else:
        # Siap panen — sparkle
        vline(s, 7, 11, 15, C.g0); vline(s, 8, 11, 15, C.g0)
        rect(s, 2, 3, 13, 10, c1)
        rect(s, 3, 2, 12, 9, c2)
        rect(s, 4, 1, 11, 8, c1)
        rect(s, 5, 2, 10, 7, c2)
        for sx, sy in [(3,1),(12,1),(2,5),(13,5)]:
            pp(s, sx, sy, C.wt)
        pp(s, 6, 3, C.wt); pp(s, 7, 2, C.wt)
    return s


# ══════════════════════════════════════════════════════
#  WILD PLANTS & SUPERNATURAL
# ══════════════════════════════════════════════════════
def make_mandrake():
    s = make_surface()
    rect(s, 5, 1, 10, 3, C.g1)
    rect(s, 6, 0, 9, 2, C.g2)
    pp(s, 5, 2, C.g0); pp(s, 10, 2, C.g0)
    vline(s, 7, 3, 5, C.g0); vline(s, 8, 3, 5, C.g0)
    rect(s, 5, 6, 10, 11, C.mandrake_skin)
    pp(s, 6, 7, C.bk); pp(s, 9, 7, C.bk)
    rect(s, 6, 9, 9, 9, C.bk)
    pp(s, 7, 9, (120, 40, 40))
    rect(s, 5, 12, 6, 15, C.mandrake_skin)
    rect(s, 9, 12, 10, 15, C.mandrake_skin)
    return s

def make_running_mushroom(frame=0):
    """Animated dengan bouncing kepala."""
    s = make_surface()
    bounce = 1 if frame else 0
    # Tudung
    rect(s, 3, 2-bounce, 12, 7-bounce, C.mushroom_red)
    rect(s, 4, 1-bounce, 11, 6-bounce, (255, 80, 80))
    rect(s, 5, 0 if bounce else 1, 10, 5-bounce, (255, 100, 100))
    # Bintik putih
    pp(s, 5, 3-bounce, C.wt)
    pp(s, 9, 4-bounce, C.wt)
    pp(s, 7, 2-bounce, C.wt)
    pp(s, 11, 5-bounce, C.wt)
    # Mata
    pp(s, 5, 5-bounce, C.bk); pp(s, 10, 5-bounce, C.bk)
    pp(s, 5, 4-bounce, C.wt); pp(s, 10, 4-bounce, C.wt)
    # Batang
    rect(s, 6, 8, 9, 12, C.mushroom_white)
    # Kaki
    leg_y_off = 0 if frame else 1
    rect(s, 5, 13-leg_y_off, 6, 15, (220, 200, 180))
    rect(s, 9, 13-(1-leg_y_off), 10, 15, (220, 200, 180))
    return s

def make_firefly(frame=0):
    s = make_surface()
    glow_radius = 4 + frame
    # Glow aura
    for r in range(glow_radius):
        alpha = 80 - r * 15
        if alpha > 0:
            for dx in range(-r, r+1):
                for dy in range(-r, r+1):
                    if dx*dx + dy*dy <= r*r:
                        x, y = 7 + dx, 8 + dy
                        if 0 <= x < 16 and 0 <= y < 16:
                            existing = s.get_at((x, y))
                            if existing[3] == 0:
                                s.set_at((x, y), (255, 255, 200, alpha))
    rect(s, 6, 7, 9, 11, C.firefly_glow)
    rect(s, 6, 12, 9, 13, (80, 40, 20))
    rect(s, 7, 5, 8, 7, (60, 30, 15))
    pp(s, 6, 5, (60, 30, 15)); pp(s, 9, 5, (60, 30, 15))
    rect(s, 4, 7, 5, 9, (180, 255, 200))
    rect(s, 10, 7, 11, 9, (180, 255, 200))
    pp(s, 7, 14, C.firefly_glow)
    pp(s, 8, 14, C.firefly_glow)
    return s

def make_wild_herb():
    s = make_surface()
    vline(s, 7, 8, 15, C.g0); vline(s, 8, 8, 15, C.g0)
    rect(s, 4, 6, 11, 9, C.g2)
    rect(s, 3, 7, 5, 8, C.g1)
    rect(s, 10, 7, 12, 8, C.g1)
    pp(s, 5, 5, (255, 200, 100))
    pp(s, 9, 5, (255, 200, 100))
    pp(s, 7, 4, (255, 150, 200))
    return s

def make_wild_berry():
    s = make_surface()
    vline(s, 7, 10, 15, C.g0)
    rect(s, 3, 7, 4, 9, (180, 30, 80))
    rect(s, 6, 5, 7, 7, (220, 40, 100))
    rect(s, 9, 7, 10, 9, (180, 30, 80))
    rect(s, 11, 5, 12, 7, (200, 40, 90))
    pp(s, 3, 7, (255, 150, 180))
    pp(s, 6, 5, (255, 150, 180))
    pp(s, 9, 7, (255, 150, 180))
    pp(s, 11, 5, (255, 150, 180))
    rect(s, 4, 4, 5, 5, C.g1)
    rect(s, 10, 4, 11, 5, C.g1)
    return s


# ══════════════════════════════════════════════════════
#  CAVE & PEN TILES
# ══════════════════════════════════════════════════════
def make_cave_wall():
    s = make_surface(fill=C.cave_stone)
    rng = random.Random(99)
    for _ in range(20):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([C.cave_stone_lt, C.cave_stone_dk]))
    # Crack lines
    for x in [3, 8, 12]:
        for y in range(0, 16, 2):
            pp(s, x, y, C.cave_stone_dk)
    return s

def make_cave_floor():
    s = make_surface(fill=C.cave_floor)
    rng = random.Random(101)
    for _ in range(14):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([C.cave_stone_lt, C.cave_stone_dk]))
    return s

def make_pen_post():
    """Tiang kandang."""
    s = make_surface()
    rect(s, 5, 0, 10, 15, C.wo0)
    vline(s, 5, 0, 15, C.wo1)
    vline(s, 10, 0, 15, C.wo1)
    hline(s, 0, 5, 10, C.wo2)
    # Top cap
    rect(s, 4, 1, 11, 2, C.wo2)
    return s

def make_straw():
    """Lantai jerami untuk kandang."""
    s = make_surface(fill=(180, 140, 80))
    rng = random.Random(105)
    for _ in range(16):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([(200, 160, 100), (140, 100, 50), (220, 180, 110)]))
    # Strands
    for _ in range(6):
        sx = rng.randint(2, 13)
        sy = rng.randint(2, 13)
        pp(s, sx, sy, (240, 200, 130))
        pp(s, sx+1, sy+1, (240, 200, 130))
    return s


# ══════════════════════════════════════════════════════
#  NAGA SANG HYANG — 48x32 sprite besar (3x2 tile)
# ══════════════════════════════════════════════════════
def make_naga(direction='down', frame=0):
    """
    Naga oriental Indonesia. 48 x 32 pixel native.
    Bentuk: tubuh berliuk, kepala berjenggot, mata hijau magis.
    """
    s = make_surface(48, 32)
    bob = 1 if frame else 0  # napas/melayang

    # ═══ EKOR (kanan) berliuk ═══
    # Tail tip
    rect(s, 42, 18+bob, 47, 21+bob, C.naga_body)
    rect(s, 43, 19+bob, 46, 20+bob, C.naga_body_lt)
    rect(s, 44, 17+bob, 45, 18+bob, C.naga_body)
    pp(s, 47, 19+bob, C.naga_body_dk)
    # Tail middle (curving)
    for x in range(35, 42):
        y_off = int(math.sin((x-35)*0.9) * 2) + bob
        rect(s, x, 19 + y_off, x, 22 + y_off, C.naga_body)
        pp(s, x, 19 + y_off, C.naga_body_lt)
        pp(s, x, 22 + y_off, C.naga_body_dk)

    # ═══ TUBUH UTAMA (tengah) ═══
    rect(s, 18, 14+bob, 35, 24+bob, C.naga_body)
    # Belly emas
    rect(s, 19, 21+bob, 34, 24+bob, C.naga_belly)
    pp(s, 19, 21+bob, C.naga_body_dk)
    pp(s, 34, 21+bob, C.naga_body_dk)
    # Highlight atas tubuh
    hline(s, 14+bob, 19, 34, C.naga_body_lt)
    # Scale pattern
    for sx in range(20, 34, 3):
        pp(s, sx, 16+bob, C.naga_scale)
        pp(s, sx+1, 18+bob, C.naga_scale)
        pp(s, sx, 19+bob, C.naga_belly)
    # Outline tubuh
    hline(s, 13+bob, 18, 35, C.naga_body_dk)
    hline(s, 25+bob, 18, 35, C.naga_body_dk)

    # ═══ KAKI BELAKANG (dengan cakar) ═══
    # Front leg (kiri)
    rect(s, 22, 24+bob, 25, 28+bob, C.naga_body)
    rect(s, 23, 25+bob, 24, 27+bob, C.naga_body_lt)
    # Cakar kiri
    pp(s, 22, 28+bob, (255, 240, 180))
    pp(s, 23, 28+bob, (255, 240, 180))
    pp(s, 25, 28+bob, (255, 240, 180))
    # Back leg (kanan)
    rect(s, 30, 24+bob, 33, 28+bob, C.naga_body)
    rect(s, 31, 25+bob, 32, 27+bob, C.naga_body_lt)
    # Cakar kanan
    pp(s, 30, 28+bob, (255, 240, 180))
    pp(s, 32, 28+bob, (255, 240, 180))
    pp(s, 33, 28+bob, (255, 240, 180))

    # ═══ LEHER (curving up to head) ═══
    rect(s, 12, 12+bob, 18, 18+bob, C.naga_body)
    rect(s, 13, 13+bob, 17, 17+bob, C.naga_body_lt)
    pp(s, 12, 18+bob, C.naga_belly)
    pp(s, 13, 18+bob, C.naga_belly)

    # ═══ KEPALA (kiri) ═══
    head_y = 6 + bob
    rect(s, 4, head_y, 16, head_y+10, C.naga_body)
    rect(s, 5, head_y+1, 15, head_y+9, C.naga_body)
    # Atas kepala highlight
    hline(s, head_y, 6, 14, C.naga_body_lt)
    hline(s, head_y+1, 5, 15, C.naga_body_lt)
    # Mulut bawah
    hline(s, head_y+9, 5, 13, C.naga_belly)
    rect(s, 4, head_y+8, 7, head_y+10, C.naga_body_dk)

    # ═══ TANDUK (atas kepala) ═══
    rect(s, 7, head_y-3, 8, head_y, C.naga_horn)
    rect(s, 11, head_y-3, 12, head_y, C.naga_horn)
    pp(s, 7, head_y-4, C.naga_horn)
    pp(s, 12, head_y-4, C.naga_horn)
    # Branch tanduk
    pp(s, 6, head_y-2, C.naga_horn)
    pp(s, 13, head_y-2, C.naga_horn)

    # ═══ MATA (hijau magis, glowing) ═══
    rect(s, 8, head_y+3, 9, head_y+4, C.wt)
    rect(s, 11, head_y+3, 12, head_y+4, C.wt)
    pp(s, 8, head_y+3, C.naga_eye)
    pp(s, 11, head_y+3, C.naga_eye)
    # Glow
    pp(s, 8, head_y+2, (140, 255, 140))
    pp(s, 11, head_y+2, (140, 255, 140))

    # ═══ JANGGUT EMAS (whiskers, dragon style) ═══
    rect(s, 0, head_y+5, 4, head_y+5, C.naga_whiskers)
    rect(s, 0, head_y+7, 3, head_y+7, C.naga_whiskers)
    pp(s, 4, head_y+6, C.naga_whiskers)
    pp(s, 1, head_y+8, C.naga_whiskers)

    # ═══ NAFAS API (frame ke-1 saja, di mulut) ═══
    if frame:
        pp(s, 3, head_y+8, C.fire2)
        pp(s, 2, head_y+9, C.fire1)
        pp(s, 1, head_y+9, C.fire3)
        pp(s, 0, head_y+10, C.fire1)

    # ═══ AURA EMAS (sparkles random) ═══
    sparkle_offsets = [(20, 5), (28, 10), (38, 16), (15, 28), (32, 4)]
    for sx, sy in sparkle_offsets[:2 + frame]:
        pp(s, sx, sy, C.gl)
        pp(s, sx+1, sy, (255, 255, 200))

    return s


def make_naga_sprite():
    """Return naga sprite. v7: coba load dari assets/chars/naga/ dulu (sprite kustom),
    kalau tidak ada baru pakai procedural make_naga."""
    import os
    out = {}
    base_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                              'assets', 'chars', 'naga')
    custom_exists = os.path.exists(os.path.join(base_path, 'down_0.png'))
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        if custom_exists:
            # Load 3 frame PNG kustom
            for f in range(3):
                fp = os.path.join(base_path, f'{direction}_{f}.png')
                if os.path.exists(fp):
                    img = pygame.image.load(fp).convert_alpha()
                    frames.append(pygame.transform.scale(img, (96, 64)))
                else:
                    # fallback ke frame 0
                    if frames:
                        frames.append(frames[0])
                    else:
                        s = pygame.Surface((96, 64), pygame.SRCALPHA)
                        frames.append(s)
        else:
            # Procedural
            for f in range(2):
                base = make_naga(direction, f)
                scaled = pygame.transform.scale(base, (96, 64))
                if direction == 'right':
                    scaled = pygame.transform.flip(scaled, True, False)
                frames.append(scaled)
        out[direction] = frames
    return out


# ─── DUNGEON ORE TILES (v7) ──────────────────────────
def make_ore_tile(ore_color, accent_color):
    """Tile cave wall dengan urat warna ore."""
    s = make_surface(fill=C.cave_stone)
    for _ in range(8):
        x, y = random.randint(2, 13), random.randint(2, 13)
        pp(s, x, y, ore_color)
        if random.random() < 0.5:
            pp(s, x+1, y, accent_color)
    return s


def make_ore_tembaga():
    return make_ore_tile((200, 130, 70), (240, 170, 100))


def make_ore_besi():
    return make_ore_tile((180, 180, 200), (220, 220, 240))


def make_ore_emas():
    return make_ore_tile((250, 220, 100), (255, 240, 150))


def make_ore_kristal():
    return make_ore_tile((200, 150, 250), (240, 200, 255))


def make_ore_mithril():
    return make_ore_tile((140, 220, 240), (190, 250, 255))


def make_crystal_big():
    """Kristal besar di lv 12+."""
    s = make_surface(fill=C.cave_floor)
    # Kristal piramidal ungu
    for y in range(2, 14):
        w = max(1, (14 - y) // 2)
        for x in range(8 - w, 8 + w):
            if 0 <= x < 16:
                c = (180, 130, 230) if (y % 2) else (220, 170, 255)
                pp(s, x, y, c)
    return s


def make_stairs_down():
    s = make_surface(fill=C.cave_floor)
    for y in range(4, 14):
        for x in range(2, 14):
            if (y - 4) >= (x - 2) // 2:
                c = (40, 30, 50) if y % 2 == 0 else (60, 50, 70)
                pp(s, x, y, c)
    return s


def make_stairs_up():
    s = make_surface(fill=C.cave_floor)
    for y in range(2, 14):
        for x in range(2, 14):
            if (14 - y) >= (x - 2) // 2:
                c = (80, 70, 90) if y % 2 == 0 else (100, 90, 110)
                pp(s, x, y, c)
    return s


def make_mined():
    """Tile habis tambang — cave_floor lebih gelap."""
    s = make_surface(fill=C.cave_stone_dk)
    for _ in range(5):
        x, y = random.randint(2, 13), random.randint(2, 13)
        pp(s, x, y, C.cave_floor)
    return s


# ─── LAKE TILES (v7 port from v6) ─────────────────────
def make_dock():
    """Dermaga kayu."""
    s = make_surface(fill=(140, 100, 60))
    for y in [2, 7, 12]:
        hline(s, y, 0, 15, (90, 60, 30))
    pp(s, 4, 4, (90, 60, 30))
    pp(s, 11, 9, (90, 60, 30))
    return s


def make_boat():
    """Perahu kecil view atas."""
    s = make_surface()
    rect(s, 0, 0, 15, 15, (60, 140, 210))  # water bg
    rect(s, 2, 4, 13, 11, (90, 60, 30))    # outline
    rect(s, 3, 5, 12, 10, (140, 100, 60))  # hull
    rect(s, 5, 7, 10, 8, (90, 60, 30))     # bench
    return s


def make_water_lily():
    """Eceng gondok / teratai."""
    s = make_surface()
    rect(s, 0, 0, 15, 15, (60, 140, 210))  # water bg
    # Daun lebar
    for y in range(8, 13):
        for x in range(2, 8):
            d = (x - 5)**2 + (y - 10)**2
            if d <= 9: pp(s, x, y, (50, 130, 70))
    # Bunga ungu
    rect(s, 6, 8, 8, 10, (200, 130, 230))
    pp(s, 7, 9, C.cy)
    return s



# ══════════════════════════════════════════════════════
#  CHARACTER SPRITE — HM:BTN STYLE
#  16x16 dengan outline, expressive eyes, blush
# ══════════════════════════════════════════════════════
def make_char(direction, frame, hair=C.h0, shirt=C.s0, pants=C.pn, hat=True, blink=False):
    """
    Karakter dengan style HM:BTN:
    - Kepala besar (chibi) dengan rambut detail
    - Mata ekspresif (blink saat frame tertentu)
    - Outline gelap
    - 3-tone shading
    """
    s = make_surface()

    # ═══ TOPI (kalau ada) ═══
    if hat:
        rect(s, 4, 1, 11, 1, darker(C.ht, 30))  # outline atas
        rect(s, 5, 0, 10, 0, C.ht)               # tip
        rect(s, 4, 1, 11, 2, C.ht)
        rect(s, 3, 2, 12, 2, C.ht2)              # brim
        rect(s, 4, 3, 11, 3, darker(C.ht2, 20))  # shadow brim
        # Pita kuning tua di topi
        hline(s, 2, 5, 10, darker(C.ht, 50))

    # ═══ KEPALA ═══
    head_top = 3 if hat else 2
    rect(s, 4, head_top, 11, 7, C.sk)
    # Highlight pipi (HM:BTN khas: blush!)
    pp(s, 4, 6, lighter(C.sk, 10))
    pp(s, 11, 6, lighter(C.sk, 10))
    # Blush kanan-kiri (rosy cheeks)
    pp(s, 5, 6, (255, 180, 180))
    pp(s, 10, 6, (255, 180, 180))

    # ═══ RAMBUT ═══
    if direction == "up":
        # Belakang kepala — full hair
        rect(s, 4, head_top, 11, head_top+2, hair)
        # Hair tuft
        pp(s, 5, head_top, lighter(hair, 20))
        pp(s, 9, head_top, lighter(hair, 20))
    else:
        # Front bangs
        for xi in [4, 5]:
            for yi in [head_top, head_top+1]:
                pp(s, xi, yi, hair)
        for xi in [10, 11]:
            for yi in [head_top, head_top+1]:
                pp(s, xi, yi, hair)
        # Rambut tengah (poni)
        pp(s, 6, head_top, hair)
        pp(s, 9, head_top, hair)
        pp(s, 7, head_top, lighter(hair, 15))  # highlight

    # ═══ MATA — expressive ═══
    if direction != "up":
        if blink:
            # Mata tertutup — garis horizontal
            hline(s, 5, 5, 6, C.bk)
            hline(s, 5, 9, 10, C.bk)
        else:
            # Mata terbuka — putih + pupil
            pp(s, 5, 5, C.wt); pp(s, 6, 5, C.wt)
            pp(s, 9, 5, C.wt); pp(s, 10, 5, C.wt)
            # Pupil — lebih kecil + colorful (biru)
            if direction == "left":
                pp(s, 5, 5, (60, 80, 160))
                pp(s, 9, 5, (60, 80, 160))
            elif direction == "right":
                pp(s, 6, 5, (60, 80, 160))
                pp(s, 10, 5, (60, 80, 160))
            else:
                pp(s, 5, 5, (60, 80, 160))
                pp(s, 9, 5, (60, 80, 160))
            # Sparkle di mata
            pp(s, 6, 5, C.wt) if direction != "left" else None

        # Mulut kecil
        if not blink:
            pp(s, 7, 7, (200, 100, 100))
            pp(s, 8, 7, (200, 100, 100))

    # ═══ LEHER & BAHU ═══
    pp(s, 6, 8, C.sk2)
    pp(s, 9, 8, C.sk2)

    # ═══ BADAN ═══
    rect(s, 4, 8, 11, 12, shirt)
    # Highlight di tengah baju (light from above)
    rect(s, 5, 8, 10, 8, lighter(shirt, 20))
    # Shadow bawah baju
    rect(s, 4, 12, 11, 12, darker(shirt, 25))
    # Kerah
    pp(s, 7, 8, C.wt)
    pp(s, 8, 8, C.wt)

    # ═══ TANGAN ═══
    if direction in ("left", "right"):
        off = 1 if frame else 0
        pp(s, 3, 8, C.sk)
        pp(s, 3, 9 + off, C.sk)
        pp(s, 12, 8 + (1 - off), C.sk)
        pp(s, 12, 9, C.sk)
    else:
        pp(s, 3, 8, C.sk); pp(s, 3, 9, C.sk)
        pp(s, 12, 8, C.sk); pp(s, 12, 9, C.sk)

    # ═══ CELANA ═══
    rect(s, 4, 12, 11, 15, pants)
    vline(s, 8, 12, 15, C.pn2)  # seam
    # Highlight di paha
    pp(s, 5, 13, lighter(pants, 15))
    pp(s, 10, 13, lighter(pants, 15))

    # ═══ SEPATU ═══
    rect(s, 4, 15, 5, 15, C.h2)
    rect(s, 10, 15, 11, 15, C.h2)

    # ═══ ANIMASI WALK ═══
    if frame and direction in ("left", "right"):
        pp(s, 4, 14, pants)
        pp(s, 11, 15, C.h2)

    # Tambah outline di tepi sprite
    return outline_sprite(s, color=(20, 10, 20))


# ══════════════════════════════════════════════════════
#  SUPERNATURAL CHARACTERS
# ══════════════════════════════════════════════════════
def make_jin(direction, frame):
    s = make_surface()
    # Aura ungu
    for r in range(2):
        rect(s, 3-r, 3-r, 12+r, 12+r, (180, 120, 255, 40))
    rect(s, 4, 2, 11, 12, C.jin_aura)
    rect(s, 5, 1, 10, 11, C.jin_skin)
    rect(s, 4, 3, 11, 7, C.jin_skin)
    pp(s, 5, 5, C.bk); pp(s, 9, 5, C.bk)
    pp(s, 5, 4, C.gl); pp(s, 9, 4, C.gl)
    pp(s, 5, 0, C.gl); pp(s, 8, 0, C.gl)
    pp(s, 7, 0, C.gl); pp(s, 10, 0, C.gl)
    if frame:
        rect(s, 5, 13, 10, 15, (180, 120, 255, 150))
    else:
        rect(s, 4, 14, 11, 15, (180, 120, 255, 150))
        pp(s, 6, 13, (180, 120, 255, 180))
        pp(s, 9, 13, (180, 120, 255, 180))
    pp(s, 3, 7, C.jin_skin); pp(s, 3, 8, C.jin_skin)
    pp(s, 12, 7, C.jin_skin); pp(s, 12, 8, C.jin_skin)
    return s

def make_demit(direction, frame):
    s = make_surface()
    rect(s, 4, 2, 11, 15, C.demit_dark)
    rect(s, 5, 1, 10, 14, C.demit_dark)
    rect(s, 3, 5, 12, 12, C.demit_dark)
    pp(s, 5, 5, C.demit_glow); pp(s, 9, 5, C.demit_glow)
    pp(s, 5, 4, (180, 80, 255)); pp(s, 9, 4, (180, 80, 255))
    if frame:
        pp(s, 2, 7, C.demit_glow); pp(s, 13, 9, C.demit_glow)
    else:
        pp(s, 2, 9, C.demit_glow); pp(s, 13, 7, C.demit_glow)
    pp(s, 7, 7, C.wt); pp(s, 8, 7, C.wt)
    return s

def make_tuyul(direction, frame):
    s = make_surface()
    rect(s, 4, 2, 11, 8, C.tuyul_skin)
    rect(s, 3, 4, 12, 7, C.tuyul_skin)
    rect(s, 5, 5, 6, 6, C.wt)
    rect(s, 9, 5, 10, 6, C.wt)
    pp(s, 5, 6, C.bk); pp(s, 10, 6, C.bk)
    pp(s, 7, 7, C.bk); pp(s, 8, 7, C.bk)
    rect(s, 5, 9, 10, 12, C.tuyul_red)
    pp(s, 4, 10, C.tuyul_skin); pp(s, 11, 10, C.tuyul_skin)
    rect(s, 5, 13, 6, 15, C.tuyul_skin)
    rect(s, 9, 13, 10, 15, C.tuyul_skin)
    if frame:
        pp(s, 5, 15, C.tuyul_skin); pp(s, 10, 14, C.tuyul_skin)
    return s


# ══════════════════════════════════════════════════════
#  ANIMALS
# ══════════════════════════════════════════════════════
def make_sapi(direction, frame):
    s = make_surface()
    rect(s, 2, 7, 13, 12, C.sapi_white)
    rect(s, 3, 8, 5, 10, C.sapi_brown)
    rect(s, 9, 9, 12, 11, C.sapi_brown)
    rect(s, 6, 7, 7, 8, C.sapi_brown)
    rect(s, 1, 5, 5, 9, C.sapi_white)
    rect(s, 2, 4, 4, 8, C.sapi_white)
    pp(s, 1, 4, C.bk); pp(s, 4, 4, C.bk)
    pp(s, 1, 3, C.bk); pp(s, 4, 3, C.bk)
    pp(s, 3, 6, C.bk)
    pp(s, 1, 7, (220, 150, 150)); pp(s, 2, 7, (220, 150, 150))
    if frame:
        rect(s, 3, 13, 4, 15, C.sapi_brown)
        rect(s, 8, 13, 9, 15, C.sapi_brown)
        rect(s, 5, 13, 6, 15, C.sapi_brown)
        rect(s, 11, 13, 12, 15, C.sapi_brown)
    else:
        rect(s, 3, 13, 4, 15, C.sapi_brown)
        rect(s, 11, 13, 12, 15, C.sapi_brown)
        rect(s, 6, 13, 7, 15, C.sapi_brown)
        rect(s, 9, 13, 10, 15, C.sapi_brown)
    vline(s, 14, 8, 12, C.sapi_white)
    pp(s, 14, 12, C.bk)
    return s

def make_ayam(direction, frame):
    s = make_surface()
    rect(s, 5, 8, 11, 13, C.ayam_white)
    rect(s, 6, 7, 10, 12, C.ayam_white)
    rect(s, 3, 7, 5, 10, C.ayam_white)
    pp(s, 2, 7, C.ayam_white); pp(s, 2, 9, C.ayam_white)
    rect(s, 9, 5, 12, 8, C.ayam_white)
    pp(s, 10, 4, C.ayam_red); pp(s, 11, 4, C.ayam_red); pp(s, 9, 4, C.ayam_red)
    pp(s, 12, 7, (220, 180, 40)); pp(s, 13, 7, (220, 180, 40))
    pp(s, 11, 6, C.bk)
    pp(s, 11, 8, C.ayam_red)
    if frame:
        vline(s, 7, 14, 15, (220, 180, 40))
        vline(s, 9, 14, 15, (220, 180, 40))
    else:
        vline(s, 6, 14, 15, (220, 180, 40))
        vline(s, 10, 14, 15, (220, 180, 40))
    return s

def make_kambing(direction, frame):
    s = make_surface()
    rect(s, 3, 7, 12, 12, C.kambing_grey)
    rect(s, 2, 8, 13, 11, C.kambing_grey)
    rect(s, 1, 5, 4, 9, C.kambing_grey)
    pp(s, 1, 4, C.bk); pp(s, 3, 4, C.bk)
    pp(s, 0, 3, C.bk); pp(s, 4, 3, C.bk)
    pp(s, 2, 9, C.wt); pp(s, 2, 10, C.wt)
    pp(s, 3, 6, C.bk)
    if frame:
        vline(s, 4, 13, 15, C.bk)
        vline(s, 11, 13, 15, C.bk)
        vline(s, 7, 13, 15, C.bk)
        vline(s, 9, 13, 15, C.bk)
    else:
        vline(s, 3, 13, 15, C.bk)
        vline(s, 12, 13, 15, C.bk)
        vline(s, 6, 13, 15, C.bk)
        vline(s, 10, 13, 15, C.bk)
    pp(s, 13, 8, C.kambing_grey); pp(s, 13, 7, C.kambing_grey)
    return s


# ══════════════════════════════════════════════════════
#  FURNITURE
# ══════════════════════════════════════════════════════
def make_bed():
    s = make_surface()
    rect(s, 1, 4, 14, 13, C.fn)
    vline(s, 1, 4, 13, C.fn2); vline(s, 14, 4, 13, C.fn2)
    rect(s, 2, 5, 13, 12, C.wt)
    rect(s, 3, 5, 13, 12, C.s0)
    rect(s, 3, 5, 7, 7, C.wl)
    return s

def make_stove():
    s = make_surface()
    rect(s, 1, 1, 14, 14, (64, 64, 64))
    rect(s, 2, 2, 13, 13, (80, 80, 80))
    for bx, by in [(3,3),(9,3),(3,9),(9,9)]:
        rect(s, bx, by, bx+3, by+3, (40, 40, 40))
        rect(s, bx+1, by+1, bx+2, by+2, C.fire1)
    rect(s, 2, 12, 13, 14, (96, 96, 96))
    return s

def make_table():
    s = make_surface()
    rect(s, 0, 3, 15, 5, C.fn)
    hline(s, 3, 0, 15, C.fn2); hline(s, 4, 0, 15, C.fn3)
    vline(s, 2, 5, 15, C.fn); vline(s, 13, 5, 15, C.fn)
    rect(s, 6, 0, 9, 3, C.cy)
    return s

def make_bookshelf():
    s = make_surface(fill=C.fn)
    for y in [0, 5, 10, 15]: hline(s, y, 0, 15, C.fn2)
    book_colors = [C.cr, C.s0, C.cg, C.gl, C.cp, C.co, (0, 160, 180), C.nc_sari]
    for row_y in [1, 6, 11]:
        bx = 2
        for color in book_colors[:4]:
            rect(s, bx, row_y, bx+1, row_y+3, color)
            bx += 3
    return s

def make_mirror():
    s = make_surface(fill=C.fn)
    rect(s, 2, 1, 13, 14, C.fn2)
    rect(s, 3, 2, 12, 13, (200, 232, 248))
    rect(s, 4, 3, 6, 12, (220, 245, 255))
    return s

def make_fireplace(frame=0):
    """Animated fire."""
    s = make_surface(fill=(64, 64, 64))
    rect(s, 2, 4, 13, 14, (32, 32, 32))
    rect(s, 3, 5, 12, 14, (24, 24, 24))
    fy_off = 0 if frame else 1
    rect(s, 4, 7+fy_off, 11, 14, C.fire1)
    rect(s, 5, 6+fy_off, 10, 12, C.fire2)
    rect(s, 6, 5+fy_off, 9, 10, C.fire3)
    rect(s, 7, 5+fy_off, 8, 8, C.wt)
    rect(s, 0, 0, 15, 2, C.p1)
    return s

def make_clock():
    s = make_surface(fill=C.fn)
    rect(s, 3, 1, 12, 14, C.fn2)
    vline(s, 3, 1, 14, C.fn3); vline(s, 12, 1, 14, C.fn3)
    rect(s, 5, 5, 10, 11, C.fl3)
    cx, cy, cr = 7, 8, 4
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        ex = cx + int(cr * math.sin(rad))
        ey = cy - int(cr * math.cos(rad))
        pp(s, ex, ey, C.wl2)
    pp(s, cx, cy, (40, 40, 40))
    return s

def make_plant_pot():
    s = make_surface()
    rect(s, 5, 11, 10, 15, C.d0)
    rect(s, 4, 13, 11, 15, C.d1)
    vline(s, 7, 4, 12, C.g0); vline(s, 8, 4, 12, C.g0)
    rect(s, 3, 5, 6, 9, C.g1)
    rect(s, 9, 7, 12, 10, C.g1)
    rect(s, 5, 2, 10, 6, C.g2)
    return s

def make_chest():
    s = make_surface()
    rect(s, 1, 5, 14, 14, C.fn)
    rect(s, 1, 3, 14, 6, C.fn2)
    hline(s, 5, 1, 14, C.wo2)
    rect(s, 6, 8, 9, 11, C.gl)
    rect(s, 7, 9, 8, 10, C.ht)
    return s

def make_counter():
    s = make_surface(fill=C.fn)
    rect(s, 0, 4, 15, 14, C.fn)
    hline(s, 4, 0, 15, C.fn2); hline(s, 5, 0, 15, C.fn3)
    for ox in [2, 6, 10]: rect(s, ox, 1, ox+2, 3, C.cg)
    return s

def make_shelf_store():
    s = make_surface(fill=C.fn)
    for y in [0, 5, 10, 15]: hline(s, y, 0, 15, C.fn2)
    for bx in [1, 4, 7, 10, 13]:
        pp(s, bx, 2, C.cr); pp(s, bx, 3, C.cr)
        pp(s, bx, 7, C.cy); pp(s, bx, 8, C.cy)
        pp(s, bx, 12, C.s0); pp(s, bx, 13, C.s0)
    return s

def make_grave():
    s = make_surface()
    rect(s, 4, 4, 11, 12, (140, 130, 120))
    rect(s, 5, 3, 10, 11, (160, 150, 140))
    rect(s, 5, 2, 10, 4, (140, 130, 120))
    vline(s, 7, 5, 9, (80, 70, 60))
    vline(s, 8, 5, 9, (80, 70, 60))
    hline(s, 7, 6, 9, (80, 70, 60))
    rect(s, 3, 13, 12, 15, C.g0)
    return s

def make_lantern(frame=0):
    s = make_surface()
    vline(s, 7, 7, 15, (60, 40, 20))
    vline(s, 8, 7, 15, (60, 40, 20))
    rect(s, 4, 2, 11, 8, C.gl)
    light_y = 1 if frame else 2
    rect(s, 5, light_y, 10, 7, C.fire2)
    rect(s, 6, light_y+1, 9, 6, C.fire3)
    rect(s, 7, light_y+1, 8, 5, C.wt)
    rect(s, 5, 1, 10, 2, (80, 60, 30))
    pp(s, 7, 0, (80, 60, 30)); pp(s, 8, 0, (80, 60, 30))
    return s


# ══════════════════════════════════════════════════════
#  SPRITE REGISTRY (lazy init)
# ══════════════════════════════════════════════════════
SPRITES = {}
ANIMATED = {}

def init_sprites():
    """Generate semua sprite & cache di SPRITES & ANIMATED."""
    global SPRITES, ANIMATED

    def sc(s):
        return pygame.transform.scale(s, (TILE, TILE))

    SPRITES['grass'] = sc(make_grass_tile())
    SPRITES['dirt'] = sc(make_dirt_tile())
    SPRITES['tilled_dry'] = sc(make_tilled_dry())
    SPRITES['tilled_wet'] = sc(make_tilled_wet())
    SPRITES['path'] = sc(make_path_tile())
    SPRITES['floor'] = sc(make_floor_tile())
    SPRITES['wall'] = sc(make_wall_tile())
    SPRITES['tree'] = sc(make_tree())
    SPRITES['dead_tree'] = sc(make_dead_tree())
    SPRITES['fence'] = sc(make_fence())
    SPRITES['gate'] = sc(make_gate())
    SPRITES['mailbox'] = sc(make_mailbox())
    SPRITES['door'] = sc(make_door())
    SPRITES['chest'] = sc(make_chest())
    SPRITES['bed'] = sc(make_bed())
    SPRITES['stove'] = sc(make_stove())
    SPRITES['table'] = sc(make_table())
    SPRITES['bookshelf'] = sc(make_bookshelf())
    SPRITES['mirror'] = sc(make_mirror())
    SPRITES['clock'] = sc(make_clock())
    SPRITES['plant_pot'] = sc(make_plant_pot())
    SPRITES['counter'] = sc(make_counter())
    SPRITES['shelf_store'] = sc(make_shelf_store())
    SPRITES['grave'] = sc(make_grave())
    SPRITES['cave_wall'] = sc(make_cave_wall())
    SPRITES['cave_floor'] = sc(make_cave_floor())
    SPRITES['pen_post'] = sc(make_pen_post())
    SPRITES['straw'] = sc(make_straw())
    # Dungeon ore tiles (v7)
    SPRITES['ore_tembaga'] = sc(make_ore_tembaga())
    SPRITES['ore_besi'] = sc(make_ore_besi())
    SPRITES['ore_emas'] = sc(make_ore_emas())
    SPRITES['ore_kristal'] = sc(make_ore_kristal())
    SPRITES['ore_mithril'] = sc(make_ore_mithril())
    SPRITES['crystal'] = sc(make_crystal_big())
    SPRITES['stairs_down'] = sc(make_stairs_down())
    SPRITES['stairs_up'] = sc(make_stairs_up())
    SPRITES['mined'] = sc(make_mined())
    # Lake tiles (v7 port from v6)
    SPRITES['dock'] = sc(make_dock())
    SPRITES['boat'] = sc(make_boat())
    SPRITES['water_lily'] = sc(make_water_lily())

    # Wild plants
    SPRITES['mandrake'] = sc(make_mandrake())
    SPRITES['wild_herb'] = sc(make_wild_herb())
    SPRITES['wild_berry'] = sc(make_wild_berry())

    # Animated
    ANIMATED['water'] = [sc(make_water_tile(i*4)) for i in range(4)]
    ANIMATED['fireplace'] = [sc(make_fireplace(i)) for i in range(2)]
    ANIMATED['lantern'] = [sc(make_lantern(i)) for i in range(2)]
    ANIMATED['running_mushroom'] = [sc(make_running_mushroom(i)) for i in range(2)]
    ANIMATED['firefly'] = [sc(make_firefly(i)) for i in range(3)]

    # Player & humans (4 dir × 4 frames: walk0, walk1, idle, blink)
    ANIMATED['player'] = build_char_anim()
    ANIMATED['npc_arya'] = build_char_anim(C.ng, C.g1, C.pn)
    ANIMATED['npc_sari'] = build_char_anim(C.cr, C.nc_sari, C.pn)
    ANIMATED['npc_raka'] = build_char_anim(C.ng, C.nc_raka, C.s0)
    ANIMATED['npc_maya'] = build_char_anim(C.gl, C.nc_maya, C.pn)
    ANIMATED['npc_budi'] = build_char_anim(C.ng, C.nc_budi, C.p2)
    # Human NPC tambahan dari v6 (variasi warna hair/shirt/pants)
    ANIMATED['npc_joko'] = build_char_anim(C.h0, (80, 60, 130), C.pn)
    ANIMATED['npc_cici'] = build_char_anim(C.gl, (240, 180, 200), C.pn)
    ANIMATED['npc_bowo'] = build_char_anim(C.ng, (180, 80, 60), C.p2)
    ANIMATED['npc_ningsih'] = build_char_anim(C.cr, (140, 200, 140), C.pn)
    ANIMATED['npc_pak_guru'] = build_char_anim((220, 220, 220), (60, 80, 130), (40, 40, 60))
    ANIMATED['npc_mbok_jum'] = build_char_anim((180, 180, 180), (200, 100, 80), (80, 50, 30))
    ANIMATED['npc_jaka_ronda'] = build_char_anim(C.ng, (80, 80, 80), C.p2)

    # Supernatural & animals
    ANIMATED['npc_jin'] = build_special_anim(make_jin)
    ANIMATED['npc_demit'] = build_special_anim(make_demit)
    ANIMATED['npc_tuyul'] = build_special_anim(make_tuyul)
    # Alias untuk supernatural type lain (pakai sprite jin/demit sebagai fallback)
    ANIMATED['npc_kuntilanak'] = build_special_anim(make_demit)  # putih melayang
    ANIMATED['npc_pocong'] = build_special_anim(make_demit)
    ANIMATED['npc_genderuwo'] = build_special_anim(make_demit)
    ANIMATED['npc_wewe'] = build_special_anim(make_demit)
    ANIMATED['npc_banaspati'] = build_special_anim(make_jin)      # api → jin
    ANIMATED['npc_leak'] = build_special_anim(make_demit)
    # Hewan
    ANIMATED['npc_sapi'] = build_special_anim(make_sapi)
    ANIMATED['npc_ayam'] = build_special_anim(make_ayam)
    ANIMATED['npc_kambing'] = build_special_anim(make_kambing)
    # Hewan tambahan (alias)
    ANIMATED['npc_bebek'] = build_special_anim(make_ayam)
    ANIMATED['npc_domba'] = build_special_anim(make_kambing)
    ANIMATED['npc_kuda'] = build_special_anim(make_sapi)
    ANIMATED['npc_kucing'] = build_special_anim(make_ayam)
    ANIMATED['npc_rubah'] = build_special_anim(make_ayam)
    ANIMATED['npc_kelinci'] = build_special_anim(make_ayam)

    # Naga (sprite besar 96x64)
    ANIMATED['npc_naga'] = make_naga_sprite()

    # Crops
    SPRITES['crops'] = {}
    CROP_COLORS = {
        'lobak': (C.cg, C.cg2),
        'wortel': (C.co, C.d1),
        'stroberi': (C.cr, C.cg),
        'jagung': (C.cy, C.cg),
        'tomat': (C.cr, (255, 80, 80)),
        'labu': (C.co, C.fn),
        'bayam': (C.g2, C.g0),
        'jamur': ((212, 164, 116), C.fn2),
    }
    for crop_id, (c1, c2) in CROP_COLORS.items():
        SPRITES['crops'][crop_id] = [
            sc(make_crop_sprite(stage, c1, c2)) for stage in range(4)
        ]

def build_char_anim(hair=C.h0, shirt=C.s0, pants=C.pn):
    """4 arah × 3 frame: walk0, walk1, blink."""
    out = {}
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        # walk 0 & 1
        for f in range(2):
            d = direction
            flip = False
            if direction == 'left':
                d = 'right'
                flip = True
            surf = make_char(d, f, hair, shirt, pants)
            scaled = pygame.transform.scale(surf, (TILE, TILE))
            if flip:
                scaled = pygame.transform.flip(scaled, True, False)
            frames.append(scaled)
        # blink frame
        d = 'right' if direction == 'left' else direction
        flip = (direction == 'left')
        blink_surf = make_char(d, 0, hair, shirt, pants, blink=True)
        blink_scaled = pygame.transform.scale(blink_surf, (TILE, TILE))
        if flip:
            blink_scaled = pygame.transform.flip(blink_scaled, True, False)
        frames.append(blink_scaled)
        out[direction] = frames
    return out

def build_special_anim(maker_func):
    out = {}
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(2):
            surf = maker_func(direction, f)
            scaled = pygame.transform.scale(surf, (TILE, TILE))
            if direction == 'left':
                scaled = pygame.transform.flip(scaled, True, False)
            frames.append(scaled)
        out[direction] = frames
    return out
