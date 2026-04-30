"""
config.py — Semua konstanta global di sini.
Edit nilai di sini untuk tweaking game.
"""

# ─── DISPLAY ──────────────────────────────────────────
TILE = 32             # ukuran tile di layar (pixel)
SPRITE = 16           # ukuran sprite asli (pixel art 16x16)
VIEW_W = 22           # viewport lebar (tile)
VIEW_H = 14           # viewport tinggi (tile)
SCREEN_W = VIEW_W * TILE
SCREEN_H = VIEW_H * TILE + 96
FPS = 60              # 60 FPS untuk smooth movement

# ─── WAKTU ────────────────────────────────────────────
# 1 hari in-game = 15 menit real time
REAL_SECONDS_PER_INGAME_DAY = 900
INGAME_MINUTES_PER_REAL_SECOND = 1440 / REAL_SECONDS_PER_INGAME_DAY  # 1.6
FORCE_SLEEP_HOUR = 23

# ─── SAVE ─────────────────────────────────────────────
SAVE_FILE = "lembah_karsa_save.json"

# ─── MOVEMENT ─────────────────────────────────────────
PLAYER_SPEED_TILES_PER_SEC = 4.5  # smooth movement, 4.5 tile/detik
PLAYER_RUN_MULTIPLIER = 1.7       # tahan SHIFT untuk lari
NPC_SPEED_TILES_PER_SEC = 2.5
ANIMATION_FPS = 8                  # animasi sprite 8 fps

# ─── GAMEPLAY ─────────────────────────────────────────
DAYS_PER_SEASON = 28
START_GOLD = 100
START_ENERGY = 100

# ─── PALETTE (dipakai di banyak tempat) ──────────────
class C:
    # Rumput
    g0,g1,g2,g3 = (45,107,48),(61,138,64),(77,160,80),(30,72,32)
    # Tanah
    d0,d1,d2,d3 = (90,58,24),(122,82,40),(106,72,32),(74,48,16)
    # Air
    w0,w1,w2 = (24,72,168),(32,104,208),(96,160,240)
    # Jalan batu
    p0,p1,p2 = (128,112,96),(160,144,128),(96,88,72)
    # Kayu
    wo0,wo1,wo2 = (122,80,32),(90,56,16),(154,112,56)
    # Atap merah
    r0,r1,r2 = (192,56,48),(160,32,32),(224,112,96)
    # Dinding beige
    b0,b1,b2 = (208,168,112),(184,136,80),(232,200,152)
    # Kulit
    sk,sk2,sk3 = (248,200,144),(224,160,104),(248,224,192)
    # Rambut
    h0,h1,h2 = (96,40,16),(128,64,32),(58,24,8)
    # Baju
    s0,s1,s2 = (48,80,160),(32,64,128),(96,128,200)
    pn,pn2 = (64,96,48),(48,72,32)
    ht,ht2 = (248,208,32),(208,168,16)
    # Tanaman
    cg,cg2 = (128,224,64),(80,176,32)
    cy = (248,224,32)
    cr,co,cp = (240,56,24),(248,112,32),(192,128,240)
    # Furniture
    fn,fn2,fn3 = (96,64,32),(64,40,16),(128,88,48)
    # UI dasar
    wt,bk,gl = (255,255,255),(16,8,8),(248,216,48)
    # Lantai indoor
    fl,fl2,fl3 = (176,144,96),(160,128,80),(200,168,112)
    wl,wl2 = (200,184,152),(184,168,136)
    # Api
    fire1,fire2,fire3 = (255,68,0),(255,136,0),(255,204,0)
    # NPC clothes
    nc_sari,nc_raka,nc_maya,nc_budi = (192,40,64),(240,240,224),(144,32,192),(72,72,72)
    ng = (160,160,144)
    # Supernatural
    jin_aura = (180,120,255)
    jin_skin = (200,160,240)
    demit_dark = (40,30,60)
    demit_glow = (120,40,200)
    tuyul_skin = (220,200,170)
    tuyul_red = (220,40,40)
    # Animals
    sapi_white = (240,235,220)
    sapi_brown = (110,70,40)
    ayam_white = (250,250,240)
    ayam_red = (220,40,40)
    kambing_grey = (200,200,200)
    # Wild plants
    mandrake_skin = (200,180,140)
    mushroom_red = (220,60,60)
    mushroom_white = (250,240,240)
    firefly_glow = (180,255,140)
    # UI
    ui_bg = (20,10,35)
    ui_bg2 = (35,20,55)
    ui_border = (120,80,180)
    ui_text = (220,200,255)
    ui_gold = (245,215,80)
    ui_green = (127,255,127)
    ui_red = (255,112,112)
    ui_cyan = (127,220,255)

# ─── TILE IDs ─────────────────────────────────────────
(G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS, MR, FP, CL, PP, CH,
 CT, SH, GR, LN, DT) = range(26)

TILE_NAMES = {
    G:'grass', D:'dirt', P:'path', W:'water', FL:'floor', WL:'wall',
    TR:'tree', H:'house', MB:'mailbox', DR:'door', FN:'fence', GT:'gate',
    BD:'bed', ST:'stove', TB:'table', BS:'bookshelf', MR:'mirror',
    FP:'fireplace', CL:'clock', PP:'plant_pot', CH:'chest',
    CT:'counter', SH:'shelf_store', GR:'grave', LN:'lantern', DT:'dead_tree',
}

WALKABLE = {G, D, P, FL, GT}
TILLABLE = {G, D}
BLOCKING = {W, WL, TR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT}

# ─── SEASONS ──────────────────────────────────────────
SEASONS = ['Semi','Panas','Gugur','Dingin']
SEASON_NAMES = {
    'Semi':'Musim Semi',
    'Panas':'Musim Panas',
    'Gugur':'Musim Gugur',
    'Dingin':'Musim Dingin',
}

# ─── TOOLS ────────────────────────────────────────────
TOOLS = ['Cangkul','Siram','Tanam','Panen','Kapak','Hadiah']
