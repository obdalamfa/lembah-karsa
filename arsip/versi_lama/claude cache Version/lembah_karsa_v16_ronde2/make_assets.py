"""
make_assets.py — Asset pipeline generator untuk Lembah Karsa v5.

Jalankan dari root project:
    python make_assets.py

Akan generate semua PNG ke folder assets/{tiles,objects,chars}/.
Sprites menggunakan procedural drawing identik dengan v4 (style HM:BTN
inspired: outline gelap, 3-tone shading, mata ekspresif, animasi 4 frame).

Setelah generate, jalankan game:
    python main.py

Game akan otomatis load PNG dari assets/. Kalau PNG belum ada,
sprites.py fallback ke kotak warna sehingga game tetap jalan.

Konten yang di-generate:
  TILES (assets/tiles/):
    - grass, dirt, path, floor, wall, tilled_dry, tilled_wet
    - cave_wall, cave_floor, straw
    - water_0..3 (animasi 4 frame)
    - waterfall_0..2 (animasi 3 frame)        [BARU v5]
    - crypt_wall, crypt_floor, bat_dropping   [BARU v5]
    - dock, water_lily                        [BARU v5]

  OBJECTS (assets/objects/):
    - tree, dead_tree, fence, gate, mailbox, door
    - bed, stove, table, bookshelf, mirror, fireplace_0..1
    - clock, plant_pot, chest, counter, shelf_store
    - grave, lantern_0..1, pen_post
    - mandrake, wild_herb, wild_berry
    - running_mushroom_0..1, firefly_0..2 (animated)
    - crystal, boat                            [BARU v5]
    - {crop}_0..3 untuk 8 crops (lobak, wortel, stroberi, jagung, tomat, labu, bayam, jamur)

  CHARS (assets/chars/<nama>/):
    Tiap karakter = 4 arah × 3 frame = 12 PNG file.
    {arah}_{frame}.png dimana arah=up/down/left/right, frame=0/1/2.

    Total 26 karakter:
    - player (1)
    - npc manusia (12): arya, sari, raka, maya, budi, joko, cici, bowo,
                        ningsih, pak_guru, mbok_jum, jaka_ronda
    - npc supernatural (10): jin, demit, tuyul, kuntilanak, pocong,
                             genderuwo, wewe, banaspati, leak, naga
    - npc hewan (9 tipe): sapi, ayam, kambing, bebek, domba, kuda,
                          kucing, rubah, kelinci

Total file PNG: ~340+
"""
import pygame
import math
import random
import os
import sys

# Init pygame headless agar bisa di-run di server tanpa display
os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
pygame.init()
pygame.display.set_mode((1, 1))

# Import konstanta dari game.config (dari root project)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from game.config import C, TILE, SPRITE



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
    """Return naga sprite scaled (96x64 = 3x2 tile)."""
    out = {}
    for direction in ['up', 'down', 'left', 'right']:
        frames = []
        for f in range(2):
            base = make_naga(direction, f)
            scaled = pygame.transform.scale(base, (96, 64))
            if direction == 'right':
                scaled = pygame.transform.flip(scaled, True, False)
            frames.append(scaled)
        out[direction] = frames
    return out



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
#  HEWAN BARU
# ══════════════════════════════════════════════════════
def make_bebek(direction, frame):
    """Bebek kuning kecil."""
    s = make_surface()
    # Tubuh
    rect(s, 4, 9, 12, 13, C.bebek_white)
    rect(s, 5, 8, 11, 12, C.bebek_white)
    # Sayap shadow
    rect(s, 6, 10, 8, 12, (220, 220, 210))
    # Kepala
    rect(s, 9, 6, 13, 9, C.bebek_white)
    rect(s, 10, 5, 12, 7, C.bebek_white)
    # Paruh oranye
    pp(s, 13, 7, C.bebek_orange)
    pp(s, 14, 7, C.bebek_orange)
    pp(s, 13, 8, C.bebek_yellow)
    # Mata
    pp(s, 11, 6, C.bk)
    # Ekor
    rect(s, 2, 9, 4, 11, C.bebek_white)
    pp(s, 1, 10, C.bebek_white)
    # Kaki oranye
    if frame:
        vline(s, 6, 13, 15, C.bebek_orange)
        vline(s, 10, 14, 15, C.bebek_orange)
    else:
        vline(s, 7, 14, 15, C.bebek_orange)
        vline(s, 9, 13, 15, C.bebek_orange)
    return s


def make_domba(direction, frame):
    """Domba berbulu putih."""
    s = make_surface()
    # Tubuh berbulu (cloud-like)
    for cx, cy, r in [(5,8,2),(8,7,2),(11,8,2),(6,10,2),(9,11,2),(11,10,2),(4,9,1),(13,9,1)]:
        for dx in range(-r, r+1):
            for dy in range(-r, r+1):
                if dx*dx + dy*dy <= r*r:
                    pp(s, cx+dx, cy+dy, C.domba_white)
    # Highlight
    pp(s, 4, 7, lighter(C.domba_white, 5))
    pp(s, 9, 6, lighter(C.domba_white, 5))
    # Kepala domba (gelap)
    rect(s, 1, 6, 4, 10, C.domba_dark)
    rect(s, 2, 5, 3, 9, C.domba_dark)
    pp(s, 0, 7, C.domba_dark)
    # Mata
    pp(s, 3, 7, C.wt)
    pp(s, 3, 8, C.bk)
    # Telinga
    pp(s, 1, 5, C.domba_dark)
    pp(s, 4, 5, C.domba_dark)
    # Kaki gelap
    if frame:
        vline(s, 5, 12, 15, C.domba_dark)
        vline(s, 8, 13, 15, C.domba_dark)
        vline(s, 11, 12, 15, C.domba_dark)
    else:
        vline(s, 6, 13, 15, C.domba_dark)
        vline(s, 9, 12, 15, C.domba_dark)
        vline(s, 12, 13, 15, C.domba_dark)
    return s


def make_kuda(direction, frame):
    """Kuda coklat."""
    s = make_surface()
    # Body
    rect(s, 2, 7, 12, 11, C.kuda_brown)
    rect(s, 3, 6, 11, 10, C.kuda_brown)
    # Highlight punggung
    hline(s, 6, 4, 11, lighter(C.kuda_brown, 20))
    # Belly shadow
    hline(s, 11, 3, 11, C.kuda_dark)
    # Leher
    rect(s, 11, 4, 13, 8, C.kuda_brown)
    # Kepala
    rect(s, 12, 3, 15, 7, C.kuda_brown)
    rect(s, 13, 2, 15, 6, C.kuda_brown)
    # Telinga
    pp(s, 13, 1, C.kuda_brown)
    pp(s, 14, 1, C.kuda_brown)
    # Mata
    pp(s, 14, 4, C.bk)
    # Mulut
    pp(s, 15, 5, C.kuda_dark)
    # Surai (mane)
    rect(s, 9, 3, 12, 6, C.kuda_mane)
    pp(s, 8, 4, C.kuda_mane)
    # Tail
    rect(s, 0, 7, 2, 10, C.kuda_mane)
    pp(s, 0, 6, C.kuda_mane)
    # Kaki
    if frame:
        vline(s, 3, 12, 15, C.kuda_dark)
        vline(s, 7, 12, 15, C.kuda_dark)
        vline(s, 9, 13, 15, C.kuda_dark)
        vline(s, 11, 13, 15, C.kuda_dark)
    else:
        vline(s, 4, 12, 15, C.kuda_dark)
        vline(s, 6, 13, 15, C.kuda_dark)
        vline(s, 10, 12, 15, C.kuda_dark)
        vline(s, 12, 13, 15, C.kuda_dark)
    # Hoof
    for fx in [4, 7, 9, 11]:
        pp(s, fx, 15, C.bk)
    return s


def make_kucing(direction, frame):
    """Kucing oren peliharaan."""
    s = make_surface()
    # Body
    rect(s, 4, 9, 12, 13, C.kucing_oren)
    rect(s, 5, 8, 11, 12, C.kucing_oren)
    # Stripes
    pp(s, 6, 10, C.kucing_white); pp(s, 9, 10, C.kucing_white)
    pp(s, 7, 11, C.kucing_white); pp(s, 10, 11, C.kucing_white)
    # Head
    rect(s, 5, 4, 11, 8, C.kucing_oren)
    # Ears (triangular)
    pp(s, 5, 3, C.kucing_oren); pp(s, 11, 3, C.kucing_oren)
    pp(s, 6, 3, C.kucing_oren); pp(s, 10, 3, C.kucing_oren)
    pp(s, 6, 4, C.kucing_white); pp(s, 10, 4, C.kucing_white)
    # Eyes (slit)
    pp(s, 7, 6, C.bk); pp(s, 9, 6, C.bk)
    # Nose
    pp(s, 8, 7, (200, 100, 100))
    # Whiskers
    pp(s, 4, 7, C.wt); pp(s, 12, 7, C.wt)
    # Tail (curling)
    if frame:
        rect(s, 13, 8, 14, 11, C.kucing_oren)
        pp(s, 14, 7, C.kucing_oren)
    else:
        rect(s, 13, 9, 14, 12, C.kucing_oren)
        pp(s, 14, 8, C.kucing_oren)
    # Legs
    if frame:
        vline(s, 5, 13, 15, C.kucing_oren)
        vline(s, 11, 13, 15, C.kucing_oren)
        vline(s, 7, 14, 15, C.kucing_oren)
        vline(s, 9, 14, 15, C.kucing_oren)
    else:
        vline(s, 6, 13, 15, C.kucing_oren)
        vline(s, 10, 13, 15, C.kucing_oren)
        vline(s, 8, 14, 15, C.kucing_oren)
    return s


def make_rubah(direction, frame):
    """Rubah liar oranye-putih."""
    s = make_surface()
    # Body sleek
    rect(s, 3, 8, 13, 12, C.rubah_orange)
    rect(s, 4, 9, 12, 11, C.rubah_orange)
    # White belly
    rect(s, 5, 11, 11, 12, C.rubah_white)
    # Head pointed
    rect(s, 1, 5, 6, 9, C.rubah_orange)
    rect(s, 2, 6, 5, 8, C.rubah_orange)
    # Pointed ears
    pp(s, 1, 3, C.rubah_orange); pp(s, 1, 4, C.rubah_orange)
    pp(s, 5, 3, C.rubah_orange); pp(s, 5, 4, C.rubah_orange)
    # Eyes cunning
    pp(s, 2, 6, C.bk); pp(s, 5, 6, C.bk)
    pp(s, 2, 7, C.gl); pp(s, 5, 7, C.gl)  # mata kuning
    # Nose
    pp(s, 0, 7, C.bk)
    # Long tail bushy with white tip
    if frame:
        rect(s, 13, 7, 15, 10, C.rubah_orange)
        pp(s, 15, 7, C.rubah_white); pp(s, 15, 8, C.rubah_white)
    else:
        rect(s, 13, 8, 15, 11, C.rubah_orange)
        pp(s, 15, 9, C.rubah_white); pp(s, 15, 10, C.rubah_white)
    # Legs slim
    if frame:
        vline(s, 4, 12, 15, C.rubah_orange)
        vline(s, 11, 12, 15, C.rubah_orange)
        vline(s, 7, 13, 15, C.rubah_orange)
        vline(s, 9, 13, 15, C.rubah_orange)
    else:
        vline(s, 5, 12, 15, C.rubah_orange)
        vline(s, 10, 12, 15, C.rubah_orange)
        vline(s, 6, 13, 15, C.rubah_orange)
        vline(s, 11, 13, 15, C.rubah_orange)
    # Black paws
    for fx in [4, 7, 9, 11]:
        pp(s, fx, 15, C.bk)
    return s


def make_kelinci(direction, frame):
    """Kelinci putih kecil."""
    s = make_surface()
    # Body bulat
    rect(s, 5, 9, 11, 13, C.kelinci_white)
    rect(s, 6, 8, 10, 13, C.kelinci_white)
    # Pinkish spots
    pp(s, 7, 11, C.kelinci_pink); pp(s, 9, 11, C.kelinci_pink)
    # Head bulat
    rect(s, 5, 5, 11, 8, C.kelinci_white)
    # Long ears
    rect(s, 6, 1, 7, 5, C.kelinci_white)
    rect(s, 9, 1, 10, 5, C.kelinci_white)
    pp(s, 6, 2, C.kelinci_pink); pp(s, 7, 3, C.kelinci_pink)
    pp(s, 9, 3, C.kelinci_pink); pp(s, 10, 2, C.kelinci_pink)
    # Eyes
    pp(s, 6, 6, C.bk); pp(s, 10, 6, C.bk)
    # Nose pink
    pp(s, 8, 7, C.kelinci_pink)
    # Whiskers
    pp(s, 5, 7, (180,180,180)); pp(s, 11, 7, (180,180,180))
    # Cottontail
    if frame:
        pp(s, 12, 11, C.wt); pp(s, 13, 11, C.wt)
        pp(s, 12, 12, C.wt); pp(s, 13, 12, C.wt)
    else:
        pp(s, 12, 10, C.wt); pp(s, 13, 10, C.wt)
        pp(s, 12, 11, C.wt); pp(s, 13, 11, C.wt)
    # Legs (bouncy when frame=1)
    if frame:
        # crouched
        rect(s, 5, 14, 6, 15, C.kelinci_white)
        rect(s, 10, 14, 11, 15, C.kelinci_white)
    else:
        # extended (jumping)
        rect(s, 4, 13, 6, 15, C.kelinci_white)
        rect(s, 10, 13, 12, 15, C.kelinci_white)
    return s


def make_banaspati(direction, frame):
    """Banaspati — kepala api melayang."""
    s = make_surface()
    bob = -1 if frame else 0
    # Aura api
    rect(s, 3, 4+bob, 12, 13+bob, C.fire1)
    rect(s, 4, 3+bob, 11, 12+bob, C.fire2)
    rect(s, 5, 2+bob, 10, 11+bob, C.fire3)
    # Wajah api
    rect(s, 5, 7+bob, 10, 11+bob, C.fire1)
    # Mata
    pp(s, 6, 8+bob, C.bk); pp(s, 9, 8+bob, C.bk)
    pp(s, 6, 7+bob, C.gl); pp(s, 9, 7+bob, C.gl)
    # Mulut menganga
    rect(s, 7, 10+bob, 8, 11+bob, C.bk)
    # Lidah api
    pp(s, 7, 12+bob, C.fire2); pp(s, 8, 12+bob, C.fire3)
    # Spark trail bawah
    pp(s, 6, 14, C.fire2)
    pp(s, 9, 14, C.fire3)
    pp(s, 7, 15, C.gl)
    pp(s, 8, 15, C.fire2)
    return s


def make_leak(direction, frame):
    """Leak Bali — kepala terbang dengan rambut acak."""
    s = make_surface()
    # Kepala melayang
    rect(s, 4, 5, 11, 11, C.demit_dark)
    rect(s, 5, 4, 10, 10, C.demit_dark)
    # Rambut wild
    pp(s, 3, 4, C.demit_dark); pp(s, 12, 4, C.demit_dark)
    pp(s, 3, 6, C.demit_dark); pp(s, 12, 6, C.demit_dark)
    pp(s, 4, 3, C.demit_dark); pp(s, 11, 3, C.demit_dark)
    pp(s, 5, 2, C.demit_dark); pp(s, 10, 2, C.demit_dark)
    # Mata merah menyala
    pp(s, 6, 7, (255,40,40)); pp(s, 9, 7, (255,40,40))
    pp(s, 6, 6, C.gl); pp(s, 9, 6, C.gl)
    # Taring
    pp(s, 7, 9, C.wt); pp(s, 8, 9, C.wt)
    pp(s, 7, 10, C.wt); pp(s, 8, 10, C.wt)
    # Lidah panjang
    if frame:
        rect(s, 7, 11, 8, 13, (220, 40, 40))
        pp(s, 7, 14, (220, 40, 40))
    else:
        rect(s, 7, 11, 8, 12, (220, 40, 40))
    # Aura merah
    rect(s, 2, 5, 3, 11, (180, 30, 30, 100))
    rect(s, 12, 5, 13, 11, (180, 30, 30, 100))
    return s


# ══════════════════════════════════════════════════════
#  MAKHLUK HALUS BARU
# ══════════════════════════════════════════════════════
def make_kuntilanak(direction, frame):
    """Kuntilanak — wanita putih melayang dengan rambut panjang."""
    s = make_surface()
    bob = 1 if frame else 0
    # Rambut hitam panjang (membungkus)
    rect(s, 3, 1+bob, 12, 14+bob, C.kunti_hair)
    # Wajah putih
    rect(s, 5, 4+bob, 10, 10+bob, C.kunti_white)
    rect(s, 6, 3+bob, 9, 9+bob, C.kunti_white)
    # Mata merah
    pp(s, 6, 6+bob, C.kunti_red)
    pp(s, 9, 6+bob, C.kunti_red)
    # Mulut menyeringai
    rect(s, 6, 8+bob, 9, 8+bob, C.bk)
    pp(s, 7, 9+bob, C.kunti_red)
    # Dress putih
    rect(s, 4, 11+bob, 11, 15, C.kunti_white)
    # Rambut juga di samping
    pp(s, 2, 5+bob, C.kunti_hair)
    pp(s, 13, 5+bob, C.kunti_hair)
    pp(s, 2, 8+bob, C.kunti_hair)
    pp(s, 13, 8+bob, C.kunti_hair)
    # Aura kalau frame
    if frame:
        pp(s, 1, 7, (200, 200, 220, 100))
        pp(s, 14, 7, (200, 200, 220, 100))
    return s


def make_pocong(direction, frame):
    """Pocong — kain kafan putih, melompat."""
    s = make_surface()
    # Pocong lompat berbeda di tiap frame
    y_off = 0 if frame else 2  # frame 0 di atas, frame 1 di bawah
    # Kain putih (segitiga)
    rect(s, 5, 1+y_off, 10, 14+y_off, C.pocong_white)
    rect(s, 4, 3+y_off, 11, 13+y_off, C.pocong_white)
    rect(s, 3, 5+y_off, 12, 12+y_off, C.pocong_white)
    # Top simpul
    rect(s, 6, 0+y_off, 9, 1+y_off, C.pocong_white)
    pp(s, 7, 0+y_off, C.pocong_shadow)
    pp(s, 8, 0+y_off, C.pocong_shadow)
    # Wajah area gelap
    rect(s, 6, 4+y_off, 9, 7+y_off, C.pocong_shadow)
    pp(s, 6, 5+y_off, C.bk); pp(s, 9, 5+y_off, C.bk)  # mata
    rect(s, 7, 7+y_off, 8, 7+y_off, C.bk)  # mulut
    # Tali simpul
    hline(s, 9+y_off, 4, 11, (180, 170, 160))
    hline(s, 13+y_off, 4, 11, (180, 170, 160))
    return s


def make_genderuwo(direction, frame):
    """Genderuwo — raksasa hitam berbulu."""
    s = make_surface()
    # Tubuh besar
    rect(s, 2, 4, 13, 14, C.genderuwo_brown)
    rect(s, 3, 3, 12, 13, C.genderuwo_brown)
    # Shadow
    rect(s, 3, 12, 12, 14, darker(C.genderuwo_brown, 30))
    # Bulu cakar
    for fx in [2, 4, 11, 13]:
        pp(s, fx, 4, C.bk)
    # Kepala besar
    rect(s, 3, 1, 12, 7, C.genderuwo_brown)
    # Mata merah menyala
    pp(s, 5, 4, C.genderuwo_red)
    pp(s, 6, 4, C.genderuwo_red)
    pp(s, 9, 4, C.genderuwo_red)
    pp(s, 10, 4, C.genderuwo_red)
    pp(s, 5, 3, lighter(C.genderuwo_red, 40))
    pp(s, 9, 3, lighter(C.genderuwo_red, 40))
    # Taring putih
    pp(s, 6, 6, C.wt)
    pp(s, 9, 6, C.wt)
    # Tanduk kecil
    pp(s, 4, 0, C.bk)
    pp(s, 11, 0, C.bk)
    # Kaki & cakar
    if frame:
        rect(s, 3, 14, 5, 15, C.bk)
        rect(s, 10, 14, 12, 15, C.bk)
    else:
        rect(s, 4, 14, 6, 15, C.bk)
        rect(s, 9, 14, 11, 15, C.bk)
    return s


def make_wewe_gombel(direction, frame):
    """Wewe Gombel — perempuan tua, dada panjang menyeramkan."""
    s = make_surface()
    bob = 1 if frame else 0
    # Rambut acak hitam
    rect(s, 3, 0+bob, 12, 5+bob, C.wewe_dark)
    pp(s, 2, 1+bob, C.wewe_dark); pp(s, 13, 1+bob, C.wewe_dark)
    pp(s, 2, 3+bob, C.wewe_dark); pp(s, 13, 3+bob, C.wewe_dark)
    # Wajah keriput hijau pucat
    rect(s, 5, 4+bob, 10, 9+bob, (140, 160, 130))
    # Mata hitam dalam
    pp(s, 6, 6+bob, C.bk); pp(s, 9, 6+bob, C.bk)
    pp(s, 6, 5+bob, C.wewe_red); pp(s, 9, 5+bob, C.wewe_red)
    # Senyum bengis
    rect(s, 6, 8+bob, 9, 8+bob, C.bk)
    pp(s, 7, 9+bob, C.wt)
    # Tubuh kurus
    rect(s, 6, 10+bob, 9, 13, (90, 100, 90))
    # Tangan panjang
    rect(s, 3, 11+bob, 5, 14, C.wewe_dark)
    rect(s, 10, 11+bob, 12, 14, C.wewe_dark)
    # Cakar
    pp(s, 3, 14, C.bk); pp(s, 12, 14, C.bk)
    # Kaki
    rect(s, 6, 14, 7, 15, C.wewe_dark)
    rect(s, 8, 14, 9, 15, C.wewe_dark)
    return s


# ══════════════════════════════════════════════════════
#  VISUAL HELPERS — bayangan & cloud
# ══════════════════════════════════════════════════════
def make_shadow(width=20, height=8):
    """Shadow ellipse hitam transparan untuk di kaki karakter."""
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.ellipse(s, (0, 0, 0, C.SHADOW_ALPHA if hasattr(C,'SHADOW_ALPHA') else 110),
                        (0, 0, width, height))
    return s


def make_cloud_shadow(width=120, height=80):
    """Soft cloud shadow untuk parallax."""
    s = pygame.Surface((width, height), pygame.SRCALPHA)
    # Multiple ellipse stacked
    cx = width // 2
    cy = height // 2
    for i in range(5):
        offset_x = (i - 2) * 18
        offset_y = (i % 2) * 6
        radius_x = 30 + (i % 3) * 8
        radius_y = 20 + (i % 2) * 5
        pygame.draw.ellipse(s, (0, 0, 30, 50),
                            (cx + offset_x - radius_x, cy + offset_y - radius_y,
                             radius_x * 2, radius_y * 2))
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



# ═══════════════════════════════════════════════════
#  TILE BARU v5 — kuburan, gua spesifik, danau
#  Dibuat dengan style yang konsisten dengan v4 (3-tone shading)
# ═══════════════════════════════════════════════════
def make_crypt_floor():
    """Lantai crypt — batu poles abu gelap."""
    s = make_surface(fill=C.crypt_floor)
    rng = random.Random(110)
    for _ in range(12):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, darker(C.crypt_floor, 15))
    # Pola batu kotak
    hline(s, 7, 0, 15, C.crypt_stone_dk)
    vline(s, 7, 0, 15, C.crypt_stone_dk)
    return s


def make_crypt_wall():
    """Dinding crypt — batu kuno bertekstur."""
    s = make_surface(fill=C.crypt_stone)
    rng = random.Random(111)
    for _ in range(20):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        c = rng.choice([C.crypt_stone_dk, lighter(C.crypt_stone, 10)])
        pp(s, x, y, c)
    # Mortar lines (batu bata)
    hline(s, 5, 0, 15, C.crypt_stone_dk)
    hline(s, 11, 0, 15, C.crypt_stone_dk)
    vline(s, 7, 0, 4, C.crypt_stone_dk)
    vline(s, 8, 6, 10, C.crypt_stone_dk)
    return s


def make_crystal():
    """Kristal cluster — ungu/biru/pink dengan sparkle."""
    s = make_surface()
    # Lantai gua dasar
    rect(s, 0, 0, 15, 15, C.cave_floor)
    # 3 kristal cluster dengan warna berbeda
    # Kristal 1: ungu (kiri)
    rect(s, 3, 8, 5, 14, C.crystal_purple)
    rect(s, 2, 9, 4, 13, lighter(C.crystal_purple, 15))
    pp(s, 3, 7, lighter(C.crystal_purple, 30))  # tip
    # Kristal 2: biru (tengah, paling tinggi)
    rect(s, 7, 4, 9, 14, C.crystal_blue)
    rect(s, 6, 6, 8, 13, lighter(C.crystal_blue, 15))
    pp(s, 7, 3, lighter(C.crystal_blue, 30))
    pp(s, 8, 3, C.crystal_glow)  # sparkle
    # Kristal 3: pink (kanan)
    rect(s, 11, 9, 13, 14, C.crystal_pink)
    rect(s, 10, 10, 12, 13, lighter(C.crystal_pink, 15))
    pp(s, 11, 8, lighter(C.crystal_pink, 30))
    # Sparkles random
    pp(s, 4, 11, C.crystal_glow)
    pp(s, 12, 12, C.crystal_glow)
    return s


def make_bat_dropping():
    """Lantai gua dengan kotoran kelelawar."""
    s = make_surface(fill=C.cave_floor)
    rng = random.Random(112)
    for _ in range(8):
        x, y = rng.randint(1, 14), rng.randint(1, 14)
        pp(s, x, y, C.bat_dropping)
        if x + 1 < 15:
            pp(s, x + 1, y, C.bat_brown)
    # Beberapa flek kering
    for _ in range(4):
        x, y = rng.randint(2, 13), rng.randint(2, 13)
        pp(s, x, y, darker(C.bat_dropping, 15))
    return s


def make_waterfall(frame=0):
    """Air terjun bergerak — vertikal."""
    s = make_surface(fill=C.waterfall_blue)
    # Pita putih bergerak vertikal (4 frame untuk loop)
    off = frame % 4
    for y in range(0, 16, 4):
        py = (y + off) % 16
        hline(s, py, 2, 13, C.waterfall_white)
        hline(s, (py + 1) % 16, 4, 11, lighter(C.waterfall_white, 10))
    # Tepi gelap di sisi (bayangan tebing)
    vline(s, 0, 0, 15, darker(C.waterfall_blue, 30))
    vline(s, 15, 0, 15, darker(C.waterfall_blue, 30))
    return s


def make_dock():
    """Dermaga kayu — papan horizontal."""
    s = make_surface(fill=C.dock_wood)
    # Papan horizontal
    for y in [2, 7, 12]:
        hline(s, y, 0, 15, C.dock_wood_dk)
    # Knot kayu
    pp(s, 4, 4, C.dock_wood_dk)
    pp(s, 5, 4, darker(C.dock_wood_dk, 15))
    pp(s, 11, 9, C.dock_wood_dk)
    pp(s, 10, 14, C.dock_wood_dk)
    # Highlight di papan atas (matahari)
    hline(s, 0, 0, 15, lighter(C.dock_wood, 20))
    return s


def make_boat():
    """Perahu kecil — view dari atas."""
    s = make_surface()
    # Latar air biru (perahu di atas air)
    rect(s, 0, 0, 15, 15, C.w1)
    # Hull oval dari kayu
    # Outer outline (gelap)
    rect(s, 2, 4, 13, 11, C.boat_wood_dk)
    # Inner hull (kayu cerah)
    rect(s, 3, 5, 12, 10, C.boat_wood)
    # Bangku tengah
    rect(s, 5, 7, 10, 8, C.dock_wood_dk)
    # Lambung depan & belakang lancip
    pp(s, 1, 7, C.boat_wood_dk); pp(s, 1, 8, C.boat_wood_dk)
    pp(s, 14, 7, C.boat_wood_dk); pp(s, 14, 8, C.boat_wood_dk)
    return s


def make_water_lily():
    """Eceng gondok — daun bulat + bunga ungu."""
    s = make_surface()
    # Latar air
    rect(s, 0, 0, 15, 15, C.w1)
    # Daun besar (kiri)
    for y in range(8, 13):
        for x in range(2, 8):
            dist = (x - 5) ** 2 + (y - 10) ** 2
            if dist <= 8:
                pp(s, x, y, C.lily_green)
            elif dist <= 12:
                pp(s, x, y, darker(C.lily_green, 15))
    # Daun kecil (kanan-atas)
    for y in range(4, 8):
        for x in range(9, 14):
            dist = (x - 11) ** 2 + (y - 6) ** 2
            if dist <= 6:
                pp(s, x, y, C.lily_green)
    # Bunga ungu di tengah
    rect(s, 6, 8, 8, 10, C.lily_purple)
    pp(s, 7, 9, C.cy)  # benang sari kuning
    return s


# ═══════════════════════════════════════════════════
#  DRIVER — generate semua asset PNG
# ═══════════════════════════════════════════════════
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')


def _save(surf, rel_path):
    """Save surface ke ASSETS_DIR/rel_path."""
    full = os.path.join(ASSETS_DIR, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    pygame.image.save(surf, full)


def _scale(surf, target_size=None):
    """Scale 16×16 surface ke TILE×TILE (32×32)."""
    if target_size is None:
        target_size = (TILE, TILE)
    return pygame.transform.scale(surf, target_size)


def generate_tiles():
    """Generate semua tile dasar."""
    print("🌱 Generating tiles...")
    _save(_scale(make_grass_tile()), "tiles/grass.png")
    _save(_scale(make_dirt_tile()), "tiles/dirt.png")
    _save(_scale(make_path_tile()), "tiles/path.png")
    _save(_scale(make_floor_tile()), "tiles/floor.png")
    _save(_scale(make_wall_tile()), "tiles/wall.png")
    _save(_scale(make_tilled_dry()), "tiles/tilled_dry.png")
    _save(_scale(make_tilled_wet()), "tiles/tilled_wet.png")
    _save(_scale(make_cave_wall()), "tiles/cave_wall.png")
    _save(_scale(make_cave_floor()), "tiles/cave_floor.png")
    _save(_scale(make_straw()), "tiles/straw.png")
    # Animated water (4 frame)
    for i in range(4):
        _save(_scale(make_water_tile(i * 4)), f"tiles/water_{i}.png")
    # Tile baru v5
    _save(_scale(make_crypt_floor()), "tiles/crypt_floor.png")
    _save(_scale(make_crypt_wall()), "tiles/crypt_wall.png")
    _save(_scale(make_crystal()), "tiles/crystal.png")
    _save(_scale(make_bat_dropping()), "tiles/bat_dropping.png")
    _save(_scale(make_dock()), "tiles/dock.png")
    _save(_scale(make_boat()), "tiles/boat.png")
    _save(_scale(make_water_lily()), "tiles/water_lily.png")
    # Animated waterfall (4 frame)
    for i in range(4):
        _save(_scale(make_waterfall(i)), f"tiles/waterfall_{i}.png")
    print(f"   ✓ {len(os.listdir(os.path.join(ASSETS_DIR, 'tiles')))} tile assets")


def generate_objects():
    """Generate semua objek (furniture, decor)."""
    print("🏠 Generating objects...")
    _save(_scale(make_tree()), "objects/tree.png")
    _save(_scale(make_dead_tree()), "objects/dead_tree.png")
    _save(_scale(make_fence()), "objects/fence.png")
    _save(_scale(make_gate()), "objects/gate.png")
    _save(_scale(make_mailbox()), "objects/mailbox.png")
    _save(_scale(make_door()), "objects/door.png")
    _save(_scale(make_bed()), "objects/bed.png")
    _save(_scale(make_stove()), "objects/stove.png")
    _save(_scale(make_table()), "objects/table.png")
    _save(_scale(make_bookshelf()), "objects/bookshelf.png")
    _save(_scale(make_mirror()), "objects/mirror.png")
    _save(_scale(make_clock()), "objects/clock.png")
    _save(_scale(make_plant_pot()), "objects/plant_pot.png")
    _save(_scale(make_chest()), "objects/chest.png")
    _save(_scale(make_counter()), "objects/counter.png")
    _save(_scale(make_shelf_store()), "objects/shelf_store.png")
    _save(_scale(make_grave()), "objects/grave.png")
    _save(_scale(make_pen_post()), "objects/pen_post.png")
    # Animated fireplace, lantern (2 frame)
    for i in range(2):
        _save(_scale(make_fireplace(i)), f"objects/fireplace_{i}.png")
        _save(_scale(make_lantern(i)), f"objects/lantern_{i}.png")
    # Wild items
    _save(_scale(make_mandrake()), "objects/mandrake.png")
    _save(_scale(make_wild_herb()), "objects/wild_herb.png")
    _save(_scale(make_wild_berry()), "objects/wild_berry.png")
    # Running mushroom (2 frame)
    for i in range(2):
        _save(_scale(make_running_mushroom(i)), f"objects/running_mushroom_{i}.png")
    # Firefly (3 frame)
    for i in range(3):
        _save(_scale(make_firefly(i)), f"objects/firefly_{i}.png")
    print(f"   ✓ {len(os.listdir(os.path.join(ASSETS_DIR, 'objects')))} object assets")


def generate_crops():
    """Generate crop sprites (4 stage per tanaman)."""
    print("🌾 Generating crops...")
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
        for stage in range(4):
            _save(_scale(make_crop_sprite(stage, c1, c2)),
                  f"objects/{crop_id}_{stage}.png")
    print(f"   ✓ {len(crop_colors)} tanaman × 4 stage = {len(crop_colors) * 4} files")


def _save_char_anim(name, maker_func, hair=None, shirt=None, pants=None,
                    is_human=True, is_huge=False):
    """Save 4 arah × 3 frame untuk satu karakter.

    Ukuran target: TILE×TILE (32×32) — sprite fit di tile, kaki menapak.
    Naga huge: 96×64 (3 tile × 2 tile)."""
    target_w = 96 if is_huge else TILE
    target_h = 64 if is_huge else TILE  # 32×32 (BUKAN 1.5×) supaya menapak

    for d in ['up', 'down', 'left', 'right']:
        # Logika mirror left dari right (mengikuti pattern v4)
        actual_d = 'right' if d == 'left' else d
        flip = (d == 'left')

        # 3 frame: walk0, walk1, blink/idle
        for f_idx in range(3):
            if is_human:
                # frame 0,1 = walk; frame 2 = blink
                blink = (f_idx == 2)
                walk_frame = 0 if f_idx == 0 else 1
                surf = maker_func(actual_d, walk_frame, hair, shirt, pants,
                                  hat=True, blink=blink)
            else:
                # Special makers: cuma butuh (direction, frame)
                # frame 2 jadikan duplikat frame 0 (tidak ada blink konsep)
                actual_f = 0 if f_idx == 2 else f_idx
                surf = maker_func(actual_d, actual_f)

            # Scale ke TILE×TILE*1.5 atau 96×64 untuk huge
            if is_huge:
                # Naga butuh perlakuan khusus karena sprite-nya dimensinya beda
                # Asumsi naga returns ukuran bukan SPRITE — handle terpisah
                scaled = pygame.transform.scale(surf, (target_w, target_h))
            else:
                scaled = pygame.transform.scale(surf, (target_w, target_h))

            if flip:
                scaled = pygame.transform.flip(scaled, True, False)

            _save(scaled, f"chars/{name}/{d}_{f_idx}.png")


def generate_characters():
    """Generate semua 32 karakter (player + 12 manusia + 10 makhluk halus + 9 hewan)."""
    print("🧙 Generating characters (32 karakter × 4 dir × 3 frame = 384 files)...")

    # ─── PLAYER ───
    _save_char_anim('player', make_char,
                    hair=C.h0, shirt=C.s0, pants=C.pn, is_human=True)

    # ─── 12 MANUSIA ───
    humans = [
        ('npc_arya', C.ng, C.g1, C.pn),
        ('npc_sari', C.cr, C.nc_sari, C.pn),
        ('npc_raka', C.ng, C.nc_raka, C.s0),
        ('npc_maya', C.gl, C.nc_maya, C.pn),
        ('npc_budi', C.ng, C.nc_budi, C.p2),
        ('npc_joko', C.ng, C.nc_joko, C.p2),
        ('npc_cici', C.h1, C.nc_cici, C.cr),
        ('npc_bowo', C.h2, C.nc_bowo, C.fn2),
        ('npc_ningsih', C.ng, C.nc_ningsih, C.s0),
        ('npc_pak_guru', C.h2, C.nc_guru, C.pn2),
        ('npc_mbok_jum', C.ng, C.nc_mbokjum, C.fn),
        ('npc_jaka_ronda', C.h0, C.nc_jaka, C.p2),
    ]
    for name, hair, shirt, pants in humans:
        _save_char_anim(name, make_char, hair=hair, shirt=shirt, pants=pants,
                        is_human=True)

    # ─── 9 MAKHLUK HALUS (NPC type-keyed, mengikuti naming sprites.py) ───
    # Mapping nama folder ↔ maker function
    supernatural = [
        ('npc_jin', make_jin),
        ('npc_demit', make_demit),
        ('npc_tuyul', make_tuyul),
        ('npc_kuntilanak', make_kuntilanak),
        ('npc_pocong', make_pocong),
        ('npc_genderuwo', make_genderuwo),
        ('npc_wewe', make_wewe_gombel),
        ('npc_banaspati', make_banaspati),
        ('npc_leak', make_leak),
    ]
    for name, fn in supernatural:
        _save_char_anim(name, fn, is_human=False)

    # ─── NAGA (sprite besar 96×64) ───
    # CATATAN: Jika ada PNG kustom di assets/chars/npc_naga/down_0.png (misal
    # dari extract_naga.py), skip generate procedural agar art kustom tetap.
    custom_naga = os.path.exists(
        os.path.join(ASSETS_DIR, 'chars', 'npc_naga', 'down_0.png'))
    if custom_naga:
        print("   ✓ Naga: pakai sprite kustom yang sudah ada (skip generate)")
    else:
        print("   ✓ Generating naga (huge sprite procedural)...")
        for d in ['up', 'down', 'left', 'right']:
            actual_d = 'right' if d == 'left' else d
            for f_idx in range(3):
                actual_f = f_idx if f_idx < 2 else 0
                surf = make_naga(actual_d, actual_f)
                scaled = pygame.transform.scale(surf, (96, 64))
                if d == 'left':
                    scaled = pygame.transform.flip(scaled, True, False)
                _save(scaled, f"chars/npc_naga/{d}_{f_idx}.png")

    # ─── 9 HEWAN ───
    animals = [
        ('npc_sapi', make_sapi),
        ('npc_ayam', make_ayam),
        ('npc_kambing', make_kambing),
        ('npc_bebek', make_bebek),
        ('npc_domba', make_domba),
        ('npc_kuda', make_kuda),
        ('npc_kucing', make_kucing),
        ('npc_rubah', make_rubah),
        ('npc_kelinci', make_kelinci),
    ]
    for name, fn in animals:
        _save_char_anim(name, fn, is_human=False)

    # Hitung file karakter
    total_files = 0
    for root, dirs, files in os.walk(os.path.join(ASSETS_DIR, 'chars')):
        total_files += len([f for f in files if f.endswith('.png')])
    print(f"   ✓ {total_files} character sprite files")


def generate_all():
    print("=" * 50)
    print("🎨 LEMBAH KARSA v5 — Asset Generator")
    print("=" * 50)
    os.makedirs(ASSETS_DIR, exist_ok=True)
    generate_tiles()
    generate_objects()
    generate_crops()
    generate_characters()
    print("=" * 50)
    print("✅ Selesai! Asset siap di:", ASSETS_DIR)
    print("   Jalankan: python main.py")
    print("=" * 50)


if __name__ == '__main__':
    generate_all()
