"""
data.py — Tanaman, 31 NPC, dialog, schedule, quest, dungeon, combat, crafting.
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
    'ningsih':    {'name':'Ningsih','type':'human','gift':'bayam',
        'talks':[["Anak-anak bikin pusing."],["Sisakan sayuran."]],
        'gift_r':"Sehat!"},
    'pak_guru':   {'name':'Pak Guru','type':'human','gift':'lobak',
        'talks':[["Pendidikan kunci kemajuan."],["Murid-muridku perlu buku."]],
        'gift_r':"Bergizi."},
    'mbok_jum':   {'name':'Mbok Jum','type':'human','gift':'jamur',
        'talks':[["Eh, anaknya siapa?"],["Dulu lembah ini tidak begini..."]],
        'gift_r':"Buat sayur lodeh!"},
    'jaka_ronda': {'name':'Jaka','type':'human','gift':'kayu',
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


# ─── Dialog kontekstual: NPC bicara berbeda saat aktivitas tertentu ─────────
# Lookup: TALKS_BY_ACTIVITY[npc_id][activity] = list[str]
TALKS_BY_ACTIVITY = {
    'sari': {
        'preparing': ["Subuh-subuh sudah harus siap. Hidup pedagang!", "Lihat dagangan baru ini!"],
        'working': ["Selamat datang di warung Sari!", "Cari benih apa hari ini?", "Tomat segar baru datang!"],
        'serving': ["Mau beli atau jual?", "Jangan lupa bawa hasil panen ya."],
        'closing': ["Wah, sudah sore. Mau tutup nih.", "Besok datang lagi ya!"],
        'gossiping': ["Eh, dengar tidak? Ada yang lihat kuntilanak di danau...", "Pak Joko mancingnya makin kurus aja."],
        'sleeping': ["Zzz..."],
    },
    'budi': {
        'forging': ["*ting ting* Sebentar, lagi nempa.", "Suara palu adalah musik untukku!"],
        'crafting_tools': ["Cangkul atau penyiram? Aku bisa upgrade keduanya."],
        'forging_swords': ["Bawa mineral, kucraftkan pedang!", "Tembaga + besi = pedang besi. Mantap!"],
        'lunch': ["Makan dulu ya, perut harus diisi.", "Sari masakannya enak."],
        'drinking': ["Hahaha! Mari minum bareng!", "Habis kerja, harus rileks."],
        'sleeping': ["Zzz..."],
    },
    'raka': {
        'preparing': ["Membuka klinik. Ada yang perlu obat?"],
        'consulting': ["Ada keluhan? Aku bisa bantu.", "Sini, kuperiksa nadimu.", "Herba ini bagus untuk demam."],
        'gathering_herbs': ["Ssh... hati-hati, beberapa herba langka.", "Mandrake itu bahaya, tapi kuat efeknya."],
        'reading_books': ["Pengetahuan herbal Jawa kuno menarik."],
        'sleeping': ["Zzz..."],
    },
    'maya': {
        'painting': ["Sebentar, momen ini harus kutangkap.", "Cahaya pagi paling indah."],
        'inspiration': ["Aku lagi cari inspirasi. Boleh kulukis kamu?"],
        'sketching_farm': ["Kebunmu indah! Bisa kulukis ya?"],
        'landscape': ["Pemandangan gunung ini... sempurna."],
        'finishing': ["Hampir selesai... satu sapuan lagi."],
        'sleeping': ["Zzz..."],
    },
    'joko': {
        'fishing': ["Ssh... ikan lagi banyak.", "Sabar adalah kunci memancing.", "Hari ini banyak yang nyangkut!"],
        'changing_spot': ["Pindah spot, di sini sudah sepi."],
        'selling_fish': ["Ikan segar! Sari pasti suka."],
        'fishing_night': ["Malam ini ikan besar suka muncul.", "Kuntilanak? Ah, aku tidak takut."],
        'sleeping': ["Zzz... ngorok di pinggir danau."],
    },
    'arya': {
        'tilling': ["Tanah harus gembur dulu sebelum tanam."],
        'watering': ["Tanaman butuh air pagi-pagi."],
        'shopping': ["Mau beli benih jagung. Lagi musim panas."],
        'harvesting': ["Panen! Hasilnya lumayan hari ini."],
        'cooking': ["Memasak hasil panen sendiri paling enak."],
        'sleeping': ["Zzz..."],
    },
    'cici': {
        'breakfast': ["Mama, sarapannya enak!"],
        'school': ["Belajar dulu, belajar dulu!", "Pak Guru galak kalau telat."],
        'playing': ["Hihi! Mau main kejar-kejaran?", "Ayo lomba lari!"],
        'helping_mom': ["Aku bantu mama memasak."],
        'dinner': ["Makan malam!"],
        'sleeping': ["Zzz... mimpi indah."],
    },
    'pak_guru': {
        'teaching': ["Murid-murid, perhatikan!", "Hari ini kita belajar tentang bercocok tanam."],
        'lunch': ["Sebentar, makan dulu.", "Mengajar itu menguras tenaga."],
        'reading_library': ["Pengetahuan adalah kekayaan abadi.", "Buku-buku tua di sini banyak yang menarik."],
        'walking': ["Jalan-jalan sore baik untuk kesehatan."],
        'sleeping': ["Zzz..."],
    },
    'mbok_jum': {
        'cooking_jamu': ["Jamu kunyit asem segar!", "Ini resep nenek moyang."],
        'serving': ["Mau jamu apa? Beras kencur? Temulawak?", "Minum jamu, badan kuat!"],
        'consulting_raka': ["Pak Raka, herba ini lebih cocok untuk apa ya?"],
        'sleeping': ["Zzz..."],
    },
    'naga_bijak': {
        'sleeping': ["...zzZZZ..."],
        'meditating': ["Manusia muda... belum saatnya kau mendekat.",
                       "Aku menjaga tempat ini sejak ratusan tahun lalu."],
        'guarding': ["Berhati-hatilah di gua bawah.", "Mineral itu tertukar nyawa, anak muda."],
    },
    'jin_kebun': {
        'helping_garden': ["Kau merawat kebun dengan baik. Aku akan membantu.",
                          "Tanaman-tanamanmu... aku berkati."],
        'blessing_crops': ["Tumbuh subur, tumbuh subur..."],
    },
    'tuyul_pencuri': {
        'stealing_gold': ["Hihihi! Kupingmu kecil, aku ambil sedikit aja...",
                          "Goldmu... punyaku sekarang!"],
        'fleeing': ["Aaaa! Jangan tangkap aku!"],
    },
}


SCHEDULES = {
    # ─── Manusia: rutinitas harian detail ──────────────
    # Arya: tetangga petani, gerak antara farm-town
    'arya':       [(5, 12, 14, 'farm', 'tilling'),    # subuh: cangkul lahan
                   (8, 11, 9, 'farm', 'watering'),     # pagi: siram tanaman
                   (12, 4, 4, 'shop', 'shopping'),     # siang: belanja
                   (14, 12, 12, 'farm', 'harvesting'), # sore: panen
                   (18, 5, 5, 'farm', 'cooking'),
                   (21, 5, 5, 'farm', 'sleeping')],
    # Sari: pedagang warung
    'sari':       [(5, 4, 4, 'shop', 'preparing'),    # subuh: siapkan dagangan
                   (8, 4, 4, 'shop', 'working'),       # buka warung
                   (12, 4, 4, 'shop', 'serving'),
                   (17, 4, 4, 'shop', 'closing'),
                   (18, 12, 14, 'town', 'gossiping'),  # malam: ngobrol di alun-alun
                   (21, 5, 5, 'shop', 'sleeping')],
    # Raka: tabib di klinik
    'raka':       [(6, 6, 6, 'clinic', 'preparing'),
                   (8, 6, 6, 'clinic', 'consulting'),  # buka praktek
                   (13, 18, 12, 'mountain', 'gathering_herbs'),  # cari herba
                   (16, 6, 6, 'clinic', 'consulting'),
                   (20, 6, 6, 'clinic', 'reading_books'),
                   (23, 6, 6, 'clinic', 'sleeping')],
    # Maya: seniman pelukis
    'maya':       [(7, 10, 10, 'studio', 'painting'),
                   (10, 12, 8, 'town', 'inspiration'),  # cari inspirasi di town
                   (12, 5, 12, 'farm', 'sketching_farm'),
                   (15, 20, 10, 'mountain', 'landscape'), # melukis pemandangan
                   (18, 10, 10, 'studio', 'finishing'),
                   (22, 10, 10, 'studio', 'sleeping')],
    # Budi: pandai besi
    'budi':       [(6, 7, 7, 'smith', 'forging'),
                   (10, 7, 7, 'smith', 'crafting_tools'),
                   (13, 4, 4, 'shop', 'lunch'),
                   (15, 7, 7, 'smith', 'forging_swords'),
                   (19, 12, 12, 'town', 'drinking'),
                   (22, 7, 7, 'smith', 'sleeping')],
    # Joko: pemancing
    'joko':       [(4, 8, 8, 'lake', 'fishing'),       # subuh: mancing
                   (10, 9, 8, 'lake', 'changing_spot'),
                   (13, 4, 4, 'shop', 'selling_fish'),  # jual ikan ke Sari
                   (15, 8, 8, 'lake', 'fishing'),
                   (19, 8, 8, 'lake', 'fishing_night'),
                   (22, 8, 8, 'lake', 'sleeping')],
    # Cici: anak SD
    'cici':       [(6, 5, 5, 'farm', 'breakfast'),
                   (7, 12, 8, 'town', 'school'),       # ke sekolah jam 7
                   (13, 22, 18, 'town', 'playing'),
                   (16, 14, 14, 'farm', 'helping_mom'),
                   (19, 5, 5, 'farm', 'dinner'),
                   (21, 5, 5, 'farm', 'sleeping')],
    # Bowo: tukang
    'bowo':       [(6, 5, 5, 'farm', 'breakfast'),
                   (8, 12, 16, 'town', 'building'),    # bangun rumah
                   (12, 4, 4, 'shop', 'lunch'),
                   (14, 16, 12, 'town', 'building'),
                   (18, 12, 12, 'town', 'tavern'),
                   (22, 5, 5, 'farm', 'sleeping')],
    # Ningsih: penjahit
    'ningsih':    [(6, 4, 4, 'farm', 'sewing'),
                   (10, 12, 14, 'town', 'shopping_fabric'),
                   (13, 4, 4, 'farm', 'sewing'),
                   (17, 4, 4, 'farm', 'cooking'),
                   (19, 12, 12, 'town', 'gossiping'),
                   (22, 4, 4, 'farm', 'sleeping')],
    # Pak Guru: kepala sekolah
    'pak_guru':   [(7, 12, 8, 'town', 'teaching'),
                   (12, 4, 4, 'shop', 'lunch'),
                   (14, 12, 8, 'town', 'teaching'),
                   (16, 22, 18, 'town', 'reading_library'),
                   (19, 12, 12, 'town', 'walking'),
                   (22, 12, 8, 'town', 'sleeping')],
    # Mbok Jum: dukun
    'mbok_jum':   [(5, 18, 14, 'town', 'cooking_jamu'),
                   (10, 18, 14, 'town', 'serving'),
                   (14, 6, 6, 'clinic', 'consulting_raka'),  # diskusi dengan tabib
                   (17, 18, 14, 'town', 'serving'),
                   (21, 18, 14, 'town', 'sleeping')],
    # Jaka: ronda malam
    'jaka_ronda': [(0, 12, 14, 'town', 'patroling'),
                   (4, -1, -1, 'hidden', 'sleeping'),
                   (16, 12, 12, 'town', 'preparing'),
                   (18, 14, 14, 'town', 'patroling'),
                   (22, 16, 16, 'town', 'patroling')],
    # ─── Naga & supernatural: muncul di waktu spesifik ─
    'naga_bijak':    [(0, 7, 6, 'naga_cave', 'sleeping'),
                      (5, 7, 6, 'naga_cave', 'meditating'),
                      (12, 7, 6, 'naga_cave', 'guarding')],
    'jin_kebun':     [(0, -1, -1, 'hidden', 'dormant'),
                      (19, 5, 8, 'farm', 'helping_garden'),
                      (22, 8, 11, 'farm', 'blessing_crops'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'demit_tua':     [(0, -1, -1, 'hidden', 'dormant'),
                      (20, 5, 20, 'mountain', 'haunting'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'tuyul_pencuri': [(0, -1, -1, 'hidden', 'sleeping'),
                      (1, 5, 5, 'farm', 'stealing_gold'),
                      (3, 12, 12, 'farm', 'fleeing'),
                      (5, -1, -1, 'hidden', 'sleeping')],
    'kuntilanak':    [(0, -1, -1, 'hidden', 'dormant'),
                      (20, 3, 12, 'lake', 'haunting'),
                      (23, 5, 14, 'lake', 'wailing'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'pocong':        [(0, -1, -1, 'hidden', 'dormant'),
                      (21, 8, 19, 'cemetery', 'jumping'),
                      (3, -1, -1, 'hidden', 'dormant')],
    'genderuwo':     [(0, -1, -1, 'hidden', 'dormant'),
                      (19, 14, 12, 'mountain', 'roaming'),
                      (22, 18, 18, 'mountain', 'guarding'),
                      (5, -1, -1, 'hidden', 'dormant')],
    'wewe_gombel':   [(0, -1, -1, 'hidden', 'dormant'),
                      (22, 20, 20, 'mountain', 'haunting'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'banaspati':     [(0, -1, -1, 'hidden', 'dormant'),
                      (20, 8, 8, 'naga_cave', 'floating'),
                      (4, -1, -1, 'hidden', 'dormant')],
    'leak_bali':     [(0, -1, -1, 'hidden', 'dormant'),
                      (23, 6, 19, 'cemetery', 'transforming'),
                      (3, -1, -1, 'hidden', 'dormant')],
    # ─── Hewan: free-roam dalam pen ─────────────────────
    'sapi_betsy':      [(6, 4, 11, 'farm', 'grazing'),
                        (12, 5, 11, 'farm', 'resting'),
                        (18, 4, 11, 'farm', 'grazing'),
                        (22, 4, 11, 'farm', 'sleeping')],
    'ayam_kuning':     [(6, 5, 11, 'farm', 'pecking'),
                        (12, 6, 11, 'farm', 'pecking'),
                        (18, 5, 11, 'farm', 'pecking'),
                        (20, 5, 11, 'farm', 'roosting')],
    'kambing_jenggot': [(6, 4, 11, 'farm', 'grazing'),
                        (14, 5, 11, 'farm', 'butting'),
                        (20, 4, 11, 'farm', 'sleeping')],
    'bebek_donald':    [(6, 9, 20, 'lake', 'swimming'),
                        (12, 8, 21, 'lake', 'foraging'),
                        (18, 9, 20, 'lake', 'preening'),
                        (22, 9, 20, 'lake', 'sleeping')],
    'domba_woolly':    [(6, 5, 11, 'farm', 'grazing'),
                        (15, 4, 11, 'farm', 'resting'),
                        (20, 5, 11, 'farm', 'sleeping')],
    'kuda_pegasus':    [(6, 4, 11, 'farm', 'galloping'),
                        (12, 5, 11, 'farm', 'eating_hay'),
                        (18, 4, 11, 'farm', 'galloping'),
                        (22, 4, 11, 'farm', 'sleeping')],
    'kucing_oren':     [(6, 5, 5, 'farm', 'lazing'),
                        (10, 22, 18, 'town', 'wandering'),
                        (16, 5, 5, 'farm', 'lazing'),
                        (20, 5, 5, 'farm', 'hunting_mice')],
    'rubah_merah':     [(0, 18, 12, 'mountain', 'hunting'),
                        (10, -1, -1, 'hidden', 'hiding'),
                        (18, 18, 12, 'mountain', 'roaming'),
                        (22, 18, 12, 'mountain', 'hunting')],
    'kelinci_putih':   [(6, 14, 14, 'mountain', 'hopping'),
                        (12, 16, 14, 'mountain', 'eating_grass'),
                        (18, 14, 14, 'mountain', 'hopping'),
                        (22, 14, 14, 'mountain', 'sleeping')],
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

# ─── DUNGEON, MINING, COMBAT, CRAFTING ─────────────────
MINERALS = {
    'tembaga':  {'name':'Tembaga','sell':30,'min_level':1,'tier':1},
    'besi':     {'name':'Besi','sell':60,'min_level':3,'tier':2},
    'emas':     {'name':'Emas','sell':120,'min_level':6,'tier':3},
    'kristal':  {'name':'Kristal Cahaya','sell':90,'min_level':4,'tier':2},
    'mithril':  {'name':'Mithril','sell':250,'min_level':10,'tier':4},
}

PICKAXE_RECIPES = [
    {'tier':1,'name':'Pickaxe Kayu',   'cost_gold':50,  'needs':{'kayu':5}},
    {'tier':2,'name':'Pickaxe Tembaga','cost_gold':120,'needs':{'kayu':3,'tembaga':3}},
    {'tier':3,'name':'Pickaxe Besi',   'cost_gold':250,'needs':{'besi':5}},
    {'tier':4,'name':'Pickaxe Emas',   'cost_gold':500,'needs':{'emas':3,'besi':5}},
    {'tier':5,'name':'Pickaxe Mithril','cost_gold':1200,'needs':{'mithril':3,'emas':3}},
]

SWORD_RECIPES = [
    {'id':'sword_kayu',   'name':'Pedang Kayu',   'cost_gold':80,  'damage':10,'needs':{'kayu':8}},
    {'id':'sword_besi',   'name':'Pedang Besi',   'cost_gold':200, 'damage':25,'needs':{'besi':6,'kayu':2}},
    {'id':'sword_emas',   'name':'Pedang Emas',   'cost_gold':600, 'damage':45,'needs':{'emas':4,'besi':4}},
    {'id':'sword_mithril','name':'Pedang Mithril','cost_gold':1500,'damage':80,'needs':{'mithril':5}},
]

MOB_TEMPLATES = {
    'kelelawar':  {'name':'Kelelawar','hp':15,'damage':5, 'min_lvl':1, 'max_lvl':6,
                   'speed':2.5,'drops':{'kayu':1},'xp':5},
    'tikus_gua':  {'name':'Tikus Gua','hp':12,'damage':4, 'min_lvl':1, 'max_lvl':4,
                   'speed':2.0,'drops':{'tembaga':1},'xp':3},
    'genderuwo':  {'name':'Genderuwo','hp':50,'damage':15,'min_lvl':5, 'max_lvl':12,
                   'speed':1.5,'drops':{'besi':1,'kayu':2},'xp':15},
    'banaspati':  {'name':'Banaspati','hp':60,'damage':20,'min_lvl':6, 'max_lvl':13,
                   'speed':2.0,'drops':{'kristal':1},'xp':20},
    'kuntilanak': {'name':'Kuntilanak','hp':45,'damage':18,'min_lvl':7, 'max_lvl':12,
                   'speed':1.8,'drops':{'kristal':1},'xp':18},
    'leak':       {'name':'Leak','hp':90,'damage':30,'min_lvl':10,'max_lvl':14,
                   'speed':2.2,'drops':{'emas':1,'mithril':1},'xp':35},
    'pocong':     {'name':'Pocong','hp':100,'damage':25,'min_lvl':9, 'max_lvl':14,
                   'speed':1.0,'drops':{'emas':2},'xp':30},
}

NAGA_BOSS = {
    'name':'Sang Hyang Naga','hp':300,'damage':40,'speed':1.5,
    'spawn_level':15,'drops':{'air_keabadian':1,'mithril':5,'emas':10},
}

DUNGEON_MAX_LEVEL = 15
DUNGEON_TILES_W = 24
DUNGEON_TILES_H = 18
