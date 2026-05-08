"""
GENERATOR ASET PROCEDURAL (FROM SCRATCH)
Skrip ini akan menggambar semua pixel-art murni dari kode (dari nol)
dan menyimpannya sebagai file PNG transparan ke dalam folder 'assets/'.
"""
import pygame
import os
import lembah_karsa_revisi as lk

pygame.init()
pygame.display.set_mode((1, 1), pygame.NOFRAME)

def save_surf(surf, path, size=(lk.TILE, lk.TILE)):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if size:
        surf = pygame.transform.scale(surf, size)
    pygame.image.save(surf, path)
    print(f"Berhasil dibuat: {path}")

def generate_all_assets():
    print("Memulai pembuatan aset dari nol (from scratch)...")
    
    # 1. Terrain
    save_surf(lk.make_grass_tile(), "assets/tiles/grass.png")
    save_surf(lk.make_dirt_tile(), "assets/tiles/dirt.png")
    save_surf(lk.make_tilled_dry(), "assets/tiles/tilled_dry.png")
    save_surf(lk.make_tilled_wet(), "assets/tiles/tilled_wet.png")
    save_surf(lk.make_path_tile(), "assets/tiles/path.png")
    save_surf(lk.make_floor_tile(), "assets/tiles/floor.png")
    save_surf(lk.make_wall_tile(), "assets/tiles/wall.png")
    save_surf(lk.make_cave_wall(), "assets/tiles/cave_wall.png")

    for i in range(4):
        save_surf(lk.make_water_tile(i * 4), f"assets/tiles/water_{i}.png")

    # 2. Objects & Furniture
    objs = {
        'tree': lk.make_tree, 'fence': lk.make_fence, 'mailbox': lk.make_mailbox,
        'door': lk.make_door, 'weed': lk.make_weed, 'stone': lk.make_stone,
        'chest': lk.make_chest, 'bed': lk.make_bed, 'stove': lk.make_stove,
        'table': lk.make_table, 'bookshelf': lk.make_bookshelf, 'mirror': lk.make_mirror,
        'fireplace': lk.make_fireplace, 'clock': lk.make_clock, 'plant_pot': lk.make_plant_pot,
        'counter': lk.make_counter, 'shelf_store': lk.make_shelf_store, 'tv': lk.make_tv
    }
    for name, func in objs.items():
        save_surf(func(), f"assets/objects/{name}.png")

    # 3. Tools
    tools = ['cangkul', 'siram', 'tanam', 'panen', 'kapak', 'pancing', 'hadiah', 'palu']
    for i, tname in enumerate(tools):
        surf = lk.make_tool_sprite(i)
        os.makedirs("assets/items", exist_ok=True)
        pygame.image.save(surf, f"assets/items/{tname}.png")
        print(f"Berhasil dibuat: assets/items/{tname}.png")

    # 4. Player & NPCs
    directions = ['down', 'up', 'left', 'right']
    for d in directions:
        for f in range(2):
            dir_s = 'right' if d == 'left' else d
            flip = (d == 'left')
            
            # Player
            surf = lk.make_char(dir_s, f, role='farmer')
            if flip: surf = pygame.transform.flip(surf, True, False)
            save_surf(surf, f"assets/chars/player/{d}_{f}.png")
            
            # NPCs
            npc_configs = {
                'arya': (lk.C.ng, lk.C.g1, lk.C.pn, 'farmer'),
                'sari': (lk.C.cr, lk.C.nc_sari, lk.C.pn, 'shop'),
                'raka': (lk.C.ng, lk.C.nc_raka, lk.C.s0, 'doc'),
                'maya': (lk.C.gl, lk.C.nc_maya, lk.C.pn, 'artist'),
                'budi': (lk.C.ng, lk.C.nc_budi, lk.C.p2, 'smith'),
            }
            for npc_id, (hair, shirt, pants, role) in npc_configs.items():
                surf = lk.make_char(dir_s, f, hair, shirt, pants, role=role)
                if flip: surf = pygame.transform.flip(surf, True, False)
                save_surf(surf, f"assets/chars/npc/{npc_id}/{d}_{f}.png")

            # Mobs
            mobs = {
                'jin': lk.make_jin, 'betsy': lk.make_sapi, 'sapi': lk.make_sapi,
                'ayam': lk.make_ayam, 'kuntilanak': lk.make_demit, 'genderuwo': lk.make_demit,
                'banaspati': lk.make_jin, 'serigala': lk.make_demit, 'tuyul': lk.make_jin
            }
            for mob_id, func in mobs.items():
                surf = func(dir_s, f)
                if flip: surf = pygame.transform.flip(surf, True, False)
                save_surf(surf, f"assets/chars/mob/{mob_id}/{d}_{f}.png")

            # Naga Boss
            surf = lk.make_naga(dir_s, f)
            if flip: surf = pygame.transform.flip(surf, True, False)
            naga_w = int(lk.TILE * 2.5)
            save_surf(surf, f"assets/chars/npc_naga/{d}_{f}.png", size=(naga_w, naga_w))

    # 5. Crops
    CROP_COLORS = {
        'lobak':    (lk.C.cg, lk.C.cg2),
        'wortel':   (lk.C.co, lk.C.d1),
        'stroberi': (lk.C.cr, lk.C.cg),
        'jagung':   (lk.C.cy, lk.C.cg),
        'tomat':    (lk.C.cr, (255, 80, 80)),
        'labu':     (lk.C.co, lk.C.fn),
        'bayam':    (lk.C.g2, lk.C.g0),
        'jamur':    ((212, 164, 116), lk.C.fn2),
    }
    for crop_id, (c1, c2) in CROP_COLORS.items():
        for stage in range(4):
            save_surf(lk.make_crop_sprite(stage, c1, c2), f"assets/crops/{crop_id}_{stage}.png")

    print("\nSelesai! Sekitar ~340 aset telah berhasil dibuat 'dari nol' dan disimpan di folder 'assets/'.")

if __name__ == "__main__":
    generate_all_assets()
    pygame.quit()