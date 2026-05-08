# Lembah Karsa v5 — Ronde 1 (Bug Fixes)

Catatan: Ini ronde pertama. Saya menunggu jawaban Anda untuk pertanyaan combat style, NPC pathfinding kompleksitas, multi-world split, jumlah level gua, alat crafting, sprite mob, ukuran naga di game, save compat, dan urutan prioritas, sebelum saya kerjakan fitur besar (dungeon, combat, boss).

## Perubahan di Ronde 1

### 1. Sprite Naga dari `naga_master.png` Anda
- Diekstrak dari gambar Anda, latar checker pattern dibuang dengan filter warna
- Output: 12 PNG (4 arah × 3 frame) di `assets/chars/npc_naga/`
- Ukuran: 96×64 (huge sprite, tetap konsisten dengan v4)
- Sprite ini akan dipakai langsung (skip generate procedural di make_assets.py)
- File `extract_naga.py` ada di working dir kalau Anda mau regenerate

### 2. Smooth NPC Movement
- NPC sekarang berjalan halus ke target schedule (interpolasi 1.5 tile/detik)
- Tidak lagi teleport saat jam ganti
- Facing sprite NPC mengikuti arah gerak (right/left/up/down)
- Animasi walk frame aktif hanya saat NPC sedang bergerak
- Saat NPC pindah scene, tetap teleport (tidak smooth-walk lintas-scene)
- Implementasi: `update_npc_smooth_movement()` di `entities.py`, dipanggil tiap frame dari `app.py`

### 3. Tentang "NPC Mengapung"
Saya sudah verifikasi logic render-nya. Kalkulasinya:
- Sprite tinggi 48px (TILE × 1.5)
- Tile tinggi 32px
- offset_y = -16 → kepala sprite extending ke tile atas, kaki tepat di bottom tile

**Kalau masih terlihat mengapung saat Anda jalankan**, kemungkinan penyebab:
- Anda belum jalankan `python make_assets.py` sehingga masih pakai fallback color box (kotak warna 32×48 terlihat seperti tinggi 1.5× karakter dengan kaki "tidak ada", jadi ada gap visual)
- Atau ada issue spesifik dengan generated sprite v4 yang punya whitespace di bawah baris 15

Saran: jalankan `python make_assets.py` lalu screenshot apa yang Anda lihat sehingga saya bisa diagnosa lebih akurat.

## Yang BELUM Dikerjakan (Menunggu Klarifikasi Anda)

1. **Multi-world split** (Q4: konservatif 3-4 peta atau agresif 8-10?)
2. **Combat style** (Q1: action / auto-attack / turn-based?)
3. **NPC pathfinding kompleksitas** (Q2: simple interp / A* / hybrid?)
4. **Dungeon system** (Q5: berapa level? saya usulkan 15 level dalam 3 area)
5. **Crafting & alat baru** (Q6: pickaxe + pedang + tangga + bom OK?)
6. **Mob hostile sprites** (Q7: reuse supernatural / sprite baru / kombinasi?)
7. **Ukuran naga di game** (Q8: tetap 96×64 huge atau standar 32×48?)
8. **Save compatibility** (Q9: ada save lama atau bebas redesign?)
9. **Urutan implementasi** (Q10: setuju dengan urutan saya?)

## Cara Test Ronde 1

```bash
cd lembah_karsa_v5
pip install pygame
python make_assets.py
python main.py
```

Yang harus saya verifikasi dari sisi Anda:
1. **Apakah NPC sekarang bergerak halus** saat jam ganti dari Anda perhatikan? (sebelumnya teleport)
2. **Apakah naga muncul dengan sprite Anda** atau masih procedural lama?
3. **Apakah masih ada "mengapung" issue** setelah make_assets.py dijalankan? Kalau ya, screenshot tolong.
