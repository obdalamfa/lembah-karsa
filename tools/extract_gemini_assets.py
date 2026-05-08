"""
GEMINI ASSET EXTRACTOR & FORMATTER
Alat untuk mendeteksi, memotong, membersihkan latar AI, dan mengubah skala gambar
agar pas dengan aset Lembah Karsa (TILE=48, ITEM=28).
"""

import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

TILE_SIZE = 48
ITEM_SIZE = 28

def find_bg(surf):
    w, h = surf.get_size()
    corners = [surf.get_at((0,0)), surf.get_at((w-1,0)),
               surf.get_at((0,h-1)), surf.get_at((w-1,h-1))]
    return max(corners, key=lambda c: int(c[0])+int(c[1])+int(c[2]))

def is_bg(c, bg, tol=40):
    if len(c) > 3 and c[3] < 20:
        return True
    return all(abs(int(c[i]) - int(bg[i])) < tol for i in range(3))

def detect(surf, min_size=28, tol=40, step=3):
    bg = find_bg(surf)
    w, h = surf.get_size()

    row_occ = [any(not is_bg(surf.get_at((x, y)), bg, tol)
                   for x in range(0, w, step)) for y in range(h)]

    bands = []
    in_b = False; bs = 0
    for y, o in enumerate(row_occ):
        if o and not in_b:  in_b = True;  bs = y
        elif not o and in_b:
            in_b = False
            if y - bs >= min_size: bands.append((bs, y))
    if in_b and h - bs >= min_size: bands.append((bs, h))

    rects = []
    for y0, y1 in bands:
        col_occ = [any(not is_bg(surf.get_at((x, y)), bg, tol)
                       for y in range(y0, y1, step)) for x in range(w)]
        in_s = False; xs = 0
        for x, o in enumerate(col_occ):
            if o and not in_s:  in_s = True;  xs = x
            elif not o and in_s:
                in_s = False
                if x - xs >= min_size: rects.append((xs, y0, x-xs, y1-y0))
        if in_s and w - xs >= min_size: rects.append((xs, y0, w-xs, y1-y0))
    return rects

def clean_and_scale(surf, rect, target_size):
    x, y, w, h = rect
    cropped = surf.subsurface((x, y, w, h)).copy()
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(cropped, (0, 0))
    
    bg_color = find_bg(surf)
    for cy in range(h):
        for cx in range(w):
            c = out.get_at((cx, cy))
            if c[3] > 0:
                # Hapus latar pola catur AI (putih gading dan abu-abu)
                is_bg_color = is_bg(c, bg_color, tol=20)
                is_gray_checker = (c[0] > 180 and c[1] > 180 and c[2] > 180 and abs(c[0]-c[1]) < 15 and abs(c[1]-c[2]) < 15)
                if is_bg_color or is_gray_checker:
                    out.set_at((cx, cy), (0, 0, 0, 0))
                    
    return pygame.transform.scale(out, (target_size, target_size))

IMGS = {
    'items': (r'asset dari gemini\Gemini_Generated_Image_iarteiiarteiiart (1).png', ITEM_SIZE),
    'tiles': (r'asset dari gemini\Gemini_Generated_Image_sbz8d3sbz8d3sbz8 (1).png', TILE_SIZE),
    'chars': (r'asset dari gemini\Gemini_Generated_Image_t61vipt61vipt61v.png', TILE_SIZE),
}

# Peta otomatis direktori dan nama file
TARGET_MAPPING = {
    'items': [
        'assets/items/cangkul.png',
        'assets/items/siram.png',
        'assets/items/tanam.png',
        'assets/items/panen.png',
        'assets/items/kapak.png',
        'assets/items/pancing.png',
        'assets/items/hadiah.png'
    ],
    'tiles': [
        'assets/tiles/grass.png',
        'assets/tiles/dirt.png',
        'assets/tiles/path.png',
        'assets/tiles/tilled_dry.png',
        'assets/tiles/tilled_wet.png',
        'assets/tiles/cave_wall.png',
        'assets/objects/tree.png',
        'assets/objects/stone.png',
        'assets/objects/weed.png',
        'assets/objects/chest.png',
        'assets/objects/tv.png'
    ],
    'chars': [
        'assets/chars/player/down_0.png',
        'assets/chars/player/down_1.png',
        'assets/chars/player/up_0.png',
        'assets/chars/player/up_1.png',
        'assets/chars/player/left_0.png',
        'assets/chars/player/left_1.png',
        'assets/chars/player/right_0.png',
        'assets/chars/player/right_1.png'
    ]
}

for name, (path, target_size) in IMGS.items():
    if not os.path.exists(path):
        print(f"File tidak ditemukan: {path}")
        continue
    
    surf = pygame.image.load(path).convert_alpha()
    rects = detect(surf)
    rects_sorted = sorted(rects, key=lambda r: (r[1], r[0]))
    
    
    print(f"\nMemproses {name} ({len(rects_sorted)} objek ditemukan)...")
    for i, rect in enumerate(rects_sorted):
        final_sprite = clean_and_scale(surf, rect, target_size)
        
        # Otomatis memberikan nama yang benar agar game langsung mendeteksinya!
        if i < len(TARGET_MAPPING.get(name, [])):
            file_name = TARGET_MAPPING[name][i]
        else:
            file_name = f"assets/gemini_extras/{name}_{i}.png"
            
        os.makedirs(os.path.dirname(file_name), exist_ok=True)
        pygame.image.save(final_sprite, file_name)
        print(f"  -> Disimpan: {file_name}")

print(f"\nSelesai! Semua aset telah dipotong, dibersihkan, dan langsung diintegrasikan ke folder 'assets/'.")
print("Jalankan lembah_karsa_revisi.py untuk melihat perubahannya!")
pygame.quit()