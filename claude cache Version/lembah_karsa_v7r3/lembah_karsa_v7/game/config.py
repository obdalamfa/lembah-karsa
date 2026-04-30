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
    # CRISP PIXEL PALETTE — RPG Maker style: warna kontras tinggi + outline hitam tegas
    OUTLINE = (15, 8, 12)  # outline universal hampir hitam
    OUTLINE_LT = (40, 25, 35)  # outline lighter
    # Rumput (lebih hidup)
    g0,g1,g2,g3 = (62,139,55),(80,168,76),(108,196,96),(38,92,40)
    # Tanah (warna lebih hangat)
    d0,d1,d2,d3 = (98,62,28),(140,90,44),(118,76,32),(76,48,18)
    # Air (lebih biru jernih)
    w0,w1,w2 = (28,88,180),(48,128,224),(120,184,248)
    # Jalan batu (kontras lebih jelas)
    p0,p1,p2 = (140,124,108),(180,164,144),(96,84,72)
    # Kayu (warna kayu hangat)
    wo0,wo1,wo2 = (138,88,36),(96,60,18),(176,128,64)
    # Atap merah (saturated)
    r0,r1,r2 = (212,56,48),(176,32,28),(248,128,108)
    # Dinding beige (lebih cerah)
    b0,b1,b2 = (224,184,128),(192,148,92),(248,216,168)
    # Kulit (kontras kepala terlihat jelas)
    sk,sk2,sk3 = (252,208,156),(232,168,112),(252,232,200)
    # Rambut (saturated)
    h0,h1,h2 = (88,36,16),(132,64,28),(48,20,8)
    # Baju (biru cerah)
    s0,s1,s2 = (52,92,184),(36,72,144),(108,148,224)
    pn,pn2 = (72,108,52),(52,80,36)
    ht,ht2 = (252,212,40),(212,172,20)
    # Tanaman (lebih segar)
    cg,cg2 = (132,232,72),(84,184,36)
    cy = (252,228,40)
    cr,co,cp = (244,60,28),(252,116,36),(200,132,244)
    # Furniture (kontras)
    fn,fn2,fn3 = (104,72,36),(68,44,20),(140,96,52)
    # UI dasar
    wt,bk,gl = (255,255,255),(16,8,8),(252,220,52)
    # Lantai indoor (kontras dengan dinding)
    fl,fl2,fl3 = (180,148,100),(164,132,84),(208,176,124)
    wl,wl2 = (216,200,168),(192,176,144)
    # Api
    fire1,fire2,fire3 = (255,72,4),(255,140,8),(255,212,12)
    # NPC clothes (warna unik per NPC, kontras)
    nc_sari,nc_raka,nc_maya,nc_budi = (220,48,68),(248,248,232),(160,40,212),(80,80,80)
    ng = (168,168,152)
    # Supernatural (warna magis kontras tinggi)
    jin_aura = (200,140,255)
    jin_skin = (220,180,250)
    demit_dark = (32,24,48)
    demit_glow = (140,48,220)
    tuyul_skin = (228,208,180)
    tuyul_red = (236,52,52)
    # Animals (lebih putih dan kontras)
    sapi_white = (248,243,228)
    sapi_brown = (118,76,44)
    ayam_white = (255,255,248)
    ayam_red = (236,48,48)
    kambing_grey = (216,216,216)
    # Wild plants
    mandrake_skin = (208,188,148)
    mushroom_red = (232,68,68)
    mushroom_white = (255,248,248)
    firefly_glow = (192,255,148)
    # Naga
    naga_body = (188, 60, 40)
    naga_body_dk = (124, 30, 20)
    naga_body_lt = (228, 104, 80)
    naga_belly = (252, 220, 104)
    naga_scale = (255, 240, 136)
    naga_horn = (255, 244, 188)
    naga_eye = (88, 232, 88)
    naga_whiskers = (255, 255, 200)  # janggut emas
    # Cave colors
    cave_stone = (60, 50, 65)
    cave_stone_lt = (90, 80, 95)
    cave_stone_dk = (35, 28, 40)
    cave_floor = (55, 45, 55)
    # Pen / stable
    pen_floor = (140, 100, 60)       # jerami
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

# Dungeon & combat tiles (v7)
MINED = 30        # tile cave_floor habis tambang (visual sedikit beda)
ORE_TBG = 31      # ore tembaga
ORE_BSI = 32      # ore besi
ORE_EMS = 33      # ore emas
ORE_KRS = 34      # ore kristal
ORE_MTH = 35      # ore mithril
STAIRS_DOWN = 36
STAIRS_UP = 37
CRYS = 38         # kristal besar (di lv 12+)
DCK = 39          # dermaga (lake)
BOT = 40          # perahu
LLY = 41          # water lily

TILE_NAMES = {
    G:'grass', D:'dirt', P:'path', W:'water', FL:'floor', WL:'wall',
    TR:'tree', H:'house', MB:'mailbox', DR:'door', FN:'fence', GT:'gate',
    BD:'bed', ST:'stove', TB:'table', BS:'bookshelf', MR:'mirror',
    FP:'fireplace', CL:'clock', PP:'plant_pot', CH:'chest',
    CT:'counter', SH:'shelf_store', GR:'grave', LN:'lantern', DT:'dead_tree',
    CV_W:'cave_wall', CV_F:'cave_floor', PEN:'pen_post', STR:'straw',
    MINED:'mined', ORE_TBG:'ore_tembaga', ORE_BSI:'ore_besi',
    ORE_EMS:'ore_emas', ORE_KRS:'ore_kristal', ORE_MTH:'ore_mithril',
    STAIRS_DOWN:'stairs_down', STAIRS_UP:'stairs_up', CRYS:'crystal',
    DCK:'dock', BOT:'boat', LLY:'water_lily',
}

WALKABLE = {G, D, P, FL, GT, CV_F, STR, MINED, STAIRS_DOWN, STAIRS_UP, DCK, LLY, DR}
TILLABLE = {G, D}
BLOCKING = {W, WL, TR, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, PEN,
            ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, CRYS}
MINEABLE = [CV_W, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, CRYS]

# ─── COMBAT (v7) ──────────────────────────────────────
PLAYER_BASE_HP = 100
PLAYER_ATTACK_RANGE = 1.5
PLAYER_ATTACK_COOLDOWN_MS = 400
TOOL_DAMAGE = 5
INVULN_AFTER_HIT_MS = 600

# ─── SEASONS ──────────────────────────────────────────
SEASONS = ['Semi','Panas','Gugur','Dingin']
SEASON_NAMES = {
    'Semi':'Musim Semi',
    'Panas':'Musim Panas',
    'Gugur':'Musim Gugur',
    'Dingin':'Musim Dingin',
}

# ─── TOOLS ────────────────────────────────────────────
TOOLS = ['Cangkul','Siram','Tanam','Panen','Kapak','Pedang','Tombak','Panah','Pickaxe','Hadiah']
# Slot 1-9 + 0 untuk hadiah. Default sword tier 0 (kayu) tidak ada → slot kosong sampai craft
# Pedang/Tombak/Panah = SPACE swing (combat)
# Pickaxe = SPACE swing (mining)
# Cangkul/Siram/Tanam/Panen/Kapak/Hadiah = SPACE use (farming)
