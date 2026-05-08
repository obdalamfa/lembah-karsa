# Lembah Karsa v7 — Visual V4 Gemini + Combat

Berdasarkan **V4 Gemini** untuk visual (sprite HM-style chibi, isi rumah lengkap), 
dengan tambahan dungeon roguelike + combat dari v6.

## Visual (dari V4 Gemini)
- Sprite character HM:BTN style: chibi, 3-tone shading, mata ekspresif, blink
- Map: farm + town (3 rumah + clinic + studio + smith + greenhouse) + mountain + naga_cave
- Isi rumah lengkap: kasur, peti, rak buku, cermin, kompor, jam, pot bunga, perapian
- Animasi smooth movement, hujan, awan, malam overlay

## Tambahan v7
- **Sprite naga Anda** (dari naga_master.png) di `assets/chars/naga/`
- **Dungeon roguelike 15 level** — generated per turun (Spelunky-style)
- **Ore tiles**: tembaga, besi, emas, kristal, mithril (makin dalam makin langka)
- **Mob hostile**: kelelawar, laba-laba, genderuwo, kuntilanak, banaspati, leak, pocong, demit
- **Combat action-style**: Z attack, X mining
- **HP bar** di HUD, KO respawn rumah dengan HP penuh
- **5 tier sword**: kayu→keabadian (damage 5+10..5+100)
- **5 tier pickaxe**: tier 1 tembaga, tier 4 mithril
- **Boss naga** di level 15

## Cara Run
```bash
cd lembah_karsa_v7
pip install pygame
python main.py
```

## Kontrol
| Tombol | Fungsi |
|--------|--------|
| WASD/Arrow | Gerak |
| SHIFT | Lari |
| SPACE | Alat farming |
| **Z** | **Attack** |
| **X** | **Mining** |
| E | Interaksi |
| F | Tangkap halus |
| 1-6 | Pilih alat |
| Q/R | Ganti benih |
| T | Tidur |
| I/M/J/H | Inv/Map/Quest/Hub |
| F5/F9 | Save/Load |

## Test Status
Smoke test pass: 3000 frame + 18 transitions + dungeon lv5 + combat + mining. **No crash**.
