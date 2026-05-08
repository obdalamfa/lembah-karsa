import json, os

anim_dir = r"E:\Download\hm64-decomp-master\hm64-decomp-master\assets\sprites\entitySprites\player\animations"

for idx in range(10, 25):
    fname = "{:02d}.json".format(idx)
    path = os.path.join(anim_dir, fname)
    if os.path.exists(path):
        with open(path) as f:
            d = json.load(f)
        sprites_per_frame = [[s["spritesheet_index"] for s in fr["sprites"]] for fr in d["frames"]]
        print("anim {:02d} ({}fr): {}".format(idx, d["frame_count"], sprites_per_frame[:4]))

# Juga cek sprites 40-60 untuk mencari side-view yang lebih baik
print("\n--- Frames 40-60 sizes ---")
tex_dir = r"E:\Download\hm64-decomp-master\hm64-decomp-master\assets\sprites\entitySprites\player\textures"
from PIL import Image
for i in range(40, 65):
    p = os.path.join(tex_dir, "{:03d}.png".format(i))
    if os.path.exists(p):
        img = Image.open(p)
        print("  frame {:03d}: {}".format(i, img.size))
