"""
config.py — Semua konstanta global di sini.
"""

# ─── DISPLAY & WAKTU ──────────────────────────────────
TILE = 32             
SPRITE = 16           
VIEW_W = 22           
VIEW_H = 14           
SCREEN_W = VIEW_W * TILE
SCREEN_H = VIEW_H * TILE + 96
FPS = 60              

REAL_SECONDS_PER_INGAME_DAY = 900
INGAME_MINUTES_PER_REAL_SECOND = 1440 / REAL_SECONDS_PER_INGAME_DAY  
FORCE_SLEEP_HOUR = 23

SAVE_FILE = "lembah_karsa_save.json"

# ─── MOVEMENT & GAMEPLAY ──────────────────────────────
PLAYER_SPEED_TILES_PER_SEC = 4.5  
PLAYER_RUN_MULTIPLIER = 1.7       
NPC_SPEED_TILES_PER_SEC = 2.5
ANIMATION_FPS = 8                  
DAYS_PER_SEASON = 28
START_GOLD = 100
START_ENERGY = 100

# ─── PALETTE WARNA (UI & SCENE) ───────────────────────
class C:
    h0, h1, h2 = (50, 30, 20), (35, 20, 10), (70, 45, 30)
    s0, s1, s2 = (200, 50, 50), (150, 30, 30), (250, 80, 80)
    pn, pn1 = (50, 50, 150), (30, 30, 100)
    water_light, water_dark = (80, 150, 220), (60, 120, 200)
    cave_stone, cave_stone_dk, cave_floor = (90, 80, 95), (35, 28, 40), (55, 45, 55)
    pen_floor = (140, 100, 60)       
    ui_bg, ui_bg2 = (20,10,35), (35,20,55)
    ui_border, ui_text = (120,80,180), (220,200,255)
    ui_gold, ui_green = (245,215,80), (127,255,127)
    ui_red, ui_cyan = (255,112,112), (127,220,255)

# ─── TILE IDs & LISTS ─────────────────────────────────
(G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS, MR, FP, CL, PP, CH,
 CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR) = range(30)

TILE_NAMES = {
    G:'grass', D:'dirt', P:'path', W:'water', FL:'floor', WL:'wall',
    TR:'tree', H:'house', MB:'mailbox', DR:'door', FN:'fence', GT:'gate',
    BD:'bed', ST:'stove', TB:'table', BS:'bookshelf', MR:'mirror',
    FP:'fireplace', CL:'clock', PP:'plant_pot', CH:'chest',
    CT:'counter', SH:'shelf_store', GR:'grave', LN:'lantern', 
    DT:'dead_tree', CV_W:'cave_wall', CV_F:'cave_floor', 
    PEN:'pen_post', STR:'straw'
}

WALKABLE = [G, D, P, FL, DR, GT, CV_F, STR]
TILLABLE = [G, D]
BLOCKING = [WL, TR, H, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT, CV_W, PEN]
SEASONS = ['Semi', 'Panas', 'Gugur', 'Dingin']
SEASON_NAMES = ["Musim Semi", "Musim Panas", "Musim Gugur", "Musim Dingin"]
TOOLS = ['Cangkul', 'Siram', 'Tanam', 'Panen', 'Kapak', 'Hadiah']
