"""
panels.py — UI panels yang dibuka via hotkey (I/M/J/H/K/U/F1).
Setiap panel adalah fungsi render yang dipanggil dari Game.
"""
import pygame
from .config import C, SCREEN_W, SCREEN_H, SEASONS, TOOLS
from .data import (CROPS, WILD_ITEMS, HUMAN_NPCS, SUPERNATURAL_NPCS,
                   ANIMAL_NPCS, QUEST_STAGES)
from .scenes import SCENES
from .config import (G, D, P, W, TR, DT, H, GR, LN, FN, GT)


def render_panel_inventory(game, bx, by, bw, bh):
    """Tampilkan inventori, dikelompokkan per kategori."""
    title = game.font_big.render("📦 INVENTORI (I tutup)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    y = by + 60

    seeds, crops_list, wilds, animals, others = [], [], [], [], []
    for k, v in game.state.inventory.items():
        if v <= 0 or k.endswith('_today'):
            continue
        if k.endswith('_seed'):
            base = k[:-5]
            seeds.append(f"{CROPS.get(base, {}).get('name', base)} (benih) x{v}")
        elif k in CROPS:
            crops_list.append(f"{CROPS[k]['name']} x{v}")
        elif k in WILD_ITEMS:
            wilds.append(f"{WILD_ITEMS[k]['name']} x{v}")
        elif k in ['susu', 'telur', 'wol']:
            animals.append(f"{k.title()} x{v}")
        else:
            others.append(f"{k} x{v}")

    sections = [
        ("🌱 BENIH:", seeds, C.ui_green),
        ("🌾 PANEN:", crops_list, C.ui_gold),
        ("✨ LIAR:", wilds, C.ui_cyan),
        ("🐄 TERNAK:", animals, C.ui_text),
        ("📦 LAIN:", others, (180, 180, 180)),
    ]
    for sect, items, col in sections:
        if not items: continue
        t = game.font.render(sect, True, col)
        game.screen.blit(t, (bx + 20, y))
        y += 22
        for item in items:
            t = game.font_small.render(f"  {item}", True, C.ui_text)
            game.screen.blit(t, (bx + 30, y))
            y += 16


def render_panel_map(game, bx, by, bw, bh):
    """Mini-map peta outdoor."""
    title = game.font_big.render("🗺 PETA (M tutup)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    scene = SCENES['outdoor']
    mw, mh = 240, 180
    mx = bx + 20; my = by + 60
    sx = mw / scene.w; sy = mh / scene.h
    pygame.draw.rect(game.screen, (40, 30, 55), (mx, my, mw, mh))

    color_map = {
        G: (60, 120, 60), D: (100, 70, 40), P: (140, 140, 140),
        W: (60, 120, 200), TR: (40, 80, 40), DT: (60, 40, 30),
        H: (180, 80, 60), GR: (90, 80, 80), LN: (200, 180, 60),
        FN: (110, 80, 40), GT: (200, 180, 80),
    }
    for ty in range(scene.h):
        for tx in range(scene.w):
            t = scene.tiles[ty][tx]
            col = color_map.get(t)
            if col:
                pygame.draw.rect(game.screen, col,
                    (mx + tx*sx, my + ty*sy, max(1, sx), max(1, sy)))

    # Player marker
    if game.state.scene_name == 'outdoor':
        pygame.draw.circle(game.screen, (255, 255, 80),
            (int(mx + game.state.player_x * sx), int(my + game.state.player_y * sy)), 3)

    # Legend
    ly = by + 60
    legend = [
        ("🟩 Rumput", (60, 120, 60)),
        ("🟨 Jalan", (140, 140, 140)),
        ("🟫 Tanah", (100, 70, 40)),
        ("🟦 Air", (60, 120, 200)),
        ("🌳 Pohon", (40, 80, 40)),
        ("🏠 Bangunan", (180, 80, 60)),
        ("🪦 Kuburan", (90, 80, 80)),
        ("🏮 Pasar Malam", (200, 180, 60)),
        ("🚪 Gerbang", (200, 180, 80)),
    ]
    for label, col in legend:
        pygame.draw.rect(game.screen, col, (bx + 280, ly, 12, 12))
        t = game.font_small.render(label, True, C.ui_text)
        game.screen.blit(t, (bx + 295, ly - 1))
        ly += 18


def render_panel_quest(game, bx, by, bw, bh):
    title = game.font_big.render("📋 QUEST LOG (J tutup)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    y = by + 60
    for i, stage in enumerate(QUEST_STAGES):
        if i < game.state.quest_stage:
            col = C.ui_green; mark = "✓"
        elif i == game.state.quest_stage:
            col = C.ui_gold; mark = "▶"
        else:
            col = (100, 80, 140); mark = " "
        t = game.font_small.render(f"{mark} {stage['t']}: {stage['d']}", True, col)
        game.screen.blit(t, (bx + 20, y))
        y += 18

    y += 20
    s = game.state.stats
    lines = [
        f"Lobak: tanam {s['lobak_planted']}/3, panen {s['lobak_harvested']}/3",
        f"Penghasilan: {s['earned']}G",
        f"Hadiah: {s['gifts']}",
        f"Tangkap halus: {game.state.captured_supernatural}",
        f"Bertemu Jin: {'✓' if game.state.met_jin else '✗'}",
    ]
    for line in lines:
        t = game.font_small.render(line, True, C.ui_cyan)
        game.screen.blit(t, (bx + 20, y))
        y += 16


def render_panel_relations(game, bx, by, bw, bh):
    title = game.font_big.render("💕 HUBUNGAN (H tutup)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    y = by + 60

    for section_label, npcs, col in [
        ("👤 MANUSIA:", HUMAN_NPCS, C.ui_text),
        ("✨ SUPERNATURAL:", SUPERNATURAL_NPCS, C.ui_cyan),
        ("🐄 HEWAN TERNAK:", ANIMAL_NPCS, (220, 180, 140)),
    ]:
        t = game.font.render(section_label, True, col)
        game.screen.blit(t, (bx + 20, y))
        y += 22
        for npc_id, data in npcs.items():
            hearts = game.state.npc_hearts.get(npc_id, 0)
            heart_str = "❤"*(hearts//2) + "♡"*((10-hearts)//2)
            pos = game.state.npc_positions.get(npc_id, {})
            act = pos.get('activity', '?')
            t = game.font_small.render(f"  {data['name']}: {heart_str} ({act})", True, C.ui_text)
            game.screen.blit(t, (bx + 30, y))
            y += 16
        y += 4


def render_panel_help(game, bx, by, bw, bh):
    title = game.font_big.render("⌨️ KONTROL (F1/ESC tutup)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    y = by + 50
    controls = [
        "WASD/Arrow  → Gerak (smooth)",
        "SHIFT       → Lari (1.7×)",
        "SPACE       → Pakai alat",
        "E           → Interaksi/Bicara",
        "1-6         → Pilih alat",
        "Q/R         → Ganti benih",
        "F           → Tangkap makhluk halus",
        "G           → Lihat jadwal NPC",
        "T           → Tidur (di rumah)",
        "I/M/J/H     → Inv/Peta/Quest/Hubungan",
        "K/U         → Toko/Upgrade (di lokasi)",
        "F5/F9       → Save/Load",
        "F1/ESC      → Bantuan ini",
    ]
    for line in controls:
        t = game.font_small.render(line, True, C.ui_text)
        game.screen.blit(t, (bx + 20, y))
        y += 16


def build_shop_items(state):
    """Bangun list item di toko untuk musim ini."""
    items = []
    szn = state.get_season()
    for crop_id, crop in CROPS.items():
        if szn in crop['seasons'] or state.greenhouse_open:
            cost = crop['cost'] * 3
            items.append((f"{crop['name']} x3 = {cost}G", ('buy_seed', crop_id, cost)))
    items.append(("💰 Jual semua panen", ('sell_all', None, None)))
    items.append(("❌ Tutup (ESC)", ('close', None, None)))
    return items


def build_upgrade_items(state):
    items = []
    upgrades = [
        ('hoe', 80, 'Cangkul Baja'),
        ('water', 120, 'Penyiram Perunggu'),
        ('bag', 60, 'Tas Besar (+20 nrg)'),
        ('axe', 50, 'Kapak Besi'),
    ]
    for upg_id, cost, label in upgrades:
        if state.upgrades.get(upg_id, False):
            items.append((f"✅ {label}", ('owned', None, None)))
        else:
            items.append((f"{label} - {cost}G", ('buy_upgrade', upg_id, cost)))
    items.append(("❌ Tutup (ESC)", ('close', None, None)))
    return items


def render_panel_shop(game, bx, by, bw, bh):
    title = game.font_big.render(f"🏪 WARUNG ({game.state.gold}G)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    items = build_shop_items(game.state)
    y = by + 60
    for i, (label, _) in enumerate(items):
        if i == game.panel_select:
            pygame.draw.rect(game.screen, (60, 30, 100), (bx + 10, y - 3, bw - 20, 24))
            arrow = game.font.render("▶", True, C.ui_gold)
            game.screen.blit(arrow, (bx + 15, y))
        col = C.ui_gold if i == game.panel_select else C.ui_text
        t = game.font.render(label, True, col)
        game.screen.blit(t, (bx + 35, y))
        y += 28


def render_panel_upgrade(game, bx, by, bw, bh):
    title = game.font_big.render(f"⚒️ BENGKEL ({game.state.gold}G)", True, C.ui_gold)
    game.screen.blit(title, (bx + 20, by + 15))
    items = build_upgrade_items(game.state)
    y = by + 60
    for i, (label, _) in enumerate(items):
        if i == game.panel_select:
            pygame.draw.rect(game.screen, (60, 30, 100), (bx + 10, y - 3, bw - 20, 24))
            arrow = game.font.render("▶", True, C.ui_gold)
            game.screen.blit(arrow, (bx + 15, y))
        col = C.ui_gold if i == game.panel_select else C.ui_text
        t = game.font.render(label, True, col)
        game.screen.blit(t, (bx + 35, y))
        y += 28
