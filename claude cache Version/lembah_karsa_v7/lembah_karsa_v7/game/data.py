"""
data.py — Semua data deklaratif: tanaman, NPC, dialog, schedule, quest.
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

WILD_ITEMS = {
    'mandrake':       {'name':'Mandrake','sell':80,'description':'Akar ajaib, langka','dangerous':True},
    'running_mushroom': {'name':'Jamur Lari','sell':45,'description':'Berlari saat didekati'},
    'firefly':        {'name':'Kunang-kunang','sell':25,'description':'Hanya muncul di malam hari'},
    'wild_herb':      {'name':'Herba Liar','sell':15,'description':'Tanaman obat di hutan'},
    'wild_berry':     {'name':'Beri Liar','sell':20,'description':'Beri manis, tumbuh liar'},
}

HUMAN_NPCS = {
    'arya': {'name': 'Arya', 'type': 'human', 'gift': 'jagung', 'talks': [["Pagi! Hutan utara selalu sejuk."], ["Jangan lupa cek tanamanmu."]], 'gift_r': "Wah, makasih!"},
    'sari': {'name': 'Bu Sari', 'type': 'human', 'gift': 'tomat', 'talks': [["Halo nak, mau beli benih?"], ["Kapan-kapan mampir ke warung."]], 'gift_r': "Pas sekali untuk masak!"},
    'raka': {'name': 'Pak Raka', 'type': 'human', 'gift': 'wild_herb', 'talks': [["Jangan terlalu lelah bertani."], ["Kesehatanku agak menurun akhir-akhir ini."]], 'gift_r': "Herba yang bagus, terima kasih."},
    'maya': {'name': 'Maya', 'type': 'human', 'gift': 'stroberi', 'talks': [["Aku sedang mencari inspirasi lukisan."], ["Lembah Karsa sangat indah."]], 'gift_r': "Warna stroberinya menginspirasiku!"},
    'budi': {'name': 'Budi', 'type': 'human', 'gift': 'lobak', 'talks': [["Besinya panas, jangan dekat-dekat."], ["Kapak yang bagus butuh kayu kering."]], 'gift_r': "Bisa jadi cemilan nih."},
}

SUPERNATURAL_NPCS = {
    'naga_bijak': {'name': 'Sang Hyang', 'type': 'naga', 'talks': [["(Mendengkur halus)"], ["(Membuka satu mata)"], ["Manusia... kau peduli pada tanah ini?"], ["Aku merasakan karsa di dalam dirimu."], ["Lembah ini hidup. Jaga baik-baik."]], 'gift': 'mandrake', 'gift_r': "Benda dari kedalaman bumi... baiklah."},
    'jin_kebun': {'name': 'Jin Kebun', 'type': 'jin', 'talks': [["Hihihi... subur... subur..."], ["Aku suka tomat yang merah!"], ["Kau bisa melihatku?"]], 'gift': 'tomat', 'gift_r': "Merah! Manis! Hahaha!"},
    'demit_tua': {'name': 'Mbah Demit', 'type': 'demit', 'talks': [["Dingin... sangat dingin..."], ["Banyak yang terlupakan di kuburan itu."]], 'gift': 'jamur', 'gift_r': "Baunya mengingatkanku pada masa lalu..."},
    'tuyul_pencuri': {'name': 'Uyil', 'type': 'tuyul', 'talks': [["Uang! Emas! Hihi!"], ["Jangan kejar aku!"], ["Ah, ketahuan!"], ["Baiklah, aku tak curi hari ini."]], 'gift': 'jagung', 'gift_r': "Kuning seperti emas! Nyamm!"},
}

ANIMAL_NPCS = {
    'sapi_betsy': {'name': 'Betsy', 'type': 'sapi', 'talks': [["Moo..."], ["(Dia mengunyah rumput)"]], 'product': 'susu'},
    'ayam_kuning': {'name': 'Pio', 'type': 'ayam', 'talks': [["Petok!"]], 'product': 'telur'},
    'kambing_jenggot': {'name': 'Jenggot', 'type': 'kambing', 'talks': [["Mbekkk..."]], 'product': 'wol'},
}

def all_npcs():
    return list(HUMAN_NPCS.keys()) + list(SUPERNATURAL_NPCS.keys()) + list(ANIMAL_NPCS.keys())

SCHEDULES = {
    'arya': [(6, 12, 12, 'farm', 'walking'), (12, 15, 15, 'town', 'walking'), (18, 5, 5, 'farm', 'resting')],
    'sari': [(6, 4, 4, 'shop', 'preparing'), (8, 4, 4, 'shop', 'working'), (18, 15, 15, 'town', 'walking'), (21, 5, 5, 'shop', 'sleeping')],
    'raka': [(6, 6, 6, 'clinic', 'working'), (13, 12, 18, 'town', 'strolling'), (17, 6, 6, 'clinic', 'reading')],
    'maya': [(8, 10, 10, 'studio', 'painting'), (14, 20, 10, 'mountain', 'sketching'), (20, 10, 10, 'studio', 'sleeping')],
    'budi': [(7, 7, 7, 'smith', 'forging'), (19, 12, 12, 'town', 'drinking'), (22, 7, 7, 'smith', 'sleeping')],
    'naga_bijak': [(0, 6, 5, 'naga_cave', 'sleeping'), (5, 6, 5, 'naga_cave', 'meditating')],
    'demit_tua': [(0, -1, -1, 'hidden', 'dormant'), (19, 5, 20, 'mountain', 'haunting'), (4, -1, -1, 'hidden', 'dormant')],
    'tuyul_pencuri': [(0, -1, -1, 'hidden', 'sleeping'), (22, 5, 5, 'farm', 'stealing'), (4, -1, -1, 'hidden', 'sleeping')],
    'sapi_betsy':     [(0, 18, 5, 'farm', 'grazing')],
    'ayam_kuning':    [(0, 16, 5, 'farm', 'pecking')],
    'kambing_jenggot':[(0, 19, 6, 'farm', 'grazing')],
}

QUEST_STAGES = [
    {'s': 0, 't': 'Baru Datang', 'd': 'Cek kotak pos di depan rumah'},
    {'s': 1, 't': 'Petani Pemula', 'd': 'Tanam & siram 3 lobak'},
    {'s': 2, 't': 'Panen Pertama', 'd': 'Panen 3 lobak'},
    {'s': 3, 't': 'Ekonomi Desa', 'd': 'Kumpulkan 150G (jual ke peti/warung)'},
    {'s': 4, 't': 'Alat Lebih Baik', 'd': 'Beli 1 upgrade di Bengkel Budi'},
    {'s': 5, 't': 'Musim Panas', 'd': 'Panen 2 jagung'},
    {'s': 6, 't': 'Warga Ramah', 'd': 'Beri 3 hadiah ke siapa saja'},
    {'s': 7, 't': 'Misteri Lembah', 'd': 'Tangkap 1 makhluk halus (F)'},
    {'s': 8, 't': 'Sang Penjaga', 'd': 'Temui Jin Kebun (malam hari)'},
    {'s': 9, 't': 'Tahun Pertama', 'd': 'Bertahan hingga tahun 2'},
    {'s': 10, 't': 'TAMAT', 'd': 'Selamat! Kamu bisa terus bermain.'},
]


# ─── DUNGEON / MOB / COMBAT (v7) ────────────────────────
DUNGEON_MAX_LEVEL = 15

MOB_TEMPLATES = {
    # Level 1-5: gua atas
    'kelelawar': {'hp': 15, 'damage': 5, 'speed': 2.0,
                  'drops': {'gold': 5}, 'xp': 5, 'min_lvl': 1, 'max_lvl': 5},
    'laba_laba': {'hp': 25, 'damage': 8, 'speed': 1.3,
                  'drops': {'gold': 8}, 'xp': 8, 'min_lvl': 2, 'max_lvl': 5},
    # Level 6-10: gua tengah
    'genderuwo_hostile': {'hp': 50, 'damage': 15, 'speed': 1.5,
                          'drops': {'gold': 15}, 'xp': 15, 'min_lvl': 5, 'max_lvl': 8},
    'kuntilanak_hostile': {'hp': 40, 'damage': 12, 'speed': 1.8,
                           'drops': {'gold': 14}, 'xp': 14, 'min_lvl': 6, 'max_lvl': 9},
    'banaspati_hostile': {'hp': 60, 'damage': 18, 'speed': 1.7,
                          'drops': {'gold': 20}, 'xp': 18, 'min_lvl': 8, 'max_lvl': 10},
    # Level 11-14: gua dalam
    'leak_hostile': {'hp': 90, 'damage': 25, 'speed': 1.6,
                     'drops': {'gold': 35}, 'xp': 30, 'min_lvl': 10, 'max_lvl': 13},
    'pocong_hostile': {'hp': 80, 'damage': 22, 'speed': 1.2,
                       'drops': {'gold': 30}, 'xp': 25, 'min_lvl': 11, 'max_lvl': 14},
    'demit_hostile': {'hp': 120, 'damage': 30, 'speed': 1.4,
                      'drops': {'gold': 50}, 'xp': 40, 'min_lvl': 13, 'max_lvl': 14},
}

NAGA_BOSS = {
    'hp': 500, 'damage': 35, 'speed': 1.0,
    'drops': {'gold': 1000, 'air_keabadian': 5}, 'xp': 200,
}
