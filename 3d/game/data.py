"""
data.py — Tanaman, 31 NPC, dialog, schedule, quest, dungeon, combat, crafting.
Identik dengan v17 — tidak ada perubahan (pure data, bebas dari rendering).
"""

CROPS = {
    'lobak':    {'name':'Lobak','days':2,'sell':22,'cost':5,'seasons':['Semi']},
    'wortel':   {'name':'Wortel','days':3,'sell':35,'cost':8,'seasons':['Semi','Gugur']},
    'stroberi': {'name':'Stroberi','days':4,'sell':55,'cost':12,'seasons':['Semi']},
    'jagung':   {'name':'Jagung','days':4,'sell':48,'cost':10,'seasons':['Panas']},
    'tomat':    {'name':'Tomat','days':5,'sell':65,'cost':14,'seasons':['Panas']},
    'labu':     {'name':'Labu','days':5,'sell':70,'cost':15,'seasons':['Gugur']},
    'bayam':    {'name':'Bayam','days':2,'sell':30,'cost':7,'seasons':['Dingin']},
    'jamur':    {'name':'Jamur','days':3,'sell':55,'cost':12,'seasons':['Dingin']},
}

# ─── CONSUMABLES (python-2d-game buff_effects.py pattern) ────────────────────
# Registry: item_name → {heal_hp, heal_energy, buff, buff_ms, desc}
# Tiga phase lifecycle buff: start (apply), middle (tick), end (revert)
CONSUMABLES = {
    'lobak':     {'heal_hp': 8,  'heal_energy': 5,  'desc': '+8 HP, +5 EN'},
    'wortel':    {'heal_hp': 14, 'heal_energy': 8,  'desc': '+14 HP, +8 EN'},
    'stroberi':  {'heal_hp': 20, 'heal_energy': 12, 'desc': '+20 HP, +12 EN'},
    'jagung':    {'heal_hp': 10, 'heal_energy': 20, 'desc': '+10 HP, +20 EN'},
    'tomat':     {'heal_hp': 16, 'heal_energy': 10, 'desc': '+16 HP, +10 EN'},
    'labu':      {'heal_hp': 28, 'heal_energy': 18, 'desc': '+28 HP, +18 EN'},
    'bayam':     {'heal_hp': 10, 'heal_energy': 28, 'desc': '+10 HP, +28 EN'},
    'jamur':     {'heal_hp': 25, 'heal_energy': 15, 'desc': '+25 HP, +15 EN'},
    # Wild items: efek buff tambahan (start-effect + middle-effect)
    'wild_herb': {'heal_hp': 18, 'heal_energy': 10,
                  'buff': 'regen', 'buff_ms': 12000,
                  'desc': '+18 HP +10 EN, Regen 12 detik'},
    'wild_berry':{'heal_hp': 12, 'heal_energy': 8,
                  'desc': '+12 HP, +8 EN'},
    'mandrake':  {'heal_hp': 60, 'heal_energy': 40,
                  'buff': 'strength', 'buff_ms': 20000,
                  'desc': '+60 HP, +40 EN, Kuat 20 detik!'},
}

WILD_ITEMS = {
    'mandrake':         {'name':'Mandrake','sell':80,'description':'Akar ajaib','dangerous':True},
    'running_mushroom': {'name':'Jamur Lari','sell':45,'description':'Berlari saat didekati'},
    'firefly':          {'name':'Kunang-kunang','sell':25,'description':'Hanya muncul malam'},
    'wild_herb':        {'name':'Herba Liar','sell':15,'description':'Tanaman obat hutan'},
    'wild_berry':       {'name':'Beri Liar','sell':20,'description':'Beri manis'},
    'air_keabadian':    {'name':'Air Keabadian','sell':500,'description':'Air ruqyah dari naga'},
}

HUMAN_NPCS = {
    'arya':       {'name':'Arya','type':'human','gift':'jagung',
        'talks':[["Pagi! Hutan utara selalu sejuk."],["Cek tanamanmu, kawan."]],
        'gift_r':"Wah, makasih!"},
    'sari':       {'name':'Bu Sari','type':'human','gift':'tomat',
        'talks':[["Halo nak, mau beli benih?"],["Mampir ke warung."]],
        'gift_r':"Pas untuk masak!"},
    'raka':       {'name':'Pak Raka','type':'human','gift':'wild_herb',
        'talks':[["Jangan terlalu lelah bertani."],["Kesehatanku menurun."]],
        'gift_r':"Herba bagus."},
    'maya':       {'name':'Maya','type':'human','gift':'stroberi',
        'talks':[["Aku cari inspirasi lukisan."],["Lembah Karsa indah."]],
        'gift_r':"Warnanya menginspirasi!"},
    'budi':       {'name':'Budi','type':'human','gift':'lobak',
        'talks':[["Besinya panas!"],
                 ["Bawakan mineral, kubuatkan pickaxe atau pedang."],
                 ["Pickaxe kayu: 50G + 5 kayu."],
                 ["Pedang kayu: 80G + 8 kayu untuk lawan mob gua."]],
        'gift_r':"Cemilan."},
    'joko':       {'name':'Pak Joko','type':'human','gift':'wild_berry',
        'talks':[["Pagi enak mancing."],["Ikan terbesar..."]],
        'gift_r':"Mantap!"},
    'cici':       {'name':'Cici','type':'human','gift':'stroberi',
        'talks':[["Hihi, mau main?"],["Mama bilang jangan ke kuburan malam."]],
        'gift_r':"Yeyy!"},
    'bowo':       {'name':'Bowo','type':'human','gift':'labu',
        'talks':[["Aku mau jadi petani hebat!"],["Cici cerewet."]],
        'gift_r':"Untuk halloween!"},
    'ningsih':    {'name':'Bu Ningsih','type':'human','gift':'bayam',
        'talks':[["Anak-anak bikin pusing."],["Sisakan sayuran."]],
        'gift_r':"Sehat!"},
    'pak_guru':   {'name':'Pak Guru','type':'human','gift':'lobak',
        'talks':[["Pendidikan kunci kemajuan."],["Murid-muridku perlu buku."]],
        'gift_r':"Bergizi."},
    'mbok_jum':   {'name':'Mbok Jum','type':'human','gift':'jamur',
        'talks':[["Eh, anaknya siapa?"],["Dulu lembah ini tidak begini..."]],
        'gift_r':"Buat sayur lodeh!"},
    'jaka_ronda': {'name':'Pak Jaka','type':'human','gift':'kayu',
        'talks':[["Hati-hati malam, banyak yang aneh."],["Ronda berat."]],
        'gift_r':"Kayu bakar!"},
}

SUPERNATURAL_NPCS = {
    'naga_bijak':    {'name':'Sang Hyang Naga','type':'naga',
        'talks':[["(Naga membuka mata)"],
                 ["Manusia... mengapa kau di sini?"],
                 ["Aku menjaga lembah ribuan tahun."],
                 ["Buktikan keberanianmu — duel denganku!"],
                 ["(Setelah kalah) Kau pantas dihormati."],
                 ["Ambillah air keabadian."]],
        'gift':'mandrake','gift_r':"Benda dari kedalaman bumi."},
    'jin_kebun':     {'name':'Jin Kebun','type':'jin',
        'talks':[["Hihihi... subur..."],["Aku suka tomat merah!"]],
        'gift':'tomat','gift_r':"Merah! Manis!"},
    'demit_tua':     {'name':'Mbah Demit','type':'demit',
        'talks':[["Dingin..."],["Banyak yang terlupakan."]],
        'gift':'jamur','gift_r':"Mengingatkanku masa lalu."},
    'tuyul_pencuri': {'name':'Uyil','type':'tuyul',
        'talks':[["Uang! Hihi!"],["Jangan kejar!"]],
        'gift':'jagung','gift_r':"Kuning seperti emas!"},
    'kuntilanak':    {'name':'Kuntilanak','type':'kuntilanak',
        'talks':[["Hihihihi..."],["Carikan bunga melati..."]],
        'gift':'stroberi','gift_r':"Merah seperti darah."},
    'pocong':        {'name':'Pocong','type':'pocong',
        'talks':[["Tolong... lepaskan..."],["Ingin tenang..."]],
        'gift':'wild_herb','gift_r':"(Mengangguk)"},
    'genderuwo':     {'name':'Genderuwo','type':'genderuwo',
        'talks':[["GROOAARR!"],["Manusia kecil... berani sekali."]],
        'gift':'labu','gift_r':"Hmph. Lumayan."},
    'wewe_gombel':   {'name':'Wewe Gombel','type':'wewe',
        'talks':[["Anak nakal kuculik..."],["Kau bukan anak nakal kan?"]],
        'gift':'bayam','gift_r':"Untuk cucu-cucuku."},
    'banaspati':     {'name':'Banaspati','type':'banaspati',
        'talks':[["(Api membara)"],["Aku menjaga api."]],
        'gift':'jamur','gift_r':"(Api meredup)"},
    'leak_bali':     {'name':'Leak','type':'leak',
        'talks':[["Krrrhhh..."],["Ilmu hitam Bali..."]],
        'gift':'mandrake','gift_r':"Ilmuku bertambah."},
}

ANIMAL_NPCS = {
    'sapi_betsy':      {'name':'Betsy','type':'sapi','talks':[["Moo..."]],'product':'susu'},
    'ayam_kuning':     {'name':'Pio','type':'ayam','talks':[["Petok!"]],'product':'telur'},
    'kambing_jenggot': {'name':'Jenggot','type':'kambing','talks':[["Mbekkk..."]],'product':'wol'},
    'bebek_donald':    {'name':'Donald','type':'bebek','talks':[["Wek wek!"]],'product':None},
    'domba_woolly':    {'name':'Woolly','type':'domba','talks':[["Bee..."]],'product':'wol'},
    'kuda_pegasus':    {'name':'Pegasus','type':'kuda','talks':[["Hiiyaa!"]],'product':None},
    'kucing_oren':     {'name':'Oren','type':'kucing','talks':[["Meong"]],'product':None},
    'rubah_hutan':     {'name':'Reynard','type':'rubah','talks':[["(Mengintai)"]],'product':None},
    'kelinci_putih':   {'name':'Pinky','type':'kelinci','talks':[["(Hidung berkedut)"]],'product':None},
}

def all_npcs():
    return list(HUMAN_NPCS.keys()) + list(SUPERNATURAL_NPCS.keys()) + list(ANIMAL_NPCS.keys())

SCHEDULES = {
    'arya':       [(6, 12, 12, 'farm', 'walking'), (12, 15, 15, 'town', 'walking'),
                   (18, 5, 5, 'farm', 'resting')],
    'sari':       [(6, 4, 4, 'shop', 'preparing'), (8, 4, 4, 'shop', 'working'),
                   (18, 15, 15, 'town', 'walking'), (21, 5, 5, 'shop', 'sleeping')],
    'raka':       [(6, 6, 6, 'clinic', 'working'), (13, 12, 18, 'town', 'strolling'),
                   (17, 6, 6, 'clinic', 'reading')],
    'maya':       [(8, 10, 10, 'studio', 'painting'), (14, 20, 10, 'mountain', 'sketching'),
                   (20, 10, 10, 'studio', 'sleeping')],
    'budi':       [(7, 7, 7, 'smith', 'forging'), (19, 12, 12, 'town', 'drinking'),
                   (22, 7, 7, 'smith', 'sleeping')],
    'joko':       [(4, 8, 8, 'lake', 'fishing'), (10, 9, 8, 'lake', 'fishing'),
                   (15, 4, 4, 'shop', 'shopping'), (18, 8, 8, 'lake', 'fishing'),
                   (22, 8, 8, 'lake', 'sleeping')],
    'cici':       [(7, 10, 14, 'farm', 'playing'), (13, 22, 18, 'town', 'wandering'),
                   (18, 5, 5, 'farm', 'home')],
    'bowo':       [(7, 7, 16, 'farm', 'helping'), (12, 15, 12, 'town', 'school'),
                   (17, 5, 5, 'farm', 'home')],
    'ningsih':    [(6, 4, 4, 'farm', 'cooking'), (12, 4, 4, 'farm', 'cooking'),
                   (18, 12, 12, 'town', 'gossiping'), (21, 4, 4, 'farm', 'sleeping')],
    'pak_guru':   [(7, 12, 8, 'town', 'teaching'), (15, 22, 18, 'town', 'reading'),
                   (20, 12, 8, 'town', 'sleeping')],
    'mbok_jum':   [(6, 18, 14, 'town', 'cooking'), (14, 18, 14, 'town', 'serving'),
                   (21, 18, 14, 'town', 'sleeping')],
    'jaka_ronda': [(0, -1, -1, 'hidden', 'sleeping'), (18, 12, 14, 'town', 'patroling'),
                   (4, -1, -1, 'hidden', 'sleeping')],
    'naga_bijak':    [(0, 7, 6, 'naga_cave', 'sleeping'), (5, 7, 6, 'naga_cave', 'meditating')],
    'jin_kebun':     [(0, -1, -1, 'hidden', 'dormant'), (19, 5, 8, 'farm', 'helping'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'demit_tua':     [(0, -1, -1, 'hidden', 'dormant'), (20, 5, 20, 'mountain', 'haunting'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'tuyul_pencuri': [(0, -1, -1, 'hidden', 'sleeping'), (1, 5, 5, 'farm', 'stealing'),
                      (5, -1, -1, 'hidden', 'sleeping')],
    'kuntilanak':    [(0, -1, -1, 'hidden', 'dormant'), (20, 3, 12, 'lake', 'haunting'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'pocong':        [(0, -1, -1, 'hidden', 'dormant'), (21, 8, 19, 'cemetery', 'jumping'),
                      (3, -1, -1, 'hidden', 'dormant')],
    'genderuwo':     [(0, -1, -1, 'hidden', 'dormant'), (19, 14, 12, 'mountain', 'roaming'),
                      (5, -1, -1, 'hidden', 'dormant')],
    'wewe_gombel':   [(0, -1, -1, 'hidden', 'dormant'), (22, 20, 20, 'mountain', 'haunting'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'banaspati':     [(0, -1, -1, 'hidden', 'dormant'), (20, 8, 8, 'naga_cave', 'floating'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'leak_bali':     [(0, -1, -1, 'hidden', 'dormant'), (23, 6, 19, 'cemetery', 'transforming'),
                      (3, -1, -1, 'hidden', 'dormant')],
    'sapi_betsy':      [(0, 18, 5, 'farm', 'grazing')],
    'ayam_kuning':     [(0, 16, 5, 'farm', 'pecking')],
    'kambing_jenggot': [(0, 19, 6, 'farm', 'grazing')],
    'bebek_donald':    [(0, 9, 9, 'lake', 'swimming')],
    'domba_woolly':    [(0, 17, 7, 'farm', 'grazing')],
    'kuda_pegasus':    [(0, 20, 5, 'farm', 'grazing')],
    'kucing_oren':     [(0, 7, 9, 'farm', 'lounging')],
    'rubah_hutan':     [(0, 22, 18, 'mountain', 'prowling')],
    'kelinci_putih':   [(0, 15, 18, 'mountain', 'hopping')],
}

QUEST_STAGES = [
    {'s':0,'t':'Baru Datang','d':'Cek kotak pos depan rumah'},
    {'s':1,'t':'Petani Pemula','d':'Tanam & siram 3 lobak'},
    {'s':2,'t':'Panen Pertama','d':'Panen 3 lobak'},
    {'s':3,'t':'Ekonomi Desa','d':'Kumpulkan 150G'},
    {'s':4,'t':'Alat Lebih Baik','d':'Beli upgrade di Bengkel'},
    {'s':5,'t':'Eksplorasi Gua','d':'Crafting pickaxe & masuk gua'},
    {'s':6,'t':'Penambang Pemula','d':'5 tembaga + 3 besi'},
    {'s':7,'t':'Pendekar Karsa','d':'Pedang besi & bunuh 5 mob'},
    {'s':8,'t':'Misteri Kuburan','d':'Tangkap 1 makhluk halus'},
    {'s':9,'t':'Kedalaman','d':'Capai gua level 10'},
    {'s':10,'t':'Boss Naga','d':'Kalahkan Sang Hyang Naga'},
    {'s':11,'t':'TAMAT','d':'Air Keabadian milikmu!'},
]

MINERALS = {
    'tembaga':  {'name':'Tembaga','sell':30,'min_level':1,'tier':1},
    'besi':     {'name':'Besi','sell':60,'min_level':3,'tier':2},
    'emas':     {'name':'Emas','sell':120,'min_level':6,'tier':3},
    'kristal':  {'name':'Kristal Cahaya','sell':90,'min_level':4,'tier':2},
    'mithril':  {'name':'Mithril','sell':250,'min_level':10,'tier':4},
}

PICKAXE_RECIPES = [
    {'tier':1,'name':'Pickaxe Kayu',    'cost_gold':50,   'needs':{'kayu':5}},
    {'tier':2,'name':'Pickaxe Tembaga', 'cost_gold':120,  'needs':{'kayu':3,'tembaga':3}},
    {'tier':3,'name':'Pickaxe Besi',    'cost_gold':250,  'needs':{'besi':5}},
    {'tier':4,'name':'Pickaxe Emas',    'cost_gold':500,  'needs':{'emas':3,'besi':5}},
    {'tier':5,'name':'Pickaxe Mithril', 'cost_gold':1200, 'needs':{'mithril':3,'emas':3}},
]

SWORD_RECIPES = [
    {'id':'sword_kayu',    'name':'Pedang Kayu',    'cost_gold':80,   'damage':10, 'needs':{'kayu':8}},
    {'id':'sword_besi',    'name':'Pedang Besi',    'cost_gold':200,  'damage':25, 'needs':{'besi':6,'kayu':2}},
    {'id':'sword_emas',    'name':'Pedang Emas',    'cost_gold':600,  'damage':45, 'needs':{'emas':4,'besi':4}},
    {'id':'sword_mithril', 'name':'Pedang Mithril', 'cost_gold':1500, 'damage':80, 'needs':{'mithril':5}},
]

MOB_TEMPLATES = {
    'kelelawar':  {'name':'Kelelawar', 'hp':15,  'damage':5,  'min_lvl':1,  'max_lvl':6,
                   'speed':2.5, 'drops':{'kayu':1},              'xp':5},
    'tikus_gua':  {'name':'Tikus Gua', 'hp':12,  'damage':4,  'min_lvl':1,  'max_lvl':4,
                   'speed':2.0, 'drops':{'tembaga':1},           'xp':3},
    'genderuwo':  {'name':'Genderuwo', 'hp':50,  'damage':15, 'min_lvl':5,  'max_lvl':12,
                   'speed':1.5, 'drops':{'besi':1,'kayu':2},     'xp':15},
    'banaspati':  {'name':'Banaspati', 'hp':60,  'damage':20, 'min_lvl':6,  'max_lvl':13,
                   'speed':2.0, 'drops':{'kristal':1},           'xp':20},
    'kuntilanak': {'name':'Kuntilanak','hp':45,  'damage':18, 'min_lvl':7,  'max_lvl':12,
                   'speed':1.8, 'drops':{'kristal':1},           'xp':18},
    'leak':       {'name':'Leak',      'hp':90,  'damage':30, 'min_lvl':10, 'max_lvl':14,
                   'speed':2.2, 'drops':{'emas':1,'mithril':1},  'xp':35},
    'pocong':     {'name':'Pocong',    'hp':100, 'damage':25, 'min_lvl':9,  'max_lvl':14,
                   'speed':1.0, 'drops':{'emas':2},              'xp':30},
}

NAGA_BOSS = {
    'name':'Sang Hyang Naga', 'hp':300, 'damage':40, 'speed':1.5,
    'spawn_level':15, 'drops':{'air_keabadian':1, 'mithril':5, 'emas':10},
}

DUNGEON_MAX_LEVEL = 15
DUNGEON_TILES_W   = 24
DUNGEON_TILES_H   = 18

# ── SHOP — barang yang dijual Bu Sari di warung ──────────
SHOP_ITEMS = [
    {'id':'lobak_seed',    'name':'Benih Lobak',    'price':5,   'season':'Semi'},
    {'id':'wortel_seed',   'name':'Benih Wortel',   'price':8,   'season':'Semi/Gugur'},
    {'id':'stroberi_seed', 'name':'Benih Stroberi', 'price':12,  'season':'Semi'},
    {'id':'jagung_seed',   'name':'Benih Jagung',   'price':10,  'season':'Panas'},
    {'id':'tomat_seed',    'name':'Benih Tomat',    'price':14,  'season':'Panas'},
    {'id':'labu_seed',     'name':'Benih Labu',     'price':15,  'season':'Gugur'},
    {'id':'bayam_seed',    'name':'Benih Bayam',    'price':7,   'season':'Dingin'},
    {'id':'jamur_seed',    'name':'Benih Jamur',    'price':12,  'season':'Dingin'},
    {'id':'kayu',          'name':'Kayu',           'price':20,  'season':'all'},
]
