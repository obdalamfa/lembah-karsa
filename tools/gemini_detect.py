"""Detect sprite bounding-box regions in Gemini reference images."""
import pygame, os

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

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

IMGS = {
    'items': r'asset dari gemini\Gemini_Generated_Image_iarteiiarteiiart (1).png',
    'tiles': r'asset dari gemini\Gemini_Generated_Image_sbz8d3sbz8d3sbz8 (1).png',
    'chars': r'asset dari gemini\Gemini_Generated_Image_t61vipt61vipt61v.png',
}

for name, path in IMGS.items():
    surf = pygame.image.load(path)
    try:    surf = surf.convert_alpha()
    except: surf = surf.convert()
    rects = detect(surf)
    rects_sorted = sorted(rects, key=lambda r: (r[1], r[0]))
    print(f"\n=== {name} ({surf.get_width()}x{surf.get_height()}) — {len(rects_sorted)} regions ===")
    for i, (x, y, w, h) in enumerate(rects_sorted):
        print(f"  [{i:2d}] x={x:5d} y={y:4d}  w={w:4d} h={h:4d}")

pygame.quit()
