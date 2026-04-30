import pygame
import os

pygame.init()

# ==========================================
# KONFIGURASI KHUSUS NAGA BATA (3x4 Grid)
# ==========================================
IMAGE_FILE = "naga_master.png" 
CHAR_NAME = "naga" 

KOLOM = 3
BARIS = 4

# Urutan arah hadap pada gambar naga bata
DIRECTIONS = ['down', 'up', 'left', 'right'] 
# ==========================================

def slice_sprite():
    print(f"🔍 Mencari file {IMAGE_FILE}...")
    if not os.path.exists(IMAGE_FILE):
        print(f"❌ ERROR: File '{IMAGE_FILE}' tidak ditemukan!")
        return

    try:
        # PERBAIKAN: Menghapus .convert_alpha() karena ini script tanpa jendela game
        sheet = pygame.image.load(IMAGE_FILE)
    except pygame.error as e:
        print(f"❌ ERROR: Tidak bisa membaca file gambar. {e}")
        return

    sheet_w, sheet_h = sheet.get_size()
    frame_w = sheet_w // KOLOM
    frame_h = sheet_h // BARIS

    print(f"✅ Gambar ditemukan! Resolusi: {sheet_w}x{sheet_h} px")
    print(f"✂️ Memotong per frame: {frame_w}x{frame_h} px")

    output_folder = f"assets/chars/{CHAR_NAME}"
    os.makedirs(output_folder, exist_ok=True)

    for row in range(BARIS):
        dir_name = DIRECTIONS[row]
        for col in range(KOLOM):
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            image = pygame.Surface(rect.size, pygame.SRCALPHA)
            image.blit(sheet, (0, 0), rect)

            filename = f"{output_folder}/{dir_name}_{col}.png"
            pygame.image.save(image, filename)
            print(f"   -> {filename}")

    print("\n🎉 MAHA KARYA SELESAI! Naga Bata legendaris sudah terpotong.")

slice_sprite()
pygame.quit()
