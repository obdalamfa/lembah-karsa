"""
app.py — Game class utama.
Smooth movement (pixel-based), camera follow, input handling, render.
"""
import pygame
import math
import random
from .config import (
    C, TILE, VIEW_W, VIEW_H, SCREEN_W, SCREEN_H, FPS,
    INGAME_MINUTES_PER_REAL_SECOND, FORCE_SLEEP_HOUR,
    PLAYER_SPEED_TILES_PER_SEC, PLAYER_RUN_MULTIPLIER,
    ANIMATION_FPS, DAYS_PER_SEASON,
    TILE_NAMES, WALKABLE, BLOCKING, TILLABLE, TOOLS, SEASONS,
    G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS, MR, FP, CL, PP, CH,
    CT, SH, GR, LN, DT
)
from .state import GameState
from .data import (CROPS, WILD_ITEMS, HUMAN_NPCS, SUPERNATURAL_NPCS,
                   ANIMAL_NPCS, SCHEDULES, QUEST_STAGES, all_npcs)
from .scenes import SCENES
from .sprites import init_sprites, SPRITES, ANIMATED
from .entities import (spawn_wild_entities, respawn_wild_at_morning,
                       update_wild_entities, find_wild_at,
                       update_all_npc_positions, init_npc_data, can_walk_at,
                       update_animal_roaming)
from . import panels


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🌱 Lembah Karsa v2.5 — Smooth Edition")
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.Font(None, 16)
        self.font = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 28)
        self.font_title = pygame.font.Font(None, 40)

        init_sprites()

        self.state = GameState()
        self.running = True
        self.mode = 'title'

        # Smooth movement state
        self.move_target_x = None    # tile coords ke mana player gerak
        self.move_target_y = None
        self.is_running = False       # tahan SHIFT
        self.move_blocked_msg = 0     # cooldown notifikasi blocked

        # Camera (smooth)
        self.cam_x = 0.0              # pixel float
        self.cam_y = 0.0
        self.cam_target_x = 0.0
        self.cam_target_y = 0.0

        # Animation
        self.anim_timer = 0           # akumulator untuk animasi
        self.walk_anim_index = 0      # frame walk saat ini (0/1)
        self.blink_timer = 0
        self.show_blink = False

        # Fade transition
        self.fade_alpha = 0
        self.fade_dir = 0
        self.fade_callback = None

        # Dialog state
        self.dialog_lines = []
        self.dialog_index = 0
        self.dialog_speaker = ''
        self.dialog_callback = None
        self.typewriter_progress = 0

        # Panel state
        self.panel = None
        self.panel_select = 0

        # Notification
        self.notif_text = ''
        self.notif_timer = 0

        # Wild entity update timer
        self.wild_timer = 0

        init_npc_data(self.state)

    # ═══════════════════════════════════════════════════
    #  MAIN LOOP
    # ═══════════════════════════════════════════════════
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
            self.update(dt)
            self.render()
            pygame.display.flip()
        pygame.quit()

    # ═══════════════════════════════════════════════════
    #  INPUT
    # ═══════════════════════════════════════════════════
    def handle_keydown(self, event):
        if self.mode == 'title':
            if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                self.start_new_game()
            elif event.key == pygame.K_l:
                self.try_load_game()
            return

        if self.mode == 'fade':
            return

        if self.mode == 'dialog':
            if event.key in (pygame.K_SPACE, pygame.K_e, pygame.K_RETURN):
                self.advance_dialog()
            return

        if self.mode == 'panel':
            self.handle_panel_input(event)
            return

        # MODE PLAY
        if event.key == pygame.K_SPACE:
            self.use_tool()
        elif event.key == pygame.K_e:
            self.interact()
        elif event.key == pygame.K_f:
            self.try_capture_supernatural()
        elif event.key == pygame.K_g:
            self.show_npc_schedule()
        # Slot alat: 1-9 dan 0 (10 slot total)
        elif pygame.K_1 <= event.key <= pygame.K_9:
            idx = event.key - pygame.K_1
            if idx < len(TOOLS):
                self.state.tool_index = idx
                self.notif(f"Alat: {TOOLS[idx]}")
        elif event.key == pygame.K_0:
            if len(TOOLS) > 9:
                self.state.tool_index = 9
                self.notif(f"Alat: {TOOLS[9]}")
        # Tab untuk cycle alat
        elif event.key == pygame.K_TAB:
            self.state.tool_index = (self.state.tool_index + 1) % len(TOOLS)
            self.notif(f"Alat: {TOOLS[self.state.tool_index]}")
        elif event.key == pygame.K_q:
            self.cycle_seed(-1)
        elif event.key == pygame.K_r:
            self.cycle_seed(1)
        elif event.key == pygame.K_t:
            if self.state.scene_name == 'house':
                self.confirm_sleep()
            else:
                self.notif("Hanya bisa tidur di rumah!")
        elif event.key == pygame.K_i:
            self.open_panel('inventory')
        elif event.key == pygame.K_m:
            self.open_panel('map')
        elif event.key == pygame.K_j:
            self.open_panel('quest')
        elif event.key == pygame.K_h:
            self.open_panel('relations')
        elif event.key == pygame.K_k:
            if self.state.scene_name == 'shop' and self.state.shop_unlocked:
                self.open_panel('shop')
            else:
                self.notif("Pergi ke Warung Bu Sari!")
        elif event.key == pygame.K_u:
            if self.state.scene_name == 'smith':
                self.open_panel('upgrade')
            else:
                self.notif("Pergi ke Bengkel Budi!")
        elif event.key == pygame.K_F1:
            self.open_panel('help')
        elif event.key == pygame.K_F5:
            if self.state.save():
                self.notif("💾 Tersimpan!")
        elif event.key == pygame.K_F9:
            self.try_load_game()
        elif event.key == pygame.K_ESCAPE:
            self.open_panel('help')

    def handle_panel_input(self, event):
        # Tutup dengan key yang sama atau ESC
        close_keys = {
            'inventory': pygame.K_i, 'map': pygame.K_m,
            'quest': pygame.K_j, 'relations': pygame.K_h,
            'help': pygame.K_F1,
        }
        if event.key == pygame.K_ESCAPE:
            self.close_panel()
            return
        if self.panel in close_keys and event.key == close_keys[self.panel]:
            self.close_panel()
            return

        if self.panel == 'shop':
            self.handle_shop_input(event)
        elif self.panel == 'upgrade':
            self.handle_upgrade_input(event)

    def handle_shop_input(self, event):
        items = panels.build_shop_items(self.state)
        if event.key in (pygame.K_UP, pygame.K_w):
            self.panel_select = (self.panel_select - 1) % len(items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.panel_select = (self.panel_select + 1) % len(items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            _, action = items[self.panel_select]
            kind, arg1, arg2 = action
            if kind == 'buy_seed':
                self._buy_seeds(arg1, arg2)
            elif kind == 'sell_all':
                self._sell_all()
            elif kind == 'close':
                self.close_panel()

    def handle_upgrade_input(self, event):
        items = panels.build_upgrade_items(self.state)
        if event.key in (pygame.K_UP, pygame.K_w):
            self.panel_select = (self.panel_select - 1) % len(items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.panel_select = (self.panel_select + 1) % len(items)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_e):
            _, action = items[self.panel_select]
            kind, arg1, arg2 = action
            if kind == 'buy_upgrade':
                self._buy_upgrade(arg1, arg2)
            elif kind == 'close':
                self.close_panel()

    # ═══════════════════════════════════════════════════
    #  UPDATE — termasuk SMOOTH MOVEMENT
    # ═══════════════════════════════════════════════════
    def update(self, dt):
        self.anim_timer += dt
        self.blink_timer += dt
        if self.notif_timer > 0:
            self.notif_timer -= dt
        if self.move_blocked_msg > 0:
            self.move_blocked_msg -= dt

        # Animation walk frame
        anim_period_ms = 1000 / ANIMATION_FPS
        if self.anim_timer > anim_period_ms:
            self.anim_timer = 0
            self.walk_anim_index = (self.walk_anim_index + 1) % 2

        # Blink timer (every ~3 seconds, blink for 150ms)
        if self.blink_timer > 3000:
            self.show_blink = True
            if self.blink_timer > 3150:
                self.show_blink = False
                self.blink_timer = 0

        if self.mode == 'fade':
            self.fade_alpha += self.fade_dir * 12
            if self.fade_dir == 1 and self.fade_alpha >= 255:
                self.fade_alpha = 255
                if self.fade_callback:
                    self.fade_callback()
                    self.fade_callback = None
                self.fade_dir = -1
            elif self.fade_dir == -1 and self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.fade_dir = 0
                self.mode = 'play'
            return

        if self.mode == 'play':
            # Time advance
            self.state.time_minutes += dt * (INGAME_MINUTES_PER_REAL_SECOND / 1000.0)
            if self.state.time_minutes >= FORCE_SLEEP_HOUR * 60:
                self.state.time_minutes = FORCE_SLEEP_HOUR * 60
                self.start_dialog(["Sudah jam 23:00...", "Kamu kelelahan dan tertidur."],
                                  "🌙 Larut Malam", callback=self.sleep_next_day)

            # NPC schedule update on hour change
            old_min = self.state.time_minutes - dt * INGAME_MINUTES_PER_REAL_SECOND/1000.0
            old_hour = int(old_min // 60)
            new_hour = int(self.state.time_minutes // 60)
            if old_hour != new_hour:
                update_all_npc_positions(self.state)

            # SMOOTH MOVEMENT
            self.update_smooth_movement(dt)

            # Wild entities tick
            self.wild_timer += dt
            if self.wild_timer > 800:
                self.wild_timer = 0
                update_wild_entities(self.state, dt)

            # Animal free-roam dalam kandang
            update_animal_roaming(self.state, dt)

            # COMBAT (v7) - cooldown, mob AI, damage
            self.update_combat(dt)

            # Smooth camera
            self.update_camera(dt)

        if self.mode == 'dialog':
            current = self.dialog_lines[self.dialog_index]
            if self.typewriter_progress < len(current):
                self.typewriter_progress += 2

    def update_smooth_movement(self, dt):
        """Smooth movement: input → set target tile → lerp position."""
        keys = pygame.key.get_pressed()
        self.is_running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]

        # Tentukan input arah (WASD only — gerak via mouse hold juga didukung di bawah)
        dx, dy, new_facing = 0, 0, None
        if keys[pygame.K_w]:
            dy = -1; new_facing = 'up'
        elif keys[pygame.K_s]:
            dy = 1; new_facing = 'down'
        elif keys[pygame.K_a]:
            dx = -1; new_facing = 'left'
        elif keys[pygame.K_d]:
            dx = 1; new_facing = 'right'

        # Mouse hold: gerak ke arah cursor (kalau tidak ada WASD)
        if not new_facing:
            mouse_pressed = pygame.mouse.get_pressed()
            if mouse_pressed[0]:
                mx, my = pygame.mouse.get_pos()
                # Konversi ke world coord
                cam_px_x = self.cam_x * TILE
                cam_py_y = self.cam_y * TILE
                target_wx = (mx + cam_px_x) / TILE
                target_wy = (my + cam_py_y) / TILE
                diff_x = target_wx - self.state.player_x - 0.5
                diff_y = target_wy - self.state.player_y - 0.5
                # Hanya gerak kalau jarak cukup besar
                import math as _m
                if _m.hypot(diff_x, diff_y) > 0.5:
                    if abs(diff_x) > abs(diff_y):
                        dx = 1 if diff_x > 0 else -1
                        new_facing = 'right' if dx > 0 else 'left'
                    else:
                        dy = 1 if diff_y > 0 else -1
                        new_facing = 'down' if dy > 0 else 'up'

        # Hitung target tile
        cur_tx = round(self.state.player_x)
        cur_ty = round(self.state.player_y)
        is_aligned = (abs(self.state.player_x - cur_tx) < 0.05 and
                      abs(self.state.player_y - cur_ty) < 0.05)

        if new_facing:
            self.state.facing = new_facing
            # Set target jika di tile yang aligned dan bisa jalan
            if is_aligned and self.move_target_x is None:
                tx = cur_tx + dx
                ty = cur_ty + dy
                if self.can_walk(tx, ty):
                    self.move_target_x = tx
                    self.move_target_y = ty
                else:
                    # Bisa rotate aja, blocked
                    pass

        # Update posisi menuju target
        if self.move_target_x is not None:
            speed_tps = PLAYER_SPEED_TILES_PER_SEC
            if self.is_running:
                speed_tps *= PLAYER_RUN_MULTIPLIER
            speed_per_ms = speed_tps / 1000.0

            tdx = self.move_target_x - self.state.player_x
            tdy = self.move_target_y - self.state.player_y
            dist = math.hypot(tdx, tdy)
            move_dist = speed_per_ms * dt

            if dist <= move_dist:
                # Sampai di target — simpan dulu sebelum clear
                reached_tx = self.move_target_x
                reached_ty = self.move_target_y
                self.state.player_x = float(reached_tx)
                self.state.player_y = float(reached_ty)
                self.move_target_x = None
                self.move_target_y = None
                # Cek portal (mungkin set scene baru)
                self.check_portal_at_target()
                # Kalau scene tidak berubah dan masih ada input, lanjut
                if (self.mode == 'play' and new_facing and
                    (dx != 0 or dy != 0)):
                    next_tx = reached_tx + dx
                    next_ty = reached_ty + dy
                    if self.can_walk(next_tx, next_ty):
                        self.move_target_x = next_tx
                        self.move_target_y = next_ty
            else:
                # Lerp
                self.state.player_x += (tdx / dist) * move_dist
                self.state.player_y += (tdy / dist) * move_dist

    def can_walk(self, x, y):
        x = int(round(x)); y = int(round(y))
        # Dungeon mode: pakai dungeon_tiles
        if self.state.scene_name == 'dungeon' and self.state.dungeon_tiles:
            tiles = self.state.dungeon_tiles
            w = len(tiles[0]); h = len(tiles)
            if x < 0 or x >= w or y < 0 or y >= h:
                return False
            t = tiles[y][x]
            if t in BLOCKING and t != DR:
                return False
            return t in WALKABLE or t == DR
        scene = SCENES[self.state.scene_name]
        if x < 0 or x >= scene.w or y < 0 or y >= scene.h:
            return False
        t = scene.tiles[y][x]
        if t in BLOCKING and t != DR:
            return False
        return t in WALKABLE or t == DR

    def check_portal_at_target(self):
        """Kalau sampai di portal tile, transisi scene. Atau STAIRS dungeon."""
        from .config import STAIRS_DOWN, STAIRS_UP
        scene = SCENES[self.state.scene_name]
        tx = int(self.state.player_x)
        ty = int(self.state.player_y)
        # Cek tile dungeon: STAIRS
        cur_tile = None
        if self.state.dungeon_level > 0 and self.state.dungeon_tiles:
            tiles = self.state.dungeon_tiles
            if 0 <= ty < len(tiles) and 0 <= tx < len(tiles[0]):
                cur_tile = tiles[ty][tx]
        else:
            if 0 <= ty < scene.h and 0 <= tx < scene.w:
                cur_tile = scene.tiles[ty][tx]
        if cur_tile == STAIRS_DOWN:
            self.descend_dungeon()
            return
        if cur_tile == STAIRS_UP:
            self.ascend_dungeon()
            return
        for portal in scene.portals:
            if portal[0] == tx and portal[1] == ty:
                self.transition_to(portal[2], portal[3], portal[4])
                break

    def update_camera(self, dt):
        """Smooth camera follow."""
        scene = SCENES[self.state.scene_name]
        # Target camera centered on player
        self.cam_target_x = self.state.player_x - VIEW_W / 2
        self.cam_target_y = self.state.player_y - VIEW_H / 2
        # Clamp ke edge map
        self.cam_target_x = max(0, min(scene.w - VIEW_W, self.cam_target_x))
        self.cam_target_y = max(0, min(scene.h - VIEW_H, self.cam_target_y))
        # Lerp
        lerp_speed = 8.0 / 1000.0  # 8 per detik
        cdx = self.cam_target_x - self.cam_x
        cdy = self.cam_target_y - self.cam_y
        self.cam_x += cdx * min(1, lerp_speed * dt)
        self.cam_y += cdy * min(1, lerp_speed * dt)

    def is_moving(self):
        return self.move_target_x is not None

    # ═══════════════════════════════════════════════════
    #  TOOLS
    # ═══════════════════════════════════════════════════
    def get_facing_tile(self):
        x, y = self.state.get_player_tile()
        if self.state.facing == 'up': return (x, y - 1)
        if self.state.facing == 'down': return (x, y + 1)
        if self.state.facing == 'left': return (x - 1, y)
        return (x + 1, y)

    def use_tool(self):
        tool = TOOLS[self.state.tool_index]
        # Weapon slots → attack
        if tool in ('Pedang', 'Tombak', 'Panah'):
            # Cek apakah player punya weapon ini (sword_id, dll)
            if tool == 'Pedang' and not self.state.sword_id:
                self.notif("Belum punya pedang! Craft di Bengkel Budi.")
                return
            self.attack(weapon=tool)
            return
        # Pickaxe slot
        if tool == 'Pickaxe':
            if self.state.pickaxe_tier <= 0:
                self.notif("Belum punya pickaxe! Beli di Bengkel Budi.")
                return
            self.use_pickaxe()
            return
        # Farming tools
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.state.scene_name]
        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h:
            return
        t = scene.tiles[fy][fx]
        if tool == 'Cangkul': self.use_hoe(fx, fy, t)
        elif tool == 'Siram': self.use_watering(fx, fy)
        elif tool == 'Tanam': self.use_plant(fx, fy)
        elif tool == 'Panen': self.use_harvest(fx, fy)
        elif tool == 'Kapak': self.use_axe(fx, fy, t)
        elif tool == 'Hadiah': self.give_gift()

    def use_hoe(self, x, y, tile):
        if tile not in TILLABLE:
            self.notif("Tidak bisa dicangkul!"); return
        cost = 1 if self.state.upgrades['hoe'] else 3
        if not self.spend_energy(cost): return
        key = f"{x},{y},{self.state.scene_name}"
        self.state.soil[key] = {'tilled': True, 'watered': False, 'crop': None, 'age': 0}
        self.notif("Tanah dicangkul!")

    def use_watering(self, x, y):
        cost = 1 if self.state.upgrades['water'] else 2
        if not self.spend_energy(cost): return
        cells = [(x, y)]
        if self.state.upgrades['water']:
            cells.extend([(x, y-1), (x, y+1)])
        count = 0
        for cx, cy in cells:
            key = f"{cx},{cy},{self.state.scene_name}"
            if key in self.state.soil and self.state.soil[key].get('tilled'):
                self.state.soil[key]['watered'] = True
                if self.state.soil[key].get('crop') == 'lobak':
                    self.state.stats['watered'] += 1
                count += 1
        if count: self.notif(f"Menyiram {count} petak!")
        else: self.notif("Tidak ada lahan!")

    def use_plant(self, x, y):
        key = f"{x},{y},{self.state.scene_name}"
        soil = self.state.soil.get(key)
        if not soil or not soil.get('tilled'):
            self.notif("Cangkul dulu!"); return
        if soil.get('crop'):
            self.notif("Sudah ada tanaman."); return
        seed_key = self.state.seed_key + '_seed'
        if self.state.inventory.get(seed_key, 0) <= 0:
            self.notif(f"Benih {CROPS[self.state.seed_key]['name']} habis!"); return
        crop = CROPS[self.state.seed_key]
        if self.state.get_season() not in crop['seasons'] and not self.state.greenhouse_open:
            self.start_dialog([f"{crop['name']} hanya bisa di musim: {', '.join(crop['seasons'])}."], "🌱"); return
        if not self.spend_energy(2): return
        self.state.inventory[seed_key] -= 1
        if self.state.inventory[seed_key] <= 0:
            del self.state.inventory[seed_key]
        soil['crop'] = self.state.seed_key
        soil['age'] = 0
        if self.state.seed_key == 'lobak':
            self.state.stats['lobak_planted'] += 1
        self.notif(f"Menanam {crop['name']}!")

    def use_harvest(self, x, y):
        wild = find_wild_at(self.state, x, y, self.state.scene_name)
        if wild:
            self.harvest_wild(wild); return
        key = f"{x},{y},{self.state.scene_name}"
        soil = self.state.soil.get(key)
        if not soil or not soil.get('crop'):
            self.notif("Tidak ada tanaman."); return
        crop = CROPS[soil['crop']]
        if soil.get('age', 0) < crop['days']:
            self.notif(f"{crop['name']} belum matang!"); return
        if not self.spend_energy(2): return
        crop_id = soil['crop']
        self.state.inventory[crop_id] = self.state.inventory.get(crop_id, 0) + 1
        if crop_id == 'lobak': self.state.stats['lobak_harvested'] += 1
        if crop_id == 'jagung': self.state.stats['corn_harvested'] += 1
        szn = self.state.get_season()
        if szn not in self.state.stats['seasons_harvested']:
            self.state.stats['seasons_harvested'].append(szn)
        soil['crop'] = None; soil['age'] = 0
        self.notif(f"✨ Panen {crop['name']}!")
        self.check_quest_progress()

    def harvest_wild(self, wild):
        kind = wild['kind']
        info = WILD_ITEMS.get(kind, {})
        if kind == 'mandrake':
            self.start_dialog([
                "AAAARGHHH!!!",
                "Mandrake itu menjerit hingga membuatmu pusing!",
                f"Tapi kamu berhasil mendapat {info['name']}.",
                "(-15 energi)",
            ], "🍎 Mandrake Liar!")
            self.state.energy = max(0, self.state.energy - 15)
            self.state.inventory[kind] = self.state.inventory.get(kind, 0) + 1
            self.state.wild_entities.remove(wild)
            return
        elif kind == 'running_mushroom':
            self.notif("🍄 Jamur lari... pakai F!"); return
        elif kind == 'firefly':
            self.notif("✨ Tangkap dengan F!"); return
        else:
            if not self.spend_energy(1): return
            self.state.inventory[kind] = self.state.inventory.get(kind, 0) + 1
            self.notif(f"🌿 Panen {info['name']}!")
            self.state.wild_entities.remove(wild)

    def use_axe(self, x, y, tile):
        if not self.state.upgrades['axe']:
            self.notif("Butuh kapak! Beli dari Budi."); return
        if tile != TR and tile != DT:
            self.notif("Tidak ada pohon."); return
        if not self.spend_energy(4): return
        SCENES[self.state.scene_name].tiles[y][x] = G
        self.state.inventory['kayu'] = self.state.inventory.get('kayu', 0) + 3
        self.notif("Pohon ditebang! +3 kayu")

    def give_gift(self):
        px, py = self.state.get_player_tile()
        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] != self.state.scene_name: continue
            if abs(pos['x'] - px) <= 1 and abs(pos['y'] - py) <= 1:
                npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id)
                if not npc_data: continue
                gift_item = npc_data.get('gift')
                if not gift_item:
                    self.notif(f"{npc_data['name']} tidak menerima hadiah."); return
                if self.state.inventory.get(gift_item, 0) <= 0:
                    self.notif("Tidak punya hadiah!"); return
                self.state.inventory[gift_item] -= 1
                if self.state.inventory[gift_item] <= 0:
                    del self.state.inventory[gift_item]
                self.state.npc_hearts[npc_id] = min(10, self.state.npc_hearts[npc_id] + 2)
                self.state.stats['gifts'] += 1
                self.start_dialog([npc_data['gift_r']], npc_data['name'])
                self.check_quest_progress()
                return
        self.notif("Tidak ada warga di dekatmu.")

    def spend_energy(self, n):
        if self.state.energy < n:
            self.start_dialog(["Energimu tidak cukup!", "Tidurlah."], "⚡"); return False
        self.state.energy -= n
        # Energy habis = pingsan kelelahan, revive ke clinic
        if self.state.energy <= 0:
            self.state.energy = 30
            self.state.scene_name = 'clinic'
            self.state.player_x, self.state.player_y = 7.0, 5.0
            self.state.gold = max(0, self.state.gold - 30)
            self.notif("💤 Kelelahan! Bu Maya merawatmu. (-30G)")
            return False
        return True

    def try_capture_supernatural(self):
        px, py = self.state.get_player_tile()
        for w in list(self.state.wild_entities):
            if w['scene'] != self.state.scene_name: continue
            if abs(w['x'] - px) <= 1 and abs(w['y'] - py) <= 1:
                kind = w['kind']
                if kind == 'running_mushroom':
                    if not self.spend_energy(3): return
                    if random.random() < 0.6:
                        self.state.inventory['running_mushroom'] = \
                            self.state.inventory.get('running_mushroom', 0) + 1
                        self.state.wild_entities.remove(w)
                        self.state.captured_supernatural += 1
                        self.notif("🍄 Tertangkap!")
                        self.check_quest_progress()
                    else:
                        w['x'] = max(0, min(SCENES[w['scene']].w-1, w['x'] + random.randint(-3, 3)))
                        w['y'] = max(0, min(SCENES[w['scene']].h-1, w['y'] + random.randint(-3, 3)))
                        self.notif("🍄 Lolos!")
                    return
                elif kind == 'firefly':
                    if not self.state.is_night():
                        self.notif("✨ Hanya muncul malam!"); return
                    if not self.spend_energy(2): return
                    if random.random() < 0.7:
                        self.state.inventory['firefly'] = self.state.inventory.get('firefly', 0) + 1
                        self.state.wild_entities.remove(w)
                        self.state.captured_supernatural += 1
                        self.notif("✨ Tertangkap!")
                        self.check_quest_progress()
                    else:
                        self.notif("✨ Lolos!")
                    return
        self.notif("Tidak ada makhluk halus di dekatmu.")

    # ═══════════════════════════════════════════════════
    #  INTERACTION
    # ═══════════════════════════════════════════════════
    def interact(self):
        fx, fy = self.get_facing_tile()
        scene = SCENES[self.state.scene_name]
        if fx < 0 or fx >= scene.w or fy < 0 or fy >= scene.h: return
        t = scene.tiles[fy][fx]

        # NPC nearby?
        px, py = self.state.get_player_tile()
        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] != self.state.scene_name: continue
            # Naga occupies 3x2 area, range deteksi diperluas
            npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
            range_x = 3 if npc_data and npc_data.get('type') == 'naga' else 1
            range_y = 2 if npc_data and npc_data.get('type') == 'naga' else 1
            if abs(pos['x'] - px) <= range_x and abs(pos['y'] - py) <= range_y:
                self.talk_to_npc(npc_id); return

        # Tile interactions
        if t == MB: self.read_mail()
        elif t == BD: self.confirm_sleep()
        elif t == CH: self.open_chest()
        elif t == ST: self.use_stove()
        elif t == BS: self.read_bookshelf()
        elif t == MR: self.use_mirror()
        elif t == FP: self.sit_fireplace()
        elif t == CL: self.check_clock()
        elif t == TB: self.rest_at_table()
        elif t == GR: self.examine_grave()
        elif t == LN: self.examine_lantern()
        elif t == DT: self.start_dialog(["Pohon mati."], "🌳")
        elif t == PP: self.start_dialog(["🌿 Tanaman hias."], "🌿")
        elif t == CT:
            if self.state.scene_name == 'shop':
                if self.state.shop_unlocked:
                    self.open_panel('shop')
                else:
                    self.start_dialog(["Warung belum menerimamu."], "🏪")
        else:
            self.notif("Tidak ada interaksi.")

    def talk_to_npc(self, npc_id):
        from .data import TALKS_BY_ACTIVITY
        npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
        if not npc_data: return

        # Cek dialog kontekstual berdasarkan aktivitas current
        pos = self.state.npc_positions.get(npc_id, {})
        activity = pos.get('activity', '')
        ctx_dialogs = TALKS_BY_ACTIVITY.get(npc_id, {}).get(activity)

        if ctx_dialogs:
            # Pakai dialog kontekstual
            lines = ctx_dialogs
        else:
            # Fallback ke talks default cycle
            idx = min(self.state.npc_dialog_index.get(npc_id, 0), len(npc_data['talks'])-1)
            lines = npc_data['talks'][idx]
            self.state.npc_dialog_index[npc_id] = min(idx + 1, len(npc_data['talks'])-1)

        if npc_id == 'jin_kebun' and not self.state.met_jin:
            self.state.met_jin = True
            self.check_quest_progress()

        # Animal product
        if npc_data.get('type') in ['sapi', 'ayam', 'kambing']:
            product = npc_data.get('product')
            if product and not self.state.inventory.get(f'{product}_{npc_id}_today', False):
                self.state.inventory[product] = self.state.inventory.get(product, 0) + 1
                self.state.inventory[f'{product}_{npc_id}_today'] = True
                lines = list(lines) + [f"Kamu mendapat {product}!"]

        callback = None
        if npc_id == 'sari' and self.state.shop_unlocked:
            callback = lambda: self.open_panel('shop')
        elif npc_id == 'budi':
            callback = lambda: self.open_panel('upgrade')

        self.start_dialog(lines, npc_data['name'], callback)

    def show_npc_schedule(self):
        px, py = self.state.get_player_tile()
        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] != self.state.scene_name: continue
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
                self.start_dialog(lines, "📋 Jadwal")
                return
        self.notif("Tidak ada makhluk dekat.")

    # ═══════════════════════════════════════════════════
    #  TILE INTERACTIONS
    # ═══════════════════════════════════════════════════
    def read_mail(self):
        if not self.state.mail_read:
            self.state.mail_read = True
        self.start_dialog([
            "📬 Surat dari Paman Arsa:",
            '"Anak muda, lembah ini lebih dari yang terlihat."',
            '"Di malam hari, hutan dan kuburan tua hidup."',
            '"Mulailah dengan lobak. Sapa warga. Beri hadiah."',
            '"— Paman Arsa"',
        ], "📬 Surat", self.check_quest_progress)

    def confirm_sleep(self):
        if self.state.scene_name == 'house':
            self.sleep_next_day()
        else:
            self.notif("Hanya bisa tidur di rumah!")

    def open_chest(self):
        lines = ["📦 Tekan I untuk inventori penuh."]
        for k, v in list(self.state.inventory.items())[:5]:
            if v > 0 and not k.endswith('_today'):
                lines.append(f"  {k}: {v}")
        self.start_dialog(lines, "📦 Peti")

    def use_stove(self):
        for c in ['tomat', 'jagung', 'lobak', 'wortel', 'bayam']:
            if self.state.inventory.get(c, 0) > 0:
                self.state.inventory[c] -= 1
                if self.state.inventory[c] <= 0: del self.state.inventory[c]
                self.state.energy = min(self.state.max_energy, self.state.energy + 20)
                self.notif(f"Memasak! +20 energi")
                return
        self.start_dialog(["🍳 Tidak ada bahan!"], "🍳")

    def read_bookshelf(self):
        tips = [
            "📚 Siram tanaman tiap hari.",
            "📚 Hujan menyiram lahan otomatis.",
            "📚 Beri hadiah ke warga.",
            "📚 Tekan H untuk lihat hubungan.",
            "📚 Tekan G untuk lihat jadwal NPC.",
            "📚 Mandrake teriak saat dipanen!",
            "📚 Jamur lari hanya bisa F.",
            "📚 Kunang muncul malam.",
            "📚 Jin Kebun muncul jam 19:00+.",
            "📚 Tahan SHIFT untuk lari.",
        ]
        self.start_dialog([random.choice(tips)], "📚 Buku")

    def use_mirror(self):
        e = self.state.energy
        c = "Segar!" if e > 70 else "Lelah..." if e > 30 else "Sangat lelah!"
        self.start_dialog([
            f"🪞 Hari {self.state.day} | E:{e}/{self.state.max_energy}",
            f"Gold: {self.state.gold}G", c,
        ], "🪞")

    def sit_fireplace(self):
        self.state.energy = min(self.state.max_energy, self.state.energy + 10)
        self.notif("🔥 +10 energi")

    def check_clock(self):
        h = self.state.get_hour()
        c = "Pagi!" if h < 12 else "Sore." if h < 18 else "Malam."
        self.start_dialog([
            f"🕐 {self.state.get_time_str()}",
            f"{self.state.get_season_name()}, hari {self.state.day_in_season}", c,
        ], "🕐")

    def rest_at_table(self):
        self.state.energy = min(self.state.max_energy, self.state.energy + 5)
        self.notif("🪑 +5 energi")

    def examine_grave(self):
        self.start_dialog([
            "📿 Batu nisan tua.",
            "Aura mistis terasa...",
            "(Datanglah malam hari)",
        ], "🪦")

    def examine_lantern(self):
        if self.state.is_night():
            self.start_dialog(["🏮 Lentera menyala terang.", "Pasar malam ramai!"], "🏮")
        else:
            self.start_dialog(["🏮 Lentera padam siang."], "🏮")

    # ═══════════════════════════════════════════════════
    #  TRANSITIONS
    # ═══════════════════════════════════════════════════
    def transition_to(self, target_scene, tx, ty):
        self.mode = 'fade'
        self.fade_dir = 1
        self.fade_alpha = 0
        self.move_target_x = None
        self.move_target_y = None
        def do_switch():
            self.state.scene_name = target_scene
            self.state.player_x = float(tx)
            self.state.player_y = float(ty)
            # Reset camera ke target instan
            self.update_camera(99999)
        self.fade_callback = do_switch

    # ═══════════════════════════════════════════════════
    #  SLEEP
    # ═══════════════════════════════════════════════════
    def sleep_next_day(self):
        is_rain = self.state.weather in ('Hujan', 'Badai')
        for key, soil in self.state.soil.items():
            if is_rain and soil.get('tilled'):
                soil['watered'] = True
            if soil.get('crop') and soil.get('watered'):
                soil['age'] = soil.get('age', 0) + 1
            soil['watered'] = False
        for k in list(self.state.inventory.keys()):
            if k.endswith('_today'):
                del self.state.inventory[k]
        self.state.day += 1
        self.state.day_in_season += 1
        if self.state.day_in_season > DAYS_PER_SEASON:
            self.state.day_in_season = 1
            self.state.season_index = (self.state.season_index + 1) % 4
            if self.state.season_index == 0:
                self.state.year += 1
        self.state.time_minutes = 360
        self.state.energy = self.state.max_energy
        self.state.weather = random.choice(['Cerah','Cerah','Mendung','Hujan','Berangin'])
        respawn_wild_at_morning(self.state)
        update_all_npc_positions(self.state)
        self.state.save()
        self.start_dialog([
            f"🌅 Hari {self.state.day} dimulai",
            f"{self.state.get_season_name()}, hari {self.state.day_in_season}",
            f"Cuaca: {self.state.weather}",
        ], "🌄 Pagi")
        self.check_quest_progress()

    # ═══════════════════════════════════════════════════
    #  PANELS
    # ═══════════════════════════════════════════════════
    def open_panel(self, name):
        self.panel = name
        self.panel_select = 0
        self.mode = 'panel'

    def close_panel(self):
        self.panel = None
        self.mode = 'play'

    def cycle_seed(self, d):
        szn = self.state.get_season()
        avail = [k for k, c in CROPS.items()
                 if szn in c['seasons'] or self.state.greenhouse_open
                 or self.state.inventory.get(k+'_seed', 0) > 0]
        if not avail: return
        try: i = avail.index(self.state.seed_key)
        except ValueError: i = 0
        i = (i + d) % len(avail)
        self.state.seed_key = avail[i]
        self.notif(f"Benih: {CROPS[self.state.seed_key]['name']}")

    def _buy_seeds(self, crop_id, cost):
        if self.state.gold < cost:
            self.notif("Gold tidak cukup!"); return
        self.state.gold -= cost
        key = crop_id + '_seed'
        self.state.inventory[key] = self.state.inventory.get(key, 0) + 3
        self.notif(f"Beli {CROPS[crop_id]['name']}!")

    def _sell_all(self):
        total = 0
        for crop_id, crop in CROPS.items():
            count = self.state.inventory.get(crop_id, 0)
            if count > 0:
                total += count * crop['sell']
                del self.state.inventory[crop_id]
        for wild_id, wild in WILD_ITEMS.items():
            count = self.state.inventory.get(wild_id, 0)
            if count > 0:
                total += count * wild['sell']
                del self.state.inventory[wild_id]
        for prod in ['susu', 'telur', 'wol']:
            count = self.state.inventory.get(prod, 0)
            if count > 0:
                price = {'susu': 30, 'telur': 15, 'wol': 50}.get(prod, 20)
                total += count * price
                del self.state.inventory[prod]
        if total > 0:
            self.state.gold += total
            self.state.stats['earned'] += total
            self.notif(f"+{total}G dari penjualan!")
            self.check_quest_progress()
        else:
            self.notif("Tidak ada yang dijual.")

    def _buy_upgrade(self, upg_id, cost):
        if self.state.gold < cost:
            self.notif("Gold tidak cukup!"); return
        self.state.gold -= cost
        self.state.upgrades[upg_id] = True
        if upg_id == 'bag':
            self.state.max_energy += 20
            self.state.energy = min(self.state.energy + 20, self.state.max_energy)
        self.notif("⚒ Upgrade!")
        self.check_quest_progress()

    # ═══════════════════════════════════════════════════
    #  QUEST
    # ═══════════════════════════════════════════════════
    def check_quest_progress(self):
        s = self.state
        st = s.quest_stage
        if st == 0 and s.mail_read: s.quest_stage = 1
        elif st == 1 and s.stats['lobak_planted'] >= 3 and s.stats['watered'] >= 3: s.quest_stage = 2
        elif st == 2 and s.stats['lobak_harvested'] >= 3:
            s.quest_stage = 3
            s.shop_unlocked = True
            self.notif("🎉 Warung terbuka!")
        elif st == 3 and s.stats['earned'] >= 150: s.quest_stage = 4
        elif st == 4 and (s.upgrades['hoe'] or s.upgrades['water']): s.quest_stage = 5
        elif st == 5 and s.stats['corn_harvested'] >= 2: s.quest_stage = 6
        elif st == 6 and s.stats['gifts'] >= 3: s.quest_stage = 7
        elif st == 7 and s.captured_supernatural >= 1: s.quest_stage = 8
        elif st == 8 and s.met_jin: s.quest_stage = 9
        elif st == 9 and s.day >= DAYS_PER_SEASON * 4:
            s.quest_stage = 10
            self.start_dialog([
                "🌻 SATU TAHUN BERLALU!",
                "Lembah Karsa hidup kembali.",
                "— TAMAT —",
            ], "🌻 Selamat!")

    def notif(self, text):
        self.notif_text = text
        self.notif_timer = 2500

    # ═══════════════════════════════════════════════════
    #  DIALOG
    # ═══════════════════════════════════════════════════
    def start_dialog(self, lines, speaker, callback=None):
        self.dialog_lines = lines
        self.dialog_index = 0
        self.dialog_speaker = speaker
        self.dialog_callback = callback
        self.typewriter_progress = 0
        self.mode = 'dialog'

    def advance_dialog(self):
        current = self.dialog_lines[self.dialog_index]
        if self.typewriter_progress < len(current):
            self.typewriter_progress = len(current)
            return
        self.dialog_index += 1
        if self.dialog_index >= len(self.dialog_lines):
            self.mode = 'play'
            cb = self.dialog_callback
            self.dialog_callback = None
            if cb: cb()
        else:
            self.typewriter_progress = 0

    # ═══════════════════════════════════════════════════
    #  NEW GAME / LOAD
    # ═══════════════════════════════════════════════════
    def start_new_game(self):
        self.state = GameState()
        init_npc_data(self.state)
        spawn_wild_entities(self.state)
        self.mode = 'play'
        self.cam_x = self.state.player_x - VIEW_W / 2
        self.cam_y = self.state.player_y - VIEW_H / 2
        self.start_dialog([
            "🌅 Kamu tiba di Lembah Karsa.",
            "Kebun Paman Arsa, dunia mistis.",
            "Baca surat di kotak pos 📬.",
            "Tekan F1 untuk bantuan.",
        ], "🏡 Selamat Datang")

    def try_load_game(self):
        loaded = GameState.load()
        if loaded:
            self.state = loaded
            init_npc_data(self.state)
            if not self.state.wild_entities:
                spawn_wild_entities(self.state)
            self.mode = 'play'
            self.cam_x = self.state.player_x - VIEW_W / 2
            self.cam_y = self.state.player_y - VIEW_H / 2
            self.notif("💾 Game dimuat!")
        else:
            self.notif("❌ Tidak ada save.")

    # ═══════════════════════════════════════════════════
    #  RENDER
    # ═══════════════════════════════════════════════════
    def render(self):
        self.screen.fill(C.ui_bg)
        if self.mode == 'title':
            self.render_title(); return
        self.render_world()
        self.render_hud()
        if self.mode == 'dialog':
            self.render_dialog()
        if self.mode == 'panel':
            self.render_panel()
        if self.notif_timer > 0 and self.notif_text:
            self.render_notification()
        if self.mode == 'fade' or self.fade_alpha > 0:
            ov = pygame.Surface((SCREEN_W, SCREEN_H))
            ov.set_alpha(self.fade_alpha)
            ov.fill((0, 0, 0))
            self.screen.blit(ov, (0, 0))

    def render_title(self):
        self.screen.fill((20, 10, 35))
        title = self.font_title.render("🌱 LEMBAH KARSA 🌾", True, C.ui_gold)
        sub = self.font.render("Smooth Edition v2.5", True, C.ui_text)
        start = self.font_big.render("SPACE — Mulai Baru", True, C.ui_green)
        load = self.font_big.render("L — Load Game", True, C.ui_text)
        story1 = self.font_small.render("Paman Arsa mewariskan kebun di lembah mistis.", True, (150, 130, 180))
        story2 = self.font_small.render("Tani, jelajahi, temui makhluk halus!", True, (150, 130, 180))
        self.screen.blit(title, (SCREEN_W//2 - title.get_width()//2, 80))
        self.screen.blit(sub, (SCREEN_W//2 - sub.get_width()//2, 130))
        self.screen.blit(story1, (SCREEN_W//2 - story1.get_width()//2, 200))
        self.screen.blit(story2, (SCREEN_W//2 - story2.get_width()//2, 220))
        self.screen.blit(start, (SCREEN_W//2 - start.get_width()//2, 300))
        self.screen.blit(load, (SCREEN_W//2 - load.get_width()//2, 340))
        # Animated player preview
        idx = (pygame.time.get_ticks() // 250) % 2
        p = ANIMATED['player']['down'][idx]
        self.screen.blit(p, (SCREEN_W//2 - 16, 250))

    def render_world(self):
        scene = SCENES[self.state.scene_name]
        # Override jika di dungeon: pakai state.dungeon_tiles
        if self.state.scene_name == 'dungeon' and self.state.dungeon_tiles:
            class _DG:
                tiles = self.state.dungeon_tiles
                w = len(self.state.dungeon_tiles[0])
                h = len(self.state.dungeon_tiles)
                indoor = True
                portals = []
                name = 'dungeon'
                display = f"Lv.{self.state.dungeon_level}"
            scene = _DG()
        indoor = scene.indoor
        bg = (40, 25, 15) if indoor else (60, 100, 140) if self.state.is_night() else (135, 180, 200)
        self.screen.fill(bg, (0, 0, SCREEN_W, VIEW_H * TILE))

        # Pixel offset dari kamera
        cam_px = -int(self.cam_x * TILE)
        cam_py = -int(self.cam_y * TILE)

        # Tentukan range tile yang perlu render
        start_tx = max(0, int(self.cam_x))
        end_tx = min(scene.w, int(self.cam_x) + VIEW_W + 2)
        start_ty = max(0, int(self.cam_y))
        end_ty = min(scene.h, int(self.cam_y) + VIEW_H + 2)

        # Render tile
        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                t = scene.tiles[ty][tx]
                px_ = tx * TILE + cam_px
                py_ = ty * TILE + cam_py
                key = f"{tx},{ty},{self.state.scene_name}"
                soil = self.state.soil.get(key)
                if soil and soil.get('tilled'):
                    sprite = SPRITES['tilled_wet'] if soil.get('watered') else SPRITES['tilled_dry']
                    self.screen.blit(sprite, (px_, py_))
                    if soil.get('crop'):
                        stage = min(soil.get('age', 0), 3)
                        crop_id = soil['crop']
                        if crop_id in SPRITES['crops']:
                            self.screen.blit(SPRITES['crops'][crop_id][stage], (px_, py_))
                    continue
                if t == W:
                    f = (pygame.time.get_ticks() // 250) % 4
                    self.screen.blit(ANIMATED['water'][f], (px_, py_))
                elif t == FP:
                    f = (pygame.time.get_ticks() // 200) % 2
                    self.screen.blit(ANIMATED['fireplace'][f], (px_, py_))
                elif t == LN:
                    f = (pygame.time.get_ticks() // 300) % 2
                    self.screen.blit(ANIMATED['lantern'][f], (px_, py_))
                elif t == H:
                    s = pygame.Surface((TILE, TILE))
                    s.fill(C.r0)
                    pygame.draw.rect(s, C.r1, (0, 0, TILE, 8))
                    pygame.draw.rect(s, C.b0, (0, 8, TILE, TILE-8))
                    self.screen.blit(s, (px_, py_))
                else:
                    name = TILE_NAMES.get(t)
                    if name and name in SPRITES:
                        self.screen.blit(SPRITES[name], (px_, py_))

        # Wild entities
        is_night = self.state.is_night()
        for w in self.state.wild_entities:
            if w['scene'] != self.state.scene_name: continue
            if w.get('night_only', False) and not is_night: continue
            px_ = w['x'] * TILE + cam_px
            py_ = w['y'] * TILE + cam_py
            if -TILE < px_ < SCREEN_W and -TILE < py_ < VIEW_H * TILE:
                kind = w['kind']
                if kind == 'running_mushroom':
                    f = (pygame.time.get_ticks() // 200) % 2
                    self.screen.blit(ANIMATED['running_mushroom'][f], (px_, py_))
                elif kind == 'firefly':
                    f = (pygame.time.get_ticks() // 250) % 3
                    self.screen.blit(ANIMATED['firefly'][f], (px_, py_))
                elif kind in SPRITES:
                    self.screen.blit(SPRITES[kind], (px_, py_))

        # NPCs
        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] != self.state.scene_name: continue
            if pos['x'] < 0: continue
            px_ = pos['x'] * TILE + cam_px
            py_ = pos['y'] * TILE + cam_py

            npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
            if not npc_data: continue
            npc_type = npc_data.get('type', 'human')

            # Naga = sprite besar 96x64 (3x2 tile)
            if npc_type == 'naga':
                # Geser agar naga terpusat di posisi tile
                draw_x = px_ - TILE  # geser kiri 1 tile
                draw_y = py_ - TILE  # geser atas 1 tile
                if -96 < draw_x < SCREEN_W and -64 < draw_y < VIEW_H * TILE:
                    sprite = ANIMATED['npc_naga']['down'][self.walk_anim_index]
                    self.screen.blit(sprite, (int(draw_x), int(draw_y)))
                    # Heart kalau ada
                    hearts = self.state.npc_hearts.get(npc_id, 0)
                    if hearts > 0:
                        for i in range(min(hearts // 2, 5)):
                            pygame.draw.rect(self.screen, C.ui_red,
                                           (px_ + 2 + i*5, draw_y - 6, 3, 3))
                continue

            if -TILE < px_ < SCREEN_W and -TILE < py_ < VIEW_H * TILE:
                anim_key = f'npc_{npc_id}' if npc_type == 'human' else f'npc_{npc_type}'
                if anim_key in ANIMATED:
                    sprite = ANIMATED[anim_key]['down'][self.walk_anim_index]
                    self.screen.blit(sprite, (px_, py_))
                hearts = self.state.npc_hearts.get(npc_id, 0)
                if hearts > 0:
                    for i in range(min(hearts // 2, 5)):
                        pygame.draw.rect(self.screen, C.ui_red,
                                       (px_ + 2 + i*5, py_ - 6, 3, 3))

        # Player (smooth pixel position)
        ppx = self.state.player_x * TILE + cam_px
        ppy = self.state.player_y * TILE + cam_py
        # Pilih frame: blink kadang-kadang, walk saat moving, idle saat tidak
        if self.show_blink:
            frame_idx = 2  # blink
        elif self.is_moving():
            frame_idx = self.walk_anim_index
        else:
            frame_idx = 0  # idle
        sprite = ANIMATED['player'][self.state.facing][frame_idx]
        self.screen.blit(sprite, (int(ppx), int(ppy)))

        # ─── Render Mob (dungeon) ───────────────────
        for mob in self.state.mobs:
            mpx = mob['x'] * TILE + cam_px
            mpy = mob['y'] * TILE + cam_py
            if mpx < -TILE or mpx > SCREEN_W or mpy < -TILE or mpy > VIEW_H*TILE:
                continue
            flash = mob.get('dmg_flash_ms', 0) > 0
            color = (255, 200, 200) if flash else (180, 60, 80)
            if mob['kind'] == 'naga_boss':
                size = TILE * 2
                ms = pygame.Surface((size, size), pygame.SRCALPHA)
                pygame.draw.circle(ms, (220, 80, 60), (size//2, size//2), size//2 - 2)
                pygame.draw.circle(ms, (60, 0, 0), (size//2, size//2), size//2 - 2, 3)
                self.screen.blit(ms, (int(mpx - TILE//2), int(mpy - TILE//2)))
            else:
                ms = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
                pygame.draw.rect(ms, color, (4, 4, TILE - 8, TILE - 8))
                pygame.draw.rect(ms, (40, 20, 20), (4, 4, TILE - 8, TILE - 8), 2)
                # Mata
                pygame.draw.rect(ms, (255, 255, 100), (8, 10, 3, 3))
                pygame.draw.rect(ms, (255, 255, 100), (TILE - 11, 10, 3, 3))
                # HP bar mini
                hp_pct = max(0, mob['hp'] / max(1, mob.get('max_hp', mob['hp'])))
                pygame.draw.rect(ms, (60, 20, 20), (2, 0, TILE - 4, 3))
                pygame.draw.rect(ms, (220, 60, 80), (2, 0, int((TILE-4) * hp_pct), 3))
                self.screen.blit(ms, (int(mpx), int(mpy)))

        # Facing indicator
        fx, fy = self.get_facing_tile()
        fpx = fx * TILE + cam_px
        fpy = fy * TILE + cam_py
        if 0 <= fpx < SCREEN_W and 0 <= fpy < VIEW_H * TILE:
            pygame.draw.rect(self.screen, C.ui_gold, (fpx + 2, fpy + 2, TILE-4, TILE-4), 1)

        # Weather
        if self.state.weather == 'Hujan' and not indoor:
            t = pygame.time.get_ticks()
            for i in range(50):
                rx = (i * 37 + int(t * 0.3)) % SCREEN_W
                ry = (i * 19 + int(t * 0.4)) % (VIEW_H * TILE)
                pygame.draw.line(self.screen, (120, 180, 255), (rx, ry), (rx, ry + 6))

        # Night overlay
        if self.state.is_night() and not indoor:
            darkness = 80 if self.state.get_hour() < 5 or self.state.get_hour() >= 22 else 50
            dark = pygame.Surface((SCREEN_W, VIEW_H * TILE))
            dark.set_alpha(darkness)
            dark.fill((0, 0, 30))
            self.screen.blit(dark, (0, 0))

    def render_hud(self):
        hud_y = VIEW_H * TILE
        pygame.draw.rect(self.screen, C.ui_bg, (0, hud_y, SCREEN_W, SCREEN_H - hud_y))
        pygame.draw.rect(self.screen, C.ui_border, (0, hud_y, SCREEN_W, SCREEN_H - hud_y), 2)

        day_txt = self.font_small.render(
            f"Hari {self.state.day} | {self.state.get_time_str()} | {self.state.get_season_name()}",
            True, C.ui_text)
        self.screen.blit(day_txt, (10, hud_y + 5))

        e_txt = self.font_small.render(f"⚡ {self.state.energy}/{self.state.max_energy}", True, C.ui_green)
        g_txt = self.font_small.render(f"💰 {self.state.gold}G", True, C.ui_gold)
        w_txt = self.font_small.render(f"🌤 {self.state.weather}", True, C.ui_cyan)
        self.screen.blit(e_txt, (10, hud_y + 22))
        self.screen.blit(g_txt, (130, hud_y + 22))
        self.screen.blit(w_txt, (230, hud_y + 22))

        # HP indicator (v7)
        hp_color = (255, 100, 100) if self.state.hp < 30 else (255, 180, 180)
        hp_txt = self.font_small.render(f"❤ {self.state.hp}/{self.state.max_hp}", True, hp_color)
        self.screen.blit(hp_txt, (450, hud_y + 22))

        # Dungeon level indicator (v7)
        if self.state.dungeon_level > 0:
            dl_txt = self.font_small.render(f"⛏ Lv.{self.state.dungeon_level}", True, (200, 220, 255))
            self.screen.blit(dl_txt, (550, hud_y + 22))

        scene_name = SCENES[self.state.scene_name].display
        loc_txt = self.font_small.render(f"📍 {scene_name}", True, (200, 180, 255))
        self.screen.blit(loc_txt, (350, hud_y + 22))

        # Tool slots — 10 slot dengan icon emoji (lebih jelas dari teks)
        TOOL_ICONS = ['⛏️', '💧', '🌱', '✂️', '🪓', '⚔️', '🔱', '🏹', '⛏', '🎁']
        slot_w = 38
        for i in range(len(TOOLS)):
            x = 10 + i * (slot_w + 2)
            y = hud_y + 42
            sel = (i == self.state.tool_index)
            bg = C.ui_bg2 if sel else (30, 20, 45)
            pygame.draw.rect(self.screen, bg, (x, y, slot_w, 32), border_radius=3)
            color = C.ui_gold if sel else C.ui_border
            pygame.draw.rect(self.screen, color, (x, y, slot_w, 32), 2 if sel else 1, border_radius=3)
            # Number kecil di atas
            num = self.font_small.render(f"{(i+1) % 10}", True, C.ui_gold)
            self.screen.blit(num, (x + 2, y + 1))
            # Icon di tengah
            icon = self.font.render(TOOL_ICONS[i] if i < len(TOOL_ICONS) else '?', True, C.ui_text)
            self.screen.blit(icon, (x + slot_w//2 - icon.get_width()//2, y + 12))

        cur = self.font_small.render(
            f"Aktif: {TOOLS[self.state.tool_index]} | 🌱 {CROPS[self.state.seed_key]['name']}",
            True, C.ui_text)
        self.screen.blit(cur, (10 + len(TOOLS)*(slot_w+2) + 10, hud_y + 48))

        quest_stage = QUEST_STAGES[min(self.state.quest_stage, len(QUEST_STAGES) - 1)]
        q = self.font_small.render(f"📋 {quest_stage['t']}: {quest_stage['d']}", True, (180, 255, 180))
        self.screen.blit(q, (290, hud_y + 62))

        hints_txt = "I=Inv | M=Map | J=Quest | H=Hub | F=Tangkap | F1=Help"
        if self.is_running:
            hints_txt = "🏃 LARI | " + hints_txt
        hints = self.font_small.render(hints_txt, True, (140, 120, 170))
        self.screen.blit(hints, (10, hud_y + 78))

    def render_dialog(self):
        box_y = VIEW_H * TILE - 90
        pygame.draw.rect(self.screen, (10, 5, 25), (0, box_y, SCREEN_W, 90))
        pygame.draw.rect(self.screen, C.ui_border, (0, box_y, SCREEN_W, 90), 2)
        if self.dialog_speaker:
            sp = self.font.render(f"▶ {self.dialog_speaker}", True, C.ui_gold)
            self.screen.blit(sp, (12, box_y + 8))
        current = self.dialog_lines[self.dialog_index]
        visible = current[:self.typewriter_progress]
        words = visible.split(' ')
        line = ''; y_off = 30
        for word in words:
            test = line + word + ' '
            if self.font.size(test)[0] > SCREEN_W - 20:
                t = self.font.render(line, True, C.ui_text)
                self.screen.blit(t, (12, box_y + y_off))
                y_off += 22
                line = word + ' '
            else:
                line = test
        if line:
            t = self.font.render(line, True, C.ui_text)
            self.screen.blit(t, (12, box_y + y_off))
        if self.typewriter_progress >= len(current):
            hint = self.font_small.render(
                f"▶ SPACE  ({self.dialog_index+1}/{len(self.dialog_lines)})",
                True, (130, 110, 160))
            self.screen.blit(hint, (SCREEN_W - 180, box_y + 72))

    def render_panel(self):
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))
        bw, bh = 500, 380
        bx = SCREEN_W//2 - bw//2
        by = SCREEN_H//2 - bh//2
        pygame.draw.rect(self.screen, (15, 8, 30), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, bw, bh), 3)

        if self.panel == 'inventory':
            panels.render_panel_inventory(self, bx, by, bw, bh)
        elif self.panel == 'map':
            panels.render_panel_map(self, bx, by, bw, bh)
        elif self.panel == 'quest':
            panels.render_panel_quest(self, bx, by, bw, bh)
        elif self.panel == 'relations':
            panels.render_panel_relations(self, bx, by, bw, bh)
        elif self.panel == 'help':
            panels.render_panel_help(self, bx, by, bw, bh)
        elif self.panel == 'shop':
            panels.render_panel_shop(self, bx, by, bw, bh)
        elif self.panel == 'upgrade':
            panels.render_panel_upgrade(self, bx, by, bw, bh)

    def render_notification(self):
        text = self.font.render(self.notif_text, True, C.ui_gold)
        tw = text.get_width() + 20
        tx = SCREEN_W//2 - tw//2
        ty = 10
        pygame.draw.rect(self.screen, (10, 5, 25), (tx, ty, tw, 30))
        pygame.draw.rect(self.screen, C.ui_border, (tx, ty, tw, 30), 2)
        self.screen.blit(text, (tx + 10, ty + 6))


    # ═══════════════════════════════════════════════
    # COMBAT (v7: Z attack, X mining)
    # ═══════════════════════════════════════════════
    def attack(self, weapon='Pedang'):
        """Swing alat/pedang ke arah facing. Hit semua mob dalam radius."""
        from .config import PLAYER_ATTACK_RANGE, PLAYER_ATTACK_COOLDOWN_MS, TOOL_DAMAGE
        st = self.state
        if st.attack_cooldown_ms > 0:
            return
        # Weapon damage scaling
        sword_dmg = {'': 0, 'sword_kayu': 10, 'sword_besi': 20,
                     'sword_emas': 35, 'sword_mithril': 55,
                     'sword_keabadian': 100}.get(st.sword_id, 0)
        # Weapon-specific bonuses
        weapon_range = PLAYER_ATTACK_RANGE
        if weapon == 'Tombak':
            weapon_range = PLAYER_ATTACK_RANGE + 1.0  # tombak jangkauan jauh
        elif weapon == 'Panah':
            weapon_range = PLAYER_ATTACK_RANGE + 2.0  # panah jauh
            sword_dmg = max(sword_dmg, 8)             # panah selalu damage minimum
        dmg = TOOL_DAMAGE + sword_dmg
        st.attack_cooldown_ms = PLAYER_ATTACK_COOLDOWN_MS
        import math
        hit = 0
        for mob in list(st.mobs):
            d = math.hypot(mob['x'] - st.player_x, mob['y'] - st.player_y)
            if d <= weapon_range:
                mob['hp'] -= dmg
                mob['dmg_flash_ms'] = 200
                hit += 1
                if mob['hp'] <= 0:
                    st.mobs.remove(mob)
                    st.stats['mobs_killed'] = st.stats.get('mobs_killed', 0) + 1
                    drops = mob.get('drops', {})
                    for item, qty in drops.items():
                        if item == 'gold':
                            st.gold += qty
                        else:
                            st.inventory[item] = st.inventory.get(item, 0) + qty
        if hit:
            self.notif(f"⚔ Hit {hit}!")

    def use_pickaxe(self):
        """Tambang ore tile di depan."""
        from .config import (CV_W, ORE_TBG, ORE_BSI, ORE_EMS, ORE_KRS, ORE_MTH,
                             CRYS, MINED, D, STAIRS_DOWN)
        st = self.state
        fx, fy = self.get_facing_tile()
        if st.dungeon_level == 0:
            self.notif("Pickaxe hanya di gua!")
            return
        if st.pickaxe_tier <= 0:
            self.notif("Belum punya pickaxe!")
            return
        tiles = st.dungeon_tiles
        if not (0 <= fy < len(tiles) and 0 <= fx < len(tiles[0])):
            return
        t = tiles[fy][fx]
        ore_map = {ORE_TBG: ('tembaga', 1), ORE_BSI: ('besi', 1),
                   ORE_EMS: ('emas', 1), ORE_KRS: ('kristal', 1),
                   ORE_MTH: ('mithril', 1), CRYS: ('kristal', 2)}
        tier_req = {ORE_TBG: 1, ORE_BSI: 2, ORE_EMS: 3, ORE_KRS: 3,
                    ORE_MTH: 4, CRYS: 4, CV_W: 1}
        if t not in tier_req and t != D:
            self.notif("Tidak bisa ditambang.")
            return
        if t in tier_req and st.pickaxe_tier < tier_req[t]:
            self.notif(f"Pickaxe terlalu lemah (butuh tier {tier_req[t]})!")
            return
        if st.energy < 2:
            self.notif("Energi tidak cukup!")
            return
        st.energy -= 2
        if t == D:
            import random
            if random.random() < 0.3:
                tiles[fy][fx] = STAIRS_DOWN
                self.notif("✨ Tangga muncul!")
            else:
                self.notif("Hanya tanah biasa.")
            return
        tiles[fy][fx] = MINED
        if t in ore_map:
            mat, qty = ore_map[t]
            st.inventory[mat] = st.inventory.get(mat, 0) + qty
            st.stats['minerals_mined'] = st.stats.get('minerals_mined', 0) + qty
            self.notif(f"⛏ +{qty} {mat}")

    def update_combat(self, dt):
        """Update cooldown, invuln, mob movement+attack."""
        from .config import INVULN_AFTER_HIT_MS
        st = self.state
        st.attack_cooldown_ms = max(0, st.attack_cooldown_ms - dt)
        st.invuln_timer_ms = max(0, st.invuln_timer_ms - dt)
        import math
        for mob in list(st.mobs):
            if 'dmg_flash_ms' in mob:
                mob['dmg_flash_ms'] = max(0, mob['dmg_flash_ms'] - dt)
            dx = st.player_x - mob['x']
            dy = st.player_y - mob['y']
            d = math.hypot(dx, dy)
            if d < 0.001:
                continue
            speed = mob.get('speed', 1.5) / 1000.0
            move = speed * dt
            if d > 0.8:
                mob['x'] += (dx / d) * move
                mob['y'] += (dy / d) * move
            else:
                if 'attack_cooldown_ms' not in mob:
                    mob['attack_cooldown_ms'] = 0
                mob['attack_cooldown_ms'] = max(0, mob.get('attack_cooldown_ms', 0) - dt)
                if mob['attack_cooldown_ms'] <= 0 and st.invuln_timer_ms <= 0:
                    st.hp -= mob.get('damage', 5)
                    st.invuln_timer_ms = INVULN_AFTER_HIT_MS
                    mob['attack_cooldown_ms'] = 1000
                    if st.hp <= 0:
                        st.hp = st.max_hp
                        st.scene_name = 'clinic'
                        st.player_x, st.player_y = 7.0, 5.0
                        st.dungeon_level = 0
                        st.mobs = []
                        st.energy = max(10, st.energy // 2)
                        st.gold = max(0, st.gold - 50)  # biaya rumah sakit
                        self.notif("💀 Pingsan! Bu Maya menyelamatkanmu di klinik. (-50G)")

    def descend_dungeon(self):
        """Turun ke level berikutnya."""
        from .dungeon import generate_dungeon_level
        self.state.dungeon_level += 1
        self.state.stats['deepest_level'] = max(
            self.state.stats.get('deepest_level', 0), self.state.dungeon_level)
        self.state.dungeon_seed = int(pygame.time.get_ticks())
        tiles, sx, sy, mob_specs = generate_dungeon_level(
            self.state.dungeon_level, self.state.dungeon_seed)
        self.state.dungeon_tiles = tiles
        self.state.player_x = float(sx)
        self.state.player_y = float(sy)
        self.state.scene_name = 'dungeon'
        self.state.mobs = []
        for spec in mob_specs:
            spec['target_x'] = spec['x']
            spec['target_y'] = spec['y']
            spec['max_hp'] = spec['hp']
            self.state.mobs.append(spec)
        self.notif(f"⛏ Level {self.state.dungeon_level}")

    def ascend_dungeon(self):
        """Naik ke permukaan."""
        self.state.dungeon_level = 0
        self.state.dungeon_tiles = []
        self.state.mobs = []
        self.state.scene_name = 'naga_cave'
        self.state.player_x = 7.0
        self.state.player_y = 10.0
        self.notif("🌅 Kembali ke permukaan")
