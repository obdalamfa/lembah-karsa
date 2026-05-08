# Lembah Karsa v7r3 — Open World + Crisp Pixel + NPC Hidup

## Update Ronde Ini

### 1. NPC Lebih Hidup (jadwal + dialog kontekstual)
**138 schedule entries** total — rutinitas detail per NPC, contoh:
- **Bu Sari**: 5:00 siapkan dagangan → 8:00 buka warung → 17:00 tutup → 18:00 ngobrol di alun-alun → 21:00 tidur
- **Pak Joko**: 4:00 mancing → 13:00 jual ikan ke Sari → 15:00 mancing lagi → 22:00 tidur di pinggir danau
- **Pak Raka (tabib)**: 6:00 buka klinik → 13:00 cari herba di gunung → 16:00 konsul → 23:00 tidur
- **Maya (seniman)**: 7:00 melukis di studio → 10:00 cari inspirasi di town → 12:00 sketsa kebun → 15:00 lukis pemandangan gunung

**Dialog kontekstual**: NPC bicara berbeda berdasarkan aktivitas saat ini:
- Sari saat **working**: "Selamat datang di warung Sari!"
- Sari saat **gossiping**: "Eh, dengar tidak? Ada yang lihat kuntilanak di danau..."
- Joko saat **fishing**: "Ssh... ikan lagi banyak."
- Joko saat **fishing_night**: "Malam ini ikan besar suka muncul. Kuntilanak? Ah, aku tidak takut."

12 NPC sudah punya dialog kontekstual.

### 2. Crisp Pixel Style (RPG Maker)
- **Color palette diperbaharui**: warna kontras lebih tinggi, saturasi naik 15-25%
- **Outline tegas** di semua character sprite (warna `(15, 8, 12)` hampir hitam)
- Tile rumput, tanah, jalan lebih kontras visual
- NPC clothes warna unik, mudah dibedakan

### 3. Dunia Open World (2× Lebih Besar)
| Scene | Sebelum | Sekarang |
|-------|---------|----------|
| Farm | 25×20 | **40×30** |
| Town | 30×25 | **45×35** |
| Mountain | 30×25 | **40×35** |

**Landmark baru:**
- **Farm**: rumah utama + halaman, kandang ternak besar (10×8 tile), **sungai kecil** dengan jembatan, **tugu lentera tengah**, pohon-pohon scattered
- **Town**: alun-alun pusat dengan 4 lentera + tugu, 6 bangunan (Warung Sari, Klinik, Studio Maya, **Sekolah Pak Guru**, Smith Budi, Greenhouse), counter pasar, jalan utama berpotongan
- **Mountain**: hutan rimbun (80 pohon random), **sungai dengan jembatan**, gua entrance dengan dead trees atmosfer, **kuburan tua** mini di pinggir, jalan setapak berliku

## Konten v7 (carry over)

- **14 scene** (farm, town, mountain, lake, cemetery, naga_cave, dungeon, house, **basement**, shop, clinic, studio, smith, greenhouse)
- **31 NPC** dengan rutinitas detail
- **Combat system**: Z attack diganti dengan slot weapon (Pedang/Tombak/Panah/Pickaxe)
- **Hospital revive**: HP 0 atau Energy 0 → respawn clinic
- **Dungeon roguelike 15 level** + 8 mob hostile + naga boss
- **WASD only + mouse hold** movement
- **Slot 1-9 + 0** untuk pilih alat (icon emoji)
- **Tab** cycle alat
- **Rumah jalan rahasia** → basement

## Run
```bash
cd lembah_karsa_v7
pip install pygame
python main.py
```

## Smoke Test
3000 frame + 18 scene transitions + dungeon lv5 + combat + ascend. **No crash**.

## Stats Code
- **4737 baris** total
- 138 schedule entries
- 12 NPC dengan dialog kontekstual
- 14 scene (3 outdoor besar + 7 indoor + lake + cemetery + naga_cave + dungeon)
