"""
data.py — Semua data deklaratif: tanaman, NPC, dialog, schedule, quest.
Tambah konten baru di sini.
"""

# ─── TANAMAN ──────────────────────────────────────────
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

# ─── TANAMAN LIAR ─────────────────────────────────────
WILD_ITEMS = {
    'mandrake':       {'name':'Mandrake','sell':80,'description':'Akar ajaib, langka','dangerous':True},
    'running_mushroom':{'name':'Jamur Lari','sell':45,'description':'Jamur cerdas yang lari!'},
    'firefly':        {'name':'Kunang Halus','sell':35,'description':'Cahayanya menenangkan'},
    'wild_herb':      {'name':'Herba Liar','sell':18,'description':'Tanaman obat'},
    'wild_berry':     {'name':'Beri Liar','sell':14,'description':'Manis dan asam'},
}

# ─── NPC: MANUSIA ─────────────────────────────────────
HUMAN_NPCS = {
    'arya': {
        'name':'Pak Arya','type':'human','gift':'wortel',
        'talks':[
            ['Anak muda! Selamat datang di Lembah Karsa.','Lembah ini punya banyak rahasia.'],
            ['Tanah yang dirawat tiap hari memberi hasil.'],
            ['Wortel segar itu favoritku!'],
            ['Hati-hati di hutan dalam. Banyak makhluk halus...'],
        ],
        'gift_r':'Wortel segar! Tanahmu subur. Terima kasih!',
    },
    'sari': {
        'name':'Bu Sari','type':'human','gift':'jagung',
        'talks':[
            ['Selamat datang di Warung Sari!','Beli benih atau jual panen di sini.'],
            ['Mau beli atau jual sesuatu?'],
            ['Pasar malam buka jam 18:00! Datanglah!'],
        ],
        'gift_r':'Jagungnya segar! Makasih banyak!',
    },
    'raka': {
        'name':'Pak Raka','type':'human','gift':'stroberi',
        'talks':[
            ['Jaga kesehatanmu, ya.','Kalau lemas, makan stroberi atau tidur.'],
            ['Aku sering ke kuburan tua malam hari... eh.','Anggap aku tidak bilang apa-apa.'],
        ],
        'gift_r':'Stroberi segar! Langka. Terima kasih!',
    },
    'maya': {
        'name':'Maya','type':'human','gift':'tomat',
        'talks':[
            ['Aku Maya, seniman lembah ini.','Pemandangan ladangmu indah waktu pagi.'],
            ['Kunang-kunang di hutan dalam itu... bukan kunang biasa lho.'],
        ],
        'gift_r':'Tomat merah sempurna untuk dilukis!',
    },
    'budi': {
        'name':'Budi','type':'human','gift':'jamur',
        'talks':[
            ['Aku Budi, pandai besi lembah.','Beli upgrade alat di sini.'],
            ['Cangkul baja hemat energi.'],
        ],
        'gift_r':'Jamur segar! Mantap!',
    },
}

# ─── NPC: SUPERNATURAL ────────────────────────────────
SUPERNATURAL_NPCS = {
    'jin_kebun': {
        'name':'Jin Kebun','type':'jin','gift':'wild_herb',
        'intelligence':'high',
        'talks':[
            ['Sssh... kau bisa melihatku?','Tidak banyak manusia bisa.','Aku Jin penjaga kebun ini sejak ratusan tahun lalu.'],
            ['Kebun Paman Arsa-mu... aku kenal pamanmu.','Dia orang baik. Berbicara kepadaku saat malam.'],
            ['Ada hal-hal yang bersembunyi di hutan dalam.','Berhati-hatilah saat malam tiba.'],
            ['Aku bisa memberkati panen jika kau persembahkan herba liar.'],
        ],
        'gift_r':'Herba liar... lama tak kucium. Berkah untukmu, Manusia.',
    },
    'demit_tua': {
        'name':'Demit Tua','type':'demit','gift':'jamur',
        'intelligence':'medium',
        'talks':[
            ['Hrrr... Manusia muda... hrrr...'],
            ['Kau berani datang ke kuburan tua...'],
            ['Berikan jamur padaku... atau pergi...'],
        ],
        'gift_r':'Hrrr... lumayan... lumayan...',
    },
    'tuyul_pencuri': {
        'name':'Tuyul','type':'tuyul','gift':'wild_berry',
        'intelligence':'low',
        'talks':[
            ['Hihihi! Kakakk!'],
            ['Mau permen?'],
            ['Aku tidak nyolong! Bohong!'],
            ['Hihihi! Kabuurr!'],
        ],
        'gift_r':'Beri liar! Yummy! Hihihi!',
    },
}

# ─── NPC: HEWAN TERNAK ───────────────────────────────
ANIMAL_NPCS = {
    'sapi_betsy': {
        'name':'Betsy','type':'sapi','intelligence':'animal',
        'product':'susu','product_interval':1,
        'talks':[['Mooo!'],['Mooooo...'],['*mengunyah rumput*']],
    },
    'ayam_kuning': {
        'name':'Ayam Kuning','type':'ayam','intelligence':'animal',
        'product':'telur','product_interval':1,
        'talks':[['Petok petok!'],['*mengais tanah*'],['Kukuruyuk!']],
    },
    'kambing_jenggot': {
        'name':'Si Jenggot','type':'kambing','intelligence':'animal',
        'product':'wol','product_interval':3,
        'talks':[['Mbeeek!'],['Mbeeee...'],['*mengunyah daun*']],
    },
}

# Helper untuk gabungkan semua NPC
def all_npcs():
    return {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}

# ─── SCHEDULES — Jadwal harian NPC ────────────────────
# Format: (jam_mulai, x_target, y_target, scene, aktivitas)
# x=-1 berarti NPC menghilang
SCHEDULES = {
    'arya': [
        (5,  11, 8, 'outdoor', 'sleeping'),
        (6,  10, 9, 'outdoor', 'wake'),
        (8,  20, 14, 'outdoor', 'farming'),
        (12, 22, 3, 'shop', 'shopping'),
        (14, 11, 8, 'outdoor', 'farming'),
        (18, 30, 18, 'outdoor', 'wandering'),
        (21, 11, 8, 'outdoor', 'returning'),
        (22, 11, 8, 'outdoor', 'sleeping'),
    ],
    'sari': [
        (6,  7, 3, 'shop', 'preparing'),
        (8,  7, 3, 'shop', 'shopkeeping'),
        (17, 30, 18, 'outdoor', 'pasarmalam'),
        (22, 7, 3, 'shop', 'sleeping'),
    ],
    'raka': [
        (7,  7, 3, 'clinic', 'working'),
        (16, 7, 3, 'clinic', 'closing'),
        (20, 35, 22, 'outdoor', 'cemetery'),
        (22, 7, 3, 'clinic', 'sleeping'),
    ],
    'maya': [
        (7,  7, 3, 'studio', 'painting'),
        (10, 12, 14, 'outdoor', 'sketching'),
        (14, 30, 5, 'outdoor', 'sketching'),
        (18, 30, 18, 'outdoor', 'pasarmalam'),
        (22, 7, 3, 'studio', 'sleeping'),
    ],
    'budi': [
        (7,  7, 3, 'smith', 'forging'),
        (12, 7, 3, 'smith', 'lunch'),
        (13, 7, 3, 'smith', 'forging'),
        (19, 7, 3, 'smith', 'closing'),
        (22, 7, 3, 'smith', 'sleeping'),
    ],
    'jin_kebun': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (19, 8, 6, 'outdoor', 'manifesting'),
        (3,  -1, -1, 'hidden', 'dormant'),
    ],
    'demit_tua': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (20, 35, 22, 'outdoor', 'haunting'),
        (4,  -1, -1, 'hidden', 'dormant'),
    ],
    'tuyul_pencuri': [
        (0,  -1, -1, 'hidden', 'sleeping'),
        (1,  6, 16, 'outdoor', 'stealing'),
        (5,  -1, -1, 'hidden', 'sleeping'),
        (13, 25, 18, 'outdoor', 'mischief'),
        (15, -1, -1, 'hidden', 'sleeping'),
        (23, 6, 16, 'outdoor', 'stealing'),
    ],
    'sapi_betsy':     [(0, 4, 11, 'outdoor', 'grazing')],
    'ayam_kuning':    [(0, 6, 11, 'outdoor', 'pecking')],
    'kambing_jenggot':[(0, 5, 12, 'outdoor', 'grazing')],
}

# ─── QUEST STAGES ─────────────────────────────────────
QUEST_STAGES = [
    {'t':'Prolog',   'd':'Baca surat di kotak pos.'},
    {'t':'Bab I',    'd':'Tanam & siram 3 lobak.'},
    {'t':'Bab I',    'd':'Panen 3 lobak.'},
    {'t':'Bab II',   'd':'Kumpulkan 150G.'},
    {'t':'Bab II',   'd':'Upgrade alat dari Budi.'},
    {'t':'Bab III',  'd':'Panen 2 jagung.'},
    {'t':'Bab III',  'd':'Beri hadiah ke 3 warga.'},
    {'t':'Bab IV',   'd':'Tangkap 1 makhluk halus.'},
    {'t':'Bab IV',   'd':'Bertemu Jin Kebun (malam).'},
    {'t':'Bab V',    'd':'Selesaikan tahun pertama.'},
    {'t':'Tamat!',   'd':'Lembah Karsa bangkit!'},
]
