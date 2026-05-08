# Lembah Karsa v6 — Modular Edition

Berdasarkan arsitektur V15 Gemini (lebih bersih dari v5).

## Fitur Baru

**Multi-world:** farm + town + mountain + lake + cemetery + 5 indoor + naga_cave + dungeon

**Dungeon roguelike:** 15 level, cellular automata, ore tiles per kedalaman, mob hostile, boss naga di lv 15

**Combat action-style:**
- Z = attack (swing radius 1.5 tile)
- X = mining (pickaxe)
- HP bar di HUD, invuln frames, KO respawn rumah
- 5 tier sword: kayu→besi→emas→mithril→keabadian

**Mining 5 tier pickaxe** untuk ore: tembaga, besi, emas, kristal, mithril

**Sprite naga** Anda extracted ke `assets/chars/naga/` (12 PNG transparent)

**NPC smooth (V15 base):** tuyul kabur, hewan tidur malam, jin melayang

## Run

```bash
cd lembah_karsa_v6
pip install pygame
python make_assets.py
python main.py
```

## Kontrol

WASD/arrow gerak, SHIFT lari, mouse hold gerak ke cursor.
SPACE alat farming, **Z attack**, **X mining**, E interaksi, F tangkap halus, G jadwal NPC.
1-6 alat, Q/R benih, T tidur. I/M/J/H panel. F5/F9 save/load.

## Test Status

Smoke test pass 3000 frame + 18 scene + dungeon lv5 + combat + mining. **No crash**.
