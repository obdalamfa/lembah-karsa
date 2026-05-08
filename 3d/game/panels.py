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
from ursina import (Entity, Text, Button, color, camera, destroy,
                    Vec2, Vec4, invoke)

from .config import TOOLS, SEASON_NAMES
from .data import CROPS
from .data import (HUMAN_NPCS, SUPERNATURAL_NPCS, ANIMAL_NPCS,
                   QUEST_STAGES, SWORD_RECIPES, PICKAXE_RECIPES, SHOP_ITEMS)

_ALL_NPCS = {**HUMAN_NPCS, **SUPERNATURAL_NPCS, **ANIMAL_NPCS}


def _ui(model='quad', **kw):
    return Entity(parent=camera.ui, model=model, **kw)


def _txt(text='', pos=(0, 0), scale=1.0, col=color.white, **kw):
    return Text(text, parent=camera.ui, position=pos,
                scale=scale, color=col, **kw)


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

    # ─── PUBLIC: HUD ─────────────────────────────────────
    def _build_hud(self):
        s = self.state
        x0, y0 = -0.86, 0.46   # posisikan sedikit lebih ke tengah

        # Background strip kiri lebih gelap dan rapi
        self._hud_bg = _ui(scale=(0.35, 0.25), position=(-0.72, 0.36),
                           color=color.rgba(15, 15, 25, 200))

        # HP bar label + bar
        self._hp_lbl = _txt('HP', pos=(x0, y0), scale=1.0,
                             col=color.rgb(255, 120, 120))
        self._hp_bg  = _ui(scale=(0.22, 0.025), position=(x0+0.15, y0+0.004),
                            color=color.rgba(40, 5, 5, 200))
        self._hp_bar = _ui(scale=(0.22, 0.022), position=(x0+0.15, y0+0.004),
                            color=color.rgb(240, 60, 60))

        # Energy bar
        self._en_lbl = _txt('EN', pos=(x0, y0-0.04), scale=1.0,
                             col=color.rgb(120, 230, 255))
        self._en_bg  = _ui(scale=(0.22, 0.025), position=(x0+0.15, y0-0.036),
                            color=color.rgba(5, 30, 40, 200))
        self._en_bar = _ui(scale=(0.22, 0.022), position=(x0+0.15, y0-0.036),
                            color=color.rgb(60, 190, 255))

        # Gold
        self._gold_txt = _txt('100G', pos=(x0, y0-0.08), scale=1.1,
                               col=color.rgb(240, 210, 80))

        # Tool + seed
        self._tool_txt = _txt('Cangkul', pos=(x0, y0-0.12), scale=0.9,
                               col=color.rgb(200, 200, 200))
        self._seed_txt = _txt('Lobak', pos=(x0, y0-0.16), scale=0.9,
                               col=color.rgb(150, 255, 150))

        # Waktu / tanggal (kanan atas)
        self._time_txt = _txt('06:00', pos=(0.60, 0.47), scale=1.1,
                               col=color.white)
        self._date_txt = _txt('Hari 1 | Semi', pos=(0.55, 0.44), scale=0.85,
                               col=color.rgb(200, 220, 255))
        self._scene_txt= _txt('Kebun Paman Arsa', pos=(0.40, 0.41), scale=0.75,
                               col=color.rgb(180, 255, 180))
        self._weather_txt=_txt('Cerah', pos=(0.68, 0.44), scale=0.75,
                               col=color.rgb(220, 220, 100))

        # Kontrol mini (pojok kanan bawah)
        hints = ("WASD:Gerak  SHIFT:Lari  SPACE:Alat\n"
                 "E:Bicara  G:Hadiah  Z:Serang  F:Tangkap\n"
                 "1-8:Alat  Q/R:Benih  I/J/M/H:Panel\n"
                 "K:Toko(shop)  U:Bengkel(smith)\n"
                 "F5:Simpan  F9:Muat  T:Tidur(rumah)")
        self._hint_txt = _txt(hints, pos=(0.05, -0.41), scale=0.60,
                               col=color.rgba(200, 200, 200, 160))

        # Flash message (tengah bawah)
        self._flash_ent = _txt('', pos=(0, -0.35), scale=1.1,
                                col=color.rgb(255, 240, 100))
        self._flash_ent.enabled = False

    def _refresh_hud(self):
        s = self.state

        # HP bar
        hp_r = max(0.001, s.hp / max(s.max_hp, 1))
        self._hp_bar.scale_x = 0.22 * hp_r
        self._hp_bar.x = -0.86 + 0.15 - 0.11 * (1 - hp_r)
        self._hp_lbl.text = f'HP {s.hp}/{s.max_hp}'

        # Energy bar
        en_r = max(0.001, s.energy / max(s.max_energy, 1))
        self._en_bar.scale_x = 0.22 * en_r
        self._en_bar.x = -0.86 + 0.15 - 0.11 * (1 - en_r)
        self._en_lbl.text = f'EN {s.energy}/{s.max_energy}'

        # Gold
        self._gold_txt.text = f'Emas: {s.gold}G'

        # Tool + seed
        tool_name = TOOLS[s.tool_index] if s.tool_index < len(TOOLS) else '?'
        self._tool_txt.text = f'[{s.tool_index+1}] {tool_name}'
        seed_name = CROPS.get(s.seed_key, {}).get('name', s.seed_key)
        self._seed_txt.text = f'Benih: {seed_name}'

        # Waktu & tanggal
        self._time_txt.text  = s.get_time_str()
        season_n = SEASON_NAMES[s.season_index]
        self._date_txt.text  = f'Hari {s.day_in_season} | {season_n}'
        from .scenes import SCENES
        sc_display = SCENES.get(s.scene_name, type('o',(object,),{'display':s.scene_name})()).display
        self._scene_txt.text = sc_display
        self._weather_txt.text = s.weather

    # ─── PUBLIC: FLASH MESSAGE ───────────────────────────
    def flash_msg(self, text: str, duration: float = 1.2):
        if self._flash_ent:
            self._flash_ent.text    = text
            self._flash_ent.enabled = True
            self._flash_t           = duration

    def show_message(self, text: str, duration: float = 2.0):
        self.flash_msg(text, duration)

    # ─── PUBLIC: DIALOG ──────────────────────────────────
    def _build_dialog_box(self):
        # Background kotak dialog
        self._dlg_bg = _ui(scale=(0.80, 0.22), position=(0, -0.36),
                            color=color.rgba(15, 8, 30, 220))
        self._dlg_border = _ui(scale=(0.82, 0.24), position=(0, -0.36),
                                color=color.rgba(100, 70, 160, 180))
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
                              color=color.rgba(10, 5, 20, 210))
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
                mark = '✓' if q['s'] < qs else ('►' if q['s'] == qs else ' ')
                lines.append(f" {mark} [{q['s']}] {q['t']}: {q['d']}")
            self._panel_body.text = '\n'.join(lines)

        elif name == 'map':
            scenes_list = [
                'farm→Kebun Paman Arsa', 'town→Desa Karsa',
                'mountain→Lereng Gunung', 'lake→Danau Karsa',
                'cemetery→Kuburan Tua', 'naga_cave→Gua Sang Hyang',
                'dungeon→Gua Bertingkat (roguelike)',
                '', f'Posisi saat ini: {s.scene_name}',
                f'Kedalaman dungeon: Level {s.dungeon_level}',
            ]
            self._panel_body.text = '\n'.join(scenes_list)

        elif name == 'relations':
            lines = []
            for npc_id in list(_ALL_NPCS.keys()):
                hearts = s.npc_hearts.get(npc_id, 0)
                bar    = '♥' * int(hearts) + '♡' * (10 - int(hearts))
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
                mark = '✓' if already else ('●' if (got_gold and got_mat) else '○')
                lines.append(f"  [{i+1}] {mark} {r['name']:18s}  {r['cost_gold']:>4}G + {need}")
            lines.append('')
            lines.append("── PEDANG ──")
            for i, r in enumerate(SWORD_RECIPES):
                num = i + 6
                need = ', '.join(f"{k}×{v}" for k, v in r['needs'].items())
                got_gold = s.gold >= r['cost_gold']
                got_mat  = all(inv.get(k, 0) >= v for k, v in r['needs'].items())
                already  = s.sword_id == r['id']
                mark = '✓' if already else ('●' if (got_gold and got_mat) else '○')
                lines.append(f"  [{num}] {mark} {r['name']:18s}  {r['cost_gold']:>4}G + {need} (DMG {r['damage']})")
            lines.append('')
            lines.append("○=kurang bahan  ●=siap  ✓=sudah punya")
            self._panel_body.text = '\n'.join(lines)

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
