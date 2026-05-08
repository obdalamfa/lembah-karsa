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
DIAGONAL_MULT = 0.707              # 1/sqrt(2) untuk normalize diagonal

# ─── MOUSE ────────────────────────────────────────────
MOUSE_DEAD_ZONE = 12  # jarak minimal dari player ke cursor agar gerak (pixel)

# ─── PARALLAX & VISUAL ────────────────────────────────
CLOUD_SCROLL_SPEED = 8  # pixel per detik
SHADOW_ALPHA = 110
PARALLAX_BG_COLORS = {
    'morning': [(140,180,220),(180,210,240)],
    'noon':    [(120,170,210),(155,195,230)],
    'evening': [(220,140,100),(240,180,140)],
    'night':   [(20,30,60),(50,60,100)],
}

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
    # Naga (oriental Indonesia — emas + merah marun + scale)
    naga_body = (180, 60, 40)        # merah marun
    naga_body_dk = (120, 30, 20)     # shadow
    naga_body_lt = (220, 100, 80)    # highlight
    naga_belly = (245, 215, 100)     # emas
    naga_scale = (255, 235, 130)     # scale highlight
    naga_horn = (255, 240, 180)      # tanduk pucat
    naga_eye = (80, 220, 80)         # mata hijau magis
    naga_whiskers = (255, 255, 200)  # janggut emas
    # Cave colors
    cave_stone = (60, 50, 65)
    cave_stone_lt = (90, 80, 95)
    cave_stone_dk = (35, 28, 40)
    cave_floor = (55, 45, 55)
    # Pen / stable
    pen_floor = (140, 100, 60)       # jerami
    # Karakter manusia baru
    nc_joko = (90, 130, 80)          # nelayan hijau lumut
    nc_cici = (255, 180, 200)        # anak kecil pink
    nc_bowo = (140, 90, 50)          # tukang kayu coklat
    nc_ningsih = (220, 220, 240)     # bidan putih kebiruan
    nc_guru = (60, 80, 140)          # guru biru tua
    nc_mbokjum = (180, 140, 60)      # mbok jum kuning kunyit
    nc_jaka = (50, 60, 80)            # ronda gelap
    # Animal warna baru
    kucing_oren = (240, 140, 60)
    kucing_white = (255, 235, 200)
    rubah_orange = (220, 100, 40)
    rubah_white = (250, 240, 220)
    kelinci_white = (250, 245, 240)
    kelinci_pink = (255, 200, 200)
    # Hewan baru
    bebek_white = (250, 250, 240)
    bebek_yellow = (255, 220, 100)
    bebek_orange = (255, 140, 60)
    domba_white = (245, 240, 230)
    domba_dark = (90, 80, 70)
    kuda_brown = (120, 80, 50)
    kuda_dark = (70, 45, 25)
    kuda_mane = (40, 25, 15)
    # Makhluk halus baru
    kunti_white = (240, 240, 250)
    kunti_hair = (10, 10, 10)
    kunti_red = (200, 30, 30)
    pocong_white = (255, 250, 240)
    pocong_shadow = (180, 180, 170)
    genderuwo_brown = (80, 50, 30)
    genderuwo_red = (200, 50, 30)
    wewe_dark = (40, 40, 60)
    wewe_red = (220, 80, 100)
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
 CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR) = range(30)

TILE_NAMES = {
    G:'grass', D:'dirt', P:'path', W:'water', FL:'floor', WL:'wall',
    TR:'tree', H:'house', MB:'mailbox', DR:'door', FN:'fence', GT:'gate',
    BD:'bed', ST:'stove', TB:'table', BS:'bookshelf', MR:'mirror',
    FP:'fireplace', CL:'clock', PP:'plant_pot', CH:'chest',
    CT:'counter', SH:'shelf_store', GR:'grave', LN:'lantern', DT:'dead_tree',
    CV_W:'cave_wall', CV_F:'cave_floor', PEN:'pen_post', STR:'straw',
}

WALKABLE = {G, D, P, FL, GT, CV_F, STR}
TILLABLE = {G, D}
BLOCKING = {W, WL, TR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, PEN}

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
