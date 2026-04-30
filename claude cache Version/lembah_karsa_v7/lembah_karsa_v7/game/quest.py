"""
quest.py — Quest engine "Kutukan Akar Karsa".

Pemain mewarisi kebun Paman Arsa dan harus menyembuhkan Sang Naga
yang terinfeksi miasma di lantai dasar Gua Sang Hyang.
"""

# Quest stages: tuple (id, judul, deskripsi, hint_lokasi, completion_check_key)
QUESTS = [
    {
        'id': 'intro',
        'title': '📜 Surat Paman Arsa',
        'desc': 'Baca surat di kotak pos depan rumah.',
        'hint': 'Kotak pos di depan rumah farm',
        'flag': 'mail_read',
    },
    {
        'id': 'first_harvest',
        'title': '🌱 Panen Pertama',
        'desc': 'Tanam dan panen 3 lobak. Ini buktikan kamu serius.',
        'hint': 'Cangkul tanah → tanam benih → siram → tunggu',
        'flag': 'lobak_3_harvested',
    },
    {
        'id': 'meet_jin',
        'title': '✨ Jin Kebun',
        'desc': 'Temui Jin Kebun di malam hari. Ia bilang ada bahaya.',
        'hint': 'Datang ke farm jam 20:00+',
        'flag': 'met_jin',
    },
    {
        'id': 'first_blade',
        'title': '⚔️ Pedang Pertama',
        'desc': 'Datangi Budi si pandai besi, buat pedang kayu.',
        'hint': 'Town → Smith (jam 7-19) → craft sword_kayu',
        'flag': 'has_sword',
    },
    {
        'id': 'enter_dungeon',
        'title': '🏞️ Pintu Gua Sang Hyang',
        'desc': 'Pergi ke gunung, masuk Gua Naga. Turun ke dungeon level 1.',
        'hint': 'Mountain → Naga Cave → STAIRS_DOWN',
        'flag': 'reached_dungeon_1',
    },
    {
        'id': 'first_kill',
        'title': '👹 Pertarungan Pertama',
        'desc': 'Kalahkan 5 mob hostile di dungeon. Tekan Z untuk menyerang.',
        'hint': 'Z = swing pedang ke arah hadap',
        'flag': 'mobs_killed_5',
    },
    {
        'id': 'reach_deep',
        'title': '⛏️ Eksplorasi Mendalam',
        'desc': 'Turun hingga dungeon level 5. Bawa pickaxe untuk tambang.',
        'hint': 'Beli pickaxe di Budi → X = mining',
        'flag': 'reached_dungeon_5',
    },
    {
        'id': 'find_seed_kuno',
        'title': '🌾 Benih Kuno',
        'desc': 'Temukan "Benih Kuno" dari mob di dungeon level 6+.',
        'hint': 'Drop random dari mob lv 6+',
        'flag': 'has_seed_kuno',
    },
    {
        'id': 'grow_penawar',
        'title': '🌿 Tanaman Penawar',
        'desc': 'Tanam Benih Kuno di kebun. Tanaman Penawar akan tumbuh.',
        'hint': 'Cangkul → tanam benih_kuno → siram → 5 hari',
        'flag': 'grown_penawar',
    },
    {
        'id': 'face_naga',
        'title': '🐉 Sang Naga Bata Merah',
        'desc': 'Turun ke level 15. Sang Naga mengamuk karena miasma. Bawa Tanaman Penawar.',
        'hint': 'Dungeon level 15 — bawa minimal 3 tanaman_penawar',
        'flag': 'naga_encountered',
    },
    {
        'id': 'heal_naga',
        'title': '💚 Penyembuhan',
        'desc': 'Hindari semburan api. Tanam Tanaman Penawar di altar arena saat naga lemah.',
        'hint': 'Z untuk hit naga sampai stagger → SPACE di altar untuk tanam',
        'flag': 'naga_healed',
    },
    {
        'id': 'epilog',
        'title': '🌅 Lembah Karsa Pulih',
        'desc': 'Naga sembuh dan memberkati lembah. Air keabadian mengalir di kebunmu.',
        'hint': '— TAMAT —',
        'flag': 'game_complete',
    },
]


def check_quest_progress(state):
    """Update quest_stage berdasarkan flags & stats. Return True jika ada perubahan."""
    cur = state.quest_stage
    if cur >= len(QUESTS):
        return False
    quest = QUESTS[cur]
    flag = quest['flag']
    completed = False

    if flag == 'mail_read' and state.mail_read:
        completed = True
    elif flag == 'lobak_3_harvested' and state.stats.get('lobak_harvested', 0) >= 3:
        completed = True
    elif flag == 'met_jin' and state.met_jin:
        completed = True
    elif flag == 'has_sword' and state.sword_id != '':
        completed = True
    elif flag == 'reached_dungeon_1' and state.stats.get('deepest_level', 0) >= 1:
        completed = True
    elif flag == 'mobs_killed_5' and state.stats.get('mobs_killed', 0) >= 5:
        completed = True
    elif flag == 'reached_dungeon_5' and state.stats.get('deepest_level', 0) >= 5:
        completed = True
    elif flag == 'has_seed_kuno' and state.inventory.get('benih_kuno', 0) > 0:
        completed = True
    elif flag == 'grown_penawar':
        # Cek ada soil dengan crop='tanaman_penawar' yang sudah matang
        for key, soil in state.soil.items():
            if soil.get('crop') == 'tanaman_penawar' and soil.get('age', 0) >= 5:
                completed = True
                break
    elif flag == 'naga_encountered' and state.stats.get('deepest_level', 0) >= 15:
        completed = True
    elif flag == 'naga_healed' and state.naga_defeated:
        completed = True

    if completed:
        state.quest_stage += 1
        return True
    return False


def get_current_quest(state):
    """Return current active quest dict, atau None jika sudah tamat."""
    if state.quest_stage >= len(QUESTS):
        return None
    return QUESTS[state.quest_stage]
