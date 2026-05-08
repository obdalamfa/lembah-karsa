"""
sprites.py — Generator sprite pixel-art bergaya Octopath Traveller HD-2D.
Semua sprite digenerate runtime via pygame.Surface.
Style: Octopath Traveller + Harvest Moon hybrid
- Palette kaya & saturasi tinggi
- Outline gelap di tepi
- 4-tone shading (highlight bright + mid + base + shadow deep)
- Mata ekspresif
- Glow / aura efek pada elemen interaktif
"""
import pygame
import math
import random
import json
from pathlib import Path
from .config import C, TILE, SPRITE

# Path ke ROM HM64 sprites yang sudah diekstrak
_HM64_DIR = Path(r"E:\Download\hm64-decomp-master\hm64-decomp-master\assets\sprites")


# ── Palette Octopath Traveller (OTP) ──────────────────────
# Warna lebih saturasi & dramatis dari palette dasar C
class OTP:
    # Rumput — hangat & kaya
    g_hi  = (118, 200, 82)   # highlight
    g_mid = (78,  162, 55)   # mid
    g_base= (52,  122, 38)   # base
    g_shd = (28,   78, 24)   # shadow

    # Tanah — coklat kemerahan
    d_hi  = (168, 122, 68)
    d_mid = (138,  95, 48)
    d_base= (108,  72, 32)
    d_shd = ( 72,  45, 18)

    # Air — biru jernih
    w_hi  = (130, 210, 255)
    w_mid = ( 65, 158, 228)
    w_base= ( 28,  98, 188)
    w_shd = ( 12,  58, 128)

    # Jalan batu
    p_hi  = (188, 175, 158)
    p_mid = (155, 142, 125)
    p_base= (122, 110,  95)
    p_shd = ( 88,  78,  68)

    # Kayu — hangat
    wo_hi = (195, 148,  82)
    wo_mid= (158, 108,  45)
    wo_base=(118,  75,  22)
    wo_shd = ( 72,  42,  12)

    # Kulit karakter
    sk_hi = (255, 228, 188)
    sk_mid= (238, 195, 148)
    sk_base=(215, 162, 108)
    sk_shd = (175, 122,  78)

    # Langit
    sky_day    = (148, 208, 248)
    sky_sunset = (255, 162,  85)
    sky_night  = (  8,  12,  48)
    sky_dawn   = (215, 128, 105)

    # Cahaya / glow
    glow_fire   = (255, 168,  45)
    glow_magic  = (195, 118, 255)
    glow_nature = (108, 228,  88)
    glow_moon   = (188, 195, 255)

    # Outline gelap tajam
    outline = (12, 8, 18)

    # UI Octopath-style
    ui_bg     = (18,  12,  35)
    ui_bg2    = (32,  22,  55)
    ui_border = (148,  98, 218)
    ui_gold   = (252, 218,  68)


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
    s = make_surface(fill=OTP.g_base)
    # Layer variasi warna
    for _ in range(24):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([OTP.g_shd, OTP.g_mid, OTP.g_hi]))
    # Blade rumput — pendek, dua pixel tinggi
    for _ in range(6):
        bx = rng.randint(1, 14)
        by = rng.randint(2, 13)
        pp(s, bx, by,   OTP.g_shd)
        pp(s, bx, by-1, OTP.g_hi)
        pp(s, bx-1, by, OTP.g_mid)
    # Highlight top-left (cahaya atas)
    for y in range(5):
        for x in range(5):
            if rng.random() < 0.25:
                pp(s, x, y, OTP.g_hi)
    return s

def make_dirt_tile(seed=43):
    rng = random.Random(seed)
    s = make_surface(fill=OTP.d_base)
    for _ in range(18):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([OTP.d_shd, OTP.d_mid, OTP.d_hi]))
    # Batu kecil
    for _ in range(2):
        sx, sy = rng.randint(2, 12), rng.randint(2, 12)
        rect(s, sx, sy, sx+1, sy+1, OTP.p_base)
        pp(s, sx, sy, OTP.p_hi)
    return s

def make_tilled_dry():
    s = make_surface(fill=OTP.d_shd)
    for y in range(16):
        for x in range(16):
            if y % 3 == 0:   pp(s, x, y, OTP.d_mid)
            elif y % 3 == 1: pp(s, x, y, OTP.d_base)
            # Tekstur garis cangkul
            if x % 5 == 2: pp(s, x, y, OTP.d_shd)
    return s

def make_tilled_wet():
    s = make_surface(fill=OTP.d_shd)
    for y in range(16):
        for x in range(16):
            if y % 3 == 0:   pp(s, x, y, OTP.w_shd)
            elif y % 3 == 1: pp(s, x, y, OTP.d_shd)
            else:            pp(s, x, y, OTP.d_base)
            if x % 5 == 2: pp(s, x, y, (28, 72, 148))
    # Shimmer kecil
    pp(s, 3, 2, OTP.w_hi); pp(s, 11, 8, OTP.w_hi)
    return s

def make_water_tile(frame=0):
    s = make_surface(fill=OTP.w_base)
    for y in range(16):
        for x in range(16):
            wave = math.sin((x + y * 1.8 + frame * 0.7) * 0.75)
            if wave > 0.45:   pp(s, x, y, OTP.w_hi)
            elif wave > 0.1:  pp(s, x, y, OTP.w_mid)
            elif wave < -0.4: pp(s, x, y, OTP.w_shd)
    # Sparkle putih berkilau
    if frame % 6 < 3:
        sp = 3 + (frame % 3) * 3
        pp(s, sp, 5, (255, 255, 255))
        pp(s, (sp + 7) % 16, 11, (220, 240, 255))
    return s

def make_path_tile(seed=44):
    rng = random.Random(seed)
    s = make_surface(fill=OTP.p_base)
    # Pola batu bata
    for ty in range(0, 16, 5):
        offset = 4 if (ty // 5) % 2 else 0
        for tx in range(0, 16, 8):
            bx = (tx + offset) % 16
            rect(s, bx, ty, min(15, bx + 7), min(15, ty + 4), OTP.p_mid)
            hline(s, ty, bx, min(15, bx + 7), OTP.p_hi)
    for _ in range(8):
        x, y = rng.randint(0, 15), rng.randint(0, 15)
        pp(s, x, y, rng.choice([OTP.p_shd, OTP.p_hi]))
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
    """Pohon Octopath-style — foliage berlapis, shading 4-tone, trunk detail."""
    s = make_surface()
    # Trunk dengan shading hangat
    rect(s, 6, 10, 9, 15, OTP.wo_base)
    rect(s, 7, 10, 8, 15, OTP.wo_mid)
    vline(s, 6, 10, 15, OTP.wo_shd)
    vline(s, 9, 10, 15, OTP.wo_shd)
    pp(s, 7, 11, OTP.wo_hi)   # highlight trunk
    # Akar di bawah
    pp(s, 5, 15, OTP.wo_shd); pp(s, 10, 15, OTP.wo_shd)

    # Crown berlapis (bawah → atas, makin kecil & terang)
    layers = [
        (4,  9, 11, 11, OTP.g_shd),   # layer terbawah (bayangan)
        (3,  7, 12,  9, OTP.g_base),
        (3,  5, 12,  8, OTP.g_mid),
        (4,  3, 11,  6, OTP.g_base),
        (5,  2, 10,  4, OTP.g_mid),
        (6,  1,  9,  3, OTP.g_mid),
    ]
    for x1, y1, x2, y2, c in layers:
        rect(s, x1, y1, x2, y2, c)

    # Highlight utama (kiri-atas = sumber cahaya)
    rect(s, 6, 1, 8, 3, OTP.g_hi)
    pp(s, 5, 3, OTP.g_hi); pp(s, 4, 5, OTP.g_hi)
    pp(s, 5, 5, OTP.g_hi)

    # Shadow sisi kanan-bawah
    vline(s, 12, 7, 10, OTP.g_shd)
    hline(s, 10, 5, 12, OTP.g_shd)

    # Buah kecil / berry sesekali (detail)
    pp(s, 9, 4, (205, 58, 48)); pp(s, 11, 6, (185, 48, 38))

    return outline_sprite(s, OTP.outline)

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
#  CHARACTER SPRITE — HM:BTN STYLE
#  16x16 dengan outline, expressive eyes, blush
# ══════════════════════════════════════════════════════
def make_char(direction, frame, hair=C.h0, shirt=C.s0, pants=C.pn, hat=True, blink=False):
    """
    Karakter Octopath+HM hybrid:
    - Chibi dengan kepala sedikit lebih proporsional
    - Shading 4-tone (hi / mid / base / shadow)
    - Mata ekspresif besar dengan sparkle
    - Blush pipi khas HM
    - Outline hitam tegas OTP
    """
    s = make_surface()
    hi_sk  = OTP.sk_hi
    mid_sk = OTP.sk_mid
    base_sk= OTP.sk_base
    shd_sk = OTP.sk_shd

    # ── Topi ──────────────────────────────────────────────
    if hat:
        hat_c  = C.ht
        hat_s  = C.ht2
        hat_d  = darker(C.ht2, 30)
        rect(s, 4, 0, 11, 0, hat_c)
        rect(s, 3, 1, 12, 1, hat_c)
        rect(s, 3, 2, 12, 2, hat_s)
        hline(s, 2, 5, 10, darker(hat_c, 60))  # pita
        rect(s, 3, 3, 12, 3, hat_d)            # brim shadow

    # ── Kepala ────────────────────────────────────────────
    head_top = 4 if hat else 2
    rect(s, 4, head_top, 11, 8, mid_sk)        # base kepala
    rect(s, 5, head_top, 10, head_top + 1, hi_sk)  # dahi highlight
    rect(s, 4, 7, 11, 8, base_sk)              # dagu shadow

    # Pipi blush (HM khas)
    pp(s, 4, 7, (255, 168, 168))
    pp(s, 11, 7, (255, 168, 168))

    # ── Rambut ────────────────────────────────────────────
    hi_hair = lighter(hair, 35)
    shd_hair = darker(hair, 35)
    if direction == "up":
        rect(s, 4, head_top, 11, head_top + 2, hair)
        hline(s, head_top, 5, 9, hi_hair)
    else:
        for xi in [4, 5]:
            for yi in [head_top, head_top + 1]:
                pp(s, xi, yi, hair)
        for xi in [10, 11]:
            for yi in [head_top, head_top + 1]:
                pp(s, xi, yi, shd_hair)
        pp(s, 6, head_top, hair)
        pp(s, 9, head_top, hair)
        pp(s, 7, head_top, hi_hair)   # highlight poni

    # ── Mata ekspresif ────────────────────────────────────
    if direction != "up":
        ey = head_top + 2
        if blink:
            hline(s, ey, 5, 6, C.bk)
            hline(s, ey, 9, 10, C.bk)
        else:
            # Putih mata
            pp(s, 5, ey, (240, 240, 248)); pp(s, 6, ey, (240, 240, 248))
            pp(s, 9, ey, (240, 240, 248)); pp(s, 10, ey, (240, 240, 248))
            # Iris berwarna (biru Octopath)
            iris_c = (55, 98, 192)
            if direction == "left":
                pp(s, 5, ey, iris_c); pp(s, 9, ey, iris_c)
            elif direction == "right":
                pp(s, 6, ey, iris_c); pp(s, 10, ey, iris_c)
            else:
                pp(s, 5, ey, iris_c); pp(s, 9, ey, iris_c)
            # Sparkle putih kecil
            if direction != "left":
                pp(s, 6, ey, (240, 248, 255))
            else:
                pp(s, 5, ey - 1, (240, 248, 255))
            # Bulu mata atas
            pp(s, 5, ey - 1, C.bk); pp(s, 10, ey - 1, C.bk)

        # Mulut kecil expresif
        if not blink:
            pp(s, 7, head_top + 4, (195, 95, 95))
            pp(s, 8, head_top + 4, (195, 95, 95))

    # ── Leher ────────────────────────────────────────────
    pp(s, 7, 9, mid_sk); pp(s, 8, 9, mid_sk)

    # ── Badan ────────────────────────────────────────────
    hi_shirt  = lighter(shirt, 30)
    shd_shirt = darker(shirt, 35)
    rect(s, 4, 9, 11, 13, shirt)
    hline(s, 9, 4, 11, hi_shirt)    # highlight bahu
    hline(s, 13, 4, 11, shd_shirt)  # shadow bawah baju
    # Kerah putih
    pp(s, 7, 9, (245, 245, 250)); pp(s, 8, 9, (245, 245, 250))
    # Lipatan baju kecil
    vline(s, 7, 10, 12, darker(shirt, 15))

    # ── Tangan ───────────────────────────────────────────
    if direction in ("left", "right"):
        off = 1 if frame else 0
        pp(s, 3, 9, mid_sk); pp(s, 3, 10 + off, mid_sk)
        pp(s, 12, 9 + (1 - off), mid_sk); pp(s, 12, 10, mid_sk)
    else:
        pp(s, 3, 9, mid_sk); pp(s, 3, 10, mid_sk)
        pp(s, 12, 9, mid_sk); pp(s, 12, 10, mid_sk)

    # ── Celana ───────────────────────────────────────────
    hi_pants  = lighter(pants, 20)
    shd_pants = darker(pants, 30)
    rect(s, 4, 13, 11, 15, pants)
    vline(s, 7, 13, 15, shd_pants)   # seam
    vline(s, 8, 13, 15, shd_pants)
    pp(s, 5, 13, hi_pants); pp(s, 10, 13, hi_pants)

    # ── Animasi berjalan ─────────────────────────────────
    shoe_c = darker(C.h2, 10)
    if frame and direction in ("left", "right"):
        # Kaki melangkah (satu terangkat)
        rect(s, 4, 15, 5, 15, shoe_c)
        rect(s, 9, 14, 10, 15, shoe_c)  # kaki maju
        pp(s, 11, 15, shd_pants)
    else:
        rect(s, 4, 15, 5, 15, shoe_c)
        rect(s, 10, 15, 11, 15, shoe_c)

    # ── Animasi up/down ──────────────────────────────────
    if direction in ("up", "down"):
        if frame:
            pp(s, 4, 15, shd_pants)
        else:
            pp(s, 11, 15, shd_pants)

    return outline_sprite(s, OTP.outline)


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
#  GLOW / LIGHTING HELPERS (Octopath HD-2D style)
# ══════════════════════════════════════════════════════

# Cache glow surfaces agar tidak reallocate tiap frame
_glow_cache: dict = {}

def draw_glow(surface: pygame.Surface, cx: int, cy: int,
              color: tuple, radius: int, intensity: float = 1.0):
    """
    Gambar glow lingkaran soft di surface dengan additive blending.
    Mirip efek bloom Octopath Traveller di sekitar sumber cahaya.
    """
    key = (color, radius, int(intensity * 100))
    if key not in _glow_cache:
        d = radius * 2
        gs = pygame.Surface((d, d), pygame.SRCALPHA)
        r, g, b = color[0], color[1], color[2]
        for ring in range(radius, 0, -2):
            ratio = ring / radius
            alpha = int(intensity * 90 * (1.0 - ratio) ** 1.6)
            if alpha < 2:
                continue
            pygame.draw.circle(gs, (r, g, b, alpha), (radius, radius), ring)
        _glow_cache[key] = gs
    gsurf = _glow_cache[key]
    surface.blit(gsurf, (cx - radius, cy - radius),
                 special_flags=pygame.BLEND_RGBA_ADD)


def make_vignette(w: int, h: int) -> pygame.Surface:
    """
    Buat vignette overlay sekali saat startup.
    Tepi gelap seperti efek depth Octopath.
    """
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    depth = min(w, h) // 2
    step = 3
    for i in range(0, depth, step):
        ratio = 1.0 - i / depth
        alpha = int(195 * ratio ** 2.8)
        if alpha < 3:
            break
        col = (0, 0, 0, alpha)
        pygame.draw.rect(surf, col, (i, i, step, h - 2 * i))
        pygame.draw.rect(surf, col, (w - i - step, i, step, h - 2 * i))
        pygame.draw.rect(surf, col, (i, i, w - 2 * i, step))
        pygame.draw.rect(surf, col, (i, h - i - step, w - 2 * i, step))
    return surf


def get_color_grade(hour: int, is_raining: bool = False) -> tuple:
    """
    Return (r,g,b, alpha) overlay untuk color grading berbasis waktu.
    Meniru tone HDR Octopath Traveller.
    """
    if is_raining:
        return (80, 100, 140, 40)
    if 5 <= hour < 7:     # Fajar — merah-ungu
        return (210, 105, 68, 55)
    if 7 <= hour < 9:     # Pagi — kuning hangat
        return (255, 215, 120, 28)
    if 9 <= hour < 16:    # Siang — sedikit biru cerah
        return (210, 240, 255, 12)
    if 16 <= hour < 17:   # Sore emas
        return (255, 200, 80, 38)
    if 17 <= hour < 19:   # Matahari terbenam — oranye
        return (255, 145, 58, 62)
    if 19 <= hour < 20:   # Senja — ungu
        return (95, 58, 145, 72)
    # Malam
    return (18, 22, 78, 88)


def draw_char_shadow(surface: pygame.Surface, px: int, py: int, tile_size: int):
    """Bayangan elips di bawah karakter (kedalaman Octopath)."""
    shadow_surf = pygame.Surface((tile_size, tile_size // 3), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 55),
                        (tile_size // 6, 0, tile_size * 2 // 3, tile_size // 3))
    surface.blit(shadow_surf, (px, py + tile_size - tile_size // 4))


# ══════════════════════════════════════════════════════
#  SPRITE REGISTRY (lazy init)
# ══════════════════════════════════════════════════════
SPRITES = {}
ANIMATED = {}

# ── HM64 sprite loader ─────────────────────────────────────

def _hm64_load(subdir: str, label: str, idx: int) -> pygame.Surface | None:
    path = _HM64_DIR / subdir / label / "textures" / f"{idx:03d}.png"
    if not path.exists():
        return None
    try:
        raw = pygame.image.load(str(path)).convert_alpha()
        return pygame.transform.scale(raw, (TILE, TILE))
    except Exception:
        return None

def _hm64_anim_sprites(subdir: str, label: str, anim_idx: int, max_n: int = 2) -> list[int]:
    """Baca JSON animasi HM64, kembalikan sprite indices unik (max_n pertama)."""
    path = _HM64_DIR / subdir / label / "animations" / f"{anim_idx:02d}.json"
    if not path.exists():
        return []
    try:
        d = json.loads(path.read_text())
    except Exception:
        return []
    seen, result = set(), []
    for fr in d['frames']:
        for s in fr['sprites']:
            idx = s['spritesheet_index']
            if idx not in seen:
                seen.add(idx); result.append(idx)
                if len(result) >= max_n:
                    return result
    return result

def _hm64_build_char(subdir: str, label: str,
                     anim_down: int = 5, anim_right: int = 6, anim_up: int = 9,
                     idle_anim_down: int = 0, idle_anim_right: int = 1,
                     idle_anim_up: int = 4) -> dict | None:
    """
    Bangun anim dict {dir: [surf0, surf1, surf2]} dari sprite HM64.
    LEFT = mirror RIGHT (hindari frame diagonal arah berlawanan).
    """
    def _idle(anim_n):
        idxs = _hm64_anim_sprites(subdir, label, anim_n, 1)
        return idxs[0] if idxs else None

    def _walk(anim_n):
        return _hm64_anim_sprites(subdir, label, anim_n, 2)

    i_down  = _idle(idle_anim_down)
    i_right = _idle(idle_anim_right)
    i_up    = _idle(idle_anim_up)
    w_down  = _walk(anim_down)
    w_right = _walk(anim_right)
    w_up    = _walk(anim_up)

    if not (i_down is not None and w_down and w_right and w_up):
        return None

    raw_map = {
        'down':  ([i_down]  + w_down)[:3],
        'right': ([i_right if i_right is not None else w_right[0]] + w_right)[:3],
        'up':    ([i_up    if i_up    is not None else w_up[0]]    + w_up)[:3],
    }
    # Pastikan 3 frame
    for d in raw_map:
        while len(raw_map[d]) < 3:
            raw_map[d].append(raw_map[d][-1])

    out = {}
    for direction, idxs in raw_map.items():
        frames = []
        for idx in idxs:
            s = _hm64_load(subdir, label, idx)
            if s is None:
                return None
            frames.append(s)
        out[direction] = frames

    # LEFT = mirror RIGHT (konsisten & tidak diagonal)
    out['left'] = [pygame.transform.flip(s, True, False) for s in out['right']]
    return out

def _hm64_build_animal(subdir: str, label: str,
                       idle_down: int, idle_side: int, idle_up: int,
                       anim_down: int, anim_side: int, anim_up: int) -> dict | None:
    """Bangun anim hewan dengan 3 arah berbeda + LEFT=mirror RIGHT."""
    w_down = _hm64_anim_sprites(subdir, label, anim_down, 2)
    w_side = _hm64_anim_sprites(subdir, label, anim_side, 2)
    w_up   = _hm64_anim_sprites(subdir, label, anim_up,   2)

    raw_map = {
        'down':  ([idle_down] + w_down)[:3],
        'right': ([idle_side] + w_side)[:3],
        'up':    ([idle_up]   + w_up)[:3],
    }
    for d in raw_map:
        while len(raw_map[d]) < 3:
            raw_map[d].append(raw_map[d][-1])

    out = {}
    for direction, idxs in raw_map.items():
        frames = []
        for idx in idxs:
            s = _hm64_load(subdir, label, idx)
            if s is None:
                return None
            frames.append(s)
        out[direction] = frames
    out['left'] = [pygame.transform.flip(s, True, False) for s in out['right']]
    return out

def _hm64_recolor(char_dict: dict, tint: tuple, strength: float,
                  alpha: float = 1.0) -> dict:
    """Tint semua frame dalam anim dict (untuk makhluk halus)."""
    import pygame.surfarray
    result = {}
    tr, tg, tb = tint
    for direction, frames in char_dict.items():
        new_frames = []
        for src in frames:
            dst = src.copy()
            # blend piksel warna dengan tint
            arr = pygame.surfarray.pixels3d(dst)
            arr[:, :, 0] = (arr[:, :, 0] * (1 - strength) + tr * strength).clip(0, 255).astype('uint8')
            arr[:, :, 1] = (arr[:, :, 1] * (1 - strength) + tg * strength).clip(0, 255).astype('uint8')
            arr[:, :, 2] = (arr[:, :, 2] * (1 - strength) + tb * strength).clip(0, 255).astype('uint8')
            del arr
            if alpha < 1.0:
                a_arr = pygame.surfarray.pixels_alpha(dst)
                a_arr[:] = (a_arr * alpha).clip(0, 255).astype('uint8')
                del a_arr
            new_frames.append(dst)
        result[direction] = new_frames
    return result


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

    # ── Player (HM64, left=mirror right) ─────────────────────
    p = _hm64_build_char('entitySprites', 'player')
    ANIMATED['player'] = p if p else build_char_anim()

    # ── NPC (gender-correct: arya/raka/budi=laki, sari/maya=perempuan) ──
    _npc_hm64 = {
        'npc_arya': ('entitySprites/npc', 'barley'),   # laki tua, petani
        'npc_sari': ('entitySprites/npc', 'ann'),      # perempuan
        'npc_raka': ('entitySprites/npc', 'gray'),     # laki
        'npc_maya': ('entitySprites/npc', 'karen'),    # perempuan
        'npc_budi': ('entitySprites/npc', 'cliff'),    # laki
    }
    _npc_fallback = {
        'npc_arya':  lambda: build_char_anim(C.ng, C.g1, C.pn),
        'npc_sari':  lambda: build_char_anim(C.cr, C.nc_sari, C.pn),
        'npc_raka':  lambda: build_char_anim(C.ng, C.nc_raka, C.s0),
        'npc_maya':  lambda: build_char_anim(C.gl, C.nc_maya, C.pn),
        'npc_budi':  lambda: build_char_anim(C.ng, C.nc_budi, C.p2),
    }
    for npc_key, (sub, lbl) in _npc_hm64.items():
        hm = _hm64_build_char(sub, lbl)
        ANIMATED[npc_key] = hm if hm else _npc_fallback[npc_key]()

    # ── Supernatural — recolor NPC HM64 sesuai tema ───────────
    _spirit_cfg = [
        # (key, base_sub, base_lbl, tint_rgb, strength, alpha)
        ('npc_jin',    'entitySprites/npc', 'kai',   (255, 120,  20), 0.60, 1.00),
        ('npc_demit',  'entitySprites/npc', 'cliff', ( 80,  10,  80), 0.65, 1.00),
        ('npc_tuyul',  'entitySprites/npc', 'stu',   (180, 220, 180), 0.50, 0.85),
    ]
    _spirit_fallback = {
        'npc_jin':   lambda: build_special_anim(make_jin),
        'npc_demit': lambda: build_special_anim(make_demit),
        'npc_tuyul': lambda: build_special_anim(make_tuyul),
    }
    for key, sub, lbl, tint, strength, alpha in _spirit_cfg:
        base = _hm64_build_char(sub, lbl)
        if base:
            ANIMATED[key] = _hm64_recolor(base, tint, strength, alpha)
        else:
            ANIMATED[key] = _spirit_fallback[key]()

    # ── Animals — frame per arah yang benar ───────────────────
    # Chicken: down=0 side=1 up=3 | walk: anim5=down anim6=side anim7=up
    ayam = _hm64_build_animal('entitySprites/animals', 'chicken',
                              idle_down=0, idle_side=1, idle_up=3,
                              anim_down=5, anim_side=6, anim_up=7)
    ANIMATED['npc_ayam'] = ayam if ayam else build_special_anim(make_ayam)

    # Cow: idle dari anim00-04 (frame 61-65), walk anim5=down 6=side 7=up
    import json as _json
    def _cow_idle(anim_n):
        p2 = _HM64_DIR / 'entitySprites/animals' / 'cow' / 'animations' / f'{anim_n:02d}.json'
        if p2.exists():
            d = _json.loads(p2.read_text())
            return d['frames'][0]['sprites'][0]['spritesheet_index']
        return None
    ci_d, ci_s, ci_u = _cow_idle(0), _cow_idle(1), _cow_idle(4)
    if all(x is not None for x in [ci_d, ci_s, ci_u]):
        sapi = _hm64_build_animal('entitySprites/animals', 'cow',
                                  idle_down=ci_d, idle_side=ci_s, idle_up=ci_u,
                                  anim_down=5, anim_side=6, anim_up=7)
        ANIMATED['npc_sapi'] = sapi if sapi else build_special_anim(make_sapi)
    else:
        ANIMATED['npc_sapi'] = build_special_anim(make_sapi)

    # Sheep (kambing): idle dari anim01/03/02, walk anim5=down 6=side 7=up
    def _sheep_idle(anim_n):
        p2 = _HM64_DIR / 'entitySprites/animals' / 'sheep' / 'animations' / f'{anim_n:02d}.json'
        if p2.exists():
            d = _json.loads(p2.read_text())
            return d['frames'][0]['sprites'][0]['spritesheet_index']
        return None
    si_d = _sheep_idle(1); si_s = _sheep_idle(3); si_u = _sheep_idle(2)
    if all(x is not None for x in [si_d, si_s, si_u]):
        kambing = _hm64_build_animal('entitySprites/animals', 'sheep',
                                     idle_down=si_d, idle_side=si_s, idle_up=si_u,
                                     anim_down=5, anim_side=6, anim_up=7)
        ANIMATED['npc_kambing'] = kambing if kambing else build_special_anim(make_kambing)
    else:
        ANIMATED['npc_kambing'] = build_special_anim(make_kambing)

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
