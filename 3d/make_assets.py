"""
make_assets.py — Generate semua tekstur PNG untuk Lembah Karsa 3D.
Jalankan sekali: python make_assets.py
Menghasilkan folder assets/ berisi ~35 file PNG 64x64 RGBA.
"""
import os, random
from PIL import Image, ImageDraw, ImageFilter

random.seed(42)
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
os.makedirs(OUT, exist_ok=True)
S = 64


# ─── HELPERS ─────────────────────────────────────────────
def new(r, g, b, a=255):
    return Image.new('RGBA', (S, S), (r, g, b, a))

def save(name, img):
    img.save(os.path.join(OUT, f'{name}.png'))
    print(f'  {name}.png')

def noise(img, amt=14):
    px = img.load()
    for y in range(S):
        for x in range(S):
            r, g, b, a = px[x, y]
            d = random.randint(-amt, amt)
            px[x, y] = (
                max(0, min(255, r + d)),
                max(0, min(255, g + d)),
                max(0, min(255, b + d)),
                a)

def clamp(v): return max(0, min(255, v))

def blend(c1, c2, t):
    return tuple(int(c1[i]*(1-t) + c2[i]*t) for i in range(3)) + (255,)


# ─── TILE TEXTURES ───────────────────────────────────────
def make_grass():
    img = new(72, 148, 42)
    draw = ImageDraw.Draw(img)
    # bintik rumput terang/gelap
    for _ in range(30):
        x, y = random.randint(0, S-5), random.randint(0, S-5)
        c = random.choice([(55, 115, 30), (92, 185, 55), (45, 95, 25)])
        w, h = random.randint(2, 6), random.randint(2, 5)
        draw.ellipse([x, y, x+w, y+h], fill=c)
    # helai rumput pendek
    for _ in range(18):
        x, y = random.randint(2, S-3), random.randint(3, S-4)
        h2 = random.randint(3, 6)
        draw.line([(x, y), (x + random.randint(-1,1), y - h2)],
                  fill=(42, 95, 22), width=1)
    noise(img, 10)
    return img

def make_dirt():
    img = new(112, 78, 48)
    draw = ImageDraw.Draw(img)
    for _ in range(20):
        x, y = random.randint(0, S-6), random.randint(0, S-6)
        c = random.choice([(88, 58, 32), (138, 95, 62), (72, 50, 30)])
        w, h = random.randint(3, 8), random.randint(2, 5)
        draw.ellipse([x, y, x+w, y+h], fill=c)
    # retakan kecil
    for _ in range(5):
        x, y = random.randint(5, S-10), random.randint(5, S-10)
        draw.line([(x, y), (x + random.randint(-4, 4), y + random.randint(3, 6))],
                  fill=(65, 40, 22), width=1)
    noise(img, 12)
    return img

def make_path_stone():
    img = new(130, 122, 108)
    draw = ImageDraw.Draw(img)
    # pola batu kerikil
    for _ in range(12):
        x, y = random.randint(2, S-10), random.randint(2, S-10)
        w, h = random.randint(6, 12), random.randint(5, 10)
        c = random.choice([(108, 100, 88), (155, 145, 130), (118, 110, 98)])
        draw.rounded_rectangle([x, y, x+w, y+h], radius=2, fill=c, outline=(85, 78, 65))
    noise(img, 8)
    return img

def make_water():
    img = new(38, 120, 210)
    draw = ImageDraw.Draw(img)
    # gelombang horizontal
    for row in range(0, S, 8):
        for x in range(0, S, 12):
            off = random.randint(-2, 2)
            draw.arc([x-4, row+off, x+8, row+off+6], 0, 180,
                     fill=(65, 155, 240), width=1)
    # pantulan cahaya
    for _ in range(8):
        x, y = random.randint(0, S-4), random.randint(0, S-4)
        draw.ellipse([x, y, x+3, y+3], fill=(130, 200, 255, 180))
    noise(img, 8)
    return img

def make_floor_wood():
    img = new(118, 82, 48)
    draw = ImageDraw.Draw(img)
    # garis serat kayu horizontal
    for y in range(0, S, 8):
        c = random.choice([(100, 68, 38), (138, 95, 58), (108, 75, 42)])
        draw.line([(0, y), (S, y)], fill=c, width=random.randint(1, 2))
        # serat halus
        for x in range(0, S, 10):
            draw.line([(x, y), (x + random.randint(-2, 2), y + 7)],
                      fill=(88, 60, 32), width=1)
    noise(img, 10)
    return img

def make_cave_floor():
    img = new(45, 38, 58)
    draw = ImageDraw.Draw(img)
    for _ in range(15):
        x, y = random.randint(0, S-8), random.randint(0, S-8)
        w, h = random.randint(4, 10), random.randint(3, 8)
        c = random.choice([(35, 28, 45), (58, 48, 72), (28, 22, 38)])
        draw.ellipse([x, y, x+w, y+h], fill=c)
    for _ in range(4):
        x, y = random.randint(5, S-10), random.randint(5, S-10)
        draw.line([(x, y), (x + random.randint(-6, 6), y + random.randint(4, 8))],
                  fill=(22, 16, 32), width=1)
    noise(img, 6)
    return img

def make_straw():
    img = new(185, 148, 52)
    draw = ImageDraw.Draw(img)
    for i in range(-S, S*2, 4):
        c = random.choice([(165, 128, 38), (205, 168, 65), (148, 118, 40)])
        draw.line([(i, 0), (i + S//2, S)], fill=c, width=1)
    noise(img, 10)
    return img

def make_dock():
    img = new(88, 62, 35)
    draw = ImageDraw.Draw(img)
    for y in range(0, S, 10):
        c = random.choice([(75, 52, 28), (105, 75, 42), (68, 48, 25)])
        draw.rectangle([0, y+1, S, y+9], fill=c)
        draw.line([(0, y), (S, y)], fill=(42, 28, 15), width=1)
    for x in range(0, S, 18):
        draw.line([(x, 0), (x, S)], fill=(42, 28, 15), width=1)
    noise(img, 8)
    return img

def make_lily():
    img = new(35, 105, 35)
    draw = ImageDraw.Draw(img)
    draw.ellipse([8, 8, S-8, S-8], fill=(42, 135, 42), outline=(25, 88, 25))
    draw.line([(S//2, 8), (S//2, S//2)], fill=(25, 88, 25), width=1)
    draw.line([(8, S//2), (S//2, S//2)], fill=(25, 88, 25), width=1)
    # bunga kecil
    draw.ellipse([S//2-3, S//2-10, S//2+3, S//2-4], fill=(255, 200, 200))
    noise(img, 6)
    return img

def make_mined():
    img = new(28, 22, 35)
    draw = ImageDraw.Draw(img)
    for _ in range(8):
        x, y = random.randint(2, S-6), random.randint(2, S-6)
        w, h = random.randint(3, 8), random.randint(2, 6)
        draw.ellipse([x, y, x+w, y+h], fill=(18, 14, 24))
    noise(img, 4)
    return img

def make_stairs(direction='down'):
    img = new(105, 88, 68)
    draw = ImageDraw.Draw(img)
    # tangga
    steps = 4
    step_h = S // steps
    for i in range(steps):
        y = i * step_h
        bright = 68 + i * 15
        draw.rectangle([i*8, y, S-i*8, y+step_h-1],
                       fill=(bright, bright-12, bright-22))
        draw.line([(i*8, y), (S-i*8, y)], fill=(55, 42, 28), width=1)
    # panah
    cx, cy = S//2, S//2
    if direction == 'down':
        pts = [(cx, cy+10), (cx-8, cy-4), (cx+8, cy-4)]
        c = (200, 100, 40)
    else:
        pts = [(cx, cy-10), (cx-8, cy+4), (cx+8, cy+4)]
        c = (80, 200, 80)
    draw.polygon(pts, fill=c)
    noise(img, 6)
    return img


# ─── OBJECT TEXTURES ─────────────────────────────────────
def make_wall_stone():
    img = new(95, 88, 80)
    draw = ImageDraw.Draw(img)
    bh = 12  # tinggi bata
    for row in range(S // bh + 1):
        offset = (row % 2) * 16
        y0 = row * bh
        for col in range(-1, S // 20 + 2):
            x0 = col * 20 + offset
            c = random.choice([(82, 75, 68), (108, 100, 92), (72, 65, 58)])
            draw.rectangle([x0+1, y0+1, x0+18, y0+bh-1], fill=c)
            draw.rectangle([x0+1, y0+1, x0+18, y0+bh-1],
                           outline=(58, 52, 45))
    noise(img, 6)
    return img

def make_wall_cave():
    img = new(38, 28, 50)
    draw = ImageDraw.Draw(img)
    for _ in range(20):
        x, y = random.randint(0, S-12), random.randint(0, S-12)
        w, h = random.randint(4, 14), random.randint(3, 10)
        c = random.choice([(28, 20, 40), (50, 38, 65), (22, 16, 32)])
        draw.polygon([(x,y), (x+w,y+random.randint(-2,2)),
                       (x+w+random.randint(-2,2),y+h), (x,y+h)], fill=c)
    noise(img, 5)
    return img

def make_house_wall():
    img = new(185, 135, 85)
    draw = ImageDraw.Draw(img)
    pw = 10
    for x in range(0, S, pw):
        c = random.choice([(168, 120, 72), (205, 155, 98), (148, 105, 62)])
        draw.rectangle([x+1, 0, x+pw-1, S], fill=c)
        draw.line([(x, 0), (x, S)], fill=(115, 78, 42), width=1)
    noise(img, 10)
    return img

def make_roof():
    img = new(188, 62, 45)
    draw = ImageDraw.Draw(img)
    th = 10
    for row in range(S // th + 1):
        offset = (row % 2) * 12
        y0 = row * th
        for col in range(-1, S // 12 + 2):
            x0 = col * 12 + offset
            c = random.choice([(168, 50, 35), (210, 75, 55), (148, 42, 28)])
            draw.rounded_rectangle([x0+1, y0+1, x0+10, y0+th-1], radius=2, fill=c)
            draw.rounded_rectangle([x0+1, y0+1, x0+10, y0+th-1],
                                    radius=2, outline=(120, 32, 18))
    noise(img, 8)
    return img

def make_trunk():
    img = new(92, 62, 32)
    draw = ImageDraw.Draw(img)
    for x in range(0, S, 6):
        c = random.choice([(75, 50, 24), (112, 75, 40), (62, 42, 20)])
        draw.rectangle([x+1, 0, x+5, S], fill=c)
        # serat
        draw.line([(x+2, 0), (x+3, S)], fill=(55, 35, 15), width=1)
    noise(img, 10)
    return img

def make_leaves():
    img = new(35, 125, 28)
    draw = ImageDraw.Draw(img)
    # daun stipple
    base_colors = [(28, 108, 22), (45, 148, 38), (22, 88, 18), (55, 165, 45)]
    for _ in range(40):
        x, y = random.randint(0, S-6), random.randint(0, S-6)
        c = random.choice(base_colors)
        w, h = random.randint(3, 8), random.randint(3, 7)
        draw.ellipse([x, y, x+w, y+h], fill=c)
    noise(img, 8)
    return img

def make_lamp():
    img = new(245, 215, 60)
    draw = ImageDraw.Draw(img)
    # efek cahaya radial
    for r in range(28, 0, -4):
        alpha = 255 - (28-r)*8
        brightness = 255 - (28-r)*5
        draw.ellipse([S//2-r, S//2-r, S//2+r, S//2+r],
                     fill=(brightness, clamp(brightness-20), 30, alpha))
    noise(img, 4)
    return img

def make_crystal(r_base, g_base, b_base):
    img = new(r_base, g_base, b_base)
    draw = ImageDraw.Draw(img)
    # bidang-bidang kristal (facets)
    pts = [(S//2, 4), (S-4, S//2), (S//2, S-4), (4, S//2)]
    draw.polygon(pts, fill=(
        clamp(r_base+40), clamp(g_base+30), clamp(b_base+60)))
    draw.line([(S//2, 4), (4, S//2)], fill=(255, 255, 255, 120), width=2)
    draw.line([(S//2, 4), (S-4, S//2)], fill=(200, 200, 255, 100), width=1)
    for _ in range(12):
        x, y = random.randint(8, S-8), random.randint(8, S-8)
        draw.point((x, y), fill=(255, 255, 255, 180))
    noise(img, 6)
    return img

def make_ore(wall_r, wall_g, wall_b, spot_r, spot_g, spot_b):
    img = new(wall_r, wall_g, wall_b)
    draw = ImageDraw.Draw(img)
    for _ in range(20):
        x, y = random.randint(2, S-6), random.randint(2, S-6)
        w, h = random.randint(3, 8), random.randint(3, 7)
        c = random.choice([
            (wall_r-10, wall_g-10, wall_b-10),
            (wall_r+10, wall_g+10, wall_b+10)])
        draw.ellipse([x, y, x+w, y+h], fill=c)
    for _ in range(8):
        x, y = random.randint(4, S-8), random.randint(4, S-8)
        w, h = random.randint(4, 10), random.randint(4, 8)
        c = (clamp(spot_r + random.randint(-15, 15)),
             clamp(spot_g + random.randint(-15, 15)),
             clamp(spot_b + random.randint(-15, 15)))
        draw.ellipse([x, y, x+w, y+h], fill=c)
        draw.point((x + w//2, y + h//2), fill=(255, 255, 255))
    noise(img, 5)
    return img


# ─── CHARACTER TEXTURES ──────────────────────────────────
def make_solid_tex(r, g, b, noise_amt=12):
    img = new(r, g, b)
    draw = ImageDraw.Draw(img)
    # sedikit shading pojok
    draw.rectangle([0, 0, S, 4], fill=(clamp(r-15), clamp(g-15), clamp(b-15), 180))
    draw.rectangle([0, S-4, S, S], fill=(clamp(r+15), clamp(g+15), clamp(b+15), 180))
    noise(img, noise_amt)
    return img

def make_skin():
    return make_solid_tex(218, 175, 130, 8)

def make_hat():
    img = make_solid_tex(82, 55, 32, 6)
    draw = ImageDraw.Draw(img)
    for x in range(0, S, 8):
        draw.line([(x, 0), (x, S)], fill=(62, 40, 20), width=1)
    return img

def make_plank_tex(r, g, b):
    img = make_solid_tex(r, g, b, 8)
    draw = ImageDraw.Draw(img)
    for y in range(8, S, 8):
        draw.line([(0, y), (S, y)], fill=(clamp(r-20), clamp(g-20), clamp(b-20)), width=1)
    return img


# ─── SOIL TEXTURES ───────────────────────────────────────
def make_soil_dry():
    img = new(95, 68, 42)
    draw = ImageDraw.Draw(img)
    for _ in range(15):
        x, y = random.randint(0, S-6), random.randint(0, S-6)
        c = random.choice([(78, 54, 32), (115, 82, 52)])
        draw.ellipse([x, y, x+random.randint(4,8), y+random.randint(3,6)], fill=c)
    noise(img, 10)
    return img

def make_soil_wet():
    img = new(65, 45, 28)
    draw = ImageDraw.Draw(img)
    for _ in range(12):
        x, y = random.randint(0, S-5), random.randint(0, S-5)
        draw.ellipse([x, y, x+random.randint(3,7), y+random.randint(3,5)],
                     fill=(48, 32, 18))
    noise(img, 6)
    return img

def make_crop_seed():
    img = make_soil_dry()
    draw = ImageDraw.Draw(img)
    draw.ellipse([S//2-4, S//2-4, S//2+4, S//2+4], fill=(145, 108, 62))
    noise(img, 3)
    return img

def make_crop_sprout():
    img = make_soil_wet()
    draw = ImageDraw.Draw(img)
    draw.line([(S//2, S-4), (S//2, S//2)], fill=(55, 155, 35), width=2)
    draw.ellipse([S//2-5, S//2-8, S//2+5, S//2+2], fill=(75, 185, 45))
    return img

def make_crop_ready(r, g, b):
    img = make_soil_wet()
    draw = ImageDraw.Draw(img)
    draw.line([(S//2, S-4), (S//2, S//4)], fill=(45, 128, 28), width=2)
    draw.ellipse([S//2-10, S//4-10, S//2+10, S//4+10], fill=(r, g, b))
    draw.ellipse([S//2-5, S//4-5, S//2+5, S//4+5],
                 fill=(clamp(r+40), clamp(g+40), clamp(b+40)))
    return img


# ─── MAIN ────────────────────────────────────────────────
def main():
    random.seed(42)
    print("Membuat aset tekstur Lembah Karsa 3D...")

    # Ground tiles
    save('grass',       make_grass())
    save('dirt',        make_dirt())
    save('path_stone',  make_path_stone())
    save('water',       make_water())
    save('floor_wood',  make_floor_wood())
    save('cave_floor',  make_cave_floor())
    save('straw',       make_straw())
    save('dock',        make_dock())
    save('lily',        make_lily())
    save('mined',       make_mined())
    save('stairs_down', make_stairs('down'))
    save('stairs_up',   make_stairs('up'))

    # Walls & structures
    save('wall_stone',  make_wall_stone())
    save('wall_cave',   make_wall_cave())
    save('house_wall',  make_house_wall())
    save('roof_red',    make_roof())
    save('tree_trunk',  make_trunk())
    save('tree_leaf',   make_leaves())
    save('lamp_glow',   make_lamp())

    # Crystals & ores
    save('crystal',     make_crystal(180, 130, 240))
    save('ore_copper',  make_ore(38, 28, 50, 195, 115, 55))
    save('ore_iron',    make_ore(38, 28, 50, 135, 140, 165))
    save('ore_gold',    make_ore(38, 28, 50, 248, 215, 65))
    save('ore_crystal', make_ore(38, 28, 50, 185, 140, 240))
    save('ore_mithril', make_ore(38, 28, 50, 130, 228, 252))

    # Character parts
    save('skin',        make_skin())
    save('cloth_orange',make_solid_tex(240, 128, 45, 10))
    save('cloth_blue',  make_solid_tex(65, 118, 215, 10))
    save('cloth_green', make_solid_tex(55, 165, 60, 10))
    save('cloth_white', make_solid_tex(240, 238, 230, 6))
    save('cloth_yellow',make_solid_tex(235, 205, 55, 10))
    save('cloth_red',   make_solid_tex(210, 50, 50, 10))
    save('cloth_purple',make_solid_tex(148, 62, 195, 10))
    save('pants_dark',  make_plank_tex(72, 55, 100))
    save('hat_brown',   make_hat())
    save('shoe_dark',   make_solid_tex(50, 38, 25, 6))
    save('mob_bat',     make_solid_tex(88, 65, 108, 8))
    save('mob_rat',     make_solid_tex(108, 82, 62, 8))
    save('mob_ghost',   make_solid_tex(225, 225, 245, 5))
    save('mob_fire',    make_solid_tex(240, 118, 18, 12))
    save('mob_naga',    make_crystal(205, 162, 30))

    # Soil states
    save('soil_dry',    make_soil_dry())
    save('soil_wet',    make_soil_wet())
    save('crop_seed',   make_crop_seed())
    save('crop_sprout', make_crop_sprout())
    save('crop_lobak',  make_crop_ready(135, 248, 135))
    save('crop_wortel', make_crop_ready(248, 140, 0))
    save('crop_stroberi', make_crop_ready(245, 42, 80))
    save('crop_jagung', make_crop_ready(248, 228, 38))
    save('crop_tomat',  make_crop_ready(248, 58, 50))
    save('crop_labu',   make_crop_ready(238, 120, 38))
    save('crop_bayam',  make_crop_ready(38, 215, 75))
    save('crop_jamur',  make_crop_ready(205, 162, 118))

    # Misc objects
    save('wood_plank',  make_plank_tex(155, 108, 62))
    save('metal_grey',  make_solid_tex(138, 132, 125, 8))
    save('mirror_blue', make_solid_tex(175, 210, 240, 5))
    save('fire_orange', make_solid_tex(205, 88, 42, 15))
    save('grave_stone', make_solid_tex(105, 95, 118, 8))
    save('chest_wood',  make_plank_tex(142, 98, 58))
    save('boat_wood',   make_plank_tex(185, 138, 88))

    print(f"\nSelesai! {len(os.listdir(OUT))} file di folder: {OUT}")


if __name__ == '__main__':
    main()
