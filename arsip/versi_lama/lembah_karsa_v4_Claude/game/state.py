"""
state.py — GameState dataclass dan save/load logic.
"""
import json
import os
from dataclasses import dataclass, field
from .config import SAVE_FILE, START_GOLD, START_ENERGY, SEASONS, SEASON_NAMES, TILE


@dataclass
class GameState:
    # Lokasi player (smooth movement: pixel float)
    scene_name: str = 'outdoor'
    player_x: float = 5.0          # tile coords (float untuk smooth)
    player_y: float = 7.0
    target_tile_x: int = 5         # target tile saat moving
    target_tile_y: int = 7
    facing: str = 'down'

    # Waktu
    day: int = 1
    year: int = 1
    day_in_season: int = 1
    season_index: int = 0
    time_minutes: float = 360.0    # 6:00
    weather: str = 'Cerah'

    # Stats
    energy: int = START_ENERGY
    max_energy: int = START_ENERGY
    gold: int = START_GOLD
    tool_index: int = 0
    seed_key: str = 'lobak'

    # Inventory & soil
    inventory: dict = field(default_factory=lambda: {'lobak_seed': 3})
    soil: dict = field(default_factory=dict)

    # NPC
    npc_hearts: dict = field(default_factory=dict)
    npc_dialog_index: dict = field(default_factory=dict)
    npc_positions: dict = field(default_factory=dict)  # {npc_id: {scene,x,y,activity}}

    # Wild entities (list of dicts)
    wild_entities: list = field(default_factory=list)

    # Upgrades
    upgrades: dict = field(default_factory=lambda: {
        'hoe': False, 'water': False, 'bag': False, 'axe': False
    })

    # Quest & flags
    quest_stage: int = 0
    mail_read: bool = False
    shop_unlocked: bool = False
    greenhouse_open: bool = False
    met_jin: bool = False
    captured_supernatural: int = 0

    # Stats counter
    stats: dict = field(default_factory=lambda: {
        'lobak_planted': 0, 'watered': 0, 'lobak_harvested': 0,
        'corn_harvested': 0, 'earned': 0, 'gifts': 0,
        'seasons_harvested': [],
    })

    # ─── Convenience getters ───
    def get_season(self):
        return SEASONS[self.season_index]

    def get_season_name(self):
        return SEASON_NAMES[self.get_season()]

    def get_time_str(self):
        h = int(self.time_minutes // 60) % 24
        mi = int(self.time_minutes % 60)
        return f"{h:02d}:{mi:02d}"

    def get_hour(self):
        return int(self.time_minutes // 60) % 24

    def is_night(self):
        h = self.get_hour()
        return h < 5 or h >= 19

    def get_player_tile(self):
        """Posisi player di tile (integer)."""
        return (int(round(self.player_x)), int(round(self.player_y)))

    # ─── Persistence ───
    def save(self):
        try:
            data = {k: v for k, v in self.__dict__.items()}
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False

    @classmethod
    def load(cls):
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            gs = cls()
            for k, v in data.items():
                if hasattr(gs, k):
                    setattr(gs, k, v)
            return gs
        except Exception as e:
            print(f"Load error: {e}")
            return None
