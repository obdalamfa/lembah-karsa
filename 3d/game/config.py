"""config.py — Konstanta global untuk Lembah Karsa 3D.
Basis dari v17, ditambah konstanta 3D untuk Ursina Engine.
"""

# ─── TILE SIZE 2D (kept for data compatibility) ──────────
TILE = 32
SPRITE = 16

# ─── 3D WORLD SCALE ──────────────────────────────────────
TILE_SIZE   = 2.0   # ukuran satu tile dalam world units (meter)
GROUND_H    = 0.20  # ketinggian lantai/tanah
WALL_H      = 2.80  # ketinggian dinding
TREE_H      = 3.60  # ketinggian pohon
HOUSE_H     = 3.20  # ketinggian bangunan rumah
OBJ_H       = 1.20  # ketinggian objek standar (furniture, pagar)
SMALL_OBJ_H = 0.70  # objek kecil (ore, batu, pot)

# ─── DISPLAY ─────────────────────────────────────────────
SCREEN_W = 1280
SCREEN_H = 720
FPS      = 60

# ─── CAMERA (RF4-style fixed-angle) ──────────────────────
CAM_HEIGHT      = 14    # lebih rendah agar terasa lebih dekat (Action-RPG)
CAM_BACK        = 18    # sedikit menjauh ke belakang agar pandangan luas
CAM_SIDE        = 0
CAM_TARGET_LIFT = 1.0   # titik fokus kamera lebih terpusat ke badan karakter
CAM_LERP        = 8.0   # kamera bergerak mengikuti lebih cepat

# ─── TIMING ──────────────────────────────────────────────
REAL_SECONDS_PER_INGAME_DAY     = 900
INGAME_MINUTES_PER_REAL_SECOND  = 1440 / REAL_SECONDS_PER_INGAME_DAY
FORCE_SLEEP_HOUR                = 23
SAVE_FILE                       = "lembah_karsa_3d_save.json"

# ─── PLAYER ──────────────────────────────────────────────
PLAYER_SPEED            = 12.0  # pergerakan dasar dipercepat
PLAYER_RUN_MULTIPLIER   = 1.85  # lari (SHIFT) menjadi sangat gesit
NPC_SPEED               = 5.0   # world-units / detik
ANIMATION_FPS           = 8
DAYS_PER_SEASON         = 28
START_GOLD              = 100
START_ENERGY            = 100

# ─── COMBAT ──────────────────────────────────────────────
PLAYER_BASE_HP              = 100
SPRINT_ENERGY_DRAIN         = 5    # energy per second while sprinting
PLAYER_ATTACK_RANGE         = 3.0   # world-units (≈1.5 tile)
PLAYER_ATTACK_COOLDOWN_MS   = 400
TOOL_DAMAGE                 = 5
SWORD_AUTO_ATTACK_RANGE     = 4.0
SWORD_AUTO_ATTACK_COOLDOWN_MS = 600
INVULN_AFTER_HIT_MS         = 600

# ─── 42 TILE IDs (identik dengan v17) ────────────────────
G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS, MR, FP, CL, PP, CH, \
CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR_T, \
DCK, BOT, LLY, CRYS, \
ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, \
STAIRS_DOWN, STAIRS_UP, MINED = range(42)

TILE_NAMES = {
    G:'grass', D:'dirt', P:'path', W:'water', FL:'floor', WL:'wall',
    TR:'tree', H:'house', MB:'mailbox', DR:'door', FN:'fence', GT:'gate',
    BD:'bed', ST:'stove', TB:'table', BS:'bookshelf', MR:'mirror',
    FP:'fireplace', CL:'clock', PP:'plant_pot', CH:'chest',
    CT:'counter', SH:'shelf_store', GR:'grave', LN:'lantern',
    DT:'dead_tree', CV_W:'cave_wall', CV_F:'cave_floor',
    PEN:'pen_post', STR_T:'straw',
    DCK:'dock', BOT:'boat', LLY:'water_lily', CRYS:'crystal',
    ORE_TBG:'ore_tembaga', ORE_BSI:'ore_besi', ORE_EMS:'ore_emas',
    ORE_KRS:'ore_kristal', ORE_MTH:'ore_mithril',
    STAIRS_DOWN:'stairs_down', STAIRS_UP:'stairs_up', MINED:'mined_floor',
}

WALKABLE  = [G, D, P, FL, DR, GT, CV_F, STR_T, DCK, LLY, MINED, STAIRS_DOWN, STAIRS_UP]
TILLABLE  = [G, D]
BLOCKING  = [WL, TR, H, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT,
             CV_W, PEN, BOT, CRYS, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, MB]
MINEABLE  = [CV_W, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, CRYS]

SEASONS      = ['Semi', 'Panas', 'Gugur', 'Dingin']
SEASON_NAMES = ['Musim Semi', 'Musim Panas', 'Musim Gugur', 'Musim Dingin']
TOOLS        = ['Cangkul', 'Siram', 'Tanam', 'Panen', 'Kapak', 'Hadiah', 'Pickaxe', 'Pedang']
