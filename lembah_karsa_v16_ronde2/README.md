# 🌱 Lembah Karsa v5 — Modular Edition

RPG farming Indonesia bertema mistis Nusantara, dibangun dengan Python + Pygame.
Inspirasi gaya: Harvest Moon: Back to Nature.

## ✨ Yang Baru di v5

### Arsitektur (rebuild major)
- **Modular 10 file** — `app.py` v4 (1441 baris) dipisah jadi `app.py` (orchestrator tipis) + `player.py` (PlayerController)
- **Asset pipeline lengkap** — `make_assets.py` generate ~340 file PNG ke folder `assets/`
- **Loader dengan fallback** — `sprites.py` baca PNG dari disk; jika belum ada, render kotak warna agar game tetap jalan
- **Composition pattern** — `PlayerController(game)` punya akses balik via `self.game.*`

### Konten Baru
- **Kuburan 3 zona**: `cemetery_z1` (depan, mudah) → `cemetery_z2` (tengah, ada crypt) → `cemetery_z3` (terdalam, altar batu)
- **Crypt indoor** — rumah Mbah Demit di `cemetery_z2`
- **3 gua**:
  - `bat_cave` — gua kelelawar dengan tile bat dropping (Genderuwo malam)
  - `crystal_cave` — kristal warna-warni (Banaspati malam, paling indah)
  - `naga_cave` — diperluas jadi 18×14 dengan stalagmit lebih banyak
- **Danau (`lake`)** — 24×16 dengan air terjun animasi, dermaga, perahu, eceng gondok ungu

### Dipertahankan dari v4
- 31 karakter lengkap dengan dialog & jadwal harian
- 12 manusia: Pak Arya, Bu Sari, Pak Raka, Maya, Budi, Pak Joko, Cici, Pak Bowo, Bu Ningsih, Pak Guru Hadi, Mbok Jum, Bang Jaka
- 10 makhluk halus: Naga Sang Hyang, Jin Kebun, Demit Tua, Tuyul, Kuntilanak, Pocong, Genderuwo, Wewe Gombel, Banaspati, Leak Bali
- 9 hewan: Sapi Betsy, Ayam Kuning, Kambing Jenggot, Bebek Donald, Domba Woolly, Kuda Pegasus, Kucing Oren, Rubah Liar, Kelinci Putih
- Smooth movement 8-arah (keyboard + mouse hold)
- SHIFT untuk lari (1.7×)
- Depth sort, parallax cloud, bayangan, fade transition
- Save/load JSON, schedule sistem, weather, night overlay

## 🎮 Cara Jalankan

```bash
# 1. Install pygame (sekali saja)
pip install pygame

# 2. Generate semua asset PNG (sekali, atau setiap kali ada perubahan visual)
python make_assets.py

# 3. Jalankan game
python main.py
```

> **Catatan**: `make_assets.py` opsional — game tetap jalan tanpa step ini, hanya saja
> sprite akan tampil sebagai kotak warna fallback (untuk debugging cepat).

## ⌨️ Kontrol

| Key | Aksi |
|-----|------|
| WASD / Arrow | Gerak (smooth, 8-arah) |
| Mouse hold (kiri) | Gerak ke arah kursor |
| SHIFT | Lari (1.7×) |
| SPACE | Pakai alat |
| E | Interaksi / Bicara |
| 1-6 | Pilih alat (Cangkul, Siram, Tanam, Panen, Kapak, Hadiah) |
| Q / R | Ganti benih |
| F | Tangkap makhluk halus |
| G | Lihat jadwal NPC |
| T | Tidur (di rumah) |
| I / M / J / H | Inventori / Peta / Quest / Hubungan |
| K / U | Toko (di Warung) / Upgrade (di Bengkel) |
| F5 / F9 | Save / Load |
| F1 / ESC | Bantuan |

## 📁 Struktur Project

```
lembah_karsa_v5/
├── main.py                    # entry point
├── make_assets.py             # generator asset PNG (procedural, port dari v4)
├── README.md
├── assets/                    # output make_assets.py (~340 PNG)
│   ├── tiles/                 # grass, dirt, water_0..3, waterfall_0..3, ...
│   ├── objects/               # tree, fence, fireplace_0..1, crops, ...
│   └── chars/                 # 26 folder karakter, masing-masing 12 frame PNG
│       ├── player/            # down_0.png, down_1.png, down_2.png, up_0..2, ...
│       ├── npc_arya/
│       ├── npc_sari/
│       └── ... (24 lagi)
└── game/
    ├── __init__.py
    ├── config.py              # konstanta + palette warna + tile IDs
    ├── data.py                # 31 NPC + dialog + schedule + crops + quest
    ├── state.py               # GameState dataclass + save/load
    ├── scenes.py              # 15 scene (outdoor + 6 indoor v4 + 8 baru v5)
    ├── entities.py            # wild entities + NPC AI multi-scene
    ├── sprites.py             # asset loader dengan fallback
    ├── player.py              # PlayerController — semua logic player [BARU]
    ├── panels.py              # UI panels (inventory, map, quest, dll)
    └── app.py                 # Game class tipis — event + render orchestration
```

## 🎨 Asset Pipeline

`make_assets.py` adalah port lengkap dari `sprites.py` v4 (procedural drawing 1500+ baris)
yang sekarang menulis output ke disk. Style yang dihasilkan:

- **Outline gelap 1px** di tepi sprite
- **3-tone shading** (highlight + base + shadow)
- **Mata ekspresif** dengan blink frame
- **Animasi 4 frame** (walk0, walk1, blink/idle) per arah
- **Naga oriental Indonesia** 96×64 dengan tubuh berliuk + jenggot emas
- **Procedural noise** untuk grass/dirt/path agar tidak repetitif

## 🐛 Troubleshooting

**Sprite muncul sebagai kotak warna**
→ Belum jalankan `python make_assets.py`. Jalankan sekali, lalu restart `main.py`.

**`ModuleNotFoundError: No module named 'pygame'`**
→ `pip install pygame` (atau `pip install pygame --break-system-packages` di Linux modern).

**Game crash saat masuk scene baru**
→ Pastikan menggunakan save baru (atau hapus `lembah_karsa_save.json`). Save lama dari v4
   masih kompatibel struktur, tapi posisi NPC mungkin perlu di-init ulang.

**Lampu lentera & api tidak animasi**
→ Pastikan `assets/objects/fireplace_0.png`, `fireplace_1.png`, `lantern_0.png`,
   `lantern_1.png` ada. Jalankan ulang `make_assets.py`.

## 📝 Versi

- **v5.0** (sekarang) — rebuild modular, asset pipeline, ekspansi dunia
- **v4** — 26+ karakter, depth sort, smooth movement, single outdoor scene
- **v3** dan sebelumnya — prototype awal
