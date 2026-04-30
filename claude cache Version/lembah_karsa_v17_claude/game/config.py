"""config.py — Konstanta global. V15 + dungeon/combat/craft."""

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

PLAYER_SPEED_TILES_PER_SEC = 4.5
PLAYER_RUN_MULTIPLIER = 1.7
NPC_SPEED_TILES_PER_SEC = 2.5
ANIMATION_FPS = 8
DAYS_PER_SEASON = 28
START_GOLD = 100
START_ENERGY = 100

# Combat
PLAYER_BASE_HP = 100
PLAYER_ATTACK_RANGE = 1.5
PLAYER_ATTACK_COOLDOWN_MS = 400
TOOL_DAMAGE = 5
SWORD_AUTO_ATTACK_RANGE = 2.0
SWORD_AUTO_ATTACK_COOLDOWN_MS = 600
INVULN_AFTER_HIT_MS = 600


class C:
    h0, h1, h2 = (50,30,20), (35,20,10), (70,45,30)
    s0, s1, s2 = (200,50,50), (150,30,30), (250,80,80)
    pn, pn1 = (50,50,150), (30,30,100)
    water_light, water_dark = (80,150,220), (60,120,200)
    cave_stone, cave_stone_dk, cave_floor = (90,80,95), (35,28,40), (55,45,55)
    pen_floor = (140,100,60)
    ui_bg, ui_bg2 = (20,10,35), (35,20,55)
    ui_border, ui_text = (120,80,180), (220,200,255)
    ui_gold, ui_green = (245,215,80), (127,255,127)
    ui_red, ui_cyan = (255,112,112), (127,220,255)
    ore_tembaga = (180,110,60)
    ore_besi = (140,140,160)
    ore_emas = (240,210,90)
    ore_kristal = (180,140,220)
    ore_mithril = (140,210,230)
    stairs_down = (110,80,50)
    stairs_up = (160,130,90)


# 42 tile IDs
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

WALKABLE = [G, D, P, FL, DR, GT, CV_F, STR_T, DCK, LLY, MINED, STAIRS_DOWN, STAIRS_UP]
TILLABLE = [G, D]
BLOCKING = [WL, TR, H, FN, BD, ST, TB, BS, MR, FP, CL, PP, CH, CT, SH, GR, LN, DT,
            CV_W, PEN, BOT, CRYS, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH]
MINEABLE = [CV_W, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH, CRYS]

SEASONS = ['Semi','Panas','Gugur','Dingin']
SEASON_NAMES = ["Musim Semi","Musim Panas","Musim Gugur","Musim Dingin"]
TOOLS = ['Cangkul','Siram','Tanam','Panen','Kapak','Hadiah','Pickaxe','Pedang']
