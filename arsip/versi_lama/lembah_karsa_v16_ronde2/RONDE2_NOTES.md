# Lembah Karsa v5 — Ronde 2 (Crash Fix + NPC Tidak Mengapung)

## 🐛 Bug Crash yang Ditemukan & Diperbaiki

**Lokasi**: `game/entities.py` → `update_animal_roaming()` → `can_walk_at()`

**Akar masalah**: Ronde 1 saya ubah `pos['x']` dan `pos['y']` jadi float (untuk smooth movement). Tapi `update_animal_roaming` menambahkan `dx + pos['x']` (int + float = float), lalu pakai sebagai index ke `tiles[ny][nx]` → **TypeError: list indices must be integers or slices, not float**.

**Fix**:
1. `can_walk_at()` sekarang cast input ke int dengan `int(round(x))` — defensive.
2. `update_animal_roaming` ambil `cur_x = int(round(pos['x']))` sebelum random walk, simpan kembali sebagai float.
3. `player.can_walk()` juga di-cast defensive.

**Verifikasi**: smoke test (mock pygame) jalankan 3000 frame + 18 scene transitions + 24h day cycle tanpa crash.

## 🚶 Bug "NPC Mengapung" yang Diperbaiki

**Akar masalah**: Sprite character di-generate sebagai `TILE × TILE × 1.5` (32×48). Walaupun secara matematis kaki sprite ada di bottom tile, scaling 16×16 → 32×48 (factor 2:3 vertikal vs 2:1 horizontal) menyebabkan distorsi proporsi yang membuat kepala besar dan kaki tampak "menggantung".

**Fix**: Ubah ukuran sprite character ke `TILE × TILE` (32×32 square), sama dengan tile. Ini meniru pattern V15. Kaki sprite menapak tepat di bottom tile, tidak ada offset.

**File yang berubah**:
- `make_assets.py`: `target_h = 64 if is_huge else TILE` (sebelumnya `int(TILE * 1.5)`)
- `game/sprites.py`: same di `load_char_anim()`

**Naga**: TETAP huge 96×64 (3×2 tile). Render code di app.py sudah handle ini terpisah.

## 🎨 Sprite Naga (Carry-over dari Ronde 1)

Sprite dari `naga_master.png` Anda sudah ter-extract dan ada di `assets/chars/npc_naga/` (12 PNG, 4 arah × 3 frame, 96×64 dengan transparent background).

## ✅ Yang Sudah Berfungsi

- Smooth NPC movement (interpolasi 1.5 tile/sec ke target schedule)
- NPC facing mengikuti arah gerak
- Walk animation aktif saat NPC bergerak, idle frame saat diam
- Naga sprite kustom Anda
- Game tidak crash di 3000 frame simulasi

## ❓ Pertanyaan yang Masih Saya Tunggu

Sebelum saya kerjakan fitur besar (dungeon, combat, boss), saya butuh jawaban Anda:

1. **Combat style** — Action (Z/X swing) / Auto-attack (Vampire Survivors) / Hybrid?
2. **NPC pathfinding** — Simple (sekarang) / A* lengkap / Hybrid?
3. **Multi-world split** — Pisah outdoor 50×35 jadi 3-4 peta (konservatif) atau 8-10 peta (agresif)?
4. **Berapa level kedalaman gua**? Saya usulkan 15 level dalam 3 area (atas/tengah/dalam)
5. **Crafting alat baru** — pickaxe + pedang + tangga + bom OK?
6. **Sprite mob hostile** — reuse supernatural / generate baru / kombinasi?
7. **Ukuran naga di game** — tetap 96×64 huge atau standar 32×32?
8. **Save compatibility** — ada save lama atau bebas redesign GameState?
9. **Urutan implementasi**: multi-world → dungeon → combat → crafting → boss → cutscene OK?

## 🧪 Cara Test

```bash
cd lembah_karsa_v5
pip install pygame
python make_assets.py    # Generate ulang asset (ukuran sprite character berubah!)
python main.py           # Mainkan
```

**Penting**: Setelah update ronde 2, Anda WAJIB run `make_assets.py` lagi karena ukuran sprite character berubah dari 32×48 ke 32×32. Kalau Anda tidak regenerate, asset lama akan di-stretch ke ukuran baru oleh sprite loader (mungkin tampak aneh).
