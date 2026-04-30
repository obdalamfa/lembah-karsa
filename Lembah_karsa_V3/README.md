# 🌱 Lembah Karsa v2.5 — Modular Edition

Farming RPG dengan makhluk halus Nusantara, dibangun dengan Python + Pygame.
Sekarang dalam **struktur modular** untuk maintainability.

---

## ✨ FITUR FASE 1 (BARU di v2.5)

### 🎮 SMOOTH MOVEMENT
- **Slide antar tile** dengan interpolasi pixel — tidak teleport lagi!
- **Tahan SHIFT untuk lari** (1.7× kecepatan)
- **Camera smooth follow** dengan lerp lembut (bukan snap kaku)
- 60 FPS untuk gerakan halus

### 🎨 SPRITE UPGRADE (HM:BTN style)
- **Outline gelap** di tepi sprite (definisi lebih jelas)
- **3-tone shading** — highlight di atas, base, shadow di bawah
- **Mata ekspresif** dengan pupil biru + sparkle
- **Pipi rosy (blush)** untuk vibes Harvest Moon
- **Animasi blink** — player kedip tiap ~3 detik
- **Topi dengan pita gelap** (detail kecil bermakna)

### 📦 STRUKTUR MODULAR
```
lembah_karsa/
├── main.py                  ← Entry point (8 baris!)
├── README.md
└── game/
    ├── __init__.py
    ├── config.py            ← Konstanta, palette, tile IDs (129 baris)
    ├── data.py              ← Crops, NPCs, dialogs, schedules (209 baris)
    ├── sprites.py           ← Generator pixel art (868 baris)
    ├── scenes.py            ← Definisi peta (219 baris)
    ├── state.py             ← GameState + save/load (115 baris)
    ├── entities.py          ← Wild creatures + NPC AI (192 baris)
    ├── panels.py            ← UI panels (240 baris)
    └── app.py               ← Game class + main loop (1258 baris)
```

**Total: ~3,200 baris** dipecah jadi 10 file. Lebih mudah dikembangkan!

---

## 🚀 CARA MENJALANKAN

```bash
# Install pygame
pip install pygame-ce

# Jalankan
cd lembah_karsa
python main.py
```

---

## 🎮 KONTROL

### Movement
| Tombol | Aksi |
|--------|------|
| **WASD** / **Arrow** | Gerak smooth |
| **SHIFT** (tahan) | Lari (1.7×) |

### Action
| Tombol | Aksi |
|--------|------|
| **SPACE** | Pakai alat aktif |
| **E** | Interaksi / Bicara |
| **F** | Tangkap makhluk halus |
| **G** | Lihat jadwal NPC dekat |
| **T** | Tidur (di rumah) |
| **1-6** | Pilih alat |
| **Q/R** | Ganti benih |

### Panels
| Tombol | Buka |
|--------|------|
| **I** | Inventori |
| **M** | Peta dunia |
| **J** | Quest log |
| **H** | Hubungan NPC |
| **K** | Toko (di Warung) |
| **U** | Upgrade (di Bengkel) |
| **F1** | Bantuan kontrol |

### System
| Tombol | Aksi |
|--------|------|
| **F5** | Save game |
| **F9** | Load game |
| **ESC** | Menu/tutup panel |

---

## 🛠 CARA TAMBAH FITUR

Karena modular, tambah konten gampang banget:

### Tambah tanaman baru
Edit `game/data.py`:
```python
CROPS = {
    ...
    'kentang': {'name':'Kentang','days':4,'sell':40,'cost':9,'seasons':['Gugur']},
}
```

### Tambah NPC baru
Edit `game/data.py`:
```python
HUMAN_NPCS = {
    ...
    'pak_eko': {
        'name':'Pak Eko','type':'human','gift':'wortel',
        'talks':[['Halo nak!']],
        'gift_r':'Terima kasih!'
    },
}
SCHEDULES['pak_eko'] = [
    (6, 10, 5, 'outdoor', 'walking'),
    (12, 22, 3, 'shop', 'shopping'),
]
```

### Tambah scene baru
Edit `game/scenes.py`, tambah fungsi `build_xxx()`, masukkan ke dict `SCENES`.

### Tambah sprite baru
Edit `game/sprites.py`, tambah fungsi `make_xxx()`, daftarkan di `init_sprites()`.

---

## 📋 ROADMAP — Fase Selanjutnya

### Fase 2: Karakter & Dunia
- 🐉 Naga Bijak — NPC besar 64x48 di gua
- A* Pathfinding untuk NPC
- Tambang scene baru

### Fase 3: Naratif
- Cutscene system dengan kamera scripted
- Side quest dari NPC
- Marriage prep

---

Selamat bermain! 🌾✨
