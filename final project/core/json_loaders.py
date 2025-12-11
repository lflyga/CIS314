"""
Author: L. Flygare
Description: 
"""

import json
from pathlib import Path
from typing import Dict, List

from .models import Monster, Move

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"

def load_monsters_json(path: str | None = None) -> Dict[str, Monster]:
    """
    returns {dex_str: Monster}
    """
    p = Path(path) if path else DATA_DIR / "monsters.json"
    raw = json.loads(p.read_text(encoding = "utf-8"))

    monsters: Dict[str, Monster] = {}
    for dex, data in raw.items():
        monsters[dex] = Monster(
            dex = data["dex"], 
            name = data["name"], 
            type1 = data["type1"], 
            type2 = data.get("type2"), 
            hp = data["hp"], 
            atk = data["atk"], 
            dfn = data["dfn"], 
            sp_atk = data["sp_atk"], 
            sp_dfn = data["sp_atk"], 
            speed = data["speed"], 
        )
    return monsters

def load_moves_json(path: str | None = None) -> Dict[str, Move]:
    """
    returns {move_name: Move}
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
    returns {dex_str: [move_name, ...]}
    """
    p = Path(path) if path else DATA_DIR / "move_learners.json"
    raw = json.loads(p.read_text(encoding = "utf-8"))

    