"""
app.py — Main Ursina Application untuk Lembah Karsa 3D.

Arsitektur:
  LKApp(Entity) → update() + input() dipanggil Ursina setiap frame.
  World3D   → render tile 3D
  Player3D  → controller player
  EntitiesManager → NPC, mob, wild
  UIManager → HUD, dialog, panel

Kamera:
  RF4-style fixed isometric:
    - Posisi: player + (0, CAM_HEIGHT, -CAM_BACK)
    - Look-at: player + (0, 0, CAM_TARGET_LIFT)
    - Smooth lerp via CAM_LERP
"""
import math
import random

from ursina import (Ursina, Entity, Vec3, color, camera, window,
                    AmbientLight, DirectionalLight, time, held_keys)
from ursina.shaders import unlit_shader

from .config import (TILE_SIZE, GROUND_H,
                     CAM_HEIGHT, CAM_BACK, CAM_TARGET_LIFT, CAM_LERP,
                     INGAME_MINUTES_PER_REAL_SECOND, FORCE_SLEEP_HOUR,
                     INVULN_AFTER_HIT_MS, DAYS_PER_SEASON,
                     STAIRS_DOWN, STAIRS_UP)
from .state    import GameState
from .scenes   import SCENES
from .world    import World3D
from .player   import Player3D
from .entities import EntitiesManager
from .panels   import UIManager

TS = TILE_SIZE


class LKApp(Entity):
    """Controller utama game — semua sistem dipasang di sini."""

    def __init__(self):
        super().__init__()

        # ─── STATE ───────────────────────────────────────
        self.state = GameState.load() or GameState()
        s = self.state

        # ─── LIGHTING ────────────────────────────────────
        self._setup_lighting(s.scene_name)

        # ─── SYSTEMS ─────────────────────────────────────
        self.world   = World3D(s)
        self.world.load_scene(s.scene_name)

        self.player  = Player3D(s, self.world)
        self.player.set_tile_pos(s.player_x, s.player_y)

        self.ents    = EntitiesManager(s)
        self.ents.load_scene(s.scene_name)

        self.ui      = UIManager(s)

        # ─── CAMERA ──────────────────────────────────────
        camera.orthographic = False
        camera.fov          = 60
        # Posisi awal kamera
        px = s.player_x * TS;  pz = s.player_y * TS
        camera.position = Vec3(px, CAM_HEIGHT, pz - CAM_BACK)
        camera.look_at(Vec3(px, 0, pz + CAM_TARGET_LIFT))

        # ─── INTERNAL TIMERS ─────────────────────────────
        self._ent_t    = 0.0   # timer untuk update entitas
        self._sched_t  = 0.0   # timer NPC schedule

        print("[LK3D] Game dimulai. Gunakan F1 untuk bantuan kontrol.")

    # ─── URSINA: UPDATE ──────────────────────────────────
    def update(self):
        dt = time.dt
        s  = self.state
        ui = self.ui

        # ── Waktu in-game ─────────────────────────────
        if ui.mode == 'hud':
            s.time_minutes += INGAME_MINUTES_PER_REAL_SECOND * dt
            if s.time_minutes >= 1440:
                s.time_minutes -= 1440
                self._midnight()

        # ── World ─────────────────────────────────────
        self.world.update(dt)

        # ── Entities ──────────────────────────────────
        self._ent_t += dt
        if self._ent_t >= 0.05:
            self.ents.update(self._ent_t)
            self._ent_t = 0

        # ── Player (hanya saat 'hud') ──────────────────
        if ui.mode == 'hud':
            self.player.tick()
            self._check_portals()
            self._check_mob_hit()

        # ── UI ────────────────────────────────────────
        ui.update(s, dt)

        # ── Langit dinamis (siang/malam/cuaca) ────────
        self._update_sky()

        # ── Kamera smooth follow ───────────────────────
        self._update_camera(dt)

    # ─── URSINA: INPUT ───────────────────────────────────
    def input(self, key):
        ui = self.ui
        s  = self.state

        # ── Global hotkeys ────────────────────────────
        if key == 'f5':
            if s.save():
                ui.flash_msg("Game tersimpan! (F5)", 1.5)
            return
        if key == 'f9':
            loaded = GameState.load()
            if loaded:
                self.state = loaded
                self._reload_all()
                ui.flash_msg("Game dimuat! (F9)", 1.5)
            return
        if key == 'f1':
            ui.flash_msg(
                "WASD:Gerak  SHIFT:Lari  SPACE:Alat\n"
                "E:Bicara  G:Hadiah  Z:Serang  F:Tangkap  T:Tidur\n"
                "1-8:Alat  Q/R:Benih  I/J/M/H:Panel\n"
                "K:Toko (shop scene)  U:Bengkel (smith)", 5.0)
            return

        # ── Dialog mode ───────────────────────────────
        if ui.mode == 'dialog':
            if key in ('e', 'space', 'enter'):
                done = ui.advance_dialog()
                if done:
                    ui.mode = 'hud'
            elif key == 'escape':
                ui._end_dialog()
                ui.mode = 'hud'
            return

        # ── Panel mode ────────────────────────────────
        if ui.mode == 'panel':
            if key == 'escape':
                ui.close_all()
                return
            # Angka 1-9 untuk shop/crafting
            if key in '123456789':
                msg = ui.panel_action(int(key))
                if msg:
                    ui.flash_msg(msg, 1.4)
            return

        # ── Play mode ─────────────────────────────────
        if key == 'escape':
            return

        # Tool selection 1-8
        if key in '12345678':
            s.tool_index = int(key) - 1
            return

        # Shop (K) — hanya di scene 'shop' atau 'town'
        if key == 'k':
            if s.scene_name in ('shop', 'town'):
                ui.open_panel('shop')
            else:
                ui.flash_msg("Toko hanya bisa diakses di Warung Bu Sari.", 1.5)
            return

        # Crafting (U) — hanya di scene 'smith'
        if key == 'u':
            if s.scene_name == 'smith':
                ui.open_panel('crafting')
            else:
                ui.flash_msg("Crafting hanya di Bengkel Pak Budi.", 1.5)
            return

        # Gift (G) — beri hadiah ke NPC terdekat
        if key == 'g':
            self.player.give_gift(self.ents, ui)
            return

        # Panel toggles
        panel_keys = {'i': 'inventory', 'j': 'quest', 'm': 'map', 'h': 'relations'}
        if key in panel_keys:
            ui.open_panel(panel_keys[key])
            return

        # Player action keys
        self.player.handle_input(key, self.ents, ui)

    # ─── CAMERA ──────────────────────────────────────────
    def _update_camera(self, dt: float):
        px = self.player.x
        pz = self.player.z
        target = Vec3(px, CAM_HEIGHT, pz - CAM_BACK)
        look_pt= Vec3(px, 0, pz + CAM_TARGET_LIFT)

        # Smooth lerp
        lerp_f = min(1.0, CAM_LERP * dt)
        camera.position = Vec3(
            camera.x + (target.x - camera.x) * lerp_f,
            camera.y + (target.y - camera.y) * lerp_f,
            camera.z + (target.z - camera.z) * lerp_f,
        )
        camera.look_at(look_pt)

    # ─── PORTALS ─────────────────────────────────────────
    def _check_portals(self):
        s  = self.state
        sc = SCENES.get(s.scene_name)
        if not sc: return
        px, py = self.player.get_tile_pos()
        for portal in sc.portals:
            ptx, pty, dest, dx, dy = portal
            if px == ptx and py == pty:
                self._transition_to(dest, dx, dy)
                return

    def _transition_to(self, dest: str, dx: float, dy: float):
        s = self.state

        # Naik/turun dungeon via stairs
        tile = self.world.get_tile(*self.player.get_tile_pos())
        if tile == STAIRS_DOWN and dest == 'dungeon':
            s.dungeon_level = max(1, s.dungeon_level + 1)
            self._enter_dungeon()
            return
        elif tile == STAIRS_UP and s.scene_name == 'dungeon':
            if s.dungeon_level <= 1:
                dest = 'naga_cave';  dx = 7;  dy = 9
                s.dungeon_level = 0
            else:
                s.dungeon_level -= 1
                self._enter_dungeon()
                return

        s.scene_name = dest
        s.player_x   = float(dx)
        s.player_y   = float(dy)

        self.world.load_scene(dest)
        self.ents.load_scene(dest)
        self.player.set_tile_pos(dx, dy)
        self._setup_lighting(dest)

    def _enter_dungeon(self):
        s = self.state
        from .dungeon import generate_dungeon_level
        import random
        seed = random.randint(0, 999999)
        grid, spx, spy, mobs = generate_dungeon_level(s.dungeon_level, seed)

        # Update dungeon scene
        SCENES['dungeon'].tiles = grid
        SCENES['dungeon'].w     = len(grid[0])
        SCENES['dungeon'].h     = len(grid)
        s.dungeon_tiles = grid
        s.dungeon_seed  = seed
        s.mobs          = mobs
        s.scene_name    = 'dungeon'
        s.player_x      = float(spx)
        s.player_y      = float(spy)
        s.stats['deepest_level'] = max(s.stats.get('deepest_level', 0), s.dungeon_level)

        self.world.load_scene('dungeon')
        self.ents.load_scene('dungeon')
        self.ents.spawn_mobs(mobs)
        self.player.set_tile_pos(spx, spy)
        self._setup_lighting('dungeon')
        self.ui.flash_msg(f"Masuk Gua Level {s.dungeon_level}!", 1.5)

    # ─── MOB HIT CHECK ───────────────────────────────────
    def _check_mob_hit(self):
        s = self.state
        if s.scene_name != 'dungeon': return
        if s.invuln_timer_ms > 0:
            s.invuln_timer_ms = max(0, s.invuln_timer_ms - time.dt * 1000)
            return

        px, py = self.player.get_float_tile()
        for mob in s.mobs:
            dist = math.sqrt((mob['x']-px)**2 + (mob['y']-py)**2)
            atk  = 1.5 if mob.get('is_boss') else 1.0
            if dist <= atk and mob.get('attack_cooldown_ms', 0) <= 0:
                s.hp = max(0, s.hp - mob['damage'])
                s.invuln_timer_ms = INVULN_AFTER_HIT_MS
                self.player._invuln = INVULN_AFTER_HIT_MS
                mob['attack_cooldown_ms'] = 1000
                if s.hp <= 0:
                    self._player_ko()
                break

    def _player_ko(self):
        s = self.state
        s.hp     = s.max_hp // 2
        s.energy = max(0, s.energy - 30)
        s.mobs.clear()
        s.dungeon_level = 0
        self._transition_to('house', 7, 9)
        self.ui.flash_msg("Kamu pingsan! Kembali ke rumah...", 3.0)

    # ─── MIDNIGHT ────────────────────────────────────────
    def _midnight(self):
        s = self.state
        if s.get_hour() >= FORCE_SLEEP_HOUR:
            s.day           += 1
            s.day_in_season += 1
            s.time_minutes   = 360.0
            s.energy         = s.max_energy
            s.hp             = s.max_hp
            for soil in s.soil.values():
                if soil.get('watered') and soil.get('crop'):
                    soil['age'] = soil.get('age', 0) + 1
                    soil['watered'] = False
            if s.day_in_season > DAYS_PER_SEASON:
                s.day_in_season = 1
                s.season_index  = (s.season_index + 1) % 4
            from .entities import respawn_wild_at_morning
            respawn_wild_at_morning(s)
            s.weather = random.choice(self._WEATHER_POOL.get(s.get_season(), ['Cerah']))

    # ─── LIGHTING ────────────────────────────────────────
    _DARK_SCENES   = frozenset(('dungeon', 'naga_cave'))
    _INDOOR_SCENES = frozenset(('house', 'shop', 'clinic', 'studio', 'smith', 'greenhouse'))
    _WEATHER_POOL  = {
        'Semi':   ['Cerah', 'Cerah', 'Mendung', 'Hujan'],
        'Panas':  ['Cerah', 'Cerah', 'Cerah', 'Mendung'],
        'Gugur':  ['Cerah', 'Mendung', 'Mendung', 'Hujan'],
        'Dingin': ['Cerah', 'Mendung', 'Hujan', 'Hujan'],
    }

    def _setup_lighting(self, scene_name: str):
        if scene_name in self._DARK_SCENES:
            camera.background = color.rgb(10, 6, 16)
        elif scene_name in self._INDOOR_SCENES:
            camera.background = color.rgb(90, 82, 70)
        else:
            self._update_sky()

    def _update_sky(self):
        s = self.state
        if s.scene_name in self._DARK_SCENES or s.scene_name in self._INDOOR_SCENES:
            return
        hour = s.get_hour()
        if hour < 5 or hour >= 20:
            r, g, b = 8, 12, 40
        elif hour < 6:
            r, g, b = 80, 40, 90
        elif hour < 7:
            r, g, b = 255, 130, 60
        elif hour < 18:
            r, g, b = 120, 180, 245
        elif hour < 19:
            r, g, b = 220, 110, 50
        else:
            r, g, b = 90, 45, 70
        if s.weather == 'Hujan':
            r = int(r * 0.55); g = int(g * 0.58); b = int(b * 0.72)
        elif s.weather == 'Mendung':
            r = int(r * 0.75); g = int(g * 0.78); b = int(b * 0.85)
        camera.background = color.rgb(r, g, b)

    # ─── RELOAD ──────────────────────────────────────────
    def _reload_all(self):
        s = self.state
        self.world.load_scene(s.scene_name)
        self.ents.load_scene(s.scene_name)
        self.player.set_tile_pos(s.player_x, s.player_y)
        self._setup_lighting(s.scene_name)


# ─── ENTRY POINT ─────────────────────────────────────────
def run():
    app = Ursina(
        title     = 'Lembah Karsa 3D',
        borderless= False,
        fullscreen= False,
        development_mode=False,
        vsync     = True,
    )

    window.size             = (1280, 720)
    window.fps_counter.enabled = True
    window.exit_button.visible = False

    # Unlit shader: warna entity tampil langsung tanpa perhitungan lighting.
    # Wajib diset sebelum LKApp() agar semua entity mewarisinya.
    Entity.default_shader = unlit_shader

    camera.background = color.rgb(120, 180, 245)

    game = LKApp()

    print("=" * 50)
    print(" LEMBAH KARSA 3D — Farming RPG Nusantara")
    print(" Framework: Ursina Engine (Panda3D)")
    print(" Terinspirasi: Rune Factory 4")
    print("=" * 50)
    print(" Kontrol:")
    print("   WASD / Arrow  = Bergerak")
    print("   SHIFT         = Lari")
    print("   SPACE         = Pakai alat")
    print("   E             = Bicara / Interaksi")
    print("   Z             = Serang (butuh pedang)")
    print("   F             = Tangkap makhluk")
    print("   T             = Tidur (di rumah)")
    print("   G             = Beri hadiah ke NPC terdekat")
    print("   1-8           = Pilih alat")
    print("   Q / R         = Ganti benih")
    print("   I / J / M / H = Inventori / Quest / Peta / Hubungan")
    print("   K             = Toko Bu Sari (di scene shop)")
    print("   U             = Bengkel Pak Budi (di scene smith)")
    print("   F5 / F9       = Simpan / Muat")
    print("   F1            = Bantuan kontrol")
    print("=" * 50)

    app.run()
