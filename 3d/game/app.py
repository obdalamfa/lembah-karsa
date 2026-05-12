import logging
import random
from ursina import Ursina, camera, window, color, Vec3, Vec4, time, Entity, DirectionalLight, AmbientLight, lerp
from ursina.shaders import unlit_shader

# Fix: Override fungsi warna Ursina agar outputnya konsisten Vec4 (0.0 - 1.0).
# Ini mencegah layar & HUD terbakar warna putih karena kelebihan nilai.
color.rgb = lambda r, g, b, a=255: Vec4(r/255.0, g/255.0, b/255.0, a/255.0)
color.rgba = color.rgb

from .state import GameState
from .world import World3D
from .player import Player3D
from .entities import EntitiesManager
from .panels import UIManager
from .config import (SCREEN_W, SCREEN_H, CAM_HEIGHT, CAM_BACK, CAM_LERP,
                     CAM_TARGET_LIFT, INGAME_MINUTES_PER_REAL_SECOND, FORCE_SLEEP_HOUR)

class GameHandler(Entity):
    """Menjembatani event update dan input Ursina ke class Game3D."""
    def __init__(self, game, **kwargs):
        super().__init__(**kwargs)
        self.game = game

    def update(self):
        self.game.update(time.dt)

    def input(self, key):
        self.game.input(key)

class Game3D:
    def __init__(self):
        logging.info("Inisialisasi Game Engine 3D (Ursina)...")
        
        # Inisialisasi Ursina Engine
        self.app = Ursina(size=(SCREEN_W, SCREEN_H), title='Lembah Karsa 3D', borderless=False)
        window.color = color.rgb(30, 20, 40)
        window.fps_counter.enabled = True
        
        # Pencahayaan — arah lebih datar agar detail karakter chibi terlihat
        self.sun = DirectionalLight(shadows=False)
        self.sun.look_at(Vec3(-1, -1.5, -0.8))
        # Ambient hangat: cream kekuningan (Animal Crossing golden hour feel)
        self.ambient = AmbientLight(color=color.rgb(95, 90, 78, 255))

        # Setup Awan (Minecraft-style blocky clouds) melayang di atas peta
        self.clouds = []
        for _ in range(8):
            cloud = Entity(
                model='cube',
                shader=unlit_shader,
                transparent=True,
                scale=(random.uniform(8, 16), 0.5, random.uniform(5, 12)),
                position=(random.uniform(-10, 60), 25, random.uniform(-10, 60))
            )
            self.clouds.append(cloud)

        # Setup Partikel Hujan (Object pool bergaya balok)
        self.rain_drops = []
        for _ in range(150):
            drop = Entity(
                model='cube',
                shader=unlit_shader,
                color=color.rgb(130, 185, 255, 160),
                transparent=True,
                scale=(0.04, 1.2, 0.04),
                position=(random.uniform(-10, 50), random.uniform(2, 18),
                          random.uniform(-10, 50)),
                enabled=False
            )
            self.rain_drops.append(drop)

        # Inisialisasi suara prosedural (pygame.mixer, tidak konflik dengan panda3d audio)
        from .sound import init_sound, build_sounds
        if init_sound():
            build_sounds()

        logging.info("Memuat data Game State...")
        self.state = GameState.load() or GameState()

        logging.info("Membangun sistem UI, Dunia, dan Entitas...")
        self.panels = UIManager(self.state)
        self.world = World3D(self.state)
        self.entities = EntitiesManager(self.state)
        
        # Load map awal
        self.world.load_scene(self.state.scene_name)
        self.entities.load_scene(self.state.scene_name)

        logging.info("Membangun Player...")
        self.player = Player3D(self.state, self.world)

        # Setup Kamera (Isometric fixed-angle)
        camera.orthographic = True
        camera.fov          = 16
        camera.rotation_x   = 29   # arctan(CAM_HEIGHT / sqrt(CAM_BACK²+CAM_BACK²)) ≈ 29°
        camera.rotation_y   = 45
        camera.position     = (self.player.position +
                                Vec3(0, CAM_TARGET_LIFT, 0) +
                                Vec3(-CAM_BACK, CAM_HEIGHT, -CAM_BACK))

        # Inisialisasi lingkungan langsung sesuai waktu awal (bukan fade dari gelap)
        self._init_env()

        # Handler untuk Game Loop
        self.handler = GameHandler(self)

    def update(self, dt):
        s = self.state
        # Update UI HUD
        self.panels.update(s, dt)

        if self.panels.mode == 'hud':
            # ── Maju waktu in-game ──────────────────────────
            s.time_minutes += INGAME_MINUTES_PER_REAL_SECOND * dt
            if s.time_minutes >= 1440:
                s.time_minutes -= 1440
            # Paksa tidur lewat tengah malam
            if s.get_hour() >= FORCE_SLEEP_HOUR:
                self.player._advance_day()
                self.panels.flash_msg("Sudah larut malam — hari baru!", 2.5)

            self.player.tick()
            # Jika HP habis → pingsan, balik ke rumah, mulai hari baru
            if s.hp <= 0:
                s.scene_name = 'house'
                s.player_x, s.player_y = 7.0, 8.0
                self.player._advance_day()
                self.panels.flash_msg("Kamu pingsan! Terbangun di rumah...", 3.5)
            self.entities.update(dt)
            self.world.update(dt)

            # Cek transisi scene (misal keluar pintu / portal)
            current_scene = s.scene_name
            if current_scene != self.world.scene_name or (current_scene == 'dungeon' and getattr(self.world, 'dungeon_level', -1) != s.dungeon_level):
                logging.info(f"Pindah ke scene: {current_scene} (Level Dungeon: {s.dungeon_level})")
                self.world.dungeon_level = s.dungeon_level
                self.world.load_scene(current_scene)
                self.entities.load_scene(current_scene)
                self.player.set_tile_pos(s.player_x, s.player_y)
                self.player._set_initial_rotation()
                self._init_env()  # Snap pencahayaan langsung, tidak lerp dari gelap/putih

            # Kamera mengikuti pemain (smooth lerp) — fokus ke badan, bukan kaki
            look_target = self.player.position + Vec3(0, CAM_TARGET_LIFT, 0)
            target_cam  = look_target + Vec3(-CAM_BACK, CAM_HEIGHT, -CAM_BACK)
            camera.position += (target_cam - camera.position) * CAM_LERP * dt

            # Efek pencahayaan (Siang/Sore/Malam) dan Indoor/Outdoor
            is_indoor = self.world.scene_obj.indoor if self.world.scene_obj else False
            is_raining = (self.state.weather in ('Hujan', 'Badai')) and not is_indoor

            if is_indoor:
                # Indoor: tidak ada matahari, ambient hangat seperti lampu dalam ruangan
                target_sun   = color.rgb(0, 0, 0)
                target_amb   = color.rgb(150, 140, 160, 255)
                target_sky   = color.rgb(10, 5, 15)
                target_cloud = color.rgb(0, 0, 0, 0)
            else:
                hour = (self.state.time_minutes / 60.0) % 24.0
                # Catatan: ambient + sun×dot ≤ 100% agar warna tidak overflow putih
                # ambient max ~70, sun max ~185 (di floor dot≈0.82: 70/255+185/255×0.82 ≈ 87%)
                if 6 <= hour < 17:
                    # Siang: sinar matahari hangat keemasan (Animal Crossing golden feel)
                    target_sun = color.rgb(255, 248, 215) if not is_raining else color.rgb(145, 145, 158)
                    target_amb = color.rgb(95, 90, 78, 255) if not is_raining else color.rgb(62, 62, 72, 255)
                    target_sky = color.rgb(128, 205, 248) if not is_raining else color.rgb(88, 98, 115)
                    target_cloud = color.rgb(248, 248, 255, 175) if not is_raining else color.rgb(145, 148, 162, 215)
                elif 17 <= hour < 19:
                    # Senja: oranye kemerahan lembut
                    target_sun = color.rgb(255, 162, 72) if not is_raining else color.rgb(148, 95, 72)
                    target_amb = color.rgb(88, 55, 45, 255) if not is_raining else color.rgb(55, 38, 35, 255)
                    target_sky = color.rgb(248, 138, 88) if not is_raining else color.rgb(115, 82, 82)
                    target_cloud = color.rgb(255, 195, 148, 145) if not is_raining else color.rgb(135, 108, 102, 195)
                else:
                    # Malam: biru gelap lembut (bukan hitam total)
                    target_sun   = color.rgb(35, 48, 92)
                    target_amb   = color.rgb(28, 28, 52, 255)
                    target_sky   = color.rgb(18, 12, 42)
                    target_cloud = color.rgb(45, 45, 72, 75)
            
            self.sun.color = lerp(self.sun.color, target_sun, dt)
            self.ambient.color = lerp(self.ambient.color, target_amb, dt)
            window.color = lerp(window.color, target_sky, dt)

            # Animasi awan melayang dan transisi warnanya
            for cloud in self.clouds:
                cloud.color = lerp(cloud.color, target_cloud, dt)
                cloud.x += 1.2 * dt
                if cloud.x > 70:
                    cloud.x = -20
                    cloud.z = random.uniform(-10, 60)

            # Animasi Hujan
            for drop in self.rain_drops:
                drop.enabled = is_raining
                if is_raining:
                    drop.y -= 25 * dt
                    if drop.y < -0.5:
                        drop.x = self.player.x + random.uniform(-15, 15)
                        drop.z = self.player.z + random.uniform(-15, 15)
                        drop.y = random.uniform(10, 25)

    def input(self, key):
        # Intercept input saat UI / Dialog aktif
        if self.panels.mode == 'dialog':
            if key in ('space', 'e', 'enter'):
                self.panels.advance_dialog()
            return

        if self.panels.mode == 'panel':
            if key == 'escape':
                self.panels.close_all()
            elif key.isdigit():
                msg = self.panels.panel_action(int(key))
                if msg:
                    self.panels.flash_msg(msg)
            return

        if self.panels.mode == 'hud':
            # Input untuk aksi pemain (gerak/tool/serang/tangkap)
            if self.player.handle_input(key, self.entities, self.panels):
                return

            # Hotkeys menu
            if key == 'i':
                self.panels.open_panel('inventory')
            elif key == 'm':
                self.panels.open_panel('map')
            elif key == 'j':
                self.panels.open_panel('quest')
            elif key == 'h':
                self.panels.open_panel('relations')
            elif key == 'k':
                if self.state.scene_name == 'shop':
                    self.panels.open_panel('shop')
                else:
                    self.panels.flash_msg("Pergi ke Warung Bu Sari!")
            elif key == 'u':
                if self.state.scene_name == 'smith':
                    self.panels.open_panel('crafting')
                else:
                    self.panels.flash_msg("Pergi ke Bengkel Budi!")
            elif key == 'f1':
                self.panels.open_panel('help')
            elif key == 'f5':
                if self.state.save():
                    self.panels.flash_msg("[F5] Game Tersimpan!")
            elif key == 'f9':
                loaded = GameState.load()
                if loaded:
                    self.state = loaded
                    self.world.load_scene(self.state.scene_name)
                    self.entities.load_scene(self.state.scene_name)
                    self.player.state = self.state
                    self.player.set_tile_pos(self.state.player_x, self.state.player_y)
                    self.player._set_initial_rotation()
                    self.panels.flash_msg("[F9] Game Dimuat!")

    # ─── ENVIRONMENT INIT ───────────────────────────────────
    def _init_env(self):
        """Snap pencahayaan langsung sesuai scene & jam — dipanggil saat init dan tiap transisi scene."""
        s        = self.state
        hour     = (s.time_minutes / 60.0) % 24.0
        is_indoor= self.world.scene_obj.indoor if self.world.scene_obj else False

        if is_indoor:
            sun_col   = color.rgb(0, 0, 0)
            amb_col   = color.rgb(150, 140, 160, 255)
            sky_col   = color.rgb(10, 5, 15)
            cloud_col = color.rgb(0, 0, 0, 0)
        elif 6 <= hour < 17:
            sun_col   = color.rgb(255, 248, 215)
            amb_col   = color.rgb(95, 90, 78, 255)
            sky_col   = color.rgb(128, 205, 248)
            cloud_col = color.rgb(248, 248, 255, 175)
        elif 17 <= hour < 19:
            sun_col   = color.rgb(255, 162, 72)
            amb_col   = color.rgb(88, 55, 45, 255)
            sky_col   = color.rgb(248, 138, 88)
            cloud_col = color.rgb(255, 195, 148, 145)
        else:
            sun_col   = color.rgb(35, 48, 92)
            amb_col   = color.rgb(28, 28, 52, 255)
            sky_col   = color.rgb(18, 12, 42)
            cloud_col = color.rgb(45, 45, 72, 75)

        self.sun.color     = sun_col
        self.ambient.color = amb_col
        window.color       = sky_col
        for cloud in self.clouds:
            cloud.color = cloud_col

    def run(self):
        logging.info("Memulai Game Loop utama...")
        self.app.run()

def run():
    game = Game3D()
    game.run()