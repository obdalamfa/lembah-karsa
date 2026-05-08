"""
test_chars.py — Quick visual preview untuk verifikasi kualitas karakter.

Jalankan SETELAH 'python make_assets.py' untuk lihat semua karakter
dalam satu grid PNG. Membantu memastikan kualitas asset cocok dengan v4.

Usage:
  python make_assets.py    # Generate dulu
  python test_chars.py     # Buat preview grid di char_preview.png
"""
import os
import pygame

os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
pygame.init()
pygame.display.set_mode((1, 1))

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')

CHARS = [
    'player',
    # Manusia (12)
    'npc_arya', 'npc_sari', 'npc_raka', 'npc_maya',
    'npc_budi', 'npc_joko', 'npc_cici', 'npc_bowo',
    'npc_ningsih', 'npc_pak_guru', 'npc_mbok_jum', 'npc_jaka_ronda',
    # Makhluk halus (9, kecuali naga)
    'npc_jin', 'npc_demit', 'npc_tuyul', 'npc_kuntilanak',
    'npc_pocong', 'npc_genderuwo', 'npc_wewe', 'npc_banaspati',
    'npc_leak',
    # Hewan (9)
    'npc_sapi', 'npc_ayam', 'npc_kambing', 'npc_bebek',
    'npc_domba', 'npc_kuda', 'npc_kucing', 'npc_rubah', 'npc_kelinci',
]

CELL_W, CELL_H = 130, 80
COLS = 8
ROWS = (len(CHARS) + COLS - 1) // COLS

surf = pygame.Surface((CELL_W * COLS, CELL_H * ROWS + 150), pygame.SRCALPHA)
surf.fill((30, 20, 50))

font = pygame.font.Font(None, 14)
title_font = pygame.font.Font(None, 24)

title = title_font.render(
    "Lembah Karsa v5 — Character Preview (down direction, 3 frames)",
    True, (220, 200, 100))
surf.blit(title, (10, 10))

for i, name in enumerate(CHARS):
    col = i % COLS
    row = i // COLS
    x = col * CELL_W + 8
    y = row * CELL_H + 50

    char_dir = os.path.join(ASSETS_DIR, 'chars', name)
    if not os.path.isdir(char_dir):
        err = font.render(f"{name}: missing", True, (200, 100, 100))
        surf.blit(err, (x, y))
        continue

    # Tampilkan 3 frame down (walk0, walk1, blink)
    for f_idx in range(3):
        path = os.path.join(char_dir, f'down_{f_idx}.png')
        if os.path.exists(path):
            sprite = pygame.image.load(path).convert_alpha()
            surf.blit(sprite, (x + f_idx * 36, y))

    label = font.render(name, True, (200, 200, 220))
    surf.blit(label, (x, y + 50))

# Naga (huge sprite)
naga_dir = os.path.join(ASSETS_DIR, 'chars', 'npc_naga')
if os.path.isdir(naga_dir):
    naga_y = ROWS * CELL_H + 60
    label = title_font.render("Naga (huge sprite 96×64):", True, (220, 200, 100))
    surf.blit(label, (10, naga_y))
    for f in range(3):
        path = os.path.join(naga_dir, f'down_{f}.png')
        if os.path.exists(path):
            sprite = pygame.image.load(path).convert_alpha()
            surf.blit(sprite, (10 + f * 110, naga_y + 30))

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'char_preview.png')
pygame.image.save(surf, out_path)
print(f"Preview saved: {out_path}")
print(f"Open the file to visually verify character quality.")
