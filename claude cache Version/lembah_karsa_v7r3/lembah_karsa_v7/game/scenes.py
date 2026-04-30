"""
scenes.py — Definisi semua peta.
V15 base: farm, town, mountain, house, shop, clinic, studio, smith, greenhouse, naga_cave.
v6 baru: lake, cemetery (outdoor); dungeon di-generate procedurally (lihat dungeon.py).
"""
import random
from .config import (G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS,
                     MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR,
                     DCK, BOT, LLY, CRYS, STAIRS_DOWN, STAIRS_UP)


class Scene:
    def __init__(self, name, display, tiles, portals=None, indoor=False):
        self.name = name
        self.display = display
        self.tiles = tiles
        self.w = len(tiles[0])
        self.h = len(tiles)
        self.portals = portals or []
        self.indoor = indoor


# ─── 3 OUTDOOR DASAR (v7r3 — open world expanded) ─────────────
def build_farm():
    """Kebun Paman Arsa — open world 40x30: rumah, kandang besar, kebun luas, sungai kecil."""
    W_, H_ = 40, 30
    m = [[G]*W_ for _ in range(H_)]

    # ─── Pagar luar ───
    for x in range(W_): m[0][x] = FN; m[H_-1][x] = FN
    for y in range(H_): m[y][0] = FN; m[y][W_-1] = FN
    # Pintu keluar utara→mountain, timur→town, barat→lake
    m[0][20] = GT; m[0][21] = GT
    for y in (15, 16): m[y][W_-1] = P
    for y in (18, 19): m[y][0] = P

    # ─── Lahan farmable utama (kiri) ───
    for y in range(3, 13):
        for x in range(2, 14): m[y][x] = D

    # ─── Rumah utama dengan halaman ───
    for y in range(2, 7):
        for x in range(16, 22): m[y][x] = H
    m[6][18] = DR
    m[2][24] = MB  # mailbox di samping rumah

    # ─── Kandang ternak (kanan-atas, lebih besar) ───
    for y in range(3, 11):
        for x in range(28, 38):
            m[y][x] = STR
            if y in (3, 10) or x in (28, 37): m[y][x] = PEN
    m[10][33] = GT

    # ─── Sungai kecil ke arah lake (estetik) ───
    for x in range(0, 8):
        m[22][x] = W; m[23][x] = W
    # Jembatan
    m[22][6] = P; m[23][6] = P

    # ─── Pohon scattered & landmark ───
    tree_spots = [(15, 13),(16, 14),(20, 15),(28, 17),(35, 19),(33, 23),(8, 25),
                  (25, 25),(32, 27),(20, 24),(38, 14),(2, 14),(2, 15)]
    for x, y in tree_spots:
        if 0 < x < W_-1 and 0 < y < H_-1 and m[y][x] == G:
            m[y][x] = TR

    # ─── Tugu kecil di tengah farm (landmark) ───
    m[18][20] = LN  # lentera tengah
    m[18][19] = PP; m[18][21] = PP  # tanaman hias

    # ─── Jalan utama farm ───
    for x in range(0, 28): m[15][x] = P; m[16][x] = P
    for y in range(7, 30): m[y][22] = P; m[y][23] = P  # jalan vertical
    # Cabang jalan ke kandang
    for x in range(22, 28): m[8][x] = P

    return Scene('farm', 'Kebun Paman Arsa', m, portals=[
        (18, 6, 'house', 7, 9),
        (W_-1, 15, 'town', 1, 14),
        (W_-1, 16, 'town', 1, 15),
        (0, 18, 'lake', 23, 7),
        (0, 19, 'lake', 23, 8),
        (20, 0, 'mountain', 20, H_-2),
        (21, 0, 'mountain', 21, H_-2),
    ])


def build_town():
    """Desa Karsa — open world 45x35: alun-alun, 6 bangunan, pasar, sekolah, tugu."""
    W_, H_ = 45, 35
    m = [[G]*W_ for _ in range(H_)]
    # ─── Pagar luar ───
    for x in range(W_): m[0][x] = FN; m[H_-1][x] = FN
    for y in range(H_): m[y][0] = FN; m[y][W_-1] = FN
    # Pintu: barat→farm, utara→mountain, timur→lake, selatan→cemetery
    for y in (16, 17): m[y][0] = P
    for x in (20, 21): m[0][x] = GT
    for y in (18, 19): m[y][W_-1] = P
    for x in (22, 23): m[H_-1][x] = GT

    # ─── Jalan utama berpotongan (lebar) ───
    for y in range(15, 20):
        for x in range(W_): m[y][x] = P
    for y in range(H_):
        for x in range(20, 25): m[y][x] = P

    # ─── BANGUNAN UTARA: Warung Sari (kiri), Klinik (tengah), Studio Maya (kanan) ───
    for y in range(4, 11):
        for x in range(3, 11): m[y][x] = H      # Warung
        for x in range(14, 22): m[y][x] = H     # Klinik
        for x in range(28, 36): m[y][x] = H     # Studio
    m[10][6] = DR; m[10][17] = DR; m[10][32] = DR
    # Atap merah ditandai dengan SH untuk display
    for x in range(36, 42):
        for y in range(5, 9): m[y][x] = H       # Sekolah (Pak Guru)
    m[9][39] = DR

    # ─── BANGUNAN SELATAN: Smith (kiri), Pasar (tengah), Greenhouse (kanan) ───
    for y in range(24, 31):
        for x in range(5, 13): m[y][x] = H      # Smith Budi
        for x in range(28, 36): m[y][x] = H     # Greenhouse
    m[24][8] = DR; m[24][32] = DR

    # ─── ALUN-ALUN tengah: pasar malam + tugu ───
    # Lentera 4 sudut
    for x, y in [(18, 13),(26, 13),(18, 21),(26, 21)]: m[y][x] = LN
    # Counter pasar (tengah)
    for x in range(20, 25): m[14][x] = CT; m[20][x] = CT
    # Tugu di pusat (PP = plant pot sebagai landmark monumen)
    m[17][22] = PP; m[18][22] = LN  # tugu lentera tinggi

    # ─── Pohon-pohon dekorasi ───
    deco_trees = [(2, 2),(13, 2),(25, 2),(38, 2),(2, 22),(13, 23),(38, 24),(2, 32),
                  (13, 32),(38, 32),(38, 14),(2, 14),(36, 22)]
    for x, y in deco_trees:
        if 0 < x < W_-1 and 0 < y < H_-1 and m[y][x] == G:
            m[y][x] = TR

    return Scene('town', 'Desa Karsa', m, portals=[
        (0, 16, 'farm', W_-2, 15),
        (0, 17, 'farm', W_-2, 16),
        (20, 0, 'mountain', 14, H_-2),
        (21, 0, 'mountain', 15, H_-2),
        (W_-1, 18, 'lake', 1, 7),
        (W_-1, 19, 'lake', 1, 8),
        (22, H_-1, 'cemetery', 8, 1),
        (23, H_-1, 'cemetery', 9, 1),
        # Building entries
        (6, 10, 'shop', 7, 9),
        (17, 10, 'clinic', 7, 9),
        (32, 10, 'studio', 7, 9),
        (39, 9, 'studio', 7, 9),  # sekolah pakai studio sebagai placeholder
        (8, 24, 'smith', 7, 9),
        (32, 24, 'greenhouse', 7, 9),
    ])


def build_mountain():
    """Lereng Gunung — open world 40x35: hutan rimbun + entrance gua naga + landmark."""
    W_, H_ = 40, 35
    m = [[G]*W_ for _ in range(H_)]
    # ─── Border ───
    for x in range(W_): m[0][x] = TR; m[H_-1][x] = TR
    for y in range(H_): m[y][0] = TR; m[y][W_-1] = TR
    # Pintu keluar selatan→town
    m[H_-1][14] = P; m[H_-1][15] = P
    m[H_-2][14] = G; m[H_-2][15] = G

    # ─── Hutan rimbun (banyak pohon) ───
    import random as _r
    rng = _r.Random(42)
    for _ in range(80):
        x = rng.randint(2, W_-3); y = rng.randint(2, H_-3)
        if m[y][x] == G:
            m[y][x] = TR

    # ─── Pohon mati (zone supernatural) ───
    for x, y in [(8, 8),(10, 6),(7, 9),(28, 25),(30, 27)]:
        m[y][x] = DT

    # ─── Sungai mengalir ───
    for x in range(0, 8): m[18][x] = W; m[19][x] = W
    m[18][6] = P; m[19][6] = P  # jembatan

    # ─── Gua entrance (dengan tile khusus) ───
    for y in range(3, 7):
        for x in range(W_-7, W_-3): m[y][x] = CV_W
    m[6][W_-5] = DR  # pintu gua
    # Pohon mati di sekitar gua (atmosphere)
    for x, y in [(W_-9, 5),(W_-9, 7),(W_-2, 4)]:
        if m[y][x] == G: m[y][x] = DT

    # ─── Jalan setapak utama (panjang, berliku) ───
    for y in range(H_-2, 25, -1): m[y][14] = P; m[y][15] = P
    for x in range(15, 28): m[24][x] = P; m[25][x] = P
    for y in range(24, 7, -1): m[y][27] = P; m[y][28] = P
    for x in range(27, W_-3): m[7][x] = P; m[7][x] = P
    # Junction: Tugu di puncak
    m[7][26] = LN
    m[24][16] = LN
    m[15][14] = PP

    # ─── Goa cemetery (kuburan tua) ───
    for x, y in [(5, 28),(6, 28),(7, 29)]:
        m[y][x] = GR

    return Scene('mountain', 'Lereng Gunung Karsa', m, portals=[
        (14, H_-1, 'town', 20, 1),
        (15, H_-1, 'town', 21, 1),
        (W_-5, 6, 'naga_cave', 7, 11),
        (5, 28, 'cemetery', 8, 1),
    ])


def build_lake():
    """Danau dengan dermaga, perahu, eceng gondok."""
    W_, H_ = 18, 14
    m = [[G]*W_ for _ in range(H_)]
    # Air mengisi sebagian besar
    for y in range(2, 12):
        for x in range(3, 16): m[y][x] = W
    # Dock dari kiri
    for x in range(3, 8): m[7][x] = DCK
    m[8][7] = DCK
    # Perahu di ujung dock
    m[7][9] = BOT
    # Eceng gondok scattered
    for x, y in [(5, 4), (12, 5), (14, 8), (11, 10), (6, 10), (13, 3)]:
        if 0 <= x < W_ and 0 <= y < H_ and m[y][x] == W:
            m[y][x] = LLY
    # Pohon tepi
    rng = random.Random(50)
    for y in range(H_):
        for x in [0, W_-2]:
            if rng.random() < 0.4:
                m[y][x] = TR
    # Path keluar (ke town)
    m[7][0] = P; m[8][0] = P; m[7][1] = P; m[8][1] = P
    # Pohon mati (ambient kuntilanak)
    m[12][2] = DT; m[3][3] = DT
    return Scene('lake', 'Danau Karsa', m, portals=[
        (0, 7, 'town', 28, 14),
        (0, 8, 'town', 28, 15),
    ])


def build_cemetery():
    """Kuburan — banyak nisan, pohon mati, lentera."""
    W_, H_ = 18, 22
    m = [[D]*W_ for _ in range(H_)]
    # Pagar kayu mati
    for x in range(W_): m[0][x] = DT; m[H_-1][x] = DT
    for y in range(H_): m[y][0] = DT; m[y][W_-1] = DT
    # Path tengah
    for y in range(1, H_-1): m[y][8] = P; m[y][9] = P
    # Nisan-nisan
    for row in [3, 6, 9, 12, 15, 18]:
        for col in [2, 4, 6, 11, 13, 15]:
            m[row][col] = GR
    # Lentera
    m[2][2] = LN; m[2][15] = LN; m[19][2] = LN; m[19][15] = LN
    # Pohon mati ambient
    m[10][3] = DT; m[14][14] = DT; m[7][12] = DT; m[16][5] = DT
    # Gerbang keluar (atas, ke mountain)
    m[0][8] = GT; m[0][9] = GT
    return Scene('cemetery', 'Kuburan Tua', m, portals=[
        (8, 0, 'mountain', 2, 23),
        (9, 0, 'mountain', 2, 23),
    ])


# ─── INDOOR ROOMS ─────────────────────────────────────
def _build_indoor_room(name, display, furniture, exit_portal):
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_): m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    for (x, y, tile) in furniture:
        if 0 <= x < W_ and 0 <= y < H_: m[y][x] = tile
    return Scene(name, display, m, portals=[
        (7, 11, exit_portal[0], exit_portal[1], exit_portal[2])
    ], indoor=True)


def build_house():
    """Rumah kamu dengan jalan rahasia ke basement (tile STAIRS_DOWN tersembunyi di pojok)."""
    house = _build_indoor_room('house', 'Rumah Kamu', [
        (1,1,BD),(2,1,BD),(1,2,CH),(4,1,BS),(5,1,BS),(1,3,MR),(1,4,PP),
        (7,1,FP),(9,1,CL),(6,3,TB),(7,3,TB),(11,1,ST),(12,1,ST),
        (11,2,SH),(12,2,SH),(13,5,PP),
    ], ('farm', 3, 5))
    # Jalan rahasia: STAIRS_DOWN di pojok di balik rak buku
    house.tiles[6][13] = STAIRS_DOWN  # tile bawah-kanan
    house.portals.append((13, 6, 'basement', 7, 5))
    return house


def build_basement():
    """Basement rahasia rumah — penyimpanan berharga + STAIRS_UP."""
    W_, H_ = 14, 10
    m = [[FL] * W_ for _ in range(H_)]
    for x in range(W_): m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_): m[y][0] = WL; m[y][W_-1] = WL
    # Furnitur: peti harta, rak rahasia, perapian
    for x, y, t in [(2, 2, CH), (3, 2, CH), (10, 2, BS), (11, 2, BS),
                    (6, 7, FP), (1, 7, TB), (12, 7, MR)]:
        m[y][x] = t
    # STAIRS_UP kembali ke house
    m[5][7] = STAIRS_UP
    return Scene('basement', 'Basement Rahasia', m,
                 portals=[(7, 5, 'house', 13, 5)], indoor=True)


def build_shop():
    return _build_indoor_room('shop', 'Warung Bu Sari',
        [(x, 4, CT) for x in range(1, 14)] + [(x, 1, SH) for x in range(1, 14)],
        ('town', 4, 9))


def build_clinic():
    return _build_indoor_room('clinic', 'Klinik Pak Raka', [
        (1,1,BD),(2,1,BD),(12,1,BD),(13,1,BD),(1,3,TB),(13,3,BS),
    ], ('town', 11, 9))


def build_studio():
    return _build_indoor_room('studio', 'Studio Maya', [
        (6,1,TB),(7,1,TB),(8,1,TB),(1,3,BS),(2,3,BS),
    ], ('town', 22, 9))


def build_smith():
    return _build_indoor_room('smith', 'Bengkel Budi', [
        (6,1,TB),(1,2,SH),(12,1,FP),(8,1,SH),(9,1,SH),
    ], ('town', 7, 22))


def build_greenhouse():
    W_, H_ = 15, 12
    m = [[D]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x] = WL; m[H_-1][x] = WL
    for y in range(H_): m[y][0] = WL; m[y][W_-1] = WL
    m[H_-1][7] = DR
    for x in range(1, W_-1): m[5][x] = P
    return Scene('greenhouse', 'Rumah Kaca', m,
        portals=[(7, 11, 'town', 21, 22)], indoor=True)


def build_naga_cave():
    """Gua Sang Hyang Naga — entrance ke dungeon roguelike di sini.
    Naga tidur di sini SEBELUM dikalahkan. Setelah kalah,
    yang ada adalah air mancur keabadian."""
    W_, H_ = 15, 12
    m = [[CV_F]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x] = CV_W; m[H_-1][x] = CV_W
    for y in range(H_): m[y][0] = CV_W; m[y][W_-1] = CV_W
    m[H_-1][7] = DR  # keluar ke mountain
    # Stalagmit
    for x, y in [(2, 2), (12, 2), (2, 9), (12, 9), (3, 4), (11, 6)]:
        m[y][x] = CV_W
    # STAIRS DOWN ke dungeon level 1 (di ujung kanan-bawah)
    m[10][13] = STAIRS_DOWN
    return Scene('naga_cave', 'Gua Sang Hyang', m, portals=[
        (7, 11, 'mountain', 14, 4),
    ], indoor=True)


# Dungeon scene placeholder — di-generate procedurally di dungeon.py
def build_dungeon_placeholder():
    """Placeholder. Saat player turun via STAIRS_DOWN, dungeon.py
    akan generate ulang scene 'dungeon' dengan random layout."""
    W_, H_ = 24, 18
    m = [[CV_F]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x] = CV_W; m[H_-1][x] = CV_W
    for y in range(H_): m[y][0] = CV_W; m[y][W_-1] = CV_W
    return Scene('dungeon', 'Gua Bertingkat', m, portals=[], indoor=True)


SCENES = {
    'farm': build_farm(),
    'town': build_town(),
    'mountain': build_mountain(),
    'lake': build_lake(),
    'cemetery': build_cemetery(),
    'house': build_house(),
    'basement': build_basement(),
    'shop': build_shop(),
    'clinic': build_clinic(),
    'studio': build_studio(),
    'smith': build_smith(),
    'greenhouse': build_greenhouse(),
    'naga_cave': build_naga_cave(),
    'dungeon': build_dungeon_placeholder(),
}
