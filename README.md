# Lembah Karsa

Farming RPG berbasis Python terinspirasi Harvest Moon & Rune Factory, dengan makhluk halus Nusantara (jin, demit, tuyul, mandrake). Tersedia dalam dua versi: **2D** (Pygame) dan **3D** (Ursina/Panda3D).

---

## Versi 2D (utama)

### Cara Menjalankan

```bash
pip install pygame-ce
python main.py
```

### Struktur

```
lembah-karsa/
├── main.py          ← entry point 2D
├── game/            ← modul permainan 2D
│   ├── app.py       ← game loop & rendering
│   ├── config.py    ← konstanta & palette warna
│   ├── data.py      ← crop, NPC, quest, jadwal
│   ├── sprites.py   ← generator pixel art prosedural
│   ├── scenes.py    ← definisi peta & portal
│   ├── state.py     ← GameState + save/load JSON
│   ├── entities.py  ← AI NPC & makhluk liar
│   ├── panels.py    ← UI (inventori, peta, quest)
│   ├── particles.py ← efek partikel
│   └── sound.py     ← audio prosedural (tanpa file audio)
├── assets/          ← sprite PNG
├── 3d/              ← versi 3D (lihat 3d/README.md)
├── legacy/          ← versi single-file lama (referensi)
├── tools/           ← utilitas pembuatan aset
└── arsip/           ← arsip versi-versi lama
```

### Kontrol

| Tombol | Aksi |
|--------|------|
| WASD / Arrow | Gerak |
| SHIFT | Lari (1.7×) |
| SPACE | Pakai alat |
| E | Interaksi / Bicara |
| F | Tangkap makhluk halus |
| 1–6 | Pilih alat |
| I | Inventori |
| M | Peta dunia |
| J | Quest log |
| H | Hubungan NPC |
| K | Toko (di Warung) |
| U | Upgrade (di Bengkel) |
| F5 / F9 | Save / Load |
| F1 | Bantuan kontrol |

### Fitur

- **Bertani:** 8 jenis tanaman dengan siklus musim
- **NPC:** 5 warga desa + 3 makhluk halus (Jin Kebun, Demit Pengganggu, Tuyul) dengan jadwal harian
- **Makhluk liar:** Mandrake, Jamur Lari, Kunang-kunang (malam), Herba & Berry liar
- **Waktu:** 4 musim × 28 hari, siklus siang-malam
- **Relasi:** Sistem hati NPC, preferensi hadiah
- **Upgrade:** Cangkul, kaleng siram, kapak, tas
- **Audio prosedural:** Semua suara dibuat dari sine/square wave (tanpa file audio)
- **Sprite prosedural:** Semua pixel art dibuat dari kode (tanpa file gambar eksternal)

---

## Versi 3D

Lihat [3d/README.md](3d/README.md) untuk petunjuk menjalankan versi Ursina.

---

## Menambah Konten

**Tanaman baru** — edit `CROPS` di [game/data.py](game/data.py):
```python
'kentang': {'name':'Kentang', 'days':4, 'sell':40, 'cost':9, 'seasons':['Gugur']},
```

**NPC baru** — edit `HUMAN_NPCS` + `SCHEDULES` di [game/data.py](game/data.py).

**Scene baru** — tambah fungsi `build_xxx()` di [game/scenes.py](game/scenes.py), daftarkan ke `SCENES`.

---

## Dependensi

| Versi | Paket |
|-------|-------|
| 2D | `pygame-ce` |
| 3D | `ursina >= 5.0.0` |
