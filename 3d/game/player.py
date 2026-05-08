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
from ursina import Entity, Vec3, color, held_keys, time, invoke, destroy, lerp, load_texture

from .config import (TILE_SIZE, GROUND_H, PLAYER_SPEED, PLAYER_RUN_MULTIPLIER,
                     PLAYER_ATTACK_RANGE, PLAYER_ATTACK_COOLDOWN_MS, TOOL_DAMAGE,
                     SPRINT_ENERGY_DRAIN,
                     INVULN_AFTER_HIT_MS, WALKABLE, TILLABLE, MINEABLE, TOOLS,
                     G, D, P, FL, DR, GT, CV_F, STR_T, DCK, LLY, MINED,
                     STAIRS_DOWN, STAIRS_UP, ORE_TBG, ORE_BSI, ORE_EMS,
                     ORE_KRS, ORE_MTH, CV_W, CRYS)
from .data import CROPS, SWORD_RECIPES

TS = TILE_SIZE

# Offset tubuh (titik acuan root di y=0)
BODY_Y  = GROUND_H + 0.80   # pusat badan
HEAD_Y  = GROUND_H + 1.72   # pusat kepala
HAT_Y   = GROUND_H + 2.02
ARM_Y   = GROUND_H + 0.80
LEG_Y   = GROUND_H + 0.28

SKIN_COLOR   = color.rgb(230, 188, 148)
BODY_COLOR   = color.rgb(255, 140, 60)
PANTS_COLOR  = color.rgb(78, 60, 108)
HAT_COLOR    = color.rgb(88, 58, 38)
SHOE_COLOR   = color.rgb(55, 42, 30)

_ASSET_DIR = Path(__file__).resolve().parent.parent / 'assets'
_TEX_CACHE: dict = {}

def _tex(name: str):
    if not name:
        return None
    if name in _TEX_CACHE:
        return _TEX_CACHE[name]
    p = _ASSET_DIR / f'{name}.png'
    if p.exists():
        t = load_texture(str(p))
        _TEX_CACHE[name] = t
        return t
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

        self.speed           = PLAYER_SPEED
        self.facing          = state.facing
        self._attack_cd      = 0.0    # ms
        self._invuln         = 0.0    # ms
        self._anim_t         = 0.0
        self._attack_anim    = 0.0
        self.target_rotation_y = 0.0

        self._build_model()
        self.set_tile_pos(state.player_x, state.player_y)
        self._set_initial_rotation()

    def _set_initial_rotation(self):
        """Set initial rotation based on saved state without animation."""
        rot_map = {'down': 0, 'up': 180, 'left': 90, 'right': -90}
        self.rotation_y = rot_map.get(self.state.facing, 0)
        self.target_rotation_y = self.rotation_y

    # ─── MODEL BUILDING ──────────────────────────────────
    def _build_model(self):
        p = self
        self.body  = _part('cube', Vec3(0, BODY_Y, 0),  (0.72, 1.22, 0.52), 'cloth_orange', parent=p)
        self.head  = _part('cube', Vec3(0, HEAD_Y, 0),  (0.58, 0.58, 0.58), 'skin',         parent=p)
        self.hat   = _part('cube', Vec3(0, HAT_Y,  0),  (0.65, 0.20, 0.65), 'hat_brown',    parent=p)
        self.arm_l = _part('cube', Vec3(-0.48, ARM_Y, 0), (0.22, 1.00, 0.22), 'cloth_orange', parent=p)
        self.arm_r = _part('cube', Vec3( 0.48, ARM_Y, 0), (0.22, 1.00, 0.22), 'cloth_orange', parent=p)
        self.leg_l = _part('cube', Vec3(-0.20, LEG_Y, 0), (0.26, 0.58, 0.36), 'pants_dark',   parent=p)
        self.leg_r = _part('cube', Vec3( 0.20, LEG_Y, 0), (0.26, 0.58, 0.36), 'pants_dark',   parent=p)
        self.shoe_l= _part('cube', Vec3(-0.20, GROUND_H + 0.06, 0.05), (0.28, 0.14, 0.40), 'shoe_dark', parent=p)
        self.shoe_r= _part('cube', Vec3( 0.20, GROUND_H + 0.06, 0.05), (0.28, 0.14, 0.40), 'shoe_dark', parent=p)

    # ─── POSITION HELPERS ────────────────────────────────
    def set_tile_pos(self, tx: float, ty: float):
        self.x = tx * TS
        self.y = 0
        self.z = ty * TS

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
        self._invuln     = max(0.0, self._invuln     - dt * 1000)
        self._attack_anim= max(0.0, self._attack_anim- dt * 1000)
        s.invuln_timer_ms = self._invuln

        # Movement
        mx = (held_keys['d'] or held_keys['right arrow']) - (held_keys['a'] or held_keys['left arrow'])
        mz = (held_keys['s'] or held_keys['down arrow'])  - (held_keys['w'] or held_keys['up arrow'])

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

            # Facing
            if abs(mz) > abs(mx):
                self.facing = 'down' if mz > 0 else 'up'
            else:
                self.facing = 'right' if mx > 0 else 'left'

            # Set target rotasi berdasarkan arah hadap
            rot_map = {'down': 0, 'up': 180, 'left': 90, 'right': -90}
            self.target_rotation_y = rot_map.get(self.facing, 0)

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

        # Animasi attack
        if self._attack_anim > 0:
            self.arm_r.rotation_z = -55 * (self._attack_anim / 200)
        else:
            self.arm_r.rotation_z = 0

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
        self.y     = 0  # tetap di permukaan

    def _reset_anim(self):
        for p in (self.leg_l, self.leg_r, self.arm_l, self.arm_r):
            if abs(p.rotation_x) > 0.5:
                p.rotation_x *= 0.75
            else:
                p.rotation_x = 0

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

        if key == 'q':
            keys = list(CROPS.keys())
            idx  = keys.index(s.seed_key) if s.seed_key in keys else 0
            s.seed_key = keys[(idx - 1) % len(keys)]
            return True

        if key == 'r':
            keys = list(CROPS.keys())
            idx  = keys.index(s.seed_key) if s.seed_key in keys else 0
            s.seed_key = keys[(idx + 1) % len(keys)]
            return True

        return False

    # ─── PRIVATE: TOOL ───────────────────────────────────
    def _facing_tile(self):
        tx, ty = self.get_tile_pos()
        dmap = {'up': (0,-1), 'down': (0,1), 'left': (-1,0), 'right': (1,0)}
        dx, dz = dmap.get(self.facing, (0,1))
        return tx + dx, ty + dz

    def _use_tool(self, entities_mgr, panels):
        s    = self.state
        tool = TOOLS[s.tool_index] if s.tool_index < len(TOOLS) else 'Cangkul'
        tx, ty   = self._facing_tile()
        sc_name  = s.scene_name
        soil_key = f"{tx},{ty},{sc_name}"
        tid      = self.world.get_tile(tx, ty)

        if tool == 'Cangkul':
            if tid in TILLABLE and s.energy >= 2:
                soil = s.soil.setdefault(soil_key, {})
                soil['tilled'] = True
                s.energy -= 2
                self.world.refresh_tile(tx, ty, soil_key)
                panels.flash_msg("Tanah dicangkul!", 0.8)

        elif tool == 'Siram':
            soil = s.soil.get(soil_key)
            if soil and soil.get('tilled') and s.energy >= 1:
                soil['watered'] = True
                s.energy -= 1
                s.stats['watered'] = s.stats.get('watered', 0) + 1
                self.world.refresh_tile(tx, ty, soil_key)
                panels.flash_msg("Tanaman disiram!", 0.8)
                self._check_quest_progress()

        elif tool == 'Tanam':
            soil     = s.soil.get(soil_key, {})
            seed_key = s.seed_key + '_seed'
            if soil.get('tilled') and not soil.get('crop') and s.inventory.get(seed_key, 0) > 0:
                soil = s.soil.setdefault(soil_key, {})
                soil.update({'crop': s.seed_key, 'age': 0, 'tilled': True})
                s.inventory[seed_key] -= 1
                s.energy = max(0, s.energy - 2)
                self.world.refresh_tile(tx, ty, soil_key)
                if s.seed_key == 'lobak':
                    s.stats['lobak_planted'] = s.stats.get('lobak_planted', 0) + 1
                panels.flash_msg(f"{CROPS[s.seed_key]['name']} ditanam!", 0.8)

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
                    panels.flash_msg(f"{CROPS[crop_name]['name']} dipanen! +{sold}G", 1.2)
                    self._check_quest_progress()
                else:
                    panels.flash_msg("Belum siap panen.", 0.8)

        elif tool == 'Pickaxe':
            if tid in MINEABLE and s.pickaxe_tier > 0 and s.energy >= 2:
                ore_map = {
                    ORE_TBG: 'tembaga', ORE_BSI: 'besi', ORE_EMS: 'emas',
                    ORE_KRS: 'kristal', ORE_MTH: 'mithril', CRYS: 'kristal',
                }
                mineral = ore_map.get(tid)
                if mineral:
                    s.inventory[mineral] = s.inventory.get(mineral, 0) + 1
                    s.stats['minerals_mined'] = s.stats.get('minerals_mined', 0) + 1
                    panels.flash_msg(f"+1 {mineral.capitalize()}", 0.8)
                sc = self.world.scene_obj
                if 0 <= tx < sc.w and 0 <= ty < sc.h:
                    sc.tiles[ty][tx] = MINED
                    self.world.load_scene(s.scene_name)
                s.energy -= 2
                self._check_quest_progress()

        elif tool == 'Pedang':
            self._attack(entities_mgr, panels)

    # ─── PRIVATE: INTERACT ───────────────────────────────
    def _interact(self, entities_mgr, panels):
        tx, ty = self.get_tile_pos()
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
                panels.start_dialog('mailbox', self.state)

    # ─── PRIVATE: ATTACK ─────────────────────────────────
    def _attack(self, entities_mgr, panels):
        s = self.state
        if self._attack_cd > 0:
            return
        if not s.sword_id:
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
            self._check_quest_progress()

        self._attack_cd   = PLAYER_ATTACK_COOLDOWN_MS
        self._attack_anim = 200
        # Ayunkan lengan kanan
        self.arm_r.rotation_z = -55
        invoke(lambda: setattr(self.arm_r, 'rotation_z', 0), delay=0.22)

    # ─── PRIVATE: CAPTURE ────────────────────────────────
    def _capture(self, entities_mgr, panels):
        tx, ty = self.get_tile_pos()
        result = entities_mgr.try_capture_wild(tx, ty, self.state)
        if result:
            name, sell = result
            self.state.captured_supernatural += 1
            self.state.inventory[name] = self.state.inventory.get(name, 0) + 1
            panels.flash_msg(f"{name} ditangkap! (+{sell}G jika dijual)", 1.5)
            self._check_quest_progress()
        else:
            panels.flash_msg("Tidak ada yang bisa ditangkap.", 0.8)

    # ─── PRIVATE: SLEEP ──────────────────────────────────
    def _try_sleep(self, panels):
        if self.state.scene_name == 'house':
            panels.flash_msg("Tidur... Hari baru dimulai!", 2.0)
            self._advance_day()
        else:
            panels.flash_msg("Tidur hanya di rumah (T).", 0.8)

    def _advance_day(self):
        s = self.state
        from .config import DAYS_PER_SEASON
        s.day           += 1
        s.day_in_season += 1
        s.time_minutes   = 360.0
        s.energy         = s.max_energy
        s.hp             = s.max_hp
        s.naga_fountain_used_today = False

        # Tumbuh tanaman semalam
        for soil in s.soil.values():
            if soil.get('watered') and soil.get('crop'):
                soil['age'] = soil.get('age', 0) + 1
                soil['watered'] = False

        if s.day_in_season > DAYS_PER_SEASON:
            s.day_in_season  = 1
            s.season_index   = (s.season_index + 1) % 4

        from .entities import respawn_wild_at_morning
        respawn_wild_at_morning(s)
        self._check_quest_progress()

    # ─── PUBLIC: GIFT ────────────────────────────────────
    def give_gift(self, entities_mgr, panels):
        s = self.state
        tx, ty = self.get_tile_pos()
        info = entities_mgr.get_nearest_npc(tx, ty, max_dist_tiles=3.0)
        if not info:
            panels.flash_msg("Tidak ada NPC di dekat (G).", 0.8)
            return
        npc_id = info['id']
        from .data import HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS
        all_d = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}
        npc = all_d.get(npc_id, {})
        gift = npc.get('gift')
        if not gift:
            panels.flash_msg("NPC ini tidak menerima hadiah.", 1.0)
            return
        if s.inventory.get(gift, 0) <= 0:
            panels.flash_msg(f"Butuh '{gift}' untuk hadiah ke {npc.get('name', npc_id)}.", 1.5)
            return
        s.inventory[gift] -= 1
        s.npc_hearts[npc_id] = min(10, s.npc_hearts.get(npc_id, 0) + 1.0)
        s.stats['gifts'] = s.stats.get('gifts', 0) + 1
        resp = npc.get('gift_r', 'Terima kasih!')
        panels.flash_msg(f"{npc.get('name', npc_id)}: {resp}  (+♥)", 2.0)

    # ─── PUBLIC: QUEST PROGRESSION ───────────────────────
    def _check_quest_progress(self):
        s = self.state
        qs = s.quest_stage
        st = s.stats
        if qs == 1 and st.get('lobak_planted', 0) >= 3 and st.get('watered', 0) >= 3:
            s.quest_stage = 2
        elif qs == 2 and st.get('lobak_harvested', 0) >= 3:
            s.quest_stage = 3
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
