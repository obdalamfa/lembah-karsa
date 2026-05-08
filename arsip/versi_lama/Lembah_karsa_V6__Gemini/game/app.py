"""
app.py — Game class utama tersinkronisasi.
"""
import pygame
import math
from .config import (
    C, TILE, VIEW_W, VIEW_H, SCREEN_W, SCREEN_H, FPS,
    INGAME_MINUTES_PER_REAL_SECOND, ANIMATION_FPS, DAYS_PER_SEASON,
    TILE_NAMES, TOOLS, G, D, P, W, FL, STR, BD
)
from .state import GameState
from .data import CROPS, HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS
from .scenes import SCENES
from .sprites import init_sprites, SPRITES, ANIMATED
from .entities import (spawn_wild_entities, update_wild_entities,
                       update_all_npc_positions, init_npc_data, update_dynamic_ai)
from .player import PlayerController
from . import panels

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("🌱 Lembah Karsa — RPG")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 16, bold=True)
        self.font_big = pygame.font.SysFont("Arial", 22, bold=True)
        
        init_sprites()
        self.state = GameState.load() or GameState()
        self.player_ctrl = PlayerController(self)
        init_npc_data(self.state)
        spawn_wild_entities(self.state)

        self.running = True
        self.mode = 'play'
        self.panel = None
        self.panel_select = 0
        
        self.cam_x, self.cam_y = 0.0, 0.0
        self.notif_text, self.notif_timer = "", 0
        self.dialog_lines, self.dialog_index = [], 0
        self.dialog_name, self.dialog_callback = "", None
        
        self.anim_timer, self.walk_anim_index = 0, 0
        self.wild_timer, self.npc_pos_timer = 0, 0
        self.trans_alpha, self.trans_target = 0, None

    def notif(self, text):
        self.notif_text = text
        self.notif_timer = 180

    def start_dialog(self, lines, name, callback=None):
        self.dialog_lines = lines
        self.dialog_index = 0
        self.dialog_name = name
        self.dialog_callback = callback
        self.mode = 'dialog'

    def transition_to(self, scene_name, tx, ty, facing='down'):
        self.trans_target = (scene_name, tx, ty, facing)
        self.mode = 'transition'
        self.trans_alpha = 0

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
                
            if event.type == pygame.KEYDOWN:
                if self.mode == 'play':
                    if event.key == pygame.K_i: self.open_panel('inventory')
                    elif event.key == pygame.K_m: self.open_panel('map')
                    elif event.key == pygame.K_j: self.open_panel('quest')
                    elif event.key == pygame.K_h: self.open_panel('relations')
                    elif event.key == pygame.K_SPACE: self.player_ctrl.use_tool()
                    elif event.key == pygame.K_e: self.player_ctrl.interact()
                    elif event.key == pygame.K_f: self.player_ctrl.try_capture_supernatural()
                    elif event.key == pygame.K_g: self.player_ctrl.show_npc_schedule()
                    elif event.key == pygame.K_t: 
                        if SCENES[self.state.scene_name].tiles[int(self.state.player_y)][int(self.state.player_x)] == BD:
                            self.confirm_sleep()
                    elif pygame.K_1 <= event.key <= pygame.K_6:
                        self.state.tool_index = event.key - pygame.K_1
                    elif event.key == pygame.K_q: self.cycle_seed(-1)
                    elif event.key == pygame.K_r: self.cycle_seed(1)
                    elif event.key == pygame.K_F5:
                        if self.state.save(): self.notif("Game Disimpan!")
                    elif event.key == pygame.K_F9:
                        loaded = GameState.load()
                        if loaded: self.state = loaded; self.notif("Game Dimuat!")

                elif self.mode == 'dialog':
                    if event.key in [pygame.K_SPACE, pygame.K_e, pygame.K_RETURN]:
                        self.dialog_index += 1
                        if self.dialog_index >= len(self.dialog_lines):
                            self.mode = 'play'
                            if self.dialog_callback: self.dialog_callback()
                            
                elif self.mode == 'panel':
                    if event.key == pygame.K_ESCAPE: self.mode = 'play'
                    elif event.key in [pygame.K_UP, pygame.K_w]: self.panel_select -= 1
                    elif event.key in [pygame.K_DOWN, pygame.K_s]: self.panel_select += 1
                    elif event.key in [pygame.K_SPACE, pygame.K_e, pygame.K_RETURN]:
                        pass # Panel logic

    def update(self, dt):
        if self.mode == 'play':
            self.state.time_minutes += (dt / 1000.0) * INGAME_MINUTES_PER_REAL_SECOND
            if self.state.time_minutes >= 1440: self.sleep_next_day()
            
            # 1. Update Player (Menyelesaikan Crash WASD)
            self.player_ctrl.update(dt)

            # 2. Camera Smooth Follow
            target_cam_x = self.state.player_x - VIEW_W / 2
            target_cam_y = self.state.player_y - VIEW_H / 2
            self.cam_x += (target_cam_x - self.cam_x) * 0.1
            self.cam_y += (target_cam_y - self.cam_y) * 0.1
            
            # 3. AI Update
            self.wild_timer += dt
            if self.wild_timer > 800:
                self.wild_timer = 0
                update_wild_entities(self.state, dt)
            
            update_dynamic_ai(self.state, dt)

            self.npc_pos_timer += dt
            if self.npc_pos_timer > 5000:
                self.npc_pos_timer = 0
                update_all_npc_positions(self.state)

        # Animasi Walk
        self.anim_timer += dt
        if self.anim_timer > (1000 // ANIMATION_FPS):
            self.anim_timer = 0
            self.walk_anim_index = (self.walk_anim_index + 1) % 3

        if self.mode == 'transition':
            self.trans_alpha += 10
            if self.trans_alpha >= 255:
                s, x, y, f = self.trans_target
                self.state.scene_name = s
                self.state.player_x, self.state.player_y = float(x), float(y)
                self.state.facing = f
                self.trans_alpha = 255
                self.mode = 'play'

    def render(self):
        self.render_world()
        self.render_hud()
        if self.notif_timer > 0:
            self.notif_timer -= 1
            self.draw_text(self.notif_text, SCREEN_W//2 - 50, 50, C.ui_gold)
        if self.mode == 'dialog': self.render_dialog()
        if self.mode == 'panel': self.render_panel()
        if self.mode == 'transition':
            s = pygame.Surface((SCREEN_W, SCREEN_H))
            s.set_alpha(self.trans_alpha)
            s.fill((0, 0, 0))
            self.screen.blit(s, (0, 0))
        pygame.display.flip()

    def render_world(self):
        scene = SCENES[self.state.scene_name]
        indoor = scene.indoor
        bg = (40, 25, 15) if indoor else (60, 100, 140) if self.state.is_night() else (135, 180, 200)
        self.screen.fill(bg)

        cam_px = -int(self.cam_x * TILE)
        cam_py = -int(self.cam_y * TILE)

        start_tx = max(0, int(self.cam_x))
        end_tx = min(scene.w, int(self.cam_x) + VIEW_W + 2)
        start_ty = max(0, int(self.cam_y))
        end_ty = min(scene.h, int(self.cam_y) + VIEW_H + 2)

        renderables = []

        for ty in range(start_ty, end_ty):
            for tx in range(start_tx, end_tx):
                t = scene.tiles[ty][tx]
                px_, py_ = tx * TILE + cam_px, ty * TILE + cam_py
                
                key = f"{tx},{ty},{self.state.scene_name}"
                soil = self.state.soil.get(key)
                if soil and soil.get('tilled'):
                    sprite = SPRITES['tilled_wet'] if soil.get('watered') else SPRITES['tilled_dry']
                    self.screen.blit(sprite, (px_, py_))
                    continue

                if t in [G, D, P, W, FL, STR]:
                    if t == W:
                        f = (pygame.time.get_ticks() // 250) % 4
                        self.screen.blit(ANIMATED['water'][f], (px_, py_))
                    else:
                        name = TILE_NAMES.get(t)
                        if name and name in SPRITES: self.screen.blit(SPRITES[name], (px_, py_))
                else:
                    name = TILE_NAMES.get(t)
                    if name and name in SPRITES:
                        renderables.append((py_ + TILE, px_, py_, SPRITES[name]))

        for w in self.state.wild_entities:
            if w['scene'] == self.state.scene_name:
                px_, py_ = w['x'] * TILE + cam_px, w['y'] * TILE + cam_py
                renderables.append((py_ + TILE, px_, py_, SPRITES.get(w['kind'])))

        for npc_id, pos in self.state.npc_positions.items():
            if pos['scene'] == self.state.scene_name and pos['x'] >= 0:
                px_, py_ = pos['x'] * TILE + cam_px, pos['y'] * TILE + cam_py
                npc_data = HUMAN_NPCS.get(npc_id) or SUPERNATURAL_NPCS.get(npc_id) or ANIMAL_NPCS.get(npc_id)
                anim_key = f'npc_{npc_id}' if npc_data.get('type') == 'human' else f"npc_{npc_data['type']}"
                if anim_key in ANIMATED:
                    sprite = ANIMATED[anim_key]['down'][0]
                    renderables.append((py_ + TILE - 1, px_, py_, SPRITES['shadow']))
                    renderables.append((py_ + TILE, px_, py_, sprite))

        ppx, ppy = self.state.player_x * TILE + cam_px, self.state.player_y * TILE + cam_py
        sprite = ANIMATED['player'][self.state.facing][self.walk_anim_index if self.player_ctrl.is_moving() else 0]
        renderables.append((ppy + TILE - 1, ppx, ppy, SPRITES['shadow']))
        renderables.append((ppy + TILE, ppx, ppy, sprite))

        renderables.sort(key=lambda item: item[0])
        for _, rx, ry, rsprite in renderables:
            if rsprite: self.screen.blit(rsprite, (int(rx), int(ry)))

        if not indoor and self.state.weather in ['Cerah', 'Berangin'] and 'cloud' in SPRITES:
            cloud_off = (pygame.time.get_ticks() * 0.02) % (SCREEN_W + 300)
            self.screen.blit(SPRITES['cloud'], (cloud_off - 300, 100)) 

    def render_hud(self):
        hud_y = SCREEN_H - 96
        pygame.draw.rect(self.screen, C.ui_bg, (0, hud_y, SCREEN_W, 96))
        pygame.draw.line(self.screen, C.ui_border, (0, hud_y), (SCREEN_W, hud_y), 2)
        
        e_color = C.ui_green if self.state.energy > 30 else C.ui_red
        self.draw_text(f"⚡ Energi: {self.state.energy}/{self.state.max_energy}", 20, hud_y + 15, e_color)
        self.draw_text(f"💰 Gold: {self.state.gold}G", 20, hud_y + 45, C.ui_gold)
        
        self.draw_text(f"📅 Thn {self.state.year}, {self.state.get_season_name()}", SCREEN_W - 200, hud_y + 15)
        self.draw_text(f"⏰ {self.state.get_time_str()} ({self.state.weather})", SCREEN_W - 200, hud_y + 45)

        tool = TOOLS[self.state.tool_index]
        self.draw_text(f"🛠 Alat: {tool}", 250, hud_y + 15, C.ui_cyan)
        if tool == 'Tanam':
            seed = CROPS[self.state.seed_key]['name']
            qty = self.state.inventory.get(self.state.seed_key + '_seed', 0)
            self.draw_text(f"🌱 Benih: {seed} ({qty})", 250, hud_y + 45)

    def draw_text(self, text, x, y, color=C.ui_text):
        surf = self.font.render(text, True, color)
        self.screen.blit(surf, (x, y))

    def render_dialog(self):
        box_h = 120
        box_y = SCREEN_H - 96 - box_h - 10
        pygame.draw.rect(self.screen, (10, 5, 20), (20, box_y, SCREEN_W - 40, box_h))
        pygame.draw.rect(self.screen, C.ui_border, (20, box_y, SCREEN_W - 40, box_h), 2)
        
        name_surf = self.font_big.render(self.dialog_name, True, C.ui_gold)
        self.screen.blit(name_surf, (40, box_y + 10))
        
        line = self.dialog_lines[self.dialog_index]
        text_surf = self.font.render(line, True, C.ui_text)
        self.screen.blit(text_surf, (40, box_y + 50))
        self.draw_text("[Spasi/E] Lanjut...", SCREEN_W - 150, box_y + 90, (100, 100, 100))

    def open_panel(self, p):
        self.panel = p
        self.panel_select = 0
        self.mode = 'panel'

    def sleep_next_day(self):
        self.state.day += 1
        self.state.time_minutes = 360.0 
        self.state.energy = self.state.max_energy
        self.notif(f"Hari {self.state.day} Dimulai!")
        self.state.save()

    def cycle_seed(self, step):
        seeds = list(CROPS.keys())
        idx = seeds.index(self.state.seed_key)
        self.state.seed_key = seeds[(idx + step) % len(seeds)]

    def confirm_sleep(self):
        self.start_dialog(["Apakah kamu ingin tidur?"], "Tidur", self.sleep_next_day)

    def render_panel(self):
        dim = pygame.Surface((SCREEN_W, SCREEN_H))
        dim.set_alpha(180)
        dim.fill((0, 0, 0))
        self.screen.blit(dim, (0, 0))
        
        bw, bh = 500, 380
        bx, by = SCREEN_W//2 - bw//2, (SCREEN_H - 96)//2 - bh//2
        pygame.draw.rect(self.screen, (15, 8, 30), (bx, by, bw, bh))
        pygame.draw.rect(self.screen, C.ui_border, (bx, by, bw, bh), 3)

        if self.panel == 'inventory': panels.render_panel_inventory(self, bx, by, bw, bh)
        elif self.panel == 'map': panels.render_panel_map(self, bx, by, bw, bh)
        elif self.panel == 'quest': panels.render_panel_quest(self, bx, by, bw, bh)
        elif self.panel == 'relations': panels.render_panel_relations(self, bx, by, bw, bh)
