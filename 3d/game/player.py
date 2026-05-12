"""
player.py — 3D Player controller untuk Ursina Engine.

Model: humanoid blocky (Rune Factory style):
  Badan, kepala, topi, lengan kiri/kanan, kaki kiri/kanan.
  Semua bagian adalah Entity child dari root Player3D.

Movement: WASD/Arrow di bidang XZ. Kamera tetap.
Tool system: SPACE untuk alat aktif di tile depan player.
Combat: Z untuk serang, radius PLAYER_ATTACK_RANGE world-units.
"""
import math
from pathlib import Path
from PIL import Image
from ursina import Entity, Vec3, color, held_keys, time, invoke, destroy, lerp, Texture

from .config import (TILE_SIZE, GROUND_H, PLAYER_SPEED, PLAYER_RUN_MULTIPLIER,
                     PLAYER_ATTACK_RANGE, PLAYER_ATTACK_COOLDOWN_MS, TOOL_DAMAGE,
                     SPRINT_ENERGY_DRAIN,
                     INVULN_AFTER_HIT_MS, WALKABLE, TILLABLE, MINEABLE, TOOLS,
                     G, D, P, W, FL, DR, GT, CV_F, STR_T, DCK, LLY, MINED,
                     STAIRS_DOWN, STAIRS_UP, ORE_TBG, ORE_BSI, ORE_EMS,
                     ORE_KRS, ORE_MTH, CV_W, CRYS)
from .data import CROPS, SWORD_RECIPES, QUEST_STAGES
from .sound import play as sound_play, get_step_sound
from .config import TILE_NAMES

TS = TILE_SIZE

# Offset tubuh — proporsi chibi (kepala besar, badan kompak, Animal Crossing style)
BODY_Y  = GROUND_H + 0.68
HEAD_Y  = GROUND_H + 1.62
HAT_Y   = GROUND_H + 2.08
ARM_Y   = GROUND_H + 0.68
LEG_Y   = GROUND_H + 0.22

SKIN_COLOR   = color.rgb(255, 225, 180)   # kulit hangat cerah
BODY_COLOR   = color.rgb(120, 200, 100)   # baju hijau pastel
PANTS_COLOR  = color.rgb(88, 128, 195)    # celana biru lembut
HAT_COLOR    = color.rgb(215, 170, 100)   # topi coklat hangat
SHOE_COLOR   = color.rgb(88, 65, 45)      # sepatu coklat gelap

_ASSET_DIR = Path(__file__).resolve().parent.parent / 'assets'
_TEX_CACHE: dict = {}

def _tex(name: str):
    if not name:
        return None
    if name in _TEX_CACHE:
        return _TEX_CACHE[name]
    p = _ASSET_DIR / f'{name}.png'
    if p.exists():
        try:
            img = Image.open(p)
            t = Texture(img)
            t.filtering = False  # Bikin pixel-art tajam & warnanya keluar
            _TEX_CACHE[name] = t
            return t
        except Exception:
            pass
    return None

def _part(model, pos, scale, tex_name, tint=color.white, parent=None):
    t = _tex(tex_name)
    kw = dict(model=model, position=pos, scale=scale)
    if t:
        kw['texture'] = t
        kw['color']   = tint
    else:
        kw['color'] = tint
    if parent:
        kw['parent'] = parent
    return Entity(**kw)


class Player3D(Entity):
    """Player sebagai Ursina Entity. Root di y=0, semua bagian sebagai child."""

    def __init__(self, state, world):
        super().__init__()
        self.state = state
        self.world = world

        self.speed             = PLAYER_SPEED
        self.facing            = state.facing
        self._attack_cd        = 0.0    # ms
        self._invuln           = 0.0    # ms
        self._anim_t           = 0.0
        self._attack_anim      = 0.0
        self._anim_mode        = 'swing' # swing|down|water|bend
        self.target_rotation_y = 0.0

        self._build_model()
        self.set_tile_pos(state.player_x, state.player_y)
        self._set_initial_rotation()

    def _set_initial_rotation(self):
        rot_map = {'up': 45, 'down': -135, 'left': -45, 'right': 135}
        self.rotation_y = rot_map.get(self.state.facing, -135)
        self.target_rotation_y = self.rotation_y

    # ─── MODEL BUILDING ──────────────────────────────────
    def _build_model(self):
        p = self
        # Chibi: kepala besar (0.82) relatif ke badan (0.65) → rasio >1 seperti Animal Crossing
        self.head   = _part('cube', Vec3(0, HEAD_Y, 0),           (0.82, 0.80, 0.82), 'skin', SKIN_COLOR,   parent=p)
        self.hair   = _part('cube', Vec3(0, HEAD_Y + 0.34, 0),    (0.86, 0.12, 0.86), 'hat_brown', color.rgb(58, 38, 18), parent=p)
        self.hat    = _part('cube', Vec3(0, HAT_Y,  0),           (0.78, 0.26, 0.78), 'hat_brown', HAT_COLOR, parent=p)
        # Mata lucu — dua titik kecil di muka
        self.eye_l  = _part('cube', Vec3(-0.20, HEAD_Y + 0.10, -0.40), (0.12, 0.14, 0.06), '', color.rgb(50, 35, 20), parent=p)
        self.eye_r  = _part('cube', Vec3( 0.20, HEAD_Y + 0.10, -0.40), (0.12, 0.14, 0.06), '', color.rgb(50, 35, 20), parent=p)
        self.neck   = _part('cube', Vec3(0, HEAD_Y - 0.46, 0),    (0.28, 0.18, 0.28), 'skin', SKIN_COLOR,   parent=p)
        self.body   = _part('cube', Vec3(0, BODY_Y, 0),           (0.65, 0.96, 0.46), 'cloth_green', BODY_COLOR, parent=p)
        self.belt   = _part('cube', Vec3(0, BODY_Y - 0.40, 0),    (0.68, 0.10, 0.48), 'pants_dark',  color.rgb(68, 52, 38), parent=p)
        self.arm_l  = _part('cube', Vec3(-0.46, ARM_Y, 0),        (0.22, 0.85, 0.22), 'cloth_green', BODY_COLOR, parent=p)
        self.arm_r  = _part('cube', Vec3( 0.46, ARM_Y, 0),        (0.22, 0.85, 0.22), 'cloth_green', BODY_COLOR, parent=p)
        self.hand_l = _part('sphere', Vec3(-0.46, ARM_Y - 0.50, 0),(0.26, 0.26, 0.26), 'skin', SKIN_COLOR, parent=p)
        self.hand_r = _part('sphere', Vec3( 0.46, ARM_Y - 0.50, 0),(0.26, 0.26, 0.26), 'skin', SKIN_COLOR, parent=p)
        self.leg_l  = _part('cube', Vec3(-0.18, LEG_Y, 0),        (0.24, 0.46, 0.30), 'pants_dark', PANTS_COLOR, parent=p)
        self.leg_r  = _part('cube', Vec3( 0.18, LEG_Y, 0),        (0.24, 0.46, 0.30), 'pants_dark', PANTS_COLOR, parent=p)
        self.shoe_l = _part('cube', Vec3(-0.18, GROUND_H + 0.07, 0.06), (0.26, 0.14, 0.38), 'shoe_dark', SHOE_COLOR, parent=p)
        self.shoe_r = _part('cube', Vec3( 0.18, GROUND_H + 0.07, 0.06), (0.26, 0.14, 0.38), 'shoe_dark', SHOE_COLOR, parent=p)

    # ─── POSITION HELPERS ────────────────────────────────
    def set_tile_pos(self, tx: float, ty: float):
        self.x = tx * TS
        self.y = 0
        self.z = ty * TS
        self._last_tile = (int(round(tx)), int(round(ty)))

    def get_tile_pos(self):
        return int(round(self.x / TS)), int(round(self.z / TS))

    def get_float_tile(self):
        return self.x / TS, self.z / TS

    # ─── TICK (dipanggil manual dari app.py saat mode='hud') ──
    def tick(self):
        dt = time.dt
        s  = self.state

        # Timer
        self._attack_cd  = max(0.0, self._attack_cd  - dt * 1000)
        # Absorb invuln set by mob damage before decrementing
        self._invuln     = max(self._invuln, s.invuln_timer_ms)
        self._invuln     = max(0.0, self._invuln     - dt * 1000)
        self._attack_anim= max(0.0, self._attack_anim- dt * 1000)
        s.invuln_timer_ms = self._invuln

        # Movement — camera-relative untuk isometric camera rotation_y=45
        # W/S = maju/mundur (screen-up/down), A/D = kiri/kanan (screen-left/right)
        fwd_key = (held_keys['w'] or held_keys['up arrow'])    - (held_keys['s'] or held_keys['down arrow'])
        rt_key  = (held_keys['d'] or held_keys['right arrow']) - (held_keys['a'] or held_keys['left arrow'])

        # Transformasi ke world-space: camera_rot_y=45
        # screen-up(W)=NE=(+X+Z), screen-right(D)=SE=(+X-Z)
        mx = (fwd_key + rt_key) * 0.707
        mz = (fwd_key - rt_key) * 0.707

        if mx != 0 or mz != 0:
            run  = held_keys['shift'] and s.energy > 0
            spd  = self.speed * (PLAYER_RUN_MULTIPLIER if run else 1.0)
            if run:
                s.energy = max(0, s.energy - SPRINT_ENERGY_DRAIN * dt)
            mag  = math.sqrt(mx * mx + mz * mz)
            mx  /= mag;  mz /= mag

            nx = self.x + mx * spd * dt
            nz = self.z + mz * spd * dt

            # Sliding collision: coba X dulu, lalu Z
            tx_new = int(round(nx / TS));  tz_cur = int(round(self.z / TS))
            if self.world.is_walkable(tx_new, tz_cur):
                self.x = nx

            tx_cur = int(round(self.x / TS));  tz_new = int(round(nz / TS))
            if self.world.is_walkable(tx_cur, tz_new):
                self.z = nz

            # Mainkan suara langkah berdasarkan tekstur tanah yang diinjak
            tx_i, ty_i = int(round(self.x / TS)), int(round(self.z / TS))
            if getattr(self, '_last_tile', None) != (tx_i, ty_i):
                self._last_tile = (tx_i, ty_i)
                tid = self.world.get_tile(tx_i, ty_i)
                sound_play(get_step_sound(TILE_NAMES.get(tid, 'grass')), 0.4)
                if self._check_portals(tx_i, ty_i):
                    return

            # Facing — dari key input (screen-relative), bukan mx/mz
            if abs(fwd_key) >= abs(rt_key):
                self.facing = 'up' if fwd_key > 0 else 'down'
            else:
                self.facing = 'right' if rt_key > 0 else 'left'

            # Rotasi model: camera_rot_y=45, forward=(sin θ, 0, cos θ)
            # 'up'=NE: θ=45, 'down'=SW: θ=-135, 'left'=NW: θ=-45, 'right'=SE: θ=135
            rot_map = {'up': 45, 'down': -135, 'left': -45, 'right': 135}
            self.target_rotation_y = rot_map.get(self.facing, 135)

            # Animasi kaki berjalan
            self._anim_t += dt * (12 if run else 8)
            swing = math.sin(self._anim_t) * 18.0
            self.leg_l.rotation_x =  swing
            self.leg_r.rotation_x = -swing
            self.arm_l.rotation_x = -swing * 0.7
            self.arm_r.rotation_x =  swing * 0.7
        else:
            # Reset pose
            self._reset_anim()

        # Animasi rotasi (lerp) agar tidak kaku
        target_y = self.target_rotation_y
        diff = target_y - self.rotation_y
        # Pilih jalur rotasi terpendek (misal dari -90 ke 90, jangan lewat 180)
        if diff > 180:
            target_y -= 360
        elif diff < -180:
            target_y += 360
        self.rotation_y = lerp(self.rotation_y, target_y, dt * 15)

        # Animasi alat/serangan — per mode
        if self._attack_anim > 0:
            t  = self._attack_anim / 350.0           # 1.0 → 0.0
            st = math.sin((1.0 - t) * math.pi)       # arc 0 → 1 → 0
            m  = self._anim_mode
            if m == 'swing':                          # serangan / kapak
                self.arm_r.rotation_z = -65 * t
            elif m == 'down':                         # cangkul / pickaxe
                self.arm_r.rotation_x = -85 * st
                self.arm_l.rotation_x = -50 * st
                self.body.rotation_x  =  28 * st
            elif m == 'water':                        # siram
                self.arm_r.rotation_x = -58 * t
                self.arm_l.rotation_x = -45 * t
                self.body.rotation_x  =  12 * t
            elif m == 'bend':                         # tanam / panen
                self.body.rotation_x  =  48 * st
                self.arm_r.rotation_x =  72 * st
                self.arm_l.rotation_x =  72 * st
        else:
            # Reset semua bagian tubuh ke pose normal
            self.arm_r.rotation_z = 0
            self.arm_r.rotation_x = 0
            self.arm_l.rotation_x = 0
            self.body.rotation_x  = 0

        # ── python-2d-game health_and_mana.py pattern: passive HP regen ──
        if s.hp < s.max_hp:
            regen = s.hp_regen_rate
            if s.buffs.get('regen', 0) > 0:
                regen *= 3.5   # wild_herb buff: regen 3.5×
            s.hp = min(s.max_hp, s.hp + regen * dt)

        # ── Buff tick (python-2d-game AbstractBuffEffect.apply_middle_effect) ──
        for buff_name in list(s.buffs.keys()):
            s.buffs[buff_name] = max(0, s.buffs[buff_name] - dt * 1000)
            if s.buffs[buff_name] <= 0:
                del s.buffs[buff_name]

        # Invuln: kedip merah (tint di atas tekstur)
        if self._invuln > 0:
            blink = int(self._invuln / 80) % 2 == 0
            self.body.color = color.rgb(255, 80, 80) if blink else color.white
        else:
            self.body.color = color.white

        # Sync state
        s.player_x = self.x / TS
        s.player_y = self.z / TS
        s.facing   = self.facing

        # Terrain following (Craig-Macomber pattern: query tile height cache)
        tx_i, ty_i = int(round(self.x / TS)), int(round(self.z / TS))
        target_y = self.world.get_surface_height(tx_i, ty_i)
        self.y = lerp(self.y, target_y, min(1.0, dt * 14))

    def _reset_anim(self):
        for p in (self.leg_l, self.leg_r, self.arm_l, self.arm_r):
            p.rotation_x = p.rotation_x * 0.75 if abs(p.rotation_x) > 0.5 else 0
        self.body.rotation_x = self.body.rotation_x * 0.75 if abs(self.body.rotation_x) > 0.5 else 0

    # ─── INPUT ACTIONS ───────────────────────────────────
    def handle_input(self, key, entities_mgr, panels):
        """Dipanggil dari app.py saat mode='play'.
        Return True jika input dikonsumsi."""
        s = self.state

        if key == 'space':
            self._use_tool(entities_mgr, panels)
            return True

        if key == 'e':
            self._interact(entities_mgr, panels)
            return True

        if key == 'z':
            self._attack(entities_mgr, panels)
            return True

        if key == 'f':
            self._capture(entities_mgr, panels)
            return True

        if key == 't':
            self._try_sleep(panels)
            return True

        if key == 'v':
            self._consume_item(panels)
            return True

        if key == 'g':
            self.give_gift(entities_mgr, panels)
            return True

        if key.isdigit():
            n = int(key)
            if 1 <= n <= len(TOOLS):
                s.tool_index = n - 1
                sound_play('menu_move', 0.6)
                return True

        if key == 'q':
            keys = list(CROPS.keys())
            idx  = keys.index(s.seed_key) if s.seed_key in keys else 0
            s.seed_key = keys[(idx - 1) % len(keys)]
            sound_play('menu_move', 0.6)
            return True

        if key == 'r':
            keys = list(CROPS.keys())
            idx  = keys.index(s.seed_key) if s.seed_key in keys else 0
            s.seed_key = keys[(idx + 1) % len(keys)]
            sound_play('menu_move', 0.6)
            return True

        return False

    # ─── PRIVATE: PORTAL & DUNGEON ───────────────────────
    def _check_portals(self, tx_i, ty_i) -> bool:
        s = self.state
        sc = self.world.scene_obj
        
        # 1. Cek Portal Normal
        if sc and hasattr(sc, 'portals'):
            for (px, py, t_scene, tx, ty) in sc.portals:
                if tx_i == px and ty_i == py:
                    s.scene_name = t_scene
                    s.player_x = float(tx)
                    s.player_y = float(ty)
                    sound_play('step_floor', 0.8)
                    return True

        # 2. Cek Tangga Dungeon
        if s.scene_name == 'dungeon':
            tid = self.world.get_tile(tx_i, ty_i)
            if tid == STAIRS_DOWN:
                s.dungeon_level += 1
                if s.dungeon_level > s.stats.get('deepest_level', 0):
                    s.stats['deepest_level'] = s.dungeon_level
                self._generate_and_enter_dungeon()
                return True
            elif tid == STAIRS_UP:
                s.dungeon_level -= 1
                if s.dungeon_level <= 0:
                    s.scene_name = 'naga_cave'
                    s.player_x = 7.0
                    s.player_y = 10.0
                    sound_play('step_floor', 0.8)
                else:
                    self._generate_and_enter_dungeon()
                return True
        # Masuk dungeon dari Gua Naga
        elif s.scene_name == 'naga_cave':
            tid = self.world.get_tile(tx_i, ty_i)
            if tid == STAIRS_DOWN:
                s.scene_name = 'dungeon'
                s.dungeon_level = 1
                self._generate_and_enter_dungeon()
                return True
                
        return False

    def _generate_and_enter_dungeon(self):
        s = self.state
        from .dungeon import generate_dungeon_level
        grid, px, py, mobs = generate_dungeon_level(s.dungeon_level)
        s.dungeon_tiles = grid
        s.player_x = float(px)
        s.player_y = float(py)
        s.mobs = mobs
        sound_play('step_floor', 0.8)

    def _play_tool_anim(self, mode='swing'):
        self._attack_anim = 350
        self._anim_mode   = mode

    def _fx_burst(self, wx, wy, wz, col, n=5, spread=0.45, dur=0.38):
        """Partikel ledakan singkat di posisi world — efek visual alat/serangan."""
        import random as _r
        for _ in range(n):
            ox = _r.uniform(-spread, spread)
            oy = _r.uniform(0.05, spread)
            oz = _r.uniform(-spread, spread)
            e = Entity(model='sphere',
                       position=(wx + ox, wy + oy, wz + oz),
                       scale=_r.uniform(0.08, 0.18), color=col)
            invoke(destroy, e, delay=dur)

    # ─── PRIVATE: TOOL ───────────────────────────────────
    def _facing_tile(self):
        tx, ty = self.get_tile_pos()
        # Camera-relative: 'up'=screen-up=world NE=(+tx+ty), 'right'=SE=(+tx-ty)
        dmap = {'up': (1, 1), 'down': (-1, -1), 'left': (-1, 1), 'right': (1, -1)}
        dx, dz = dmap.get(self.facing, (1, 1))
        return tx + dx, ty + dz

    def _use_tool(self, entities_mgr, panels):
        s    = self.state
        tool = TOOLS[s.tool_index] if s.tool_index < len(TOOLS) else 'Cangkul'
        tx, ty   = self._facing_tile()
        sc_name  = s.scene_name
        soil_key = f"{tx},{ty},{sc_name}"
        tid      = self.world.get_tile(tx, ty)

        # Helper: posisi world dari facing tile untuk efek partikel
        fx, fz = tx * TS, ty * TS
        fy = GROUND_H + 0.4

        if tool == 'Cangkul':
            if tid in TILLABLE and s.energy >= 2:
                soil = s.soil.setdefault(soil_key, {})
                soil['tilled'] = True
                s.energy -= 2
                self.world.refresh_tile(tx, ty, soil_key)
                self._play_tool_anim('down')
                self._fx_burst(fx, fy, fz, color.rgb(120, 82, 42))   # debu tanah
                sound_play('hoe', 0.8)
                panels.flash_msg("Tanah dicangkul!", 0.8)
            else:
                sound_play('blocked', 0.6)

        elif tool == 'Siram':
            soil = s.soil.get(soil_key)
            if soil and soil.get('tilled') and s.energy >= 1:
                soil['watered'] = True
                s.energy -= 1
                s.stats['watered'] = s.stats.get('watered', 0) + 1
                self.world.refresh_tile(tx, ty, soil_key)
                self._play_tool_anim('water')
                self._fx_burst(fx, fy + 0.2, fz, color.rgb(60, 150, 255, 200), n=6)  # percikan air
                sound_play('water', 0.8)
                panels.flash_msg("Tanaman disiram!", 0.8)
                self._check_quest_progress(panels)
            else:
                sound_play('blocked', 0.6)

        elif tool == 'Tanam':
            soil     = s.soil.get(soil_key, {})
            seed_key = s.seed_key + '_seed'
            if soil.get('tilled') and not soil.get('crop') and s.inventory.get(seed_key, 0) > 0:
                soil = s.soil.setdefault(soil_key, {})
                soil.update({'crop': s.seed_key, 'age': 0, 'tilled': True})
                s.inventory[seed_key] -= 1
                s.energy = max(0, s.energy - 2)
                self.world.refresh_tile(tx, ty, soil_key)
                self._play_tool_anim('bend')
                self._fx_burst(fx, fy, fz, color.rgb(70, 200, 70), n=4)   # percikan hijau benih
                sound_play('plant', 0.8)
                if s.seed_key == 'lobak':
                    s.stats['lobak_planted'] = s.stats.get('lobak_planted', 0) + 1
                panels.flash_msg(f"{CROPS[s.seed_key]['name']} ditanam!", 0.8)
            else:
                sound_play('blocked', 0.6)

        elif tool == 'Panen':
            soil = s.soil.get(soil_key)
            if soil and soil.get('crop'):
                crop_data = CROPS.get(soil['crop'], {})
                if soil.get('age', 0) >= crop_data.get('days', 4):
                    crop_name = soil['crop']
                    s.inventory[crop_name] = s.inventory.get(crop_name, 0) + 1
                    sold = crop_data.get('sell', 20)
                    s.gold += sold
                    s.stats['earned'] = s.stats.get('earned', 0) + sold
                    if crop_name == 'lobak':
                        s.stats['lobak_harvested'] = s.stats.get('lobak_harvested', 0) + 1
                    del s.soil[soil_key]
                    s.energy = max(0, s.energy - 2)
                    self.world.refresh_tile(tx, ty, soil_key)
                    self._play_tool_anim('bend')
                    self._fx_burst(fx, fy + 0.3, fz, color.rgb(255, 225, 50), n=7)  # kerlip emas panen
                    sound_play('harvest', 0.8)
                    panels.flash_msg(f"{CROPS[crop_name]['name']} dipanen! +{sold}G", 1.2)
                    self._check_quest_progress(panels)
                else:
                    sound_play('blocked', 0.6)
                    panels.flash_msg("Belum siap panen.", 0.8)

        elif tool == 'Hadiah':
            self.give_gift(entities_mgr, panels)

        elif tool == 'Kapak':
            from .config import TR, DT, G, D, CV_F
            if tid in (TR, DT) and s.energy >= 2:
                s.inventory['kayu'] = s.inventory.get('kayu', 0) + 1
                panels.flash_msg("+1 Kayu", 0.8)
                # Ubah tile pohon menjadi ground biasa
                if s.scene_name == 'dungeon':
                    s.dungeon_tiles[ty][tx] = CV_F
                else:
                    sc = self.world.scene_obj
                    sc.tiles[ty][tx] = G if tid == TR else D
                self.world.load_scene(s.scene_name)
                s.energy -= 2
                self._play_tool_anim('swing')
                self._fx_burst(fx, fy + 0.5, fz, color.rgb(185, 135, 72), n=6)  # serpihan kayu
                sound_play('axe', 0.8)
                self._check_quest_progress(panels)
            else:
                sound_play('blocked', 0.6)

        elif tool == 'Pickaxe':
            if tid in MINEABLE and s.pickaxe_tier > 0 and s.energy >= 2:
                ore_map = {
                    ORE_TBG: 'tembaga', ORE_BSI: 'besi', ORE_EMS: 'emas',
                    ORE_KRS: 'kristal', ORE_MTH: 'mithril', CRYS: 'kristal',
                }
                mineral = ore_map.get(tid)
                spark_col = {
                    'tembaga': color.rgb(200, 120, 55),
                    'besi':    color.rgb(180, 180, 200),
                    'emas':    color.rgb(255, 225, 60),
                    'kristal': color.rgb(200, 155, 255),
                    'mithril': color.rgb(148, 235, 255),
                }.get(mineral, color.rgb(140, 130, 118))
                if mineral:
                    s.inventory[mineral] = s.inventory.get(mineral, 0) + 1
                    s.stats['minerals_mined'] = s.stats.get('minerals_mined', 0) + 1
                    panels.flash_msg(f"+1 {mineral.capitalize()}", 0.8)
                if s.scene_name == 'dungeon':
                    if 0 <= ty < len(s.dungeon_tiles) and 0 <= tx < len(s.dungeon_tiles[0]):
                        s.dungeon_tiles[ty][tx] = MINED
                        self.world.load_scene(s.scene_name)
                else:
                    sc = self.world.scene_obj
                    if 0 <= tx < sc.w and 0 <= ty < sc.h:
                        sc.tiles[ty][tx] = MINED
                        self.world.load_scene(s.scene_name)
                s.energy -= 2
                self._play_tool_anim('down')
                self._fx_burst(fx, fy + 0.3, fz, spark_col, n=8)  # percikan batu/mineral
                sound_play('axe', 0.8)
                self._check_quest_progress(panels)
            else:
                sound_play('blocked', 0.6)

        elif tool == 'Pedang':
            self._attack(entities_mgr, panels)

    # ─── PRIVATE: INTERACT ───────────────────────────────
    def _interact(self, entities_mgr, panels):
        s = self.state
        tx, ty = self.get_tile_pos()

        # Scene-specific service interactions (prioritas sebelum NPC dialog)
        if s.scene_name == 'lake' and self._try_fishing(panels):
            return
        if s.scene_name == 'clinic' and self._try_healing(panels):
            return

        npc_info = entities_mgr.get_nearest_npc(tx, ty, max_dist_tiles=3.0)
        if npc_info:
            panels.start_dialog(npc_info['id'], self.state)
        else:
            # Cek mailbox
            ftx, fty = self._facing_tile()
            from .config import MB
            if self.world.get_tile(ftx, fty) == MB and not self.state.mail_read:
                self.state.mail_read = True
                if self.state.quest_stage == 0:
                    self.state.quest_stage = 1
                sound_play('menu_select', 0.8)
                panels.start_dialog('mailbox', self.state)

    def _try_fishing(self, panels) -> bool:
        """Mancing di danau — butuh berdiri di/dekat DCK atau menghadap air.
        Return True jika interaksi dikonsumsi."""
        import random as _rng
        tx, ty = self.get_tile_pos()
        on_dock      = self.world.get_tile(tx, ty) in (DCK, LLY)
        ftx, fty     = self._facing_tile()
        facing_water = self.world.get_tile(ftx, fty) == W
        if not (on_dock or facing_water):
            return False

        s = self.state
        if s.energy < 2:
            sound_play('blocked', 0.5)
            panels.flash_msg("Terlalu lelah untuk memancing.", 1.0)
            return True

        s.energy = max(0, s.energy - 2)
        if _rng.random() < 0.55:
            gold = _rng.randint(20, 75)
            s.gold += gold
            s.stats['earned'] = s.stats.get('earned', 0) + gold
            sound_play('harvest', 0.8)
            panels.flash_msg(f"Dapat ikan! Dijual +{gold}G", 1.5)
            self._check_quest_progress(panels)
        else:
            sound_play('blocked', 0.4)
            panels.flash_msg("Tidak ada yang menggigit... coba lagi.", 1.0)
        return True

    def _try_healing(self, panels) -> bool:
        """Klinik Pak Raka: sembuhkan HP player dengan bayar gold.
        Return True jika Pak Raka ada di clinic (interaksi dikonsumsi)."""
        s   = self.state
        pos = s.npc_positions.get('raka', {})
        if pos.get('scene') != 'clinic':
            return False
        tx, ty = self.get_tile_pos()
        if math.hypot(pos.get('x', -99) - tx, pos.get('y', -99) - ty) > 4.0:
            return False

        missing = s.max_hp - s.hp
        if missing <= 5:
            panels.flash_msg("HP kamu sudah penuh.", 0.8)
            return True

        cost = max(10, int(missing * 0.5))
        if s.gold < cost:
            sound_play('blocked', 0.6)
            panels.flash_msg(f"Pak Raka butuh {cost}G untuk menyembuhkan.", 1.5)
            return True

        s.gold -= cost
        s.hp    = s.max_hp
        sound_play('harvest', 0.8)
        panels.flash_msg(f"Pak Raka: Sudah sehat! -{cost}G, HP penuh.", 2.0)
        return True

    # ─── PRIVATE: ATTACK ─────────────────────────────────
    def _attack(self, entities_mgr, panels):
        s = self.state
        if self._attack_cd > 0:
            return
        if not s.sword_id:
            sound_play('blocked', 0.6)
            panels.flash_msg("Tidak punya pedang!", 1.0)
            return

        sword_dmg = TOOL_DAMAGE
        for r in SWORD_RECIPES:
            if r['id'] == s.sword_id:
                sword_dmg = r['damage']
                break

        tx, ty = self.get_tile_pos()
        killed = entities_mgr.attack_mobs(tx, ty, PLAYER_ATTACK_RANGE, sword_dmg)
        if killed:
            s.stats['mobs_killed'] = s.stats.get('mobs_killed', 0) + killed
            panels.flash_msg(f"{killed} musuh dikalahkan!", 1.0)
            self._check_quest_progress(panels)

        self._attack_cd = PLAYER_ATTACK_COOLDOWN_MS
        self._play_tool_anim('swing')
        sound_play('sword', 0.8)
        # Efek percikan merah di depan player
        ftx, fty = self._facing_tile()
        self._fx_burst(ftx * TS, GROUND_H + 0.8, fty * TS,
                       color.rgb(255, 48, 48), n=5, spread=0.5)

    # ─── PRIVATE: CAPTURE ────────────────────────────────
    def _capture(self, entities_mgr, panels):
        tx, ty = self.get_tile_pos()
        result = entities_mgr.try_capture_wild(tx, ty, self.state)
        if result:
            name, sell = result
            self.state.captured_supernatural += 1
            self.state.inventory[name] = self.state.inventory.get(name, 0) + 1
            sound_play('capture', 0.8)
            panels.flash_msg(f"{name} ditangkap! (+{sell}G jika dijual)", 1.5)
            self._check_quest_progress(panels)
        else:
            sound_play('blocked', 0.6)
            panels.flash_msg("Tidak ada yang bisa ditangkap.", 0.8)

    # ─── PRIVATE: CONSUME ITEM (python-2d-game buff_effects pattern) ────────
    def _consume_item(self, panels):
        """Konsumsi item pertama yang bisa dimakan dari inventori.
        Pola: start-effect (apply hp/energy), middle-effect (buff tick di tick()),
        end-effect (buff selesai otomatis di buff dict)."""
        from .data import CONSUMABLES, WILD_ITEMS
        s = self.state
        for item_name, effect in CONSUMABLES.items():
            if s.inventory.get(item_name, 0) <= 0:
                continue
            s.inventory[item_name] -= 1

            hp_gain = effect.get('heal_hp', 0)
            en_gain = effect.get('heal_energy', 0)
            s.hp     = min(s.max_hp,     s.hp     + hp_gain)
            s.energy = min(s.max_energy, s.energy + en_gain)

            # Start-effect: tambah buff aktif
            if 'buff' in effect:
                s.buffs[effect['buff']] = effect.get('buff_ms', 10000)

            sound_play('harvest', 0.7)
            buff_note = f" [{effect['buff'].upper()}]" if 'buff' in effect else ''
            display = (CROPS.get(item_name) or WILD_ITEMS.get(item_name) or {}).get('name', item_name)
            panels.flash_msg(f"Makan {display}: +{hp_gain}HP +{en_gain}EN{buff_note}", 1.8)
            return
        sound_play('blocked', 0.5)
        panels.flash_msg("Tidak ada makanan. (V = makan)", 1.0)

    # ─── PRIVATE: SLEEP ──────────────────────────────────
    def _try_sleep(self, panels):
        if self.state.scene_name == 'house':
            sound_play('sleep', 0.8)
            panels.flash_msg("Tidur... Hari baru dimulai!", 2.0)
            self._advance_day()
        else:
            panels.flash_msg("Tidur hanya di rumah (T).", 0.8)

    def _advance_day(self):
        import random as _rng
        s = self.state
        from .config import DAYS_PER_SEASON
        s.day           += 1
        s.day_in_season += 1
        s.time_minutes   = 360.0
        s.energy         = s.max_energy
        s.hp             = s.max_hp
        s.naga_fountain_used_today = False
        s.buffs.clear()

        # ── PyDew Valley sky.py pattern: rain auto-waters tilled soil ──
        if s.weather in ('Hujan', 'Badai'):
            for soil in s.soil.values():
                if soil.get('tilled') and not soil.get('watered'):
                    soil['watered'] = True

        # Tumbuh tanaman semalam
        from .data import CROPS
        cur_season = s.get_season()
        for soil in s.soil.values():
            if soil.get('watered') and soil.get('crop'):
                crop_seasons = CROPS.get(soil['crop'], {}).get('seasons', [])
                # PyDew Valley growth-rate pattern: tumbuh lebih cepat di musim yang tepat
                growth = 2 if cur_season in crop_seasons else 1
                soil['age'] = soil.get('age', 0) + growth
                soil['watered'] = False

        if s.day_in_season > DAYS_PER_SEASON:
            s.day_in_season = 1
            old_season      = s.season_index
            s.season_index  = (old_season + 1) % 4
            if s.season_index == 0 and old_season == 3:
                s.year += 1

        # ── PyDew Valley level.py reset() pattern: randomize cuaca hari baru ──
        _weathers = ['Cerah','Cerah','Cerah','Mendung','Hujan','Berangin','Badai']
        _weights  = [38, 22, 14, 12, 8, 4, 2]
        s.weather = _rng.choices(_weathers, weights=_weights)[0]

        from .entities import respawn_wild_at_morning
        sound_play('morning', 0.8)
        respawn_wild_at_morning(s)
        self._check_quest_progress()

    # ─── PUBLIC: GIFT ────────────────────────────────────
    def give_gift(self, entities_mgr, panels):
        s = self.state
        tx, ty = self.get_tile_pos()
        info = entities_mgr.get_nearest_npc(tx, ty, max_dist_tiles=3.0)
        if not info:
            sound_play('blocked', 0.6)
            panels.flash_msg("Tidak ada NPC di dekat (G).", 0.8)
            return
        npc_id = info['id']
        from .data import HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS
        all_d = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}
        npc = all_d.get(npc_id, {})
        gift = npc.get('gift')
        if not gift:
            sound_play('blocked', 0.6)
            panels.flash_msg("NPC ini tidak menerima hadiah.", 1.0)
            return
        if s.inventory.get(gift, 0) <= 0:
            sound_play('blocked', 0.6)
            panels.flash_msg(f"Butuh '{gift}' untuk hadiah ke {npc.get('name', npc_id)}.", 1.5)
            return
        s.inventory[gift] -= 1
        s.npc_hearts[npc_id] = min(10, s.npc_hearts.get(npc_id, 0) + 1.0)
        s.stats['gifts'] = s.stats.get('gifts', 0) + 1
        resp = npc.get('gift_r', 'Terima kasih!')
        sound_play('gift', 0.8)
        panels.flash_msg(f"{npc.get('name', npc_id)}: {resp}  (+*)", 2.0)

    # ─── PUBLIC: QUEST PROGRESSION ───────────────────────
    def _check_quest_progress(self, panels=None):
        s  = self.state
        qs = s.quest_stage
        st = s.stats
        if qs == 1 and st.get('lobak_planted', 0) >= 3 and st.get('watered', 0) >= 3:
            s.quest_stage = 2
        elif qs == 2 and st.get('lobak_harvested', 0) >= 3:
            s.quest_stage = 3
            s.greenhouse_open = True
        elif qs == 3 and s.gold >= 150:
            s.quest_stage = 4
        elif qs == 4 and s.pickaxe_tier > 0:
            s.quest_stage = 5
        elif qs == 5 and s.scene_name == 'dungeon':
            s.quest_stage = 6
        elif qs == 6 and s.inventory.get('tembaga', 0) >= 5 and s.inventory.get('besi', 0) >= 3:
            s.quest_stage = 7
        elif qs == 7 and s.sword_id and 'besi' in s.sword_id and st.get('mobs_killed', 0) >= 5:
            s.quest_stage = 8
        elif qs == 8 and s.captured_supernatural >= 1:
            s.quest_stage = 9
        elif qs == 9 and st.get('deepest_level', 0) >= 10:
            s.quest_stage = 10
        elif qs == 10 and s.naga_defeated:
            s.quest_stage = 11

        if panels and s.quest_stage > qs:
            new = QUEST_STAGES[s.quest_stage] if s.quest_stage < len(QUEST_STAGES) else None
            if new:
                if s.quest_stage == 11:
                    panels.flash_msg("SELAMAT! Kamu menyelesaikan Lembah Karsa!", 5.0)
                else:
                    panels.flash_msg(f"[J] Quest baru: {new['t']} — {new['d']}", 3.5)
            sound_play('quest', 0.9)
