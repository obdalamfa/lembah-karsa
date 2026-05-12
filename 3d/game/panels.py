"""
panels.py — 2D UI overlay untuk Ursina Engine.
Semua elemen UI menggunakan camera.ui sebagai parent (screen-space).

Layout layar (Ursina screen coords: -0.5 ke 0.5):
  ┌──────────────────────────────────┐
  │ [Tool] [Seed]    [Scene] [Cuaca] │  ← baris atas kiri / kanan
  │ HP ████░░░░░░                    │
  │ EN ████████░░                    │
  │ 💰 Gold: 100G      [Waktu/Hari]  │
  └──────────────────────────────────┘

Dialog box: muncul di bawah tengah.
Panel (inventori, quest, dll.): overlay penuh semi-transparan.
"""
from ursina import (Entity, Text, color, camera, destroy,
                    Vec2, Vec4, invoke)

from .config import SEASON_NAMES
from .data import CROPS
from .data import (HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS,
                   QUEST_STAGES, SWORD_RECIPES, PICKAXE_RECIPES, SHOP_ITEMS)

_ALL_NPCS = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}


def _ui(model='quad', **kw):
    # Tidak pakai shader agar color property bekerja di camera.ui space.
    # transparent=True wajib agar alpha channel diterapkan oleh renderer.
    kw.setdefault('transparent', True)
    return Entity(parent=camera.ui, model=model, **kw)


def _txt(text='', pos=(0, 0), scale=1.0, col=color.white, **kw):
    return Text(text, parent=camera.ui, position=pos,
                scale=scale * 1.8, color=col, **kw)


class UIManager:
    """Mengelola semua HUD dan panel."""

    def __init__(self, state):
        self.state       = state
        self.mode        = 'hud'    # 'hud' | 'dialog' | 'panel'
        self._panel_name = None
        self._dialog_lines: list = []
        self._dialog_idx  = 0
        self._dialog_npc  = None

        self._flash_ent = None
        self._flash_t   = 0.0

        self._build_hud()
        self._build_dialog_box()
        self._build_panel_bg()

    # ─── PUBLIC: UPDATE ──────────────────────────────────
    def update(self, state, dt: float = 0):
        self.state = state
        if self.mode == 'hud':
            self._refresh_hud()

        # Flash message timer
        if self._flash_t > 0:
            self._flash_t -= dt
            if self._flash_t <= 0 and self._flash_ent:
                self._flash_ent.enabled = False
                if hasattr(self, '_flash_bg'):
                    self._flash_bg.enabled = False

    _TOOL_NAMES = ['Cangkul','Siram','Tanam','Panen','Kapak','Hadiah','Pickaxe','Pedang']

    # ─── PUBLIC: HUD ─────────────────────────────────────
    def _build_hud(self):
        BY = -0.450   # bar center Y
        BH = 0.096    # bar height
        SY = BY + BH * 0.5   # separator line Y (top of bar)

        # Colors stored as instance attrs (used in _refresh_hud)
        self._C_HP   = color.rgb(220,  55,  55)
        self._C_EN   = color.rgb( 55, 205,  75)
        self._C_GOLD = color.rgb(255, 215,  60)
        _C_BG    = color.rgb( 20,  15,  30, 220)
        _C_SEP   = color.rgb(180, 160, 120, 220)
        _C_HP_BG = color.rgb( 60,  10,  10, 160)
        _C_EN_BG = color.rgb( 10,  40,  10, 160)
        _C_TIME  = color.rgb(255, 255, 210)
        _C_DATE  = color.rgb(170, 200, 255)
        _C_SCENE = color.rgb(140, 255, 160)
        _C_WTH   = color.rgb(255, 240, 130)
        _C_TOOL  = color.rgb(255, 240, 100)
        _C_SEED  = color.rgb(155, 255, 155)
        _C_BUFF  = color.rgb(120, 255, 180)
        _C_LBL   = color.rgb(150, 140, 170)
        _C_TBORD = color.rgb(100,  75, 160, 200)

        # ── Full-width bottom bar + gold top separator ────────
        self._bar_bg  = _ui(scale=(2.0, BH), position=(0, BY), color=_C_BG)
        self._bar_sep = _ui(scale=(2.0, 0.003), position=(0, SY), color=_C_SEP)

        # ── LEFT: HP / EN bars + Gold ─────────────────────────
        BAR_W = 0.215
        BAR_X = -0.680   # bar center x
        LBL_X = -0.875   # label left edge x
        VAL_X = -0.568   # value text left x (right of bar)

        hy = BY + 0.024   # HP row center Y
        self._hp_lbl = _txt('HP', pos=(LBL_X, hy + 0.010), scale=0.80, col=_C_LBL)
        self._hp_bg  = _ui(scale=(BAR_W, 0.016), position=(BAR_X, hy), color=_C_HP_BG)
        self._hp_bar = _ui(scale=(BAR_W, 0.013), position=(BAR_X, hy), color=self._C_HP)
        self._hp_val = _txt('100/100', pos=(VAL_X, hy + 0.010), scale=0.76, col=color.white)

        ey = BY + 0.002   # EN row center Y
        self._en_lbl = _txt('EN', pos=(LBL_X, ey + 0.010), scale=0.80, col=_C_LBL)
        self._en_bg  = _ui(scale=(BAR_W, 0.016), position=(BAR_X, ey), color=_C_EN_BG)
        self._en_bar = _ui(scale=(BAR_W, 0.013), position=(BAR_X, ey), color=self._C_EN)
        self._en_val = _txt('100/100', pos=(VAL_X, ey + 0.010), scale=0.76, col=color.white)

        self._gold_txt = _txt('[G] 0G', pos=(LBL_X, BY - 0.022), scale=0.88, col=self._C_GOLD)
        self._buff_txt = _txt('',       pos=(LBL_X, BY - 0.038), scale=0.74, col=_C_BUFF)

        # ── CENTER: Active tool box ────────────────────────────
        self._tool_bord = _ui(scale=(0.262, BH + 0.002), position=(0, BY), color=_C_TBORD)
        self._tool_bg   = _ui(scale=(0.256, BH - 0.004), position=(0, BY),
                              color=color.rgb(28, 18, 48, 230))
        self._tool_lbl  = _txt('ALAT AKTIF', pos=(-0.098, SY - 0.004), scale=0.66, col=_C_LBL)
        self._tool_name = Text('Cangkul', parent=camera.ui,
                               position=(0, BY + 0.010), scale=1.47,
                               color=_C_TOOL, origin=(0, 0))
        self._seed_txt  = Text('',        parent=camera.ui,
                               position=(0, BY - 0.020), scale=1.1,
                               color=_C_SEED, origin=(0, 0))

        # ── RIGHT: Time / Weather / Date / Scene ──────────────
        self._time_txt    = _txt('06:00',          pos=(0.235, BY + 0.034), scale=1.45, col=_C_TIME)
        self._weather_txt = _txt('^ Cerah',         pos=(0.420, BY + 0.030), scale=0.84, col=_C_WTH)
        self._date_txt    = _txt('Hari 1 | Semi',   pos=(0.235, BY + 0.000), scale=0.80, col=_C_DATE)
        self._scene_txt   = _txt('> Kebun',         pos=(0.235, BY - 0.022), scale=0.80, col=_C_SCENE)

        # ── Flash message tengah ───────────────────────────────
        self._flash_bg = _ui(scale=(0.78, 0.068), position=(0, 0.108),
                             color=color.rgb(8, 4, 22, 235))
        self._flash_bg.enabled = False
        self._flash_ent = Text('', parent=camera.ui, position=(0, 0.108),
                               scale=1.75, color=color.rgb(255, 245, 80),
                               origin=(0, 0))
        self._flash_ent.enabled = False

    def _refresh_hud(self):
        s = self.state
        BAR_W = 0.215
        BAR_X = -0.680

        # HP bar
        hp_r = max(0.001, s.hp / max(s.max_hp, 1))
        self._hp_bar.scale_x = BAR_W * hp_r
        self._hp_bar.x = BAR_X - BAR_W / 2 * (1 - hp_r)
        if hp_r > 0.6:
            self._hp_bar.color = color.rgb(55, 210, 80)
        elif hp_r > 0.3:
            self._hp_bar.color = color.rgb(255, 170, 30)
        else:
            self._hp_bar.color = self._C_HP
        self._hp_val.text = f'{int(s.hp)}/{s.max_hp}'

        # EN bar
        en_r = max(0.001, s.energy / max(s.max_energy, 1))
        self._en_bar.scale_x = BAR_W * en_r
        self._en_bar.x = BAR_X - BAR_W / 2 * (1 - en_r)
        self._en_bar.color = color.rgb(220, 80, 55) if en_r <= 0.3 else self._C_EN
        self._en_val.text = f'{int(s.energy)}/{s.max_energy}'

        # Gold + buff
        self._gold_txt.text = f'[G] {s.gold}G'
        self._buff_txt.text = '+'.join(b.upper() for b in s.buffs) if s.buffs else ''

        # Active tool name
        self._tool_name.text = self._TOOL_NAMES[min(s.tool_index, len(self._TOOL_NAMES) - 1)]

        # Seed hint (shown when Tanam/Panen active)
        if s.tool_index in (2, 3):
            seed_name = CROPS.get(s.seed_key, {}).get('name', s.seed_key)
            seed_qty  = s.inventory.get(s.seed_key + '_seed', 0)
            self._seed_txt.text = f'Q/R: {seed_name} x{seed_qty}'
        else:
            self._seed_txt.text = '[1-8] pilih alat'

        # Time / weather
        self._time_txt.text = s.get_time_str()
        w_icons = {'Cerah': '^', 'Hujan': '~', 'Badai': '!', 'Mendung': '-', 'Berangin': '='}
        self._weather_txt.text = f"{w_icons.get(s.weather, '?')} {s.weather}"

        # Date / scene
        season_n = SEASON_NAMES[s.season_index]
        self._date_txt.text = f'Hari {s.day_in_season} | {season_n} Thn {s.year}'
        from .scenes import SCENES
        sc_display = SCENES.get(s.scene_name,
                     type('o', (object,), {'display': s.scene_name})()).display
        self._scene_txt.text = f'> {sc_display}'

    # ─── PUBLIC: FLASH MESSAGE ───────────────────────────
    def flash_msg(self, text: str, duration: float = 1.2):
        if self._flash_ent:
            self._flash_ent.text    = text
            self._flash_ent.enabled = True
            if hasattr(self, '_flash_bg'):
                self._flash_bg.enabled = True
            self._flash_t           = duration

    def show_message(self, text: str, duration: float = 2.0):
        self.flash_msg(text, duration)

    # ─── PUBLIC: DIALOG ──────────────────────────────────
    def _build_dialog_box(self):
        # Background kotak dialog
        self._dlg_bg = _ui(scale=(0.80, 0.22), position=(0, -0.36),
                            color=color.rgb(15, 8, 30, 220))
        self._dlg_border = _ui(scale=(0.82, 0.24), position=(0, -0.36),
                                color=color.rgb(100, 70, 160, 180))
        self._dlg_name = _txt('', pos=(-0.37, -0.27), scale=0.90,
                               col=color.rgb(220, 190, 255))
        self._dlg_text = _txt('', pos=(-0.37, -0.34), scale=0.85,
                               col=color.rgb(230, 220, 255))
        self._dlg_cont = _txt('[E / SPACE: lanjut]', pos=(0.20, -0.44),
                               scale=0.70, col=color.rgb(150, 130, 200))
        self._set_dialog_visible(False)

    def _set_dialog_visible(self, v: bool):
        for e in (self._dlg_bg, self._dlg_border,
                  self._dlg_name, self._dlg_text, self._dlg_cont):
            e.enabled = v

    def start_dialog(self, npc_id: str, state):
        self.state      = state
        self._dialog_npc = npc_id
        self._dialog_idx = 0

        if npc_id == 'mailbox':
            self._dialog_lines = [
                ["Surat dari Paman Arsa:"],
                ["Selamat datang di Lembah Karsa!"],
                ["Rawat kebun, kenali penduduk,"],
                ["dan temukan misteri lembah ini."],
            ]
        else:
            npc_data = _ALL_NPCS.get(npc_id, {})
            dial_idx = state.npc_dialog_index.get(npc_id, 0)
            talks    = npc_data.get('talks', [["..."]])
            self._dialog_lines = [talks[dial_idx % len(talks)]]

        self._show_dialog_line()
        self.mode = 'dialog'

    def _show_dialog_line(self):
        if self._dialog_idx >= len(self._dialog_lines):
            self._end_dialog()
            return
        npc_data = _ALL_NPCS.get(self._dialog_npc, {})
        name     = npc_data.get('name', self._dialog_npc) if self._dialog_npc != 'mailbox' else 'Kotak Pos'
        line     = self._dialog_lines[self._dialog_idx]
        text     = ' '.join(line) if isinstance(line, list) else line
        self._dlg_name.text = name
        self._dlg_text.text = text
        self._set_dialog_visible(True)

    def advance_dialog(self) -> bool:
        """Maju ke baris berikutnya. Return True jika dialog selesai."""
        self._dialog_idx += 1
        if self._dialog_idx >= len(self._dialog_lines):
            self._end_dialog()
            return True
        self._show_dialog_line()
        return False

    def _end_dialog(self):
        # Majukan dialog index NPC
        if self._dialog_npc and self._dialog_npc != 'mailbox':
            s   = self.state
            npc = _ALL_NPCS.get(self._dialog_npc, {})
            idx = s.npc_dialog_index.get(self._dialog_npc, 0)
            s.npc_dialog_index[self._dialog_npc] = idx + 1
            s.npc_hearts[self._dialog_npc] = min(10, s.npc_hearts.get(self._dialog_npc, 0) + 0.1)
        self._set_dialog_visible(False)
        self.mode = 'hud'

    # ─── PUBLIC: PANEL ───────────────────────────────────
    def _build_panel_bg(self):
        self._panel_bg = _ui(scale=(1.5, 1.2), position=(0, 0),
                              color=color.rgb(10, 5, 20, 210))
        self._panel_title = _txt('', pos=(-0.45, 0.44), scale=1.2,
                                  col=color.rgb(220, 190, 255))
        self._panel_body  = _txt('', pos=(-0.45, 0.36), scale=0.80,
                                  col=color.rgb(210, 210, 230))
        self._panel_hint  = _txt('[ESC: tutup]', pos=(-0.45, -0.44), scale=0.75,
                                  col=color.rgb(140, 130, 180))
        self._set_panel_visible(False)

    def _set_panel_visible(self, v: bool):
        for e in (self._panel_bg, self._panel_title,
                  self._panel_body, self._panel_hint):
            e.enabled = v

    def open_panel(self, name: str):
        self._panel_name = name
        self._render_panel(name)
        self._set_panel_visible(True)
        self.mode = 'panel'

    def _render_panel(self, name: str):
        s = self.state
        titles = {
            'inventory': 'Inventori',
            'quest':     'Catatan Quest',
            'map':       'Peta Dunia',
            'relations': 'Hubungan NPC',
            'shop':      'Toko Bu Sari',
            'crafting':  'Bengkel Pak Budi',
            'help':      'Panduan Kontrol',
        }
        self._panel_title.text = titles.get(name, name.capitalize())
        # Update hint sesuai panel
        if name == 'shop':
            self._panel_hint.text = '[1-9: Beli]   [ESC: Tutup]'
        elif name == 'crafting':
            self._panel_hint.text = '[1-5: Pickaxe]   [6-9: Pedang]   [ESC: Tutup]'
        else:
            self._panel_hint.text = '[ESC: tutup]'

        if name == 'inventory':
            lines = [f"Emas: {s.gold}G   HP: {s.hp}/{s.max_hp}   Energi: {s.energy}/{s.max_energy}",
                     f"Pickaxe: Tier {s.pickaxe_tier}   Pedang: {s.sword_id or 'Tidak punya'}", '']
            if s.inventory:
                for item, qty in sorted(s.inventory.items()):
                    if qty > 0:
                        lines.append(f"  {item}: {qty}")
            else:
                lines.append("  (Kosong)")
            self._panel_body.text = '\n'.join(lines[:28])

        elif name == 'quest':
            qs   = s.quest_stage
            lines= []
            for q in QUEST_STAGES:
                mark = '[v]' if q['s'] < qs else ('[>]' if q['s'] == qs else '[ ]')
                lines.append(f" {mark} [{q['s']}] {q['t']}: {q['d']}")
            self._panel_body.text = '\n'.join(lines)

        elif name == 'map':
            cur = s.scene_name
            def _loc(key, label):
                return f'[{label}]' if cur != key else f'>>>{label}<<<'
            lines = [
                '',
                f"  {_loc('mountain','LERENG GUNUNG')}",
                '          |',
                f"  {_loc('farm','KEBUN')}---{_loc('town','DESA')}---{_loc('lake','DANAU')}",
                '              |',
                f"         {_loc('cemetery','KUBURAN')}",
                '              |',
                f"         {_loc('naga_cave','GUA HYANG')}",
                '              |',
                f"         {_loc('dungeon', 'DUNGEON Lv.' + str(s.dungeon_level))}",
                '',
                '  Indoor: [rumah] [warung] [klinik]',
                '          [studio] [bengkel]',
                '',
                f"  Lokasi : {s.scene_name}",
                f"  Hari   : {s.day_in_season} | {self._season_name(s)}  Thn {s.year}",
                f"  Cuaca  : {s.weather}",
            ]
            self._panel_body.text = '\n'.join(lines)

        elif name == 'relations':
            lines = []
            for npc_id in list(_ALL_NPCS.keys()):
                hearts = s.npc_hearts.get(npc_id, 0)
                bar    = '*' * int(hearts) + '-' * (10 - int(hearts))
                name_  = _ALL_NPCS[npc_id].get('name', npc_id)
                lines.append(f"  {name_:15s} {bar[:10]}")
            self._panel_body.text = '\n'.join(lines[:25])

        elif name == 'shop':
            lines = [f"Emas: {s.gold}G   Musim: {self._season_name(s)}", '']
            for i, it in enumerate(SHOP_ITEMS):
                num = i + 1
                lines.append(f"  [{num}] {it['name']:18s}  {it['price']:>4}G   ({it['season']})")
            lines.append('')
            lines.append("Tekan angka untuk beli (kurangi gold).")
            self._panel_body.text = '\n'.join(lines)

        elif name == 'crafting':
            inv = s.inventory
            lines = [
                f"Emas: {s.gold}G   Pickaxe: Tier {s.pickaxe_tier}   "
                f"Pedang: {s.sword_id or '-'}", '',
                "── PICKAXE ──",
            ]
            for i, r in enumerate(PICKAXE_RECIPES):
                need = ', '.join(f"{k}×{v}" for k, v in r['needs'].items())
                got_gold = s.gold >= r['cost_gold']
                got_mat  = all(inv.get(k, 0) >= v for k, v in r['needs'].items())
                already  = s.pickaxe_tier >= r['tier']
                mark = '[v]' if already else ('[o]' if (got_gold and got_mat) else '[ ]')
                lines.append(f"  [{i+1}] {mark} {r['name']:18s}  {r['cost_gold']:>4}G + {need}")
            lines.append('')
            lines.append("── PEDANG ──")
            for i, r in enumerate(SWORD_RECIPES):
                num = i + 6
                need = ', '.join(f"{k}×{v}" for k, v in r['needs'].items())
                got_gold = s.gold >= r['cost_gold']
                got_mat  = all(inv.get(k, 0) >= v for k, v in r['needs'].items())
                already  = s.sword_id == r['id']
                mark = '[v]' if already else ('[o]' if (got_gold and got_mat) else '[ ]')
                lines.append(f"  [{num}] {mark} {r['name']:18s}  {r['cost_gold']:>4}G + {need} (DMG {r['damage']})")
            lines.append('')
            lines.append("[ ]=kurang bahan  [o]=siap  [v]=sudah punya")
            self._panel_body.text = '\n'.join(lines)

        elif name == 'help':
            self._panel_body.text = (
                "── GERAK ──\n"
                "  WASD / Arrow  : Jalan\n"
                "  Shift+WASD    : Lari (pakai energi)\n\n"
                "── AKSI ──\n"
                "  SPACE  : Pakai alat aktif\n"
                "  E      : Bicara/Interaksi NPC\n"
                "  Z      : Serang (butuh pedang)\n"
                "  F      : Tangkap makhluk liar\n"
                "  G      : Beri hadiah ke NPC\n"
                "  V      : Makan item (pulihkan HP/EN)\n"
                "  T      : Tidur (hanya di Rumah)\n\n"
                "── ALAT (angka 1-8) ──\n"
                "  1-CNG  2-SRM  3-TNM  4-PNS\n"
                "  5-KPK  6-HDH  7-PCK  8-PDG\n"
                "  Q/R    : Ganti bibit\n\n"
                "── MENU ──\n"
                "  I: Inventori   M: Peta\n"
                "  J: Quest       H: Relasi NPC\n"
                "  K: Toko (di Warung)  U: Kerajinan (di Bengkel)\n"
                "  F5: Simpan     F9: Muat\n"
                "  ESC: Tutup panel"
            )

    @staticmethod
    def _season_name(s):
        try:
            from .config import SEASON_NAMES
            return SEASON_NAMES[s.season_index]
        except Exception:
            return '-'

    # ─── PANEL ACTIONS (shop/craft) ──────────────────────
    def panel_action(self, idx: int) -> str:
        """Dipanggil dari app.input() saat user tekan angka di panel.
        idx 1-based. Return pesan untuk flash_msg."""
        if self._panel_name == 'shop':
            return self._buy_shop_item(idx)
        elif self._panel_name == 'crafting':
            return self._craft_item(idx)
        return ''

    def _buy_shop_item(self, idx: int) -> str:
        s = self.state
        if not (1 <= idx <= len(SHOP_ITEMS)):
            return ''
        it = SHOP_ITEMS[idx - 1]
        if s.gold < it['price']:
            return f"Gold kurang ({it['price']}G)."
        s.gold -= it['price']
        s.inventory[it['id']] = s.inventory.get(it['id'], 0) + 1
        if not s.shop_unlocked:
            s.shop_unlocked = True
        self._render_panel('shop')   # refresh tampilan
        return f"Beli {it['name']} -{it['price']}G"

    def _craft_item(self, idx: int) -> str:
        s = self.state
        # 1-5 = pickaxe, 6-9 = sword
        if 1 <= idx <= len(PICKAXE_RECIPES):
            r = PICKAXE_RECIPES[idx - 1]
            if s.pickaxe_tier >= r['tier']:
                return "Sudah punya tier ini atau lebih."
            return self._do_craft(r, set_pickaxe=r['tier'])
        si = idx - len(PICKAXE_RECIPES) - 1   # 6→0, 7→1, …
        if 0 <= si < len(SWORD_RECIPES):
            r = SWORD_RECIPES[si]
            if s.sword_id == r['id']:
                return "Sudah punya pedang ini."
            return self._do_craft(r, set_sword=r['id'])
        return ''

    def _do_craft(self, r: dict, set_pickaxe: int = None, set_sword: str = None) -> str:
        s = self.state
        if s.gold < r['cost_gold']:
            return f"Gold kurang ({r['cost_gold']}G)."
        for k, v in r['needs'].items():
            if s.inventory.get(k, 0) < v:
                return f"Bahan kurang: butuh {k}×{v}."
        # Konsumsi
        s.gold -= r['cost_gold']
        for k, v in r['needs'].items():
            s.inventory[k] -= v
        if set_pickaxe is not None:
            s.pickaxe_tier = set_pickaxe
        if set_sword is not None:
            s.sword_id = set_sword
        self._render_panel('crafting')
        return f"Berhasil membuat {r['name']}!"

    def close_all(self):
        self._set_dialog_visible(False)
        self._set_panel_visible(False)
        self._panel_name = None
        self.mode = 'hud'
