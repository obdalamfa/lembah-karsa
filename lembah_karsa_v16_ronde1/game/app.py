"""
app.py — Game class utama (orchestrator tipis).

Setelah pemisahan v5:
  - Movement & tools & interaction → player.py (PlayerController)
  - Wild entities & NPC AI         → entities.py
  - Sprites loader & fallback      → sprites.py
  - UI panels                      → panels.py
  - Tile data                      → scenes.py
  - Save state                     → state.py
  - Karakter & dialog              → data.py

Game class hanya menangani:
  - Event loop & input routing
  - Camera follow
  - Render orchestration (world + HUD + dialog + panels + transitions)
  - Scene transition + sleep + quest progression
  - Buy/sell shop & upgrade transactions
"""
import pygame
import math
import random

from .config import (
    C, TILE, VIEW_W, VIEW_H, SCREEN_W, SCREEN_H, FPS,
    INGAME_MINUTES_PER_REAL_SECOND, FORCE_SLEEP_HOUR,
    ANIMATION_FPS, DAYS_PER_SEASON,
    TILE_NAMES, TOOLS,
    G, D, P, W, FL, WL, TR, H, MB, DR, FN, GT, BD, ST, TB, BS, MR, FP, CL, PP, CH,
    CT, SH, GR, LN, DT, CV_W, CV_F, PEN, STR,
    CRYPT_W, CRYPT_F, CRYS, BAT_D, WTF, DCK, BOT, LLY
)
from .state import GameState
from .data import (CROPS, WILD_ITEMS, HUMAN_NPCS, SUPERNATURAL_NPCS,
                   ANIMAL_NPCS, SCHEDULES, QUEST_STAGES, all_npcs)
from .scenes import SCENES
from .sprites import init_sprites, SPRITES, ANIMATED
from .entities import (spawn_wild_entities, respawn_wild_at_morning,
                       update_wild_entities, find_wild_at,
                       update_all_npc_positions, init_npc_data, can_walk_at,
                       update_animal_roaming, update_npc_smooth_movement)
from .player import PlayerController
from . import panels


# Tile yang occlude karakter (depth-sort)
TALL_TILES = {TR, DT, FN, H, MB, WTF}


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🌱 Lembah Karsa v5 — Modular Edition")
        self.clock = pygame.time.Clock()

        self.font_small = pygame.font.Font(None, 16)
        self.font = pygame.font.Font(None, 20)
        self.font_big = pygame.font.Font(None, 28)
        self.font_title = pygame.font.Font(None, 40)

        init_sprites()

        self.state = GameState()
        self.player_ctrl = PlayerController(self)

        self.running = True
        self.mode = 'title'

        # Camera
        self.cam_x = 0.0
        self.cam_y = 0.0
        self.cam_target_x = 0.0
        self.cam_target_y = 0.0

        # Animation
        self.anim_timer = 0
        self.walk_anim_index = 0
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

        # Periodic update timers
        self.wild_timer = 0

    # ═══════════════════════════════════════════════════
    #  GAME LOOP
    # ═══════════════════════════════════════════════════
    def run(self):
        while self.running:
            dt = self.clock.tick(FPS)
            self.handle_input()
            self.update(dt)
            self.render()
        pygame.quit()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                self.handle_keydown(event)

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

        # MODE PLAY — delegate ke player_ctrl untuk action keys
        if event.key == pygame.K_SPACE:
            self.player_ctrl.use_tool()
        elif event.key == pygame.K_e:
            self.player_ctrl.interact()
        elif event.key == pygame.K_f:
            self.player_ctrl.try_capture_supernatural()
        elif event.key == pygame.K_g:
            self.player_ctrl.show_npc_schedule()
        elif pygame.K_1 <= event.key <= pygame.K_6:
            self.state.tool_index = event.key - pygame.K_1
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
        close_keys = {
            'inventory': pygame.K_i, 'map': pygame.K_m,
            'quest': pygame.K_j, 'relations': pygame.K_h,
            'help': pygame.K_F1,
        }
        if event.key == pygame.K_ESCAPE:
            self.close_panel(); return
        if self.panel in close_keys and event.key == close_keys[self.panel]:
            self.close_panel(); return

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
    #  UPDATE
    # ═══════════════════════════════════════════════════
    def update(self, dt):
        self.anim_timer += dt
        self.blink_timer += dt
        if self.notif_timer > 0:
            self.notif_timer -= dt

        # Walk frame animation
        anim_period_ms = 1000 / ANIMATION_FPS
        if self.anim_timer > anim_period_ms:
            self.anim_timer = 0
            self.walk_anim_index = (self.walk_anim_index + 1) % 2

        # Blink (~ tiap 3 detik, durasi 150ms)
        if self.blink_timer > 3000:
            self.show_blink = True
            if self.blink_timer > 3150:
                self.show_blink = False
                self.blink_timer = 0

        # Fade transition
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
                self.start_dialog(["Sudah jam 23:00...",
                                   "Kamu kelelahan dan tertidur."],
                                  "🌙 Larut Malam", callback=self.sleep_next_day)

            # NPC schedule update on hour change
            old_min = self.state.time_minutes - dt * INGAME_MINUTES_PER_REAL_SECOND / 1000.0
            old_hour = int(old_min // 60)
            new_hour = int(self.state.time_minutes // 60)
            if old_hour != new_hour:
                update_all_npc_positions(self.state)

            # Smooth movement (di player_ctrl)
            self.player_ctrl.update_movement(dt)

            # Wild entities tick
            self.wild_timer += dt
            if self.wild_timer > 800:
                self.wild_timer = 0
                update_wild_entities(self.state, dt)

            # Animal free-roam dalam pen
            update_animal_roaming(self.state, dt)

            # NPC smooth interpolation ke target schedule
            update_npc_smooth_movement(self.state, dt)

            # Smooth camera follow
            self.update_camera(dt)

        if self.mode == 'dialog':
            current = self.dialog_lines[self.dialog_index]
            if self.typewriter_progress < len(current):
                self.typewriter_progress += 2

    def update_camera(self, dt):
        scene = SCENES[self.state.scene_name]
        self.cam_target_x = self.state.player_x - VIEW_W / 2
        self.cam_target_y = self.state.player_y - VIEW_H / 2
        self.cam_target_x = max(0, min(scene.w - VIEW_W, self.cam_target_x))
        self.cam_target_y = max(0, min(scene.h - VIEW_H, self.cam_target_y))
        lerp_speed = 8.0 / 1000.0
        cdx = self.cam_target_x - self.cam_x
        cdy = self.cam_target_y - self.cam_y
        self.cam_x += cdx * min(1, lerp_speed * dt)
        self.cam_y += cdy * min(1, lerp_speed * dt)

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
        pygame.display.flip()

    def render_title(self):
        self.screen.fill((20, 10, 35))
        title = self.font_title.render("🌱 LEMBAH KARSA 🌾", True, C.ui_gold)
        sub = self.font.render("v5 Modular Edition", True, C.ui_text)
        start = self.font_big.render("SPACE — Mulai Baru", True, C.ui_green)
        load = self.font_big.render("L — Load Game", True, C.ui_text)
        story1 = self.font_small.render(
            "Paman Arsa mewariskan kebun di lembah mistis.",
            True, (150, 130, 180))
        story2 = self.font_small.render(
            "Tani, jelajahi 15 area, temui 31 makhluk!",
            True, (150, 130, 180))
        self.screen.blit(title, (SCREEN_W // 2 - title.get_width() // 2, 80))
        self.screen.blit(sub, (SCREEN_W // 2 - sub.get_width() // 2, 130))
        self.screen.blit(story1, (SCREEN_W // 2 - story1.get_width() // 2, 200))
        self.screen.blit(story2, (SCREEN_W // 2 - story2.get_width() // 2, 220))
        self.screen.blit(start, (SCREEN_W // 2 - start.get_width() // 2, 300))
        self.screen.blit(load, (SCREEN_W // 2 - load.get_width() // 2, 340))
        # Animasi player preview
        idx = (pygame.time.get_ticks() // 250) % 2
        if 'player' in ANIMATED:
            p = ANIMATED['player']['down'][idx]
            self.screen.blit(p, (SCREEN_W // 2 - 16, 250))

        pygame.display.flip()

    def render_world(self):
        scene = SCENES[self.state.scene_name]
        indoor = scene.indoor
        if indoor:
            bg = (40, 25, 15)
        elif self.state.is_night():
            bg = (60, 100, 140)
        else:
            bg = (135, 180, 200)
        self.screen.fill(bg, (0, 0, SCREEN_W, VIEW_H * TILE))

        cam_px = -int(self.cam_x * TILE)
        cam_py = -int(self.cam_y * TILE)

        start_tx = max(0, int(self.cam_x))
        end_tx = min(scene.w, int(self.cam_x) + VIEW_W + 2)
        start_ty = max(0, int(self.cam_y))
        end_ty = min(scene.h, int(self.cam_y) + VIEW_H + 2)

        # ═══ LAYER 1: GROUND TILES ═══
        deferred_tall = []  # (sort_y, draw_callable)

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                t = scene.tiles[ty][tx]
                px_ = tx * TILE + cam_px
                py_ = ty * TILE + cam_py
                key = f"{tx},{ty},{self.state.scene_name}"
                soil = self.state.soil.get(key)

                # Soil & crop
                if soil and soil.get('tilled'):
                    sprite = (SPRITES['tilled_wet'] if soil.get('watered')
                              else SPRITES['tilled_dry'])
                    self.screen.blit(sprite, (px_, py_))
                    if soil.get('crop'):
                        stage = min(soil.get('age', 0), 3)
                        crop_id = soil['crop']
                        if crop_id in SPRITES['crops']:
                            self.screen.blit(SPRITES['crops'][crop_id][stage],
                                             (px_, py_))
                    continue

                # Tall objects → defer (depth-sort dengan sprites)
                if t in TALL_TILES:
                    self.screen.blit(SPRITES['grass'], (px_, py_))
                    sort_y = ty * TILE + TILE
                    if t == H:
                        # Composite house (red roof + beige wall)
                        def draw_h(p=px_, py=py_):
                            s = pygame.Surface((TILE, TILE))
                            s.fill(C.r0)
                            pygame.draw.rect(s, C.r1, (0, 0, TILE, 8))
                            pygame.draw.rect(s, C.b0, (0, 8, TILE, TILE - 8))
                            self.screen.blit(s, (p, py))
                        deferred_tall.append((sort_y, draw_h))
                    elif t == TR:
                        deferred_tall.append((sort_y,
                            lambda p=px_, py=py_: self.screen.blit(SPRITES['tree'], (p, py))))
                    elif t == DT:
                        deferred_tall.append((sort_y,
                            lambda p=px_, py=py_: self.screen.blit(SPRITES['dead_tree'], (p, py))))
                    elif t == FN:
                        deferred_tall.append((sort_y,
                            lambda p=px_, py=py_: self.screen.blit(SPRITES['fence'], (p, py))))
                    elif t == MB:
                        deferred_tall.append((sort_y,
                            lambda p=px_, py=py_: self.screen.blit(SPRITES['mailbox'], (p, py))))
                    elif t == WTF:
                        # Air terjun animasi
                        f = (pygame.time.get_ticks() // 200) % 4
                        deferred_tall.append((sort_y,
                            lambda p=px_, py=py_, f=f: self.screen.blit(
                                ANIMATED['waterfall'][f], (p, py))))
                    continue

                # Animated tiles
                if t == W:
                    f = (pygame.time.get_ticks() // 250) % 4
                    self.screen.blit(ANIMATED['water'][f], (px_, py_))
                elif t == FP:
                    f = (pygame.time.get_ticks() // 200) % 2
                    self.screen.blit(ANIMATED['fireplace'][f], (px_, py_))
                elif t == LN:
                    f = (pygame.time.get_ticks() // 300) % 2
                    self.screen.blit(ANIMATED['lantern'][f], (px_, py_))
                else:
                    name = TILE_NAMES.get(t)
                    if name and name in SPRITES:
                        self.screen.blit(SPRITES[name], (px_, py_))

        # ═══ LAYER 2: PARALLAX CLOUD SHADOW ═══
        if not indoor and 'cloud_shadow' in SPRITES:
            cloud_sprite = SPRITES['cloud_shadow']
            cw, ch = cloud_sprite.get_size()
            t = pygame.time.get_ticks()
            cloud_offset = int((t * 0.025) % (SCREEN_W + cw))
            for ci in range(3):
                cx = (-cw + ci * (SCREEN_W // 2 + cw // 2) + cloud_offset) \
                     % (SCREEN_W + cw) - cw
                cy = 30 + ci * 80
                if 0 < cy < VIEW_H * TILE:
                    self.screen.blit(cloud_sprite, (cx, cy))

        # ═══ LAYER 3: WILD ENTITIES (depth-sort) ═══
        is_night = self.state.is_night()
        sprite_list = []

        for w in self.state.wild_entities:
            if w['scene'] != self.state.scene_name:
                continue
            if w.get('night_only', False) and not is_night:
                continue
            wpx = w['x'] * TILE + cam_px
            wpy = w['y'] * TILE + cam_py
            if -TILE < wpx < SCREEN_W and -TILE < wpy < VIEW_H * TILE:
                kind = w['kind']
                sort_y = w['y'] * TILE + TILE
                if kind in ('mandrake', 'running_mushroom'):
                    def draw_w(wpx=wpx, wpy=wpy, kind=kind):
                        if 'shadow_small' in SPRITES:
                            self.screen.blit(SPRITES['shadow_small'],
                                           (wpx + 6, wpy + TILE - 6))
                        if kind == 'running_mushroom':
                            f = (pygame.time.get_ticks() // 200) % 2
                            self.screen.blit(ANIMATED['running_mushroom'][f], (wpx, wpy))
                        else:
                            self.screen.blit(SPRITES[kind], (wpx, wpy))
                    sprite_list.append((sort_y, draw_w))
                elif kind == 'firefly':
                    sprite_list.append((sort_y,
                        lambda wpx=wpx, wpy=wpy: self.screen.blit(
                            ANIMATED['firefly'][(pygame.time.get_ticks() // 250) % 3],
                            (wpx, wpy))))
                elif kind in SPRITES:
                    sprite_list.append((sort_y,
                        lambda wpx=wpx, wpy=wpy, k=kind: self.screen.blit(
                            SPRITES[k], (wpx, wpy))))

        # ═══ LAYER 4: NPCs (depth-sort) ═══
        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] != self.state.scene_name:
                continue
            if pos['x'] < 0:
                continue
            npx = pos['x'] * TILE + cam_px
            npy = pos['y'] * TILE + cam_py
            npc_data = (HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id)
                        or ANIMAL_NPCS.get(npc_id))
            if not npc_data:
                continue
            npc_type = npc_data.get('type', 'human')

            if npc_type == 'naga':
                draw_x = npx - TILE
                draw_y = npy - TILE
                if -96 < draw_x < SCREEN_W and -64 < draw_y < VIEW_H * TILE:
                    sort_y = pos['y'] * TILE + TILE * 2
                    hearts = self.state.npc_hearts.get(npc_id, 0)
                    def draw_naga(dx_=draw_x, dy_=draw_y, npx_=npx, h=hearts):
                        if 'shadow_large' in SPRITES:
                            self.screen.blit(SPRITES['shadow_large'],
                                           (dx_ + 18, dy_ + 50))
                        if 'npc_naga' in ANIMATED:
                            sprite = ANIMATED['npc_naga']['down'][self.walk_anim_index % 3]
                            self.screen.blit(sprite, (int(dx_), int(dy_)))
                        if h > 0:
                            for i in range(min(h // 2, 5)):
                                pygame.draw.rect(self.screen, C.ui_red,
                                               (npx_ + 2 + i * 5, dy_ - 6, 3, 3))
                    sprite_list.append((sort_y, draw_naga))
                continue

            if -TILE < npx < SCREEN_W and -TILE < npy < VIEW_H * TILE:
                # Mapping NPC ID → sprite key.
                # Manusia: anim_key = npc_<id>; selain itu: npc_<type>
                if npc_type == 'human':
                    anim_key = f'npc_{npc_id}'
                elif npc_type == 'wewe':
                    anim_key = 'npc_wewe'  # wewe_gombel data; key sprite di npc_wewe
                else:
                    anim_key = f'npc_{npc_type}'
                hearts = self.state.npc_hearts.get(npc_id, 0)
                sort_y = pos['y'] * TILE + TILE
                # NPC dianggap bergerak jika jarak ke target > 0.05 tile
                tx = pos.get('target_x', pos['x'])
                ty = pos.get('target_y', pos['y'])
                npc_moving = abs(pos['x'] - tx) > 0.05 or abs(pos['y'] - ty) > 0.05
                npc_facing = pos.get('facing', 'down')
                npc_frame = self.walk_anim_index if npc_moving else 0

                def draw_npc(npx_=npx, npy_=npy, ak=anim_key, h=hearts, t=npc_type,
                             fc=npc_facing, fi=npc_frame):
                    if 'shadow_small' in SPRITES:
                        self.screen.blit(SPRITES['shadow_small'],
                                       (int(npx_) + 6, int(npy_) + TILE - 6))
                    if ak in ANIMATED:
                        # Pilih frame sesuai facing & moving
                        sprite = ANIMATED[ak][fc][fi]
                        # Sprite karakter lebih tinggi dari TILE (1.5×) — geser ke atas
                        sh = sprite.get_height()
                        offset_y = TILE - sh if sh > TILE else 0
                        self.screen.blit(sprite, (int(npx_), int(npy_) + offset_y))
                    if h > 0:
                        for i in range(min(h // 2, 5)):
                            pygame.draw.rect(self.screen, C.ui_red,
                                           (int(npx_) + 2 + i * 5, int(npy_) - 6, 3, 3))
                sprite_list.append((sort_y, draw_npc))

        # ═══ LAYER 5: PLAYER ═══
        ppx = self.state.player_x * TILE + cam_px
        ppy = self.state.player_y * TILE + cam_py
        if self.show_blink:
            frame_idx = 2
        elif self.player_ctrl.is_moving():
            frame_idx = self.walk_anim_index
        else:
            frame_idx = 0
        sort_y_player = self.state.player_y * TILE + TILE

        def draw_player(ppx=ppx, ppy=ppy, fi=frame_idx, fc=self.state.facing):
            if 'shadow_small' in SPRITES:
                self.screen.blit(SPRITES['shadow_small'],
                               (int(ppx) + 6, int(ppy) + TILE - 6))
            if 'player' in ANIMATED:
                sprite = ANIMATED['player'][fc][fi]
                sh = sprite.get_height()
                offset_y = TILE - sh if sh > TILE else 0
                self.screen.blit(sprite, (int(ppx), int(ppy) + offset_y))
        sprite_list.append((sort_y_player, draw_player))

        # Depth-sort & render
        all_to_render = deferred_tall + sprite_list
        all_to_render.sort(key=lambda item: item[0])
        for _, draw_func in all_to_render:
            draw_func()

        # Facing indicator
        fx, fy = self.player_ctrl.get_facing_tile()
        fpx = fx * TILE + cam_px
        fpy = fy * TILE + cam_py
        if 0 <= fpx < SCREEN_W and 0 <= fpy < VIEW_H * TILE:
            pygame.draw.rect(self.screen, C.ui_gold,
                           (fpx + 2, fpy + 2, TILE - 4, TILE - 4), 1)

        # Mouse hover indicator
        if self.mode == 'play':
            mx, my = pygame.mouse.get_pos()
            if my < VIEW_H * TILE:
                hover_tx = int((mx + self.cam_x * TILE) / TILE)
                hover_ty = int((my + self.cam_y * TILE) / TILE)
                hpx = hover_tx * TILE + cam_px
                hpy = hover_ty * TILE + cam_py
                if 0 <= hpx < SCREEN_W and 0 <= hpy < VIEW_H * TILE:
                    pygame.draw.rect(self.screen, (255, 255, 255, 80),
                                   (hpx, hpy, TILE, TILE), 1)

        # Weather: hujan
        if self.state.weather == 'Hujan' and not indoor:
            t = pygame.time.get_ticks()
            for i in range(50):
                rx = (i * 37 + int(t * 0.3)) % SCREEN_W
                ry = (i * 19 + int(t * 0.4)) % (VIEW_H * TILE)
                pygame.draw.line(self.screen, (120, 180, 255),
                               (rx, ry), (rx, ry + 6))

        # Night overlay
        if self.state.is_night() and not indoor:
            darkness = 80 if self.state.get_hour() < 5 or self.state.get_hour() >= 22 else 50
            dark = pygame.Surface((SCREEN_W, VIEW_H * TILE))
            dark.set_alpha(darkness)
            dark.fill((0, 0, 30))
            self.screen.blit(dark, (0, 0))

    def render_hud(self):
        hud_y = VIEW_H * TILE
        # Bar latar
        pygame.draw.rect(self.screen, C.ui_bg,
                         (0, hud_y, SCREEN_W, SCREEN_H - hud_y))
        pygame.draw.line(self.screen, C.ui_border,
                         (0, hud_y), (SCREEN_W, hud_y), 2)

        # Energy
        ex = 16; ey = hud_y + 10
        self.draw_text("⚡", ex, ey, C.ui_gold)
        bar_w = 140; bar_h = 14
        pygame.draw.rect(self.screen, (40, 30, 50),
                         (ex + 28, ey + 4, bar_w, bar_h))
        e_pct = self.state.energy / max(1, self.state.max_energy)
        pygame.draw.rect(self.screen, C.ui_green,
                         (ex + 28, ey + 4, int(bar_w * e_pct), bar_h))
        pygame.draw.rect(self.screen, C.ui_border,
                         (ex + 28, ey + 4, bar_w, bar_h), 1)
        self.draw_text(f"{self.state.energy}/{self.state.max_energy}",
                       ex + 28 + bar_w + 8, ey, C.ui_text)

        # Gold
        self.draw_text(f"💰 {self.state.gold}G", ex, hud_y + 36, C.ui_gold)

        # Tool & seed
        tool = TOOLS[self.state.tool_index]
        self.draw_text(f"🛠 {tool}", 250, hud_y + 10, C.ui_cyan)
        if tool == 'Tanam':
            seed_name = CROPS.get(self.state.seed_key, {}).get('name', '?')
            seed_qty = self.state.inventory.get(self.state.seed_key + '_seed', 0)
            self.draw_text(f"🌱 {seed_name} x{seed_qty}",
                          250, hud_y + 36, C.ui_green)

        # Time & weather & scene
        time_str = self.state.get_time_str()
        szn = self.state.get_season_name()
        self.draw_text(
            f"🕐 {time_str}  🌤 {self.state.weather}  📅 H{self.state.day} {szn}",
            450, hud_y + 10, C.ui_text)
        scene_name = SCENES[self.state.scene_name].display
        self.draw_text(f"📍 {scene_name}", 450, hud_y + 36, C.ui_cyan)

        # Hint controls
        self.draw_text("F1 Bantuan | I Inv | M Peta | E Aksi | SPACE Alat",
                       16, hud_y + 64, (140, 120, 160))

    def draw_text(self, text, x, y, color):
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def render_dialog(self):
        # Box di bawah
        box_h = 120
        box_y = VIEW_H * TILE - box_h - 10
        bx = 16
        bw = SCREEN_W - 32

        pygame.draw.rect(self.screen, (15, 8, 25), (bx, box_y, bw, box_h))
        pygame.draw.rect(self.screen, C.ui_border, (bx, box_y, bw, box_h), 2)

        if self.dialog_speaker:
            sp = self.font.render(self.dialog_speaker, True, C.ui_gold)
            self.screen.blit(sp, (bx + 16, box_y + 8))

        if self.dialog_index < len(self.dialog_lines):
            line = self.dialog_lines[self.dialog_index]
            # Typewriter
            visible = line[:self.typewriter_progress] if self.typewriter_progress > 0 else line
            txt = self.font.render(visible, True, C.ui_text)
            self.screen.blit(txt, (bx + 16, box_y + 36))
            # Hint
            hint = self.font_small.render(
                f"[{self.dialog_index + 1}/{len(self.dialog_lines)}] SPACE/E lanjut",
                True, (140, 120, 160))
            self.screen.blit(hint, (bx + 16, box_y + box_h - 20))

    def render_panel(self):
        # Dim background
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))

        bw, bh = 540, 380
        bx, by = SCREEN_W // 2 - bw // 2, (SCREEN_H - 96) // 2 - bh // 2
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
        s = self.font.render(self.notif_text, True, C.ui_gold)
        sx = SCREEN_W // 2 - s.get_width() // 2
        sy = 16
        # Background
        pygame.draw.rect(self.screen, (30, 20, 50),
                       (sx - 8, sy - 4, s.get_width() + 16, s.get_height() + 8))
        pygame.draw.rect(self.screen, C.ui_border,
                       (sx - 8, sy - 4, s.get_width() + 16, s.get_height() + 8), 1)
        self.screen.blit(s, (sx, sy))

    # ═══════════════════════════════════════════════════
    #  HELPERS — dialog, notif, panel, transition
    # ═══════════════════════════════════════════════════
    def notif(self, text):
        self.notif_text = text
        self.notif_timer = 2500

    def start_dialog(self, lines, speaker, callback=None):
        self.dialog_lines = lines
        self.dialog_index = 0
        self.dialog_speaker = speaker
        self.dialog_callback = callback
        self.typewriter_progress = 0
        self.mode = 'dialog'

    def advance_dialog(self):
        # Skip typewriter
        if self.dialog_index < len(self.dialog_lines):
            current = self.dialog_lines[self.dialog_index]
            if self.typewriter_progress < len(current):
                self.typewriter_progress = len(current)
                return
        self.dialog_index += 1
        self.typewriter_progress = 0
        if self.dialog_index >= len(self.dialog_lines):
            self.mode = 'play'
            cb = self.dialog_callback
            self.dialog_callback = None
            if cb:
                cb()

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
                 or self.state.inventory.get(k + '_seed', 0) > 0]
        if not avail:
            return
        try:
            i = avail.index(self.state.seed_key)
        except ValueError:
            i = 0
        i = (i + d) % len(avail)
        self.state.seed_key = avail[i]
        self.notif(f"Benih: {CROPS[self.state.seed_key]['name']}")

    def transition_to(self, target_scene, tx, ty, facing=None):
        self.mode = 'fade'
        self.fade_dir = 1
        self.fade_alpha = 0
        self.player_ctrl.move_target_x = None
        self.player_ctrl.move_target_y = None

        def do_switch():
            self.state.scene_name = target_scene
            self.state.player_x = float(tx)
            self.state.player_y = float(ty)
            if facing:
                self.state.facing = facing
            # Reset camera ke target
            self.update_camera(99999)
        self.fade_callback = do_switch

    # ═══════════════════════════════════════════════════
    #  SLEEP & DAY ADVANCE
    # ═══════════════════════════════════════════════════
    def confirm_sleep(self):
        self.start_dialog(["Tidur sampai pagi?"], "Tidur", self.sleep_next_day)

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
        self.state.weather = random.choice(
            ['Cerah', 'Cerah', 'Mendung', 'Hujan', 'Berangin'])
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
    #  SHOP / UPGRADE
    # ═══════════════════════════════════════════════════
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
        if st == 0 and s.mail_read:
            s.quest_stage = 1
        elif st == 1 and s.stats['lobak_planted'] >= 3 and s.stats['watered'] >= 3:
            s.quest_stage = 2
        elif st == 2 and s.stats['lobak_harvested'] >= 3:
            s.quest_stage = 3
            s.shop_unlocked = True
            self.notif("🎉 Warung terbuka!")
        elif st == 3 and s.stats['earned'] >= 150:
            s.quest_stage = 4
        elif st == 4 and (s.upgrades['hoe'] or s.upgrades['water']):
            s.quest_stage = 5
        elif st == 5 and s.stats['corn_harvested'] >= 2:
            s.quest_stage = 6
        elif st == 6 and s.stats['gifts'] >= 3:
            s.quest_stage = 7
        elif st == 7 and s.captured_supernatural >= 1:
            s.quest_stage = 8
        elif st == 8 and s.met_jin:
            s.quest_stage = 9
        elif st == 9 and s.day >= DAYS_PER_SEASON * 4:
            s.quest_stage = 10
            self.start_dialog([
                "🌻 SATU TAHUN BERLALU!",
                "Lembah Karsa hidup kembali.",
                "— TAMAT —",
            ], "🌻 Selamat!")

    # ═══════════════════════════════════════════════════
    #  NEW GAME / LOAD
    # ═══════════════════════════════════════════════════
    def start_new_game(self):
        self.state = GameState()
        init_npc_data(self.state)
        spawn_wild_entities(self.state)
        self.mode = 'play'

    def try_load_game(self):
        loaded = GameState.load()
        if loaded:
            self.state = loaded
            init_npc_data(self.state)
            if not self.state.wild_entities:
                spawn_wild_entities(self.state)
            self.mode = 'play'
            self.notif("📂 Game dimuat!")
        else:
            self.notif("Tidak ada save file.")
