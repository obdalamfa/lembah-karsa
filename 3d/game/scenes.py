"""
scenes.py — Definisi semua peta tile.
Identik dengan v17 — menyediakan data tile 2D untuk world.py.
Koordinat tile (tx, ty) dipetakan ke 3D: x=tx*TILE_SIZE, z=ty*TILE_SIZE.
"""
import random
from .config import (G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS,
                     MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR_T,
                     DCK, BOT, LLY, CRYS, STAIRS_DOWN, STAIRS_UP)


class Scene:
    def __init__(self, name, display, tiles, portals=None, indoor=False):
        self.name    = name
        self.display = display
        self.tiles   = tiles
        self.w       = len(tiles[0])
        self.h       = len(tiles)
        self.portals = portals or []
        self.indoor  = indoor


# ─── OUTDOOR ─────────────────────────────────────────────
def build_farm():
    W_, H_ = 25, 20
    m = [[G]*W_ for _ in range(H_)]
    for y in range(2, 12):
        for x in range(2, 10): m[y][x] = D
    for y in range(1, 5):
        for x in range(1, 6): m[y][x] = H
    m[4][3] = DR; m[2][7] = MB
    for y in range(2, 8):
        for x in range(15, 22):
            m[y][x] = STR_T
            if y in (2, 7) or x in (15, 21): m[y][x] = PEN
    m[7][18] = GT
    for x in range(W_): m[0][x] = FN; m[H_-1][x] = FN
    for y in range(H_):
        m[y][0] = FN
        m[y][W_-1] = P if 12 < y < 16 else FN
    for x in range(4, W_): m[14][x] = P; m[15][x] = P
    return Scene('farm', 'Kebun Paman Arsa', m, portals=[
        (3, 4, 'house', 7, 9),
        (24, 14, 'town', 1, 14),
        (24, 15, 'town', 1, 15),
    ])


def build_town():
    W_, H_ = 30, 25
    m = [[G]*W_ for _ in range(H_)]
    for y in range(13, 17):
        for x in range(W_): m[y][x] = P
    for y in range(H_):
        for x in range(13, 17): m[y][x] = P
    for y in range(5, 9):
        for x in range(2, 7):   m[y][x] = H
        for x in range(9, 14):  m[y][x] = H
        for x in range(20, 25): m[y][x] = H
    m[8][4] = DR; m[8][11] = DR; m[8][22] = DR
    for y in range(18, 22):
        for x in range(5, 10):  m[y][x] = H
        for x in range(19, 24): m[y][x] = H
    m[21][7] = DR; m[21][21] = DR
    m[12][12] = LN; m[12][17] = LN; m[17][12] = LN; m[17][17] = LN
    for x in range(11, 19): m[14][x] = CT
    return Scene('town', 'Desa Karsa', m, portals=[
        (0, 14, 'farm', 23, 14), (0, 15, 'farm', 23, 15),
        (14, 0, 'mountain', 14, 23), (15, 0, 'mountain', 15, 23),
        (29, 14, 'lake', 1, 7), (29, 15, 'lake', 1, 8),
        (4, 8, 'shop', 7, 9), (11, 8, 'clinic', 7, 9), (22, 8, 'studio', 7, 9),
        (7, 21, 'smith', 7, 9), (21, 21, 'greenhouse', 7, 9),
    ])


def build_mountain():
    W_, H_ = 30, 25
    m = [[G]*W_ for _ in range(H_)]
    rng = random.Random(42)
    for y in range(0, 4):
        for x in range(W_): m[y][x] = CV_W
    m[3][14] = DR; m[3][15] = DR
    for y in range(4, H_):
        for x in range(W_):
            if x < 12 or x > 18:
                if rng.random() < 0.2: m[y][x] = TR
            elif y > 10 and rng.random() < 0.1: m[y][x] = DT
    for y in range(4, H_): m[y][14] = D; m[y][15] = D
    for y in range(20, 23):
        for x in range(3, 7):
            if (x+y) % 2 == 0: m[y][x] = GR
    for y in range(20, 25): m[y][2] = P
    return Scene('mountain', 'Lereng Gunung', m, portals=[
        (14, 24, 'town', 14, 1), (15, 24, 'town', 15, 1),
        (14, 3, 'naga_cave', 7, 9), (15, 3, 'naga_cave', 7, 9),
        (2, 24, 'cemetery', 7, 1),
    ])


def build_lake():
    W_, H_ = 18, 14
    m = [[G]*W_ for _ in range(H_)]
    for y in range(2, 12):
        for x in range(3, 16): m[y][x] = W
    for x in range(3, 8): m[7][x] = DCK
    m[8][7] = DCK; m[7][9] = BOT
    for x, y in [(5,4),(12,5),(14,8),(11,10),(6,10),(13,3)]:
        if 0<=x<W_ and 0<=y<H_ and m[y][x]==W: m[y][x] = LLY
    rng = random.Random(50)
    for y in range(H_):
        for x in [0, W_-2]:
            if rng.random() < 0.4: m[y][x] = TR
    m[7][0]=P; m[8][0]=P; m[7][1]=P; m[8][1]=P
    m[12][2]=DT; m[3][3]=DT
    return Scene('lake', 'Danau Karsa', m, portals=[
        (0, 7, 'town', 28, 14), (0, 8, 'town', 28, 15),
    ])


def build_cemetery():
    W_, H_ = 18, 22
    m = [[D]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x]=DT; m[H_-1][x]=DT
    for y in range(H_): m[y][0]=DT; m[y][W_-1]=DT
    for y in range(1, H_-1): m[y][8]=P; m[y][9]=P
    for row in [3,6,9,12,15,18]:
        for col in [2,4,6,11,13,15]: m[row][col]=GR
    m[2][2]=LN; m[2][15]=LN; m[19][2]=LN; m[19][15]=LN
    m[10][3]=DT; m[14][14]=DT; m[7][12]=DT; m[16][5]=DT
    m[0][8]=GT; m[0][9]=GT
    return Scene('cemetery', 'Kuburan Tua', m, portals=[
        (8, 0, 'mountain', 2, 23), (9, 0, 'mountain', 2, 23),
    ])


# ─── INDOOR ──────────────────────────────────────────────
def _build_indoor_room(name, display, furniture, exit_portal):
    W_, H_ = 15, 12
    m = [[FL]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x]=WL; m[H_-1][x]=WL
    for y in range(H_): m[y][0]=WL; m[y][W_-1]=WL
    m[H_-1][7] = DR
    for (x, y, tile) in furniture:
        if 0<=x<W_ and 0<=y<H_: m[y][x]=tile
    return Scene(name, display, m, portals=[
        (7, 11, exit_portal[0], exit_portal[1], exit_portal[2])
    ], indoor=True)


def build_house():
    return _build_indoor_room('house', 'Rumah Kamu', [
        (1,1,BD),(2,1,BD),(1,2,CH),(4,1,BS),(5,1,BS),(1,3,MR),(1,4,PP),
        (7,1,FP),(9,1,CL),(6,3,TB),(7,3,TB),(11,1,ST),(12,1,ST),
        (11,2,SH),(12,2,SH),(13,5,PP),
    ], ('farm', 3, 5))


def build_shop():
    return _build_indoor_room('shop', 'Warung Bu Sari',
        [(x, 4, CT) for x in range(1,14)] + [(x, 1, SH) for x in range(1,14)],
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
    for x in range(W_): m[0][x]=WL; m[H_-1][x]=WL
    for y in range(H_): m[y][0]=WL; m[y][W_-1]=WL
    m[H_-1][7] = DR
    for x in range(1, W_-1): m[5][x] = P
    return Scene('greenhouse', 'Rumah Kaca', m,
                 portals=[(7, 11, 'town', 21, 22)], indoor=True)


def build_naga_cave():
    W_, H_ = 15, 12
    m = [[CV_F]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x]=CV_W; m[H_-1][x]=CV_W
    for y in range(H_): m[y][0]=CV_W; m[y][W_-1]=CV_W
    m[H_-1][7] = DR
    for x, y in [(2,2),(12,2),(2,9),(12,9),(3,4),(11,6)]:
        m[y][x] = CV_W
    m[10][13] = STAIRS_DOWN
    return Scene('naga_cave', 'Gua Sang Hyang', m, portals=[
        (7, 11, 'mountain', 14, 4),
    ], indoor=True)


def build_dungeon_placeholder():
    W_, H_ = 24, 18
    m = [[CV_F]*W_ for _ in range(H_)]
    for x in range(W_): m[0][x]=CV_W; m[H_-1][x]=CV_W
    for y in range(H_): m[y][0]=CV_W; m[y][W_-1]=CV_W
    return Scene('dungeon', 'Gua Bertingkat', m, portals=[], indoor=True)


SCENES = {
    'farm':       build_farm(),
    'town':       build_town(),
    'mountain':   build_mountain(),
    'lake':       build_lake(),
    'cemetery':   build_cemetery(),
    'house':      build_house(),
    'shop':       build_shop(),
    'clinic':     build_clinic(),
    'studio':     build_studio(),
    'smith':      build_smith(),
    'greenhouse': build_greenhouse(),
    'naga_cave':  build_naga_cave(),
    'dungeon':    build_dungeon_placeholder(),
}
