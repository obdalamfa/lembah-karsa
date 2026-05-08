"""
SMART SLICER - IDENTIFIKASI & POTONG
Aplikasi ini akan menampilkan gambar AI, menyorot objek satu per satu,
dan meminta kamu memberi nama objek tersebut sebelum dipotong.
"""
import pygame
import os

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

def detect(surf, min_size=20, tol=40, step=3):
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
                is_bg_color = is_bg(c, bg_color, tol=20)
                is_gray_checker = (c[0] > 180 and c[1] > 180 and c[2] > 180 and abs(c[0]-c[1]) < 15 and abs(c[1]-c[2]) < 15)
                if is_bg_color or is_gray_checker:
                    out.set_at((cx, cy), (0, 0, 0, 0))
                    
    return pygame.transform.scale(out, (target_size, target_size))

def main():
    folder = "asset dari gemini"
    out_folder = "assets_auto_sliced"
    if not os.path.exists(folder):
        print(f"Folder '{folder}' tidak ditemukan! Pastikan nama foldernya benar.")
        return

    files = [f for f in os.listdir(folder) if f.endswith('.png')]
    if not files:
        print(f"Tidak ada file .png di dalam folder '{folder}'.")
        return

    print("=== ALAT POTONG OTOMATIS ===")
    print(f"Semua objek akan dipotong dan dimasukkan ke folder '{out_folder}'")
    os.makedirs(out_folder, exist_ok=True)

    for filename in files:
        filepath = os.path.join(folder, filename)
        print(f"\nMembuka gambar: {filename}")
        
        surf = pygame.image.load(filepath)
        surf = surf.convert_alpha()
        rects = detect(surf)
        rects_sorted = sorted(rects, key=lambda r: (r[1], r[0]))

        for i, rect in enumerate(rects_sorted):
            target_size = 28 if "item" in filename.lower() else 48
            final_sprite = clean_and_scale(surf, rect, target_size)
            
            clean_name = filename.replace('.png', '')
            save_path = os.path.join(out_folder, f"{clean_name}_objek_{i}.png")
            pygame.image.save(final_sprite, save_path)
            print(f"✅ Disimpan: {save_path}")

    print(f"\nSelesai! Semua potongan gambar ada di folder '{out_folder}'.")
    print("Silakan buka folder tersebut di File Explorer, lalu ganti nama filenya (rename) dan pindahkan ke folder assets/ sesuai yang kamu inginkan!")
    pygame.quit()

if __name__ == "__main__":
    main()