"""state.py — GameState + save/load."""
import json
import os
from dataclasses import dataclass, field
from .config import SAVE_FILE, START_GOLD, START_ENERGY, SEASONS, SEASON_NAMES, PLAYER_BASE_HP


@dataclass
class GameState:
    scene_name: str = 'farm'
    player_x: float = 8.0
    player_y: float = 8.0
    facing: str = 'down'

    day: int = 1
    year: int = 1
    day_in_season: int = 1
    season_index: int = 0
    time_minutes: float = 360.0
    weather: str = 'Cerah'

    energy: int = START_ENERGY
    max_energy: int = START_ENERGY
    gold: int = START_GOLD
    tool_index: int = 0
    seed_key: str = 'lobak'

    # Combat
    hp: int = PLAYER_BASE_HP
    max_hp: int = PLAYER_BASE_HP
    invuln_timer_ms: float = 0.0  # invuln frame setelah kena hit

    # Crafting tier
    pickaxe_tier: int = 0   # 0 = belum punya
    sword_id: str = ''      # '' = belum punya, atau 'sword_kayu' dst

    inventory: dict = field(default_factory=lambda: {'lobak_seed': 3})
    soil: dict = field(default_factory=dict)
    npc_hearts: dict = field(default_factory=dict)
    npc_dialog_index: dict = field(default_factory=dict)
    npc_positions: dict = field(default_factory=dict)
    wild_entities: list = field(default_factory=list)

    # Mob (combat entities di dungeon)
    mobs: list = field(default_factory=list)
    # Format: [{'kind','x','y','hp','target_x','target_y','speed','damage','dmg_flash_ms'}]

    # Dungeon
    dungeon_level: int = 0  # 0 = belum di dungeon. 1-15 saat di dalam
    dungeon_tiles: list = field(default_factory=list)  # 2D list saat di dungeon
    dungeon_seed: int = 0  # seed untuk regenerate

    # Naga boss state
    naga_defeated: bool = False
    naga_fountain_used_today: bool = False  # batas ambil air sekali sehari

    upgrades: dict = field(default_factory=lambda: {
        'hoe': False, 'water': False, 'bag': False, 'axe': False
    })

    quest_stage: int = 0
    mail_read: bool = False
    shop_unlocked: bool = False
    greenhouse_open: bool = False
    met_jin: bool = False
    captured_supernatural: int = 0

    stats: dict = field(default_factory=lambda: {
        'lobak_planted':0,'watered':0,'lobak_harvested':0,'corn_harvested':0,
        'earned':0,'gifts':0,'mobs_killed':0,'minerals_mined':0,'deepest_level':0,
        'seasons_harvested':[],
    })

    def get_season(self): return SEASONS[self.season_index]
    def get_season_name(self): return SEASON_NAMES[self.season_index]
    def get_time_str(self): return f"{int(self.time_minutes // 60) % 24:02d}:{int(self.time_minutes % 60):02d}"
    def get_hour(self): return int(self.time_minutes // 60) % 24
    def is_night(self): return self.get_hour() < 5 or self.get_hour() >= 19
    def get_player_tile(self): return (int(round(self.player_x)), int(round(self.player_y)))

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
        if not os.path.exists(SAVE_FILE): return None
        try:
            with open(SAVE_FILE) as f:
                data = json.load(f)
            gs = cls()
            for k, v in data.items():
                if hasattr(gs, k): setattr(gs, k, v)
            return gs
        except Exception as e:
            print(f"Load error: {e}")
            return None
