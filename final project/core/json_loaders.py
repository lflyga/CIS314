"""
Author: L. Flygare
Description: provides helper functions for loading the projects json data and converting it into internal python 
             objects (Monster and Move)
"""

import json
from pathlib import Path
from typing import Dict, List

from .models import Monster, Move

#-----------------------------
# paths
#-----------------------------

#project root (folder above /core)
ROOT = Path(__file__).resolve().parents[1]

#directory where pokeapi_loader.py stores its output json files
DATA_DIR = ROOT / "data"

def load_monsters_json(path: str | None = None) -> Dict[str, Monster]:
    """
    load monsters.json and return a dict mapping
        { "#001": Monster(...), "#002": Monster(...), ... }
    """
    p = Path(path) if path else DATA_DIR / "monsters.json"
    raw = json.loads(p.read_text(encoding = "utf-8"))

    monsters: Dict[str, Monster] = {}
    for dex, data in raw.items():
        monsters[dex] = Monster(
            dex = data["dex"], 
            name = data["name"], 
            type1 = data["type1"], 
            type2 = data.get("type2"),      #may be None
            sprite = data.get("sprite"),    #includes pokeapie sprite url
            hp = data["hp"], 
            atk = data["atk"], 
            dfn = data["dfn"], 
            sp_atk = data["sp_atk"], 
            sp_dfn = data["sp_dfn"], 
            speed = data["speed"], 
        )
    return monsters

def load_moves_json(path: str | None = None) -> Dict[str, Move]:
    """
    load moves.json and returns a dict mapping
        { "Thunderbolt": Move(...), "Ember": Move(...), ... }
    """
    p = Path(path) if path else DATA_DIR / "moves.json"
    raw = json.loads(p.read_text(encoding = "utf-8"))

    moves: Dict[str, Move] = {}
    for name, data in raw.items():
        moves[name] = Move(
            name = data["name"], 
            type = data["type"], 
            power = data["power"], 
            accuracy = data["accuracy"], 
            pp = data["pp"], 
        )
    return moves

def load_move_learners_json(path: str | None = None) -> Dict[str, List[str]]:
    """
    load move_learners.json and returns a dict mapping
        { "#001": ["Growl", "Tackle", "Vine Whip", ...], ... }
    """
    p = Path(path) if path else DATA_DIR / "move_learners.json"
    raw = json.loads(p.read_text(encoding = "utf-8"))

