"""
player.py — Menangani logika pemain: pergerakan 8-arah, mouse, penggunaan alat, dan interaksi.
"""
import pygame
import math
import random
from .config import (
    PLAYER_SPEED_TILES_PER_SEC, PLAYER_RUN_MULTIPLIER, TOOLS,
    BLOCKING, WALKABLE, TILLABLE, DR, MB, BD, CH, ST, BS, MR, FP, CL, TB, GR, LN, DT, PP, CT, TR, G
)
from .scenes import SCENES
from .data import CROPS, WILD_ITEMS, HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS, SCHEDULES
from .entities import find_wild_at

class PlayerController:
    def __init__(self, game):
        self.game = game
        self.move_target_x = None
        self.move_target_y = None
        self.is_running = False

    def is_moving(self):
        return self.move_target_x is not None

    def update(self, dt):
        if self.game.mode != 'play':
            return

        keys = pygame.key.get_pressed()
        mouse_pressed = pygame.mouse.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        speed_tps = PLAYER_SPEED_TILES_PER_SEC * (PLAYER_RUN_MULTIPLIER if self.is_running else 1.0)
        move_dist = (speed_tps / 1000.0) * dt

        dx, dy = 0.0, 0.0
        
        if keys[pygame.K_UP] or keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: dy += 1
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: dx += 1

        if mouse_pressed[0]:  
            cam_px = self.game.cam_x * 32
            cam_py = self.game.cam_y * 32
            target_x = (mouse_pos[0] + cam_px) / 32.0
            target_y = (mouse_pos[1] + cam_py) / 32.0
            
            diff_x = target_x - self.game.state.player_x - 0.5 
            diff_y = target_y - self.game.state.player_y - 0.5
            dist = math.hypot(diff_x, diff_y)
            
            if dist > 0.2: 
                dx, dy = diff_x / dist, diff_y / dist

        if dx != 0 and dy != 0 and not mouse_pressed[0]:
            dx *= 0.707
            dy *= 0.707

        self.move_target_x = None 
        if dx != 0 or dy != 0:
            self.move_target_x = 1 
            if abs(dx) > abs(dy):
                self.game.state.facing = 'right' if dx > 0 else 'left'
            else:
                self.game.state.facing = 'down' if dy > 0 else 'up'

        if dx != 0 or dy != 0:
            next_x = self.game.state.player_x + (dx * move_dist)
            next_y = self.game.state.player_y + (dy * move_dist)
            
            if self.can_walk(int(next_x + 0.5), int(self.game.state.player_y + 0.5)):
                self.game.state.player_x = next_x
            if self.can_walk(int(self.game.state.player_x + 0.5), int(next_y + 0.5)):
                self.game.state.player_y = next_y
                
            self.check_portal_at_target()

    def can_walk(self, x, y):
        scene = SCENES[self.game.state.scene_name]
        if x < 0 or x >= scene.w or y < 0 or y >= scene.h:
            return False
        t = scene.tiles[y][x]
        if t in BLOCKING and t != DR:
            return False
        return t in WALKABLE or t == DR

    def check_portal_at_target(self):
        scene = SCENES[self.game.state.scene_name]
        tx = int(self.game.state.player_x)
        ty = int(self.game.state.player_y)
        for portal in scene.portals:
            if portal[0] == tx and portal[1] == ty:
                self.game.transition_to(portal[2], portal[3], portal[4])
                break

    def get_facing_tile(self):
        x, y = self.game.state.get_player_tile()
        if self.game.state.facing == 'up': return (x, y - 1)
        if self.game.state.facing == 'down': return (x, y + 1)
        if self.game.state.facing == 'left': return (x - 1, y)
        return (x + 1, y)

    def spend_energy(self, n):
        if self.game.state.energy < n:
            self.game.start_dialog(["Energimu tidak cukup!", "Tidurlah."], "⚡")
            return False
        self.game.state.energy -= n
        return True

    def use_tool(self):
        tool = TOOLS[self.game.state.tool_index]
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.game.state.scene_name]
        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h: return
        t = scene.tiles[fy][fx]

        if tool == 'Cangkul': self.use_hoe(fx, fy, t)
        elif tool == 'Siram': self.use_watering(fx, fy)
        elif tool == 'Tanam': self.use_plant(fx, fy)
        elif tool == 'Panen': self.use_harvest(fx, fy)
        elif tool == 'Kapak': self.use_axe(fx, fy, t)
        elif tool == 'Hadiah': self.give_gift()

    def use_hoe(self, x, y, tile):
        if tile not in TILLABLE:
            self.game.notif("Tidak bisa dicangkul!"); return
        cost = 1 if self.game.state.upgrades['hoe'] else 3
        if not self.spend_energy(cost): return
        key = f"{x},{y},{self.game.state.scene_name}"
        self.game.state.soil[key] = {'tilled': True, 'watered': False, 'crop': None, 'age': 0}
        self.game.notif("Tanah dicangkul!")

    def use_watering(self, x, y):
        cost = 1 if self.game.state.upgrades['water'] else 2
        if not self.spend_energy(cost): return
        cells = [(x, y)]
        if self.game.state.upgrades['water']:
            cells.extend([(x, y-1), (x, y+1)])
        count = 0
        for cx, cy in cells:
            key = f"{cx},{cy},{self.game.state.scene_name}"
            if key in self.game.state.soil and self.game.state.soil[key].get('tilled'):
                self.game.state.soil[key]['watered'] = True
                if self.game.state.soil[key].get('crop') == 'lobak':
                    self.game.state.stats['watered'] += 1
                count += 1
        if count: self.game.notif(f"Menyiram {count} petak!")
        else: self.game.notif("Tidak ada lahan!")

    def use_plant(self, x, y):
        key = f"{x},{y},{self.game.state.scene_name}"
        soil = self.game.state.soil.get(key)
        if not soil or not soil.get('tilled'):
            self.game.notif("Cangkul dulu!"); return
        if soil.get('crop'):
            self.game.notif("Sudah ada tanaman."); return
        seed_key = self.game.state.seed_key + '_seed'
        if self.game.state.inventory.get(seed_key, 0) <= 0:
            self.game.notif(f"Benih habis!"); return
        crop = CROPS[self.game.state.seed_key]
        if self.game.state.get_season() not in crop['seasons'] and not self.game.state.greenhouse_open:
            self.game.start_dialog([f"{crop['name']} hanya bisa di musim: {', '.join(crop['seasons'])}."], "🌱"); return
        if not self.spend_energy(2): return
        self.game.state.inventory[seed_key] -= 1
        if self.game.state.inventory[seed_key] <= 0:
            del self.game.state.inventory[seed_key]
        soil['crop'] = self.game.state.seed_key
        soil['age'] = 0
        if self.game.state.seed_key == 'lobak':
            self.game.state.stats['lobak_planted'] += 1
        self.game.notif(f"Menanam {crop['name']}!")

    def use_harvest(self, x, y):
        wild = find_wild_at(self.game.state, x, y, self.game.state.scene_name)
        if wild:
            self.harvest_wild(wild); return
        key = f"{x},{y},{self.game.state.scene_name}"
        soil = self.game.state.soil.get(key)
        if not soil or not soil.get('crop'):
            self.game.notif("Tidak ada tanaman."); return
        crop = CROPS[soil['crop']]
        if soil.get('age', 0) < crop['days']:
            self.game.notif(f"{crop['name']} belum matang!"); return
        if not self.spend_energy(2): return
        crop_id = soil['crop']
        self.game.state.inventory[crop_id] = self.game.state.inventory.get(crop_id, 0) + 1
        if crop_id == 'lobak': self.game.state.stats['lobak_harvested'] += 1
        if crop_id == 'jagung': self.game.state.stats['corn_harvested'] += 1
        szn = self.game.state.get_season()
        if szn not in self.game.state.stats['seasons_harvested']:
            self.game.state.stats['seasons_harvested'].append(szn)
        soil['crop'] = None; soil['age'] = 0
        self.game.notif(f"✨ Panen {crop['name']}!")
        
        if hasattr(self.game, 'check_quest_progress'):
            self.game.check_quest_progress()

    def harvest_wild(self, wild):
        kind = wild['kind']
        info = WILD_ITEMS.get(kind, {})
        if kind == 'mandrake':
            self.game.start_dialog([
                "AAAARGHHH!!!",
                "Mandrake itu menjerit hingga membuatmu pusing!",
                f"Tapi kamu berhasil mendapat {info['name']}.",
                "(-15 energi)",
            ], "🍎 Mandrake Liar!")
            self.game.state.energy = max(0, self.game.state.energy - 15)
            self.game.state.inventory[kind] = self.game.state.inventory.get(kind, 0) + 1
            self.game.state.wild_entities.remove(wild)
            return
        elif kind == 'running_mushroom':
            self.game.notif("🍄 Jamur lari... pakai F!"); return
        elif kind == 'firefly':
            self.game.notif("✨ Tangkap dengan F!"); return
        else:
            if not self.spend_energy(1): return
            self.game.state.inventory[kind] = self.game.state.inventory.get(kind, 0) + 1
            self.game.notif(f"🌿 Panen {info['name']}!")
            self.game.state.wild_entities.remove(wild)

    def use_axe(self, x, y, tile):
        if not self.game.state.upgrades['axe']:
            self.game.notif("Butuh kapak! Beli dari Budi."); return
        if tile != TR and tile != DT:
            self.game.notif("Tidak ada pohon."); return
        if not self.spend_energy(4): return
        SCENES[self.game.state.scene_name].tiles[y][x] = G
        self.game.state.inventory['kayu'] = self.game.state.inventory.get('kayu', 0) + 3
        self.game.notif("Pohon ditebang! +3 kayu")

    def give_gift(self):
        px, py = self.game.state.get_player_tile()
        for npc_id, pos in self.game.state.npc_positions.items():
            if pos['scene'] != self.game.state.scene_name: continue
            if abs(pos['x'] - px) <= 1.5 and abs(pos['y'] - py) <= 1.5:
                npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id)
                if not npc_data: continue
                gift_item = npc_data.get('gift')
                if not gift_item:
                    self.game.notif(f"{npc_data['name']} tidak menerima hadiah."); return
                if self.game.state.inventory.get(gift_item, 0) <= 0:
                    self.game.notif("Tidak punya hadiah!"); return
                self.game.state.inventory[gift_item] -= 1
                if self.game.state.inventory[gift_item] <= 0:
                    del self.game.state.inventory[gift_item]
                self.game.state.npc_hearts[npc_id] = min(10, self.game.state.npc_hearts[npc_id] + 2)
                self.game.state.stats['gifts'] += 1
                self.game.start_dialog([npc_data['gift_r']], npc_data['name'])
                if hasattr(self.game, 'check_quest_progress'): self.game.check_quest_progress()
                return
        self.game.notif("Tidak ada warga di dekatmu.")

    def try_capture_supernatural(self):
        px, py = self.game.state.get_player_tile()
        for w in list(self.game.state.wild_entities):
            if w['scene'] != self.game.state.scene_name: continue
            if abs(w['x'] - px) <= 1.5 and abs(w['y'] - py) <= 1.5:
                kind = w['kind']
                if kind == 'running_mushroom':
                    if not self.spend_energy(3): return
                    if random.random() < 0.6:
                        self.game.state.inventory['running_mushroom'] = \
                            self.game.state.inventory.get('running_mushroom', 0) + 1
                        self.game.state.wild_entities.remove(w)
                        self.game.state.captured_supernatural += 1
                        self.game.notif("🍄 Tertangkap!")
                        if hasattr(self.game, 'check_quest_progress'): self.game.check_quest_progress()
                    else:
                        w['x'] = max(0, min(SCENES[w['scene']].w-1, w['x'] + random.randint(-3, 3)))
                        w['y'] = max(0, min(SCENES[w['scene']].h-1, w['y'] + random.randint(-3, 3)))
                        self.game.notif("🍄 Lolos!")
                    return
                elif kind == 'firefly':
                    if not self.game.state.is_night():
                        self.game.notif("✨ Hanya muncul malam!"); return
                    if not self.spend_energy(2): return
                    if random.random() < 0.7:
                        self.game.state.inventory['firefly'] = self.game.state.inventory.get('firefly', 0) + 1
                        self.game.state.wild_entities.remove(w)
                        self.game.state.captured_supernatural += 1
                        self.game.notif("✨ Tertangkap!")
                        if hasattr(self.game, 'check_quest_progress'): self.game.check_quest_progress()
                    else:
                        self.game.notif("✨ Lolos!")
                    return
        self.game.notif("Tidak ada makhluk halus di dekatmu.")

    def interact(self):
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.game.state.scene_name]
        
        # 1. Cek Interaksi dengan NPC/Hewan (Radius Diperluas)
        for npc_id, pos in self.game.state.npc_positions.items():
            if pos['scene'] != self.game.state.scene_name: continue
            
            dist = math.hypot(pos['x'] - self.game.state.player_x, pos['y'] - self.game.state.player_y)
            npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
            interact_radius = 2.5 if npc_data and npc_data.get('type') == 'naga' else 1.8
            
            if dist <= interact_radius:
                self.talk_to_npc(npc_id)
                return

        # 2. Cek Interaksi Benda di depan pemain
        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h: return
        t = scene.tiles[fy][fx]

        if t == MB: self.read_mail()
        elif t == BD: self.game.confirm_sleep()
        elif t == CH: self.open_chest()
        elif t == ST: self.use_stove()
        elif t == BS: self.read_bookshelf()
        elif t == MR: self.use_mirror()
        elif t == FP: self.sit_fireplace()
        elif t == CL: self.check_clock()
        elif t == TB: self.rest_at_table()
        elif t == GR: self.examine_grave()
        elif t == LN: self.examine_lantern()
        elif t == DT: self.game.start_dialog(["Pohon mati."], "🌳")
        elif t == PP: self.game.start_dialog(["🌿 Tanaman hias."], "🌿")
        elif t == CT:
            if self.game.state.scene_name == 'shop':
                if self.game.state.shop_unlocked:
                    self.game.open_panel('shop')
                else:
                    self.game.start_dialog(["Warung belum menerimamu."], "🏪")
        else:
            self.game.notif("Tidak ada interaksi.")

    def talk_to_npc(self, npc_id):
        npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
        if not npc_data: return
        idx = min(self.game.state.npc_dialog_index.get(npc_id, 0), len(npc_data['talks'])-1)
        lines = npc_data['talks'][idx]
        self.game.state.npc_dialog_index[npc_id] = min(idx + 1, len(npc_data['talks'])-1)

        if npc_id == 'jin_kebun' and not self.game.state.met_jin:
            self.game.state.met_jin = True
            if hasattr(self.game, 'check_quest_progress'): self.game.check_quest_progress()

        if npc_data.get('type') in ['sapi', 'ayam', 'kambing']:
            product = npc_data.get('product')
            if product and not self.game.state.inventory.get(f'{product}_{npc_id}_today', False):
                self.game.state.inventory[product] = self.game.state.inventory.get(product, 0) + 1
                self.game.state.inventory[f'{product}_{npc_id}_today'] = True
                lines = list(lines) + [f"Kamu mendapat {product}!"]

        callback = None
        if npc_id == 'sari' and self.game.state.shop_unlocked:
            callback = lambda: self.game.open_panel('shop')
        elif npc_id == 'budi':
            callback = lambda: self.game.open_panel('upgrade')

        self.game.start_dialog(lines, npc_data['name'], callback)

    def show_npc_schedule(self):
        px, py = self.game.state.get_player_tile()
        for npc_id, pos in self.game.state.npc_positions.items():
            if pos['scene'] != self.game.state.scene_name: continue
            if abs(pos['x'] - px) <= 2 and abs(pos['y'] - py) <= 2:
                npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
                if not npc_data: continue
                sched = SCHEDULES.get(npc_id, [])
                lines = [f"{npc_data['name']} — Jadwal:", f"Sekarang: {pos['activity']}"]
                for entry in sched[:6]:
                    h, sx, sy, sc, act = entry
                    if sx == -1:
                        lines.append(f"{h:02d}:00 - menghilang")
                    else:
                        lines.append(f"{h:02d}:00 - {act} di {sc}")
                self.game.start_dialog(lines, "📋 Jadwal")
                return
        self.game.notif("Tidak ada makhluk dekat.")

    def read_mail(self):
        if not self.game.state.mail_read:
            self.game.state.mail_read = True
            
        cb = self.game.check_quest_progress if hasattr(self.game, 'check_quest_progress') else None
        self.game.start_dialog([
            "📬 Surat dari Paman Arsa:",
            '"Anak muda, lembah ini lebih dari yang terlihat."',
            '"Di malam hari, hutan dan kuburan tua hidup."',
            '"Mulailah dengan lobak. Sapa warga. Beri hadiah."',
            '"— Paman Arsa"',
        ], "📬 Surat", cb)

    def open_chest(self):
        lines = ["📦 Tekan I untuk inventori penuh."]
        for k, v in list(self.game.state.inventory.items())[:5]:
            if v > 0 and not k.endswith('_today'):
                lines.append(f"  {k}: {v}")
        self.game.start_dialog(lines, "📦 Peti")

    def use_stove(self):
        for c in ['tomat', 'jagung', 'lobak', 'wortel', 'bayam']:
            if self.game.state.inventory.get(c, 0) > 0:
                self.game.state.inventory[c] -= 1
                if self.game.state.inventory[c] <= 0: del self.game.state.inventory[c]
                self.game.state.energy = min(self.game.state.max_energy, self.game.state.energy + 20)
                self.game.notif(f"Memasak! +20 energi")
                return
        self.game.start_dialog(["🍳 Tidak ada bahan!"], "🍳")

    def read_bookshelf(self):
        tips = [
            "📚 Siram tanaman tiap hari.", "📚 Hujan menyiram lahan otomatis.",
            "📚 Beri hadiah ke warga.", "📚 Tekan H untuk lihat hubungan.",
            "📚 Tekan G untuk lihat jadwal NPC.", "📚 Mandrake teriak saat dipanen!",
            "📚 Jamur lari hanya bisa F.", "📚 Kunang muncul malam.",
            "📚 Jin Kebun muncul jam 19:00+.", "📚 Tahan SHIFT untuk lari."
        ]
        self.game.start_dialog([random.choice(tips)], "📚 Buku")

    def use_mirror(self):
        e = self.game.state.energy
        c = "Segar!" if e > 70 else "Lelah..." if e > 30 else "Sangat lelah!"
        self.game.start_dialog([
            f"🪞 Hari {self.game.state.day} | E:{e}/{self.game.state.max_energy}",
            f"Gold: {self.game.state.gold}G", c,
        ], "🪞")

    def sit_fireplace(self):
        self.game.state.energy = min(self.game.state.max_energy, self.game.state.energy + 10)
        self.game.notif("🔥 +10 energi")

    def check_clock(self):
        h = self.game.state.get_hour()
        c = "Pagi!" if h < 12 else "Sore." if h < 18 else "Malam."
        self.game.start_dialog([
            f"🕐 {self.game.state.get_time_str()}",
            f"{self.game.state.get_season_name()}, hari {self.game.state.day_in_season}", c,
        ], "🕐")

    def rest_at_table(self):
        self.game.state.energy = min(self.game.state.max_energy, self.game.state.energy + 5)
        self.game.notif("🪑 +5 energi")

    def examine_grave(self):
        self.game.start_dialog([
            "📿 Batu nisan tua.", "Aura mistis terasa...", "(Datanglah malam hari)"
        ], "🪦")

    def examine_lantern(self):
        if self.game.state.is_night():
            self.game.start_dialog(["🏮 Lentera menyala terang.", "Pasar malam ramai!"], "🏮")
        else:
            self.game.start_dialog(["🏮 Lentera padam siang."], "🏮")
