"""
scenes.py — Definisi semua peta (scenes).
Tile constants di-import dari config.
"""
import random
from .config import (G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS,
                     MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR)


class Scene:
    def __init__(self, name, display, tiles, portals=None, indoor=False):
        self.name = name
        self.display = display
        self.tiles = tiles
        self.w = len(tiles[0])
        self.h = len(tiles)
        self.portals = portals or []  # [(fx,fy,target_scene,tx,ty)]
        self.indoor = indoor


def build_outdoor():
    """Dunia luar 50×35 — kebun + desa + hutan + pasar malam + kuburan."""
    W_, H_ = 50, 35
    m = [[G]*W_ for _ in range(H_)]
    rng = random.Random(7)

    def fill(x, y, w, h, t):
        for dy in range(h):
            for dx in range(w):
                if 0 <= y+dy < H_ and 0 <= x+dx < W_:
                    m[y+dy][x+dx] = t

    def hl(y, x1, x2, t):
        for x in range(x1, x2+1):
            if 0 <= y < H_ and 0 <= x < W_: m[y][x] = t

    def vl(x, y1, y2, t):
        for y in range(y1, y2+1):
            if 0 <= y < H_ and 0 <= x < W_: m[y][x] = t

    # ═══ KEBUN PEMAIN (kiri atas) ═══
    fill(1, 1, 14, 11, D)
    fill(1, 1, 5, 4, H)  # rumah
    m[4][3] = DR
    m[2][6] = MB

    # PAGAR + GERBANG
    hl(0, 1, 15, FN); vl(0, 0, 12, FN)
    hl(12, 1, 15, FN); vl(15, 1, 12, FN)
    m[12][8] = GT  # gerbang selatan
    m[6][15] = GT  # gerbang timur

    # Kandang hewan dengan pagar — sekarang proper kandang
    fill(2, 9, 7, 4, STR)  # lantai jerami
    # Pagar kandang
    for x in range(2, 9): m[9][x] = PEN  # atas
    for x in range(2, 9): m[12][x] = PEN  # bawah (akan ada gerbang)
    for y in range(9, 13): m[y][2] = PEN  # kiri
    for y in range(9, 13): m[y][8] = PEN  # kanan
    m[12][5] = GT  # gerbang kandang (player bisa masuk)

    # Jalan utama
    hl(13, 0, W_-1, P)
    vl(18, 0, H_-1, P)
    vl(35, 0, H_-1, P)

    # ═══ SUNGAI ═══
    fill(19, 0, 4, 5, W)
    fill(22, 4, 3, 4, W)
    m[13][19] = P; m[13][20] = P; m[13][21] = P  # jembatan

    # ═══ DESA ═══
    fill(20, 1, 5, 4, H); m[4][22] = DR   # warung
    fill(27, 1, 5, 4, H); m[4][29] = DR   # klinik
    fill(34, 1, 5, 4, H); m[4][36] = DR   # studio
    fill(20, 7, 5, 4, H); m[10][22] = DR  # smith
    fill(27, 7, 5, 4, H); m[10][29] = DR  # greenhouse

    # Pohon di desa
    for x, y in [(25,2),(26,5),(33,2),(33,7),(38,3),(39,7)]:
        if m[y][x] == G: m[y][x] = TR

    # ═══ PASAR MALAM ═══
    fill(28, 16, 12, 5, P)
    for x, y in [(29,17),(31,17),(33,17),(35,17),(37,17),(39,17),
                 (29,19),(31,19),(33,19),(35,19),(37,19),(39,19)]:
        m[y][x] = LN
    fill(30, 18, 2, 1, CT)
    fill(34, 18, 2, 1, CT)
    fill(38, 18, 2, 1, CT)

    # ═══ HUTAN SELATAN ═══
    for y in range(15, H_):
        for x in range(0, 18):
            if m[y][x] == G and rng.random() < 0.18:
                m[y][x] = TR

    # Hutan dalam
    for y in range(22, H_-2):
        for x in range(0, 12):
            if m[y][x] == G and rng.random() < 0.25:
                m[y][x] = DT if rng.random() < 0.3 else TR

    # Danau
    fill(5, 18, 8, 5, W)

    # ═══ KUBURAN TUA ═══
    fill(33, 22, 8, 7, D)
    for x, y in [(34,23),(36,23),(38,23),(40,23),
                 (34,25),(36,25),(38,25),(40,25),
                 (35,27),(37,27),(39,27)]:
        if 0 <= x < W_ and 0 <= y < H_:
            m[y][x] = GR
    for x, y in [(33,22),(41,28),(33,28),(41,22)]:
        if 0 <= x < W_ and 0 <= y < H_: m[y][x] = DT

    # ═══ HUTAN TIMUR ═══
    for y in range(20, H_):
        for x in range(42, W_):
            if m[y][x] == G and rng.random() < 0.22:
                m[y][x] = TR

    # ═══ GUNUNG UTARA + GUA NAGA (atas-tengah) ═══
    # Area gunung dengan banyak batu (cave wall di outdoor sebagai dinding gunung)
    for y in range(0, 3):
        for x in range(40, 50):
            m[y][x] = CV_W
    for y in range(0, 2):
        for x in range(45, 50):
            m[y][x] = CV_W
    # Pintu gua di tengah
    m[2][45] = DR  # masuk gua naga

    return Scene('outdoor', 'Lembah Karsa', m,
        portals=[
            (3, 4, 'house', 7, 9),
            (22, 4, 'shop', 7, 9),
            (29, 4, 'clinic', 7, 9),
            (36, 4, 'studio', 7, 9),
            (22, 10, 'smith', 7, 9),
            (29, 10, 'greenhouse', 7, 9),
            (45, 2, 'naga_cave', 7, 9),  # pintu ke gua naga
        ])


def _build_indoor_room(name, display, furniture_layout, npc_outdoor_pos):
    """Helper untuk indoor scenes 15x12 dengan layout furniture."""
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL
        m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL
        m[y][W_-1] = WL
    m[H_-1][7] = DR
    for (x, y, tile) in furniture_layout:
        if 0 <= x < W_ and 0 <= y < H_:
            m[y][x] = tile
    return Scene(name, display, m,
        portals=[(7, 11, 'outdoor', npc_outdoor_pos[0], npc_outdoor_pos[1])],
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
    for x in range(1, 14): layout.append((x, 4, CT))  # counter
    for x in range(1, 14): layout.append((x, 1, SH))  # shelves
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
    m = [[D]*W_ for _ in range(H_)]
    for x in range(W_):
        m[0][x] = WL
        m[H_-1][x] = WL
    for y in range(H_):
        m[y][0] = WL
        m[y][W_-1] = WL
    m[H_-1][7] = DR
    for x in range(1, W_-1):
        m[5][x] = P
    return Scene('greenhouse', 'Rumah Kaca', m,
        portals=[(7, 11, 'outdoor', 29, 11)], indoor=True)


def build_naga_cave():
    """Gua sang naga — luas, gelap mistis, naga di tengah."""
    W_, H_ = 15, 12
    m = [[CV_F]*W_ for _ in range(H_)]
    # Wall di sekeliling
    for x in range(W_):
        m[0][x] = CV_W
        m[H_-1][x] = CV_W
    for y in range(H_):
        m[y][0] = CV_W
        m[y][W_-1] = CV_W
    # Pintu keluar
    m[H_-1][7] = DR
    # Stalagmite scattered
    for x, y in [(2, 2), (12, 2), (2, 9), (12, 9), (3, 4), (11, 6)]:
        m[y][x] = CV_W
    # Naga akan di-render di posisi 6,5 (dari schedule), 3x2 tile
    return Scene('naga_cave', 'Gua Sang Hyang', m,
        portals=[(7, 11, 'outdoor', 45, 3)], indoor=True)


# Build & cache semua scene saat module di-import
SCENES = {
    'outdoor': build_outdoor(),
    'house': build_house(),
    'shop': build_shop(),
    'clinic': build_clinic(),
    'studio': build_studio(),
    'smith': build_smith(),
    'greenhouse': build_greenhouse(),
    'naga_cave': build_naga_cave(),
}
