import pygame
import os

pygame.init()

# =========================================================================
# KONFIGURASI NAGA BATA (Grid 3x4) + FITUR BOSS SIZE
# =========================================================================
IMAGE_FILE = "naga_master.png" # Pastikan file ini ada!
CHAR_NAME = "npc_naga" 

# Jumlah kolom dan baris pada gambar naga bata baru
KOLOM = 3
BARIS = 4

# Urutan arah hadap pada gambar naga bata baru
DIRECTIONS = ['down', 'up', 'left', 'right'] 

# --- KONFIGURASI UNTUK NAGA RAKSASA (Scaling) ---
# Berapa kali naga kecil asli mau diperbesar?
# (Misal: 2 = 2x lebih besar, 3 = "Boss Size" 3x lebih besar)
SCALE_FACTOR = 3 

# Warna background yang mau dihapus (Mencoba hapus salah satu warna catur)
# Ini TIDAK AKAN SEMPURNA karena latar AI itu pola catur (2 warna).
# Kita hapus warna abu-abu muda di latarnya. Putihnya akan tetap tinggal.
COLOR_KEY_TO_REMOVE = (204, 204, 204) # Warna Abu-abu Muda khas Catur AI
# =========================================================================

def slice_and_scale_sprite():
    print(f"🔍 Mencari file {IMAGE_FILE}...")
    if not os.path.exists(IMAGE_FILE):
        print(f"❌ ERROR: File '{IMAGE_FILE}' tidak ditemukan!")
        print("Pastikan kamu sudah menyimpan gambar naga baru di folder utama dan namanya benar.")
        return

    # Muat gambar utuh (Jangan convert_alpha karena kita kerjain di balik layar)
    try:
        sheet = pygame.image.load(IMAGE_FILE)
    except pygame.error as e:
        print(f"❌ ERROR: Tidak bisa membaca file gambar. {e}")
        return

    sheet_w, sheet_h = sheet.get_size()
    frame_w = sheet_w // KOLOM
    frame_h = sheet_h // BARIS

    # Hitung ukuran output yang sudah diperbesar
    final_w = frame_w * SCALE_FACTOR
    final_h = frame_h * SCALE_FACTOR

    print(f"✅ Gambar ditemukan! Resolusi Asli: {sheet_w}x{sheet_h} px")
    print(f"✂️  Memotong frame asli: {frame_w}x{frame_h} px")
    print(f"🚀 Memperbesar (Scaling) menjadi Boss Size: {final_w}x{final_h} px")
    print(f"⚠️  Mencoba menghapus sebagian latar abu-abu...")

    # Folder tujuannya
    output_folder = f"assets/chars/{CHAR_NAME}"
    os.makedirs(output_folder, exist_ok=True)

    for row in range(BARIS):
        dir_name = DIRECTIONS[row]
        for col in range(KOLOM):
            # 1. Tentukan area kotak pemotongan asli
            rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
            
            # 2. Buat kanvas kosong sementara untuk frame asli
            temp_surf = pygame.Surface(rect.size, pygame.SRCALPHA)
            temp_surf.blit(sheet, (0, 0), rect)

            # 3. Mencoba menghilangkan warna latar dominan
            # (Ini tidak sempurna pada pola catur!)
            temp_surf.set_colorkey(COLOR_KEY_TO_REMOVE)
            
            # 4. Buat kanvas baru yang sudah diperbesar (Boss Size)
            scaled_surf = pygame.Surface((final_w, final_h), pygame.SRCALPHA)
            
            # 5. Lakukan Scaling (Perbesar frame asli ke frame Boss)
            # NEAREST_NEIGHBOR dipakai biar tetap bergaya pixel art kaku
            pygame.transform.scale(temp_surf, (final_w, final_h), scaled_surf)

            # 6. Simpan file baru
            filename = f"{output_folder}/{dir_name}_{col}.png"
            pygame.image.save(scaled_surf, filename)
            print(f"   -> {filename}")

    print("\n🎉 SLICING & SCALING SELESAI!")
    print(f"Naga aslimu sudah masuk dengan ukuran Boss Size.")
    print("WARNING: Pola catur putih mungkin masih tertinggal, mohon bersabar!")

slice_and_scale_sprite()
pygame.quit()
