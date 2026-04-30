"""
scenes.py — Definisi semua peta (scenes).

Scene v4 dipertahankan:
  - outdoor (50×35: kebun, desa, hutan, pasar malam)
  - house, shop, clinic, studio, smith, greenhouse, naga_cave

Scene baru v5:
  - cemetery_z1, cemetery_z2, cemetery_z3 — kuburan 3 zona (mudah → sulit)
  - crypt — indoor di kuburan (rumah Mbah Demit)
  - bat_cave — gua kelelawar (genderuwo + bat dropping)
  - crystal_cave — gua kristal (banaspati + crystal terang)
  - lake — danau dengan air terjun, dermaga, perahu, eceng gondok

Outdoor diadjust: kuburan & danau jadi portal masuk, bukan area inline.
"""
import random
from .config import (G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS,
                     MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR,
                     CRYPT_W, CRYPT_F, CRYS, BAT_D, WTF, DCK, BOT, LLY)


class Scene:
    def __init__(self, name, display, tiles, portals=None, indoor=False):
        self.name = name
        self.display = display
        self.tiles = tiles
        self.w = len(tiles[0])
        self.h = len(tiles)
        # portal: (from_x, from_y, target_scene, target_x, target_y)
        self.portals = portals or []
        self.indoor = indoor


# ═══════════════════════════════════════════════════
#  HELPER UTILITIES
# ═══════════════════════════════════════════════════
def _new_map(w, h, fill_tile):
    return [[fill_tile] * w for _ in range(h)]


def _fill(m, x, y, w, h, t):
    H_, W_ = len(m), len(m[0])
    for dy in range(h):
        for dx in range(w):
            if 0 <= y + dy < H_ and 0 <= x + dx < W_:
                m[y + dy][x + dx] = t


def _hl(m, y, x1, x2, t):
    H_, W_ = len(m), len(m[0])
    for x in range(x1, x2 + 1):
        if 0 <= y < H_ and 0 <= x < W_:
            m[y][x] = t


def _vl(m, x, y1, y2, t):
    H_, W_ = len(m), len(m[0])
    for y in range(y1, y2 + 1):
        if 0 <= y < H_ and 0 <= x < W_:
            m[y][x] = t


def _border(m, t):
    """Wall-border tiles di sisi map indoor."""
    H_, W_ = len(m), len(m[0])
    for x in range(W_):
        m[0][x] = t
        m[H_ - 1][x] = t
    for y in range(H_):
        m[y][0] = t
        m[y][W_ - 1] = t


# ═══════════════════════════════════════════════════
#  OUTDOOR — peta utama 50×35
# ═══════════════════════════════════════════════════
def build_outdoor():
    """Dunia luar: kebun + desa + hutan + pasar malam.
    Perubahan v5: kuburan & danau jadi portal masuk ke scene terpisah."""
    W_, H_ = 50, 35
    m = _new_map(W_, H_, G)
    rng = random.Random(7)

    # ═══ KEBUN PEMAIN (kiri atas) ═══
    _fill(m, 1, 1, 14, 11, D)
    _fill(m, 1, 1, 5, 4, H)  # rumah
    m[4][3] = DR
    m[2][6] = MB

    # PAGAR + GERBANG
    _hl(m, 0, 1, 15, FN); _vl(m, 0, 0, 12, FN)
    _hl(m, 12, 1, 15, FN); _vl(m, 15, 1, 12, FN)
    m[12][8] = GT       # gerbang selatan kebun
    m[6][15] = GT       # gerbang timur kebun

    # Kandang hewan
    _fill(m, 2, 9, 7, 4, STR)
    for x in range(2, 9): m[9][x] = PEN
    for x in range(2, 9): m[12][x] = PEN
    for y in range(9, 13): m[y][2] = PEN
    for y in range(9, 13): m[y][8] = PEN
    m[12][5] = GT

    # Jalan utama
    _hl(m, 13, 0, W_ - 1, P)
    _vl(m, 18, 0, H_ - 1, P)
    _vl(m, 35, 0, H_ - 1, P)

    # ═══ SUNGAI di tengah-atas (estetika, bukan portal) ═══
    _fill(m, 19, 0, 4, 5, W)
    _fill(m, 22, 4, 3, 4, W)
    m[13][19] = P; m[13][20] = P; m[13][21] = P

    # ═══ DESA ═══
    _fill(m, 20, 1, 5, 4, H); m[4][22] = DR   # warung
    _fill(m, 27, 1, 5, 4, H); m[4][29] = DR   # klinik
    _fill(m, 34, 1, 5, 4, H); m[4][36] = DR   # studio
    _fill(m, 20, 7, 5, 4, H); m[10][22] = DR  # smith
    _fill(m, 27, 7, 5, 4, H); m[10][29] = DR  # greenhouse

    # Pohon hias di desa
    for x, y in [(25, 2), (26, 5), (33, 2), (33, 7), (38, 3), (39, 7)]:
        if m[y][x] == G:
            m[y][x] = TR

    # ═══ PASAR MALAM ═══
    _fill(m, 28, 16, 12, 5, P)
    for x, y in [(29, 17), (31, 17), (33, 17), (35, 17), (37, 17), (39, 17),
                 (29, 19), (31, 19), (33, 19), (35, 19), (37, 19), (39, 19)]:
        m[y][x] = LN
    _fill(m, 30, 18, 2, 1, CT)
    _fill(m, 34, 18, 2, 1, CT)
    _fill(m, 38, 18, 2, 1, CT)

    # ═══ HUTAN SELATAN (kiri-bawah) ═══
    for y in range(15, H_):
        for x in range(0, 18):
            if m[y][x] == G and rng.random() < 0.18:
                m[y][x] = TR

    # Hutan dalam (paling rapat)
    for y in range(22, H_ - 2):
        for x in range(0, 12):
            if m[y][x] == G and rng.random() < 0.25:
                m[y][x] = DT if rng.random() < 0.3 else TR

    # ═══ DANAU PORTAL (kiri-tengah-bawah) ═══
    # v4: danau inline di area (5,18)-(13,23). v5: jadi portal ke scene 'lake'.
    # Sisakan 1 tile air sebagai indikator visual + portal dock di tepi.
    _fill(m, 5, 18, 8, 5, W)
    m[20][9] = DCK  # dermaga kecil (tile portal masuk lake)

    # ═══ KUBURAN PORTAL (kanan-tengah-bawah) ═══
    # v4: kuburan inline grave tiles di (33,22)-(40,28). v5: jadi portal ke 'cemetery_z1'.
    # Sisakan 1 patch kecil + gerbang masuk
    _fill(m, 33, 22, 8, 7, D)
    # Beberapa nisan tetap (ambiance)
    for x, y in [(34, 23), (38, 23), (35, 27), (39, 27)]:
        if 0 <= x < W_ and 0 <= y < H_:
            m[y][x] = GR
    # Pohon mati di sudut
    for x, y in [(33, 22), (41, 28), (33, 28), (41, 22)]:
        if 0 <= x < W_ and 0 <= y < H_:
            m[y][x] = DT
    m[24][37] = GT  # gerbang kuburan (portal ke cemetery_z1)

    # ═══ HUTAN TIMUR ═══
    for y in range(20, H_):
        for x in range(42, W_):
            if m[y][x] == G and rng.random() < 0.22:
                m[y][x] = TR

    # ═══ GUNUNG UTARA + 3 PINTU GUA (atas-kanan) ═══
    # Area gunung: dinding batu + 3 pintu masuk gua
    for y in range(0, 3):
        for x in range(40, 50):
            m[y][x] = CV_W
    for y in range(0, 2):
        for x in range(45, 50):
            m[y][x] = CV_W
    # 3 pintu gua bersebelahan
    m[2][41] = DR  # bat_cave
    m[2][45] = DR  # naga_cave (utama)
    m[2][48] = DR  # crystal_cave

    return Scene('outdoor', 'Lembah Karsa', m,
        portals=[
            (3, 4, 'house', 7, 9),
            (22, 4, 'shop', 7, 9),
            (29, 4, 'clinic', 7, 9),
            (36, 4, 'studio', 7, 9),
            (22, 10, 'smith', 7, 9),
            (29, 10, 'greenhouse', 7, 9),
            # 3 gua di gunung utara
            (41, 2, 'bat_cave', 7, 10),
            (45, 2, 'naga_cave', 7, 10),
            (48, 2, 'crystal_cave', 7, 10),
            # Portal ke kuburan & danau
            (37, 24, 'cemetery_z1', 7, 13),
            (9, 20, 'lake', 7, 13),
        ])


# ═══════════════════════════════════════════════════
#  INDOOR ROOM HELPER
# ═══════════════════════════════════════════════════
def _build_indoor_room(name, display, furniture_layout, npc_outdoor_pos,
                       w=15, h=12, floor_tile=FL, wall_tile=WL):
    m = _new_map(w, h, floor_tile)
    _border(m, wall_tile)
    m[h - 1][7] = DR
    for (x, y, tile) in furniture_layout:
        if 0 <= x < w and 0 <= y < h:
            m[y][x] = tile
    return Scene(name, display, m,
        portals=[(7, h - 1, 'outdoor', npc_outdoor_pos[0], npc_outdoor_pos[1])],
        indoor=True)


def build_house():
    return _build_indoor_room('house', 'Rumah Kamu', [
        (1, 1, BD), (2, 1, BD),
        (1, 2, CH),
        (4, 1, BS), (5, 1, BS),
        (1, 3, MR),
        (1, 4, PP),
        (7, 1, FP),
        (9, 1, CL),
        (6, 3, TB), (7, 3, TB),
        (11, 1, ST), (12, 1, ST),
        (11, 2, SH), (12, 2, SH),
        (13, 5, PP),
    ], (3, 5))


def build_shop():
    layout = []
    for x in range(1, 14): layout.append((x, 4, CT))
    for x in range(1, 14): layout.append((x, 1, SH))
    return _build_indoor_room('shop', 'Warung Bu Sari', layout, (22, 5))


def build_clinic():
    return _build_indoor_room('clinic', 'Klinik Pak Raka', [
        (1, 1, BD), (2, 1, BD),
        (12, 1, BD), (13, 1, BD),
        (1, 3, TB), (13, 3, BS),
    ], (29, 5))


def build_studio():
    return _build_indoor_room('studio', 'Studio Maya', [
        (6, 1, TB), (7, 1, TB), (8, 1, TB),
        (1, 3, BS), (2, 3, BS),
    ], (36, 5))


def build_smith():
    return _build_indoor_room('smith', 'Bengkel Budi', [
        (6, 1, TB),
        (1, 2, SH),
        (12, 1, FP),
    ], (22, 11))


def build_greenhouse():
    """Greenhouse: lantai tanah, jalan tengah."""
    W_, H_ = 15, 12
    m = _new_map(W_, H_, D)
    _border(m, WL)
    m[H_ - 1][7] = DR
    for x in range(1, W_ - 1):
        m[5][x] = P
    return Scene('greenhouse', 'Rumah Kaca', m,
        portals=[(7, 11, 'outdoor', 29, 11)], indoor=True)


# ═══════════════════════════════════════════════════
#  GUA NAGA (existing v4, di-expand)
# ═══════════════════════════════════════════════════
def build_naga_cave():
    """Gua sang naga — luas, gelap mistis, naga di tengah.
    Expanded v5: ukuran lebih besar 18×14, lebih banyak stalagmit."""
    W_, H_ = 18, 14
    m = _new_map(W_, H_, CV_F)
    _border(m, CV_W)
    m[H_ - 1][7] = DR

    # Stalagmit & batu menyebar
    rng = random.Random(101)
    for x, y in [(2, 2), (15, 2), (2, 11), (15, 11),
                 (3, 4), (14, 6), (5, 9), (12, 3), (7, 11), (10, 11)]:
        m[y][x] = CV_W
    # Random extra
    for _ in range(8):
        x = rng.randint(2, W_ - 3)
        y = rng.randint(2, H_ - 3)
        if m[y][x] == CV_F and abs(x - 7) > 2 and abs(y - 5) > 1:  # jaga area naga kosong
            m[y][x] = CV_W

    # Naga ditampilkan via NPC (3x2 sprite besar) di sekitar (7,5) — area dijaga kosong
    return Scene('naga_cave', 'Gua Sang Hyang Naga', m,
        portals=[(7, 13, 'outdoor', 45, 3)], indoor=True)


# ═══════════════════════════════════════════════════
#  SCENE BARU v5: KUBURAN 3 ZONA + CRYPT
# ═══════════════════════════════════════════════════
def build_cemetery_z1():
    """Kuburan zona 1 — paling depan, baru-baru, mudah.
    16×14, banyak nisan teratur, beberapa pohon mati di tepi."""
    W_, H_ = 16, 14
    m = _new_map(W_, H_, D)

    # Pagar luar dari pohon mati (visual)
    for x in range(W_): m[0][x] = DT; m[H_ - 1][x] = DT
    for y in range(H_): m[y][0] = DT; m[y][W_ - 1] = DT

    # Gerbang masuk (selatan, balik ke outdoor)
    m[H_ - 1][7] = GT
    # Gerbang utara ke zona 2
    m[0][7] = GT

    # Jalur tengah
    for y in range(1, H_ - 1):
        m[y][7] = P

    # Nisan-nisan teratur (zona pemakaman terorganisir)
    for y in [3, 5, 9, 11]:
        for x in [2, 4, 10, 12, 14]:
            if 0 <= x < W_ and 0 <= y < H_ and m[y][x] == D:
                m[y][x] = GR

    # Beberapa lentera (di malam hari ada cahaya)
    m[2][3] = LN
    m[12][3] = LN
    m[2][13] = LN
    m[12][13] = LN

    return Scene('cemetery_z1', 'Kuburan — Zona Depan', m,
        portals=[
            (7, H_ - 1, 'outdoor', 37, 25),
            (7, 0, 'cemetery_z2', 7, 13),
        ])


def build_cemetery_z2():
    """Kuburan zona 2 — menengah, lebih tua, banyak pohon mati.
    Pocong haunting di sini malam hari."""
    W_, H_ = 16, 14
    m = _new_map(W_, H_, D)
    for x in range(W_): m[0][x] = DT; m[H_ - 1][x] = DT
    for y in range(H_): m[y][0] = DT; m[y][W_ - 1] = DT
    m[H_ - 1][7] = GT
    m[0][7] = GT  # ke zona 3

    # Jalur kasar
    for y in range(1, H_ - 1):
        m[y][7] = P

    # Nisan tua tidak teratur, beberapa miring
    grave_pos = [(2, 2), (4, 3), (3, 5), (12, 2), (14, 4),
                 (11, 6), (3, 9), (5, 10), (12, 9), (13, 11),
                 (4, 12), (11, 12)]
    for x, y in grave_pos:
        if m[y][x] == D:
            m[y][x] = GR

    # Pohon mati di tengah-tengah (creepy)
    for x, y in [(3, 7), (5, 4), (12, 7), (10, 10), (6, 6)]:
        if m[y][x] == D:
            m[y][x] = DT

    # Crypt entrance (door indoor) di sini — ke crypt
    m[5][8] = DR  # pintu crypt

    return Scene('cemetery_z2', 'Kuburan — Zona Tengah', m,
        portals=[
            (7, H_ - 1, 'cemetery_z1', 7, 1),
            (7, 0, 'cemetery_z3', 7, 13),
            (8, 5, 'crypt', 7, 11),  # masuk crypt
        ])


def build_cemetery_z3():
    """Kuburan zona 3 — paling dalam, paling kuno.
    Leak Bali transforming malam-malam. Ada altar batu di tengah."""
    W_, H_ = 16, 14
    m = _new_map(W_, H_, D)
    for x in range(W_): m[0][x] = DT; m[H_ - 1][x] = DT
    for y in range(H_): m[y][0] = DT; m[y][W_ - 1] = DT
    m[H_ - 1][7] = GT  # balik ke z2

    # Altar batu di tengah (gunakan WL untuk efek batu)
    for x in range(6, 9):
        m[6][x] = CV_W
        m[7][x] = CV_W
    # Lantai depan altar
    m[8][7] = P

    # Nisan kuno terbentuk lingkaran
    circle_pos = [(3, 3), (12, 3), (3, 11), (12, 11),
                  (2, 7), (13, 7), (5, 2), (10, 2), (5, 12), (10, 12)]
    for x, y in circle_pos:
        if m[y][x] == D:
            m[y][x] = GR

    # Pohon mati banyak
    for x, y in [(4, 5), (11, 5), (4, 9), (11, 9), (3, 6), (12, 8)]:
        if m[y][x] == D:
            m[y][x] = DT

    # Lentera misterius
    m[2][2] = LN
    m[2][13] = LN

    return Scene('cemetery_z3', 'Kuburan — Zona Terdalam', m,
        portals=[
            (7, H_ - 1, 'cemetery_z2', 7, 1),
        ])


def build_crypt():
    """Crypt indoor — rumah Mbah Demit. 14×12, batu gelap."""
    W_, H_ = 14, 12
    m = _new_map(W_, H_, CRYPT_F)
    _border(m, CRYPT_W)
    m[H_ - 1][7] = DR  # keluar ke cemetery_z2

    # Sarcophagus di tengah (table sebagai surrogate)
    m[5][6] = TB; m[5][7] = TB
    m[6][6] = TB; m[6][7] = TB

    # Bookshelf kuno di sisi
    m[2][1] = BS; m[3][1] = BS
    m[2][12] = BS; m[3][12] = BS

    # Plant pot (anggrek hitam)
    m[8][2] = PP
    m[8][11] = PP

    # Lentera abadi
    m[1][3] = LN
    m[1][10] = LN

    # Chest (item misterius?)
    m[9][6] = CH

    return Scene('crypt', 'Crypt Mbah Demit', m,
        portals=[(7, 11, 'cemetery_z2', 8, 6)],
        indoor=True)


# ═══════════════════════════════════════════════════
#  SCENE BARU v5: 2 GUA TAMBAHAN
# ═══════════════════════════════════════════════════
def build_bat_cave():
    """Gua kelelawar — gelap, banyak bat dropping (lantai khusus).
    Genderuwo roaming di sini malam hari."""
    W_, H_ = 16, 14
    m = _new_map(W_, H_, CV_F)
    _border(m, CV_W)
    m[H_ - 1][7] = DR  # keluar

    # Bat dropping patches (tile khusus, walkable)
    rng = random.Random(202)
    for _ in range(18):
        x = rng.randint(2, W_ - 3)
        y = rng.randint(2, H_ - 3)
        if m[y][x] == CV_F:
            m[y][x] = BAT_D

    # Stalagmit blocking dalam pola maze ringan
    stalag = [(3, 3), (4, 3), (11, 3), (12, 3),
              (3, 10), (4, 10), (11, 10), (12, 10),
              (7, 5), (8, 5),
              (5, 7), (10, 7)]
    for x, y in stalag:
        if 0 < x < W_ - 1 and 0 < y < H_ - 1:
            m[y][x] = CV_W

    # Beberapa lentera redup
    m[1][1] = LN
    m[1][14] = LN

    return Scene('bat_cave', 'Gua Kelelawar', m,
        portals=[(7, 13, 'outdoor', 41, 3)], indoor=True)


def build_crystal_cave():
    """Gua kristal — terang dengan kristal warna.
    Banaspati floating di sini malam. Visual paling indah."""
    W_, H_ = 16, 14
    m = _new_map(W_, H_, CV_F)
    _border(m, CV_W)
    m[H_ - 1][7] = DR

    # Kristal cluster — pola lingkaran tengah + sudut
    crystal_pos = [(3, 3), (4, 3), (12, 3), (11, 3),
                   (3, 10), (4, 10), (11, 10), (12, 10),
                   (2, 6), (13, 6), (2, 8), (13, 8),
                   (7, 2), (8, 2), (7, 11), (8, 11)]
    for x, y in crystal_pos:
        if m[y][x] == CV_F:
            m[y][x] = CRYS

    # Beberapa stalagmit
    for x, y in [(5, 5), (10, 5), (5, 9), (10, 9)]:
        m[y][x] = CV_W

    # Cluster kristal di tengah (pusat ritual)
    m[6][6] = CRYS; m[6][7] = CRYS; m[6][8] = CRYS
    m[7][7] = CV_F  # spot pemain bisa berdiri di tengah

    return Scene('crystal_cave', 'Gua Kristal', m,
        portals=[(7, 13, 'outdoor', 48, 3)], indoor=True)


# ═══════════════════════════════════════════════════
#  SCENE BARU v5: DANAU
# ═══════════════════════════════════════════════════
def build_lake():
    """Danau — air terjun di utara, dermaga, perahu, eceng gondok.
    Pak Joko mancing di sini. Kuntilanak haunting di pohon mati malam."""
    W_, H_ = 24, 16
    m = _new_map(W_, H_, G)

    # Air mengisi sebagian besar map
    _fill(m, 4, 3, 16, 10, W)

    # === AIR TERJUN (utara, atas tengah) ===
    # 3 tile waterfall berdiri (vertikal di atas air)
    for x in range(10, 14):
        m[1][x] = WTF
        m[2][x] = WTF
    # Air ekstra di bawah air terjun (kolam)
    _fill(m, 9, 3, 6, 3, W)

    # === DERMAGA (sisi kiri, tempat masuk) ===
    # Dock memanjang ke air dari pinggir
    for x in range(4, 9):
        m[10][x] = DCK
    m[11][8] = DCK  # belokan
    m[11][9] = DCK
    # Spot portal masuk ke lake (player muncul di dermaga)
    # Posisi: (7, 13) — di tepi grass dekat dermaga

    # === PERAHU (di ujung dermaga) ===
    m[10][10] = BOT  # perahu kecil di air

    # === ECENG GONDOK (eceng_gondok) ===
    # Cluster bunga ungu di tepi-tepi air, walkable (tile float)
    lily_pos = [(5, 5), (6, 5), (15, 5), (16, 5),
                (5, 11), (6, 11), (15, 11), (16, 11),
                (18, 7), (18, 8), (19, 8),
                (4, 8), (5, 8)]
    for x, y in lily_pos:
        if 0 <= x < W_ and 0 <= y < H_ and m[y][x] == W:
            m[y][x] = LLY

    # === POHON DI SEKITAR DANAU ===
    # Pohon hidup di sisi tepian (kanan)
    rng = random.Random(303)
    for y in range(2, H_ - 2):
        for x in range(20, W_ - 1):
            if m[y][x] == G and rng.random() < 0.3:
                m[y][x] = TR
    # Pohon mati di pojok kiri-bawah (untuk Kuntilanak haunt malam)
    for x, y in [(2, 14), (3, 13), (1, 12), (2, 12)]:
        if m[y][x] == G:
            m[y][x] = DT

    # Path keluar ke outdoor (bagian bawah)
    for x in range(6, 10):
        m[H_ - 1][x] = P
    m[H_ - 1][7] = GT  # gerbang keluar

    # Lentera di dermaga (untuk malam)
    m[9][4] = LN
    m[9][8] = LN

    return Scene('lake', 'Danau Karsa', m,
        portals=[(7, 15, 'outdoor', 9, 21)])


# ═══════════════════════════════════════════════════
#  REGISTRY — Build & cache semua scene saat import
# ═══════════════════════════════════════════════════
SCENES = {
    'outdoor': build_outdoor(),
    'house': build_house(),
    'shop': build_shop(),
    'clinic': build_clinic(),
    'studio': build_studio(),
    'smith': build_smith(),
    'greenhouse': build_greenhouse(),
    'naga_cave': build_naga_cave(),
    # Baru v5
    'cemetery_z1': build_cemetery_z1(),
    'cemetery_z2': build_cemetery_z2(),
    'cemetery_z3': build_cemetery_z3(),
    'crypt': build_crypt(),
    'bat_cave': build_bat_cave(),
    'crystal_cave': build_crystal_cave(),
    'lake': build_lake(),
}
