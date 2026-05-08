import pygame
import os
import time

# =========================================================================
# CHIMERA SPRITE PROCESSOR - ASSET PIPELINE
# =========================================================================
# Potong spritesheet PNG menjadi frame individual yang dibutuhkan game.
#
# Cara pakai:
#   1. Taruh file spritesheet di jalur 'file' di bawah
#   2. Jalankan: python chimera_processor.py
#   3. Frame hasil potongan masuk ke folder assets/
#
# Konvensi nama output:  {direction}_{frame}.png
#   direction: down, up, left, right
#   frame    : 0, 1 (game memakai 2 frame per arah)

CONFIGS = [
    # ── NAGA BOSS ────────────────────────────────────────────────
    {
        "file": "Lembah_karsa_V16_gemini/naga_master.png",
        "char_name": "npc_naga",           # → assets/chars/npc_naga/
        "grid": (3, 4),                    # (kolom, baris)
        "directions": ['down', 'up', 'left', 'right'],
        "scale_factor": 3,
        "color_key": (204, 204, 204),
        "out_base": "assets/chars",
    },

    # ── DEWA HUTAN BOSS ──────────────────────────────────────────
    # Taruh spritesheet dewa_hutan.png di root folder, lalu uncomment:
    # {
    #     "file": "dewa_hutan_master.png",
    #     "char_name": "boss/dewa_hutan",    # → assets/chars/boss/dewa_hutan/
    #     "grid": (4, 3),                    # 4 kolom, 3 baris (idle/attack/hurt)
    #     "directions": ['down', 'down', 'down'],  # semua baris = down (boss satu arah)
    #     "scale_factor": 3,
    #     "color_key": None,
    #     "out_base": "assets/chars",
    # },

    # ── PLAYER ───────────────────────────────────────────────────
    # {
    #     "file": "player_master.png",
    #     "char_name": "player",             # → assets/chars/player/
    #     "grid": (3, 4),                    # 3 frame, 4 arah
    #     "directions": ['down', 'up', 'left', 'right'],
    #     "scale_factor": 1,
    #     "color_key": None,
    #     "out_base": "assets/chars",
    #     "frame_prefix": "player_",         # → player_down_0.png
    # },

    # ── NPC STANDAR ──────────────────────────────────────────────
    # {
    #     "file": "npc_arya_master.png",
    #     "char_name": "npc/arya",           # → assets/chars/npc/arya/
    #     "grid": (2, 4),
    #     "directions": ['down', 'up', 'left', 'right'],
    #     "scale_factor": 1,
    #     "color_key": None,
    #     "out_base": "assets/chars",
    # },

    # ── MOB: SERIGALA ────────────────────────────────────────────
    # {
    #     "file": "serigala_master.png",
    #     "char_name": "mob/serigala",       # → assets/chars/mob/serigala/
    #     "grid": (4, 3),                    # 4 frame, 3 arah (down/left/right)
    #     "directions": ['down', 'left', 'right'],
    #     "scale_factor": 1,
    #     "color_key": None,
    #     "out_base": "assets/chars",
    # },

    # ── MOB: TUYUL ───────────────────────────────────────────────
    # {
    #     "file": "tuyul_master.png",
    #     "char_name": "mob/tuyul",
    #     "grid": (4, 3),
    #     "directions": ['down', 'left', 'right'],
    #     "scale_factor": 1,
    #     "color_key": None,
    #     "out_base": "assets/chars",
    # },
]

# Konvensi folder output per karakter
ASSET_PATHS = {
    # key: (subfolder_dalam_assets, deskripsi)
    "tiles":   ("assets/tiles/",   "Tiles tanah & air:  grass, dirt, path, tilled_dry, tilled_wet, water_0..3"),
    "objects": ("assets/objects/", "Objek 1-tile:        tree, fence, door, chest, bed, stove, table, ..."),
    "items":   ("assets/items/",   "Ikon alat (28x28):  cangkul, siram, tanam, panen, kapak, pancing, hadiah"),
    "crops":   ("assets/crops/",   "Tanaman per tahap:  lobak_0..3, wortel_0..3, jagung_0..3, tomat_0..3, ..."),
    "player":  ("assets/chars/player/",        "Karakter pemain:   player_down_0/1, player_up_0/1, ..."),
    "npc":     ("assets/chars/npc/{id}/",      "NPC desa:          arya, sari, raka, maya, budi"),
    "mob":     ("assets/chars/mob/{id}/",      "Mob:               serigala, tuyul, jin, betsy, ..."),
    "boss":    ("assets/chars/boss/dewa_hutan/","Boss:              dewa_hutan (atau npc_naga/)"),
}


def remove_checker_bg(surf, color_key=None):
    """Hapus background putih/abu checkered atau warna tertentu."""
    if color_key:
        surf.set_colorkey(color_key)
        return surf
    bg = surf.get_at((0, 0))
    for y in range(surf.get_height()):
        for x in range(surf.get_width()):
            c = surf.get_at((x, y))
            if c[3] > 0:
                is_bg = (c[:3] == bg[:3])
                is_gray = (c[0] > 180 and c[1] > 180 and c[2] > 180
                           and abs(c[0]-c[1]) < 15 and abs(c[1]-c[2]) < 15)
                if is_bg or is_gray:
                    surf.set_at((x, y), (0, 0, 0, 0))
    return surf


def run_chimera_processor(configs):
    pygame.init()

    start = time.time()
    total = 0

    print("=" * 52)
    print("  CHIMERA PROCESSOR")
    print("=" * 52)
    print()

    for cfg in configs:
        img_path = cfg["file"]
        if not os.path.exists(img_path):
            print(f"[SKIP] '{img_path}' tidak ditemukan.")
            continue

        out_base = cfg.get("out_base", "assets/chars")
        char_name = cfg["char_name"]
        out_dir = os.path.join(out_base, char_name)
        os.makedirs(out_dir, exist_ok=True)

        print(f"Memproses: {img_path}")
        print(f"  -> {out_dir}")

        try:
            sheet = pygame.image.load(img_path)
        except pygame.error as e:
            print(f"  [ERROR] {e}")
            continue

        cols, rows = cfg["grid"]
        frame_w = sheet.get_width() // cols
        frame_h = sheet.get_height() // rows
        scale   = cfg.get("scale_factor", 1)
        prefix  = cfg.get("frame_prefix", "")
        directions = cfg["directions"]
        color_key  = cfg.get("color_key")

        for row in range(rows):
            if row >= len(directions):
                break
            dir_name = directions[row]
            for col in range(cols):
                r = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                frame = sheet.subsurface(r).copy()
                frame = remove_checker_bg(frame, color_key)
                if scale != 1:
                    frame = pygame.transform.scale(
                        frame, (frame_w * scale, frame_h * scale))
                out_path = os.path.join(out_dir, f"{prefix}{dir_name}_{col}.png")
                pygame.image.save(frame, out_path)
                total += 1

        print(f"  Selesai: {cols * len(directions)} frame diekstrak.\n")

    elapsed = time.time() - start
    print(f"SELESAI: {total} frame | {elapsed:.3f} detik")

    print()
    print("=" * 52)
    print("  PANDUAN FOLDER ASSET GAME")
    print("=" * 52)
    for key, (path, desc) in ASSET_PATHS.items():
        print(f"  {path}")
        print(f"    {desc}")
    print()

    pygame.quit()


if __name__ == "__main__":
    run_chimera_processor(CONFIGS)
