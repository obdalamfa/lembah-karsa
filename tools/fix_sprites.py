"""
Fix komprehensif sprite Lembah Karsa:
1. Gender - arya (laki) pakai karakter laki HM64
2. Left/Right - pakai mirror dari RIGHT bukan frame diagonal
3. Ayam/Sapi/Kambing - frame per arah yang benar
4. Makhluk halus - recolor NPC HM64 sesuai tema
"""
from PIL import Image, ImageEnhance, ImageFilter
import json, os, shutil

HM64 = r"E:\Download\hm64-decomp-master\hm64-decomp-master\assets\sprites"
LK   = r"C:\Users\User\Desktop\gaames\lembah_karsa\assets"
TILE = 48

# â”€â”€ UTIL â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def load_frame(subdir, label, idx, flip=False):
    path = os.path.join(HM64, subdir, label, "textures", "{:03d}.png".format(idx))
    if not os.path.exists(path):
        return None
    img = Image.open(path).convert("RGBA")
    img = img.resize((TILE, TILE), Image.NEAREST)
    if flip:
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img

def save(img, *parts):
    path = os.path.join(LK, *parts)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.save(path)
    print("  saved:", "/".join(parts))

def get_anim_sprites(subdir, label, anim_idx, max_frames=2):
    """Baca JSON animasi â†’ kembalikan daftar sprite indices (max_frames pertama unik)."""
    path = os.path.join(HM64, subdir, label, "animations", "{:02d}.json".format(anim_idx))
    if not os.path.exists(path):
        return []
    with open(path) as f:
        d = json.load(f)
    seen, result = set(), []
    for fr in d["frames"]:
        for s in fr["sprites"]:
            idx = s["spritesheet_index"]
            if idx not in seen:
                seen.add(idx)
                result.append(idx)
                if len(result) >= max_frames:
                    return result
    return result

def recolor(img, tint_rgb, strength=0.55):
    """Tint gambar RGBA dengan warna solid, pertahankan alpha asli."""
    r_orig, g_orig, b_orig, a_orig = img.split()
    tint = Image.new("RGBA", img.size, tint_rgb + (255,))
    blended = Image.blend(img, tint, strength)
    blended.putalpha(a_orig)
    return blended

def make_ghost(base_img, tint_rgb=(255,255,255), strength=0.7, alpha_factor=0.7):
    """Buat efek hantu: tinted + semi-transparan."""
    img = recolor(base_img, tint_rgb, strength)
    r, g, b, a = img.split()
    a = a.point(lambda x: int(x * alpha_factor))
    img.putalpha(a)
    return img


# â”€â”€ CHARACTER SPRITE BUILDER â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

def build_char(subdir, label, anim_down=5, anim_right=6, anim_up=9,
               idle_down=0, idle_right=1, idle_up=4,
               flip_left=True):
    """
    Bangun 4 arah Ã— 3 frame (idle, walk0, walk1) untuk satu karakter.
    Left = mirror Right.
    Kembalikan dict {dir: [frame0, frame1, frame2]} atau None jika gagal.
    """
    # Ambil walk frames dari animasi
    w_down  = get_anim_sprites(subdir, label, anim_down,  max_frames=2)
    w_right = get_anim_sprites(subdir, label, anim_right, max_frames=2)
    w_up    = get_anim_sprites(subdir, label, anim_up,    max_frames=2)

    # Ambil idle frames dari anim 00..04
    i_down  = get_anim_sprites(subdir, label, idle_down,  max_frames=1)
    i_right = get_anim_sprites(subdir, label, idle_right, max_frames=1)
    i_up    = get_anim_sprites(subdir, label, idle_up,    max_frames=1)

    if not (w_down and w_right and w_up and i_down):
        return None

    mapping = {
        "down":  [i_down[0]] + w_down,
        "right": [i_right[0] if i_right else w_right[0]] + w_right,
        "up":    [i_up[0] if i_up else w_up[0]] + w_up,
    }
    # Pastikan 3 frame per arah
    for d in mapping:
        while len(mapping[d]) < 3:
            mapping[d].append(mapping[d][-1])

    result = {}
    for direction, idxs in mapping.items():
        frames = []
        for idx in idxs:
            img = load_frame(subdir, label, idx)
            if img is None:
                return None
            frames.append(img)
        result[direction] = frames

    # LEFT = mirror RIGHT
    result["left"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in result["right"]]
    return result


def save_char(char_dict, *folder_parts):
    """Simpan dict {dir: [img, img, img]} ke folder."""
    for direction, frames in char_dict.items():
        for fi, img in enumerate(frames):
            save(img, *folder_parts, "{}_{}.png".format(direction, fi))


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  1. PLAYER
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("=== PLAYER ===")
# anim 05=walk down, 06=walk right, 09=walk up
# anim 00=idle down, 01=idle right, 04=idle up
player = build_char("entitySprites", "player",
                    anim_down=5, anim_right=6, anim_up=9,
                    idle_down=0, idle_right=1, idle_up=4)
if player:
    # Simpan dengan prefix player_
    for direction, frames in player.items():
        for fi, img in enumerate(frames):
            save(img, "chars", "player", "player_{}_{}.png".format(direction, fi))
            save(img, "chars", "player", "{}_{}.png".format(direction, fi))
else:
    print("  GAGAL load player frames")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  2. NPC â€” GENDER CORRECT
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n=== NPCs ===")

# arya  = laki-laki petani â†’ barley (petani tua HM64)
# sari  = perempuan toko   â†’ ann
# raka  = laki-laki dokter â†’ gray
# maya  = perempuan seni   â†’ karen
# budi  = laki-laki pandai â†’ cliff
npc_map = {
    "arya": ("entitySprites/npc", "barley"),
    "sari": ("entitySprites/npc", "ann"),
    "raka": ("entitySprites/npc", "gray"),
    "maya": ("entitySprites/npc", "karen"),
    "budi": ("entitySprites/npc", "cliff"),
}

for npc_id, (subdir, label) in npc_map.items():
    print("  {} â†’ {}".format(npc_id, label))
    char = build_char(subdir, label)
    if char:
        save_char(char, "chars", "npc", npc_id)
    else:
        print("    GAGAL, skip")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  3. HEWAN â€” FRAME PER ARAH
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n=== HEWAN ===")

def build_animal(subdir, label, idle_down, idle_side, idle_up,
                 anim_down, anim_side, anim_up):
    """Bangun animasi hewan dengan arah yang benar."""
    w_down = get_anim_sprites(subdir, label, anim_down, 2)
    w_side = get_anim_sprites(subdir, label, anim_side, 2)
    w_up   = get_anim_sprites(subdir, label, anim_up,   2)

    mapping = {
        "down":  [idle_down] + w_down,
        "right": [idle_side] + w_side,
        "up":    [idle_up]   + w_up,
    }
    for d in mapping:
        while len(mapping[d]) < 3:
            mapping[d].append(mapping[d][-1])

    result = {}
    for direction, idxs in mapping.items():
        frames = []
        for idx in idxs:
            img = load_frame(subdir, label, idx)
            if img is None:
                return None
            frames.append(img)
        result[direction] = frames

    # Left = mirror right
    result["left"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in result["right"]]
    return result

# Ayam: anim00=down, 01=side, 03=up | walk: 05=down, 06=side, 07=up
print("  ayam â†’ chicken")
ayam_anims = json.load(open(os.path.join(HM64, "entitySprites/animals/chicken/animations/00.json")))
idle_down_ayam  = ayam_anims["frames"][0]["sprites"][0]["spritesheet_index"]  # frame 0

ayam = build_animal("entitySprites/animals", "chicken",
                    idle_down=0, idle_side=1, idle_up=3,
                    anim_down=5, anim_side=6, anim_up=7)
if ayam:
    save_char(ayam, "chars", "mob", "ayam")

# Sapi: anim00=down, 01=side, 02=up | walk: 05=down, 06=side, 07=up
# Sapi idle pakai frame 61-65 (bukan 0)
print("  sapi â†’ cow")
sapi_idle = {}
for anim_idx, direction in [(0,"down"),(1,"right"),(4,"up")]:
    a = json.load(open(os.path.join(HM64, "entitySprites/animals/cow/animations/{:02d}.json".format(anim_idx))))
    sapi_idle[direction] = a["frames"][0]["sprites"][0]["spritesheet_index"]

sapi_w_down = get_anim_sprites("entitySprites/animals", "cow", 5, 2)
sapi_w_side = get_anim_sprites("entitySprites/animals", "cow", 6, 2)
sapi_w_up   = get_anim_sprites("entitySprites/animals", "cow", 7, 2)

sapi_map = {
    "down":  [sapi_idle["down"]]  + sapi_w_down,
    "right": [sapi_idle["right"]] + sapi_w_side,
    "up":    [sapi_idle["up"]]    + sapi_w_up,
}
sapi_result = {}
ok = True
for direction, idxs in sapi_map.items():
    frames = []
    for idx in idxs[:3]:
        img = load_frame("entitySprites/animals", "cow", idx)
        if img is None:
            ok = False; break
        frames.append(img)
    if not ok: break
    sapi_result[direction] = frames
if ok:
    sapi_result["left"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in sapi_result["right"]]
    for d, betsy in [("sapi", sapi_result), ("betsy", sapi_result)]:
        save_char(betsy, "chars", "mob", d)

# Kambing: sheep
print("  kambing â†’ sheep")
sheep_idle_anim = {
    "down":  json.load(open(os.path.join(HM64, "entitySprites/animals/sheep/animations/01.json")))["frames"][0]["sprites"][0]["spritesheet_index"],
    "right": json.load(open(os.path.join(HM64, "entitySprites/animals/sheep/animations/03.json")))["frames"][0]["sprites"][0]["spritesheet_index"],
    "up":    json.load(open(os.path.join(HM64, "entitySprites/animals/sheep/animations/02.json")))["frames"][0]["sprites"][0]["spritesheet_index"],
}
sheep_w_down = get_anim_sprites("entitySprites/animals", "sheep", 5, 2)
sheep_w_side = get_anim_sprites("entitySprites/animals", "sheep", 6, 2)
sheep_w_up   = get_anim_sprites("entitySprites/animals", "sheep", 7, 2)

sheep_map = {
    "down":  [sheep_idle_anim["down"]]  + sheep_w_down,
    "right": [sheep_idle_anim["right"]] + sheep_w_side,
    "up":    [sheep_idle_anim["up"]]    + sheep_w_up,
}
sheep_result = {}
ok = True
for direction, idxs in sheep_map.items():
    frames = []
    for idx in idxs[:3]:
        img = load_frame("entitySprites/animals", "sheep", idx)
        if img is None:
            ok = False; break
        frames.append(img)
    if not ok: break
    sheep_result[direction] = frames
if ok:
    sheep_result["left"] = [f.transpose(Image.FLIP_LEFT_RIGHT) for f in sheep_result["right"]]
    save_char(sheep_result, "chars", "mob", "kambing")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  4. MAKHLUK HALUS â€” RECOLOR NPC HM64
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
print("\n=== MAKHLUK HALUS ===")

def build_spirit(base_subdir, base_label, tint_rgb, ghost_alpha=1.0,
                 strength=0.55, glow=False):
    """Bangun sprite makhluk halus dari base HM64 + recolor."""
    char = build_char(base_subdir, base_label)
    if char is None:
        return None
    result = {}
    for direction, frames in char.items():
        new_frames = []
        for img in frames:
            img = recolor(img, tint_rgb, strength)
            if ghost_alpha < 1.0:
                r, g, b, a = img.split()
                a = a.point(lambda x: int(x * ghost_alpha))
                img.putalpha(a)
            new_frames.append(img)
        result[direction] = new_frames
    return result

# Gunakan `elli` sebagai base wanita (kuntilanak/demit feminine)
# Gunakan `cliff` sebagai base laki (genderuwo/demit masculine)
# Gunakan `stu` sebagai base anak (tuyul â€” anak kecil)
# Gunakan `kai` sebagai base muda (jin â€” api)

spirit_map = {
    # nama_mob: (base_subdir, base_label, tint_rgb, ghost_alpha, strength)
    "jin":        ("entitySprites/npc", "kai",    (255, 120,  20), 1.0,  0.60),  # api merah-oranye
    "kuntilanak": ("entitySprites/npc", "elli",   (230, 230, 255), 0.75, 0.70),  # putih transparan
    "demit":      ("entitySprites/npc", "cliff",  ( 80,  10,  80), 1.0,  0.65),  # ungu gelap
    "genderuwo":  ("entitySprites/npc", "gotz",   ( 20,  40,  10), 1.0,  0.60),  # hijau gelap
    "banaspati":  ("entitySprites/npc", "stu",    (255, 200,   0), 1.0,  0.70),  # kuning api
    "serigala":   ("entitySprites/animals", "dog",( 60,  60,  60), 1.0,  0.40),  # abu gelap
    "tuyul":      ("entitySprites/npc", "stu",    (180, 220, 180), 0.85, 0.50),  # hijau pucat
}

for mob_id, (base_sub, base_label, tint, alpha, strength) in spirit_map.items():
    print("  {} â†’ {} + tint{}".format(mob_id, base_label, tint))
    spirit = build_spirit(base_sub, base_label, tint, alpha, strength)
    if spirit:
        save_char(spirit, "chars", "mob", mob_id)
    else:
        print("    GAGAL, skip")

print("\nSELESAI.")

