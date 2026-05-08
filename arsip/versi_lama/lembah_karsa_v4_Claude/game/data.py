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
    'joko': {
        'name':'Pak Joko','type':'human','gift':'wild_berry',
        'talks':[
            ['Hmm... ikan hari ini sulit.','Sungai jadi tenang.'],
            ['Aku nelayan tua. Sudah 50 tahun di danau ini.'],
            ['Kalau mancing, datanglah pagi-pagi sekali.','Ikan paling banyak jam 5 subuh.'],
            ['Beri liar... istriku dulu suka itu.'],
        ],
        'gift_r':'Beri liar... mengingatkanku pada istriku. Terima kasih.',
    },
    'cici': {
        'name':'Cici','type':'human','gift':'stroberi',
        'talks':[
            ['Hai! Kakak bertani ya?','Aku Cici! Aku sering main di kebun!'],
            ['Pernah lihat tuyul? Aku pernah! Hihihi!'],
            ['Stroberi favoritku!! Kalau ada bagi ya kakak!'],
            ['Kakak Maya yang lukis aku kemarin. Cantik nggak?'],
        ],
        'gift_r':'STROBERIIII!! Yeyy!! Makasih kakak!! Hihihi!',
    },
    'bowo': {
        'name':'Pak Bowo','type':'human','gift':'jagung',
        'talks':[
            ['Kayu pohon mati di hutan dalam paling kuat.','Cocok untuk membangun.'],
            ['Aku tukang kayu. Bisa perbaiki bangunan.'],
            ['Punya 5 kayu? Bisa kubuat barang baru untukmu.'],
            ['Jagung bakar di pasar malam... mantap.'],
        ],
        'gift_r':'Jagung untuk dibakar! Wah, terima kasih!',
    },
    'ningsih': {
        'name':'Bu Ningsih','type':'human','gift':'wortel',
        'talks':[
            ['Aku bidan desa. Sudah lama di Lembah Karsa.'],
            ['Kalau ada warga sakit, aku rawat.','Kalau warga melahirkan, aku bantu.'],
            ['Wortel bagus untuk mata. Makanlah teratur.'],
            ['Bu Sari pernah hampir kehilangan bayinya...','Untunglah aku ada saat itu.'],
        ],
        'gift_r':'Wortel segar! Bagus untuk semua warga, terima kasih!',
    },
    'pak_guru': {
        'name':'Pak Guru Hadi','type':'human','gift':'lobak',
        'talks':[
            ['Aku guru anak-anak desa.','Cici muridku yang paling rajin.'],
            ['Setiap pagi 8 sampai 12 aku mengajar di balai desa.'],
            ['Kalau ada anak baru di lembah, kirim padaku ya.'],
            ['Lobak rebus enak untuk sarapan...'],
        ],
        'gift_r':'Lobak! Aku akan rebus untuk sarapan. Terima kasih!',
    },
    'mbok_jum': {
        'name':'Mbok Jum','type':'human','gift':'jamur',
        'talks':[
            ['Aku jualan jamu keliling.','Beras kencur, kunyit asam, segala ada.'],
            ['Capek kerja kebun? Minum jamu Mbok Jum saja!'],
            ['Bu Ningsih dulu beli jamu padaku waktu hamil.','Anaknya sehat sekarang.'],
            ['Jamur masak dengan kunyit asam... wah, mantap!'],
        ],
        'gift_r':'Jamur! Bisa kucampur jamu spesial. Makasih nak!',
    },
    'jaka_ronda': {
        'name':'Bang Jaka','type':'human','gift':'tomat',
        'talks':[
            ['Aku kebagian ronda malam ini.','Kalau ada apa-apa, panggil aku.'],
            ['Pernah lihat sesuatu aneh dekat kuburan...','Tapi aku gak takut, aku ronda terus!'],
            ['Tuyul itu nyata, sungguh!','Aku hampir tangkap satu minggu lalu!'],
            ['Tomat? Buat sambal cocol nasi malam-malam...'],
        ],
        'gift_r':'Tomat segar! Buat sambal nanti malam ronda. Mantul!',
    },
}

# ─── NPC: SUPERNATURAL ────────────────────────────────
SUPERNATURAL_NPCS = {
    'naga_bijak': {
        'name':'Naga Sang Hyang','type':'naga','gift':'mandrake',
        'intelligence':'wise','size':'huge',  # ukuran besar 3x2 tile
        'talks':[
            ['Hmmm... seorang petani muda mendekat... menarik...'],
            ['Aku Sang Hyang, naga penjaga lembah ini.','Tinggal ribuan tahun di gunung utara.','Hutan, sungai, dan tanah... semua tahu namaku.'],
            ['Lembah Karsa-mu? Pamanmu pernah datang.','Membawa stroberi sebagai persembahan.','Aku sukses... dia orang baik.'],
            ['Mandrake. Akar yang menjerit.','Bawakan satu untukku, dan aku akan memberkati panenmu satu musim penuh.'],
            ['Kebijakan tidak datang dari berlari.','Datang dari menanam, menunggu, memanen.','Kau sudah mengerti, anak muda.'],
        ],
        'gift_r':'Mandrake... tubuhku terasa muda kembali. Berkah panen kau dapat.',
    },
    'jin_kebun': {
        'name':'Jin Kebun','type':'jin','gift':'wild_herb',
        'intelligence':'high',
        'talks':[
            ['Sssh... kau bisa melihatku?','Tidak banyak manusia bisa.','Aku Jin penjaga kebun ini sejak ratusan tahun lalu.'],
            ['Kebun Paman Arsa-mu... aku kenal pamanmu.','Dia orang baik. Berbicara kepadaku saat malam.'],
            ['Ada hal-hal yang bersembunyi di hutan dalam.','Berhati-hatilah saat malam tiba.'],
            ['Aku bisa memberkati panen jika kau persembahkan herba liar.'],
            ['Ada Naga di gunung utara... ia bijak. Cari dia bila siap.'],
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
    'kuntilanak': {
        'name':'Kuntilanak','type':'kuntilanak','gift':'wild_berry',
        'intelligence':'high',
        'talks':[
            ['Hihihi... kau lihat aku?'],
            ['Kekekek... rambut panjangku.','Manusia takut padaku.'],
            ['Aku tidak jahat... hanya kesepian.','Suamiku pergi 100 tahun lalu.'],
            ['Beri liar... warnanya seperti darah... menarik...'],
        ],
        'gift_r':'Beri merah... lama tak kurasakan kebaikan. Terima kasih, manusia.',
    },
    'pocong': {
        'name':'Pocong','type':'pocong','gift':'jamur',
        'intelligence':'low',
        'talks':[
            ['*Pocong melompat di tempat*'],
            ['Mmmmmphh!'],
            ['Talikuuuu... lepaaass...'],
            ['Maaf manusia... aku terjebak.'],
        ],
        'gift_r':'Mmmmmphh! *gerakan kepala terima kasih*',
    },
    'genderuwo': {
        'name':'Genderuwo','type':'genderuwo','gift':'mandrake',
        'intelligence':'medium',
        'talks':[
            ['GRRRRRR!','Manusia kecil berani sekali!'],
            ['Aku Genderuwo... penjaga hutan dalam.','Pohon-pohon ini saksinya.'],
            ['Mandrake! Kau punya mandrake?'],
            ['Hutan ini rumahku 500 tahun.','Jangan kau tebang sembarangan.'],
        ],
        'gift_r':'GRRRR! Mandrake harum! Aku akan ingat kebaikanmu.',
    },
    'wewe_gombel': {
        'name':'Wewe Gombel','type':'wewe','gift':'wortel',
        'intelligence':'high',
        'talks':[
            ['Anak nakal... mendekatlah... khekhekhe...'],
            ['Aku Wewe Gombel.','Penculik anak yang melarikan diri.'],
            ['Tapi sekarang... aku sudah tua.','Tidak ada anak nakal lagi.'],
            ['Wortel? Hmm... aku terima.','Manusia muda bertingkah baik...'],
        ],
        'gift_r':'Khekhekhe... wortel manis. Engkau berbeda dari yang lain.',
    },
    'banaspati': {
        'name':'Banaspati','type':'banaspati','gift':'jamur',
        'intelligence':'medium',
        'talks':[
            ['*api melayang dengan wajah*','Whoooo... fuh fuh!'],
            ['Aku Banaspati. Kepala api dari neraka kecil.'],
            ['Aku tidak membakar manusia baik.','Hanya yang jahat... tenang saja.'],
            ['Jamur untukku? Gosong jamur enak!','Whoosh!'],
        ],
        'gift_r':'WHOOSH! Jamur gosong nikmat! Terima kasih manusia!',
    },
    'leak_bali': {
        'name':'Leak','type':'leak','gift':'mandrake',
        'intelligence':'high',
        'talks':[
            ['Sssh... aku Leak dari Bali, mengembara di sini.'],
            ['Aku bisa berubah wujud.','Babi, monyet, atau bola api.'],
            ['Mandrake... bahan ramuanku.','Kekuatannya luar biasa.'],
            ['Manusia yang bisa lihatku... istimewa.'],
        ],
        'gift_r':'Mandrake! Untuk ramuan agungku. Berkat untukmu, manusia.',
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
    'bebek_donald': {
        'name':'Bebek Donald','type':'bebek','intelligence':'animal',
        'product':'telur','product_interval':2,
        'talks':[['Wek wek!'],['Kwek!'],['*berenang riang*']],
    },
    'domba_woolly': {
        'name':'Woolly','type':'domba','intelligence':'animal',
        'product':'wol','product_interval':4,
        'talks':[['Baaaa!'],['Baaaaaa...'],['*menggosok bulu*']],
    },
    'kuda_pegasus': {
        'name':'Pegasus','type':'kuda','intelligence':'animal',
        'product':'pupuk','product_interval':1,
        'talks':[['Hihihihi!'],['*meringkik*'],['*tos kuku*']],
    },
    'kucing_oren': {
        'name':'Si Oren','type':'kucing','intelligence':'animal',
        'product':None,'product_interval':0,
        'talks':[['Meow~'],['*menggesek kakimu*'],['Prrrr...'],['*mengeong manja*']],
    },
    'rubah_hutan': {
        'name':'Rubah Liar','type':'rubah','intelligence':'animal',
        'product':None,'product_interval':0,
        'talks':[['*menatap diam*'],['Yip yip!'],['*kabur cepat*']],
    },
    'kelinci_putih': {
        'name':'Kelinci Putih','type':'kelinci','intelligence':'animal',
        'product':None,'product_interval':0,
        'talks':[['*mengendus*'],['*melompat-lompat*'],['*bersembunyi di rumput*']],
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
    'naga_bijak': [
        # Selalu di gua naga, tidur malam. Player harus datang.
        (0,  6, 5, 'naga_cave', 'sleeping'),
        (5,  6, 5, 'naga_cave', 'meditating'),
        (10, 7, 5, 'naga_cave', 'meditating'),
        (15, 6, 5, 'naga_cave', 'wisdom'),
        (20, 6, 5, 'naga_cave', 'sleeping'),
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
    'sapi_betsy':     [(0, 5, 10, 'outdoor', 'grazing')],
    'ayam_kuning':    [(0, 6, 11, 'outdoor', 'pecking')],
    'kambing_jenggot':[(0, 4, 11, 'outdoor', 'grazing')],
    # Hewan baru — di kandang & danau
    'bebek_donald':   [(0, 8, 19, 'outdoor', 'swimming')],   # di danau
    'domba_woolly':   [(0, 5, 11, 'outdoor', 'grazing')],
    'kuda_pegasus':   [(0, 7, 11, 'outdoor', 'standing')],
    # Manusia baru
    'joko': [
        (4,  9, 22, 'outdoor', 'fishing'),     # subuh memancing
        (10, 6, 19, 'outdoor', 'fishing'),     # pagi di danau
        (15, 22, 3, 'shop', 'shopping'),       # sore beli
        (18, 9, 22, 'outdoor', 'fishing'),     # malam memancing
        (22, 9, 22, 'outdoor', 'sleeping'),
    ],
    'cici': [
        (7,  10, 14, 'outdoor', 'playing'),
        (10, 30, 5, 'outdoor', 'playing'),
        (13, 25, 14, 'outdoor', 'wandering'),
        (16, 36, 5, 'outdoor', 'visiting'),     # kunjungi Maya
        (18, 30, 18, 'outdoor', 'pasarmalam'),
        (21, 10, 14, 'outdoor', 'returning'),
    ],
    'bowo': [
        (6,  20, 22, 'outdoor', 'chopping'),    # tebang kayu
        (12, 22, 3, 'shop', 'shopping'),
        (14, 25, 25, 'outdoor', 'building'),    # build di hutan
        (19, 22, 11, 'smith', 'visiting'),
        (22, 25, 25, 'outdoor', 'sleeping'),
    ],
    'ningsih': [
        (6,  29, 3, 'clinic', 'preparing'),
        (8,  29, 3, 'clinic', 'helping'),       # bantu Pak Raka
        (14, 25, 8, 'outdoor', 'home_visit'),   # kunjungi pasien
        (18, 30, 18, 'outdoor', 'pasarmalam'),
        (22, 29, 3, 'clinic', 'sleeping'),
    ],
    'pak_guru': [
        (7,  18, 14, 'outdoor', 'walking'),     # ke balai desa
        (8,  20, 14, 'outdoor', 'teaching'),    # ngajar
        (12, 22, 3, 'shop', 'lunch'),
        (14, 30, 5, 'outdoor', 'reading'),
        (20, 36, 5, 'outdoor', 'sleeping'),
    ],
    'mbok_jum': [
        (5,  10, 14, 'outdoor', 'preparing'),   # siapkan jamu
        (7,  20, 14, 'outdoor', 'selling'),     # jualan keliling
        (12, 30, 5, 'outdoor', 'selling'),      # ke pasar
        (16, 25, 18, 'outdoor', 'pasarmalam'),
        (21, 10, 14, 'outdoor', 'sleeping'),
    ],
    'jaka_ronda': [
        (6,  -1, -1, 'hidden', 'sleeping'),     # tidur siang
        (16, 22, 11, 'smith', 'preparing'),     # siapin pentungan
        (18, 30, 18, 'outdoor', 'patroling'),   # ronda pasar malam
        (22, 35, 22, 'outdoor', 'patroling'),   # ronda kuburan
        (4,  10, 8, 'outdoor', 'returning'),
    ],
    # Makhluk halus baru
    'kuntilanak': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (20, 8, 27, 'outdoor', 'haunting'),     # malam di pohon mati hutan
        (4,  -1, -1, 'hidden', 'dormant'),
    ],
    'pocong': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (21, 38, 26, 'outdoor', 'jumping'),     # kuburan
        (3,  -1, -1, 'hidden', 'dormant'),
    ],
    'genderuwo': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (19, 5, 30, 'outdoor', 'roaming'),       # hutan dalam
        (5,  -1, -1, 'hidden', 'dormant'),
    ],
    'wewe_gombel': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (22, 12, 32, 'outdoor', 'lurking'),     # pohon tua di hutan
        (4,  -1, -1, 'hidden', 'dormant'),
    ],
    'banaspati': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (20, 8, 28, 'outdoor', 'floating'),      # melayang di hutan dalam
        (4,  -1, -1, 'hidden', 'dormant'),
    ],
    'leak_bali': [
        (0,  -1, -1, 'hidden', 'dormant'),
        (23, 38, 25, 'outdoor', 'transforming'), # malam di kuburan
        (3,  -1, -1, 'hidden', 'dormant'),
    ],
    # Hewan tambahan
    'bebek_donald':   [(0, 6, 11, 'outdoor', 'swimming')],
    'domba_woolly':   [(0, 4, 10, 'outdoor', 'grazing')],
    'kuda_pegasus':   [(0, 7, 10, 'outdoor', 'standing')],
    'kucing_oren':    [(0, 5, 6, 'outdoor', 'lounging')],   # kucing di rumah
    'rubah_hutan':    [(0, 14, 22, 'outdoor', 'sneaking')],  # liar di hutan
    'kelinci_putih':  [(0, 16, 18, 'outdoor', 'hopping')],   # liar di rumput
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
