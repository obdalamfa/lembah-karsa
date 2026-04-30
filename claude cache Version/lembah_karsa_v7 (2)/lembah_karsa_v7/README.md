# Lembah Karsa v7 — V4 Gemini Visual + v6 Complexity

Game farming + dungeon RPG bertema Indonesia.

## Visual (dari V4 Gemini)
- Sprite character **HM:BTN style chibi**: 3-tone shading, mata ekspresif, blink, blush
- Isi rumah lengkap: kasur, peti, rak buku, cermin, kompor, jam, perapian, pot bunga
- Animasi smooth, weather (hujan/awan), day/night cycle

## Konten Lengkap (dari v6)
- **13 scene**: farm, town, mountain, lake, cemetery, naga_cave, dungeon + 6 indoor
- **31 NPC**: 12 manusia + 10 supernatural (jin, tuyul, demit, kuntilanak, pocong, genderuwo, wewe, banaspati, leak, naga) + 9 hewan ternak
- **Smooth NPC AI**: tuyul kabur dari player, hewan tidur malam, jin melayang lambat
- **8 tanaman**: lobak, wortel, stroberi, jagung, tomat, labu, bayam, jamur
- **5 wild items**: mandrake, jamur lari, kunang-kunang, herba, beri liar

## Combat & Dungeon
- **Dungeon roguelike 15 level** (cellular automata, regen tiap turun)
- **5 jenis ore**: tembaga, besi, emas, kristal, mithril (makin dalam makin langka)
- **8 mob hostile**: kelelawar, tikus gua, laba-laba, genderuwo, kuntilanak, banaspati, leak, pocong/demit
- **Boss naga** di level 15 dengan sprite kustom Anda
- **Z attack** + **X mining** (action-style)
- **HP bar**, KO respawn rumah dengan HP penuh + energi 50%
- **5-tier sword** (kayu→keabadian, damage 5+10..5+100)
- **5-tier pickaxe** (kayu→mithril)

## Stats
- **4350 baris** source code modular
- 13 scene, 31 NPC, 8 mob types, 8 tanaman, 5 ore, 15 dungeon levels

## Cara Run
```bash
cd lembah_karsa_v7
pip install pygame
python main.py
```
Sprite naga Anda sudah ada di `assets/chars/naga/` (12 PNG, 4 arah × 3 frame).

## Kontrol
| Tombol | Fungsi |
|--------|--------|
| WASD/Arrow | Gerak |
| SHIFT | Lari |
| Mouse hold | Gerak ke cursor |
| SPACE | Alat farming |
| **Z** | **Attack** |
| **X** | **Mining** |
| E | Interaksi/bicara |
| F | Tangkap halus |
| G | Jadwal NPC |
| 1-6 | Pilih alat |
| Q/R | Ganti benih |
| T | Tidur (di kasur) |
| I/M/J/H | Inv/Map/Quest/Hubungan |
| K/U | Toko/Upgrade |
| F5/F9 | Save/Load |

## Test Status
Smoke test pass: 3000 frame + 18 scene transitions + dungeon lv5 + combat hit + ascend. **No crash**.
