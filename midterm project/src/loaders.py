"""
Author: L. Flygare
Description: handles all parsing and loading of data files into usable Python objects
            -converts plaintext data and JSON mappings into dictionaries of Monster and Move instances
"""

import json
import re
from typing import Dict, List, Optional, Tuple  #for type hints for easier readabilty and understanding expected outputs
from .models import Move, Monster
 
#========================
#regex for parsing text-based data from the data folder for monsters and moves
#========================

#matches lines like: "Monster: #004 ..." (hash style)
#Monster: #004 Charmander | Type: Fire | HP: 39 | ATK: 52 | DEF: 43 | SP.ATK: 60 | SP.DEF: 50 | SPD: 65
CRE_RE_NUM = re.compile(
    r"^Monster:\s*#(?P<dex>\d{3})\s+(?P<name>[^|]+)\s*\|\s*Type:\s*(?P<types>[^|]+)\s*\|"
    r"\s*HP:\s*(?P<hp>\d+)\s*\|\s*ATK:\s*(?P<atk>\d+)\s*\|\s*DEF:\s*(?P<dfn>\d+)\s*\|"
    r"\s*SP\.ATK:\s*(?P<spa>\d+)\s*\|\s*SP\.DEF:\s*(?P<spd>\d+)\s*\|\s*SPD:\s*(?P<spe>\d+)\s*$"
)

#matches line like: "Monster: No.004 ..." (No. style)
#Monster: No.004 Charmander | Type: Fire | HP: 39 | ATK: 52 | ... (same as above example)
#the two compiled regexes are OR'd together when matching
CRE_RE_NO = re.compile(
    r"^Monster:\s*No\.(?P<dex>\d{3})\s+(?P<name>[^|]+)\s*\|\s*Type:\s*(?P<types>[^|]+)\s*\|"
    r"\s*HP:\s*(?P<hp>\d+)\s*\|\s*ATK:\s*(?P<atk>\d+)\s*\|\s*DEF:\s*(?P<dfn>\d+)\s*\|"
    r"\s*SP\.ATK:\s*(?P<spa>\d+)\s*\|\s*SP\.DEF:\s*(?P<spd>\d+)\s*\|\s*SPD:\s*(?P<spe>\d+)\s*$"
)

#matches lines like:
#Move: Ember | Type: Fire | Cat: Special | Power: 40 | Acc: 100 | PP: 25 | Effect: May burn target.
MOVE_RE = re.compile(
    r"^Move:\s*(?P<name>[^|]+)\|\s*Type:\s*(?P<type>[^|]+)\|\s*Cat:\s*(?P<cat>[^|]+)\|"
    r"\s*Power:\s*(?P<power>[^|]+)\|\s*Acc:\s*(?P<acc>[^|]+)\|\s*PP:\s*(?P<pp>[^|]+)\|\s*Effect:\s*(?P<effect>.+)$"
)

#========================
#helper functions (only used in this module)
#leading '_' denotes that it is only meant to be used in this module and not be called by other modules
#========================

def _split_types(s: str) -> Tuple[str, Optional[str]]:   #returns at least one type for every pokemon
    """splits a type string like 'grass/poison' -> ('grass', 'poison')"""
    parts = [p.strip() for p in s.split("/")]
    return (parts[0], parts[1]) if len(parts) > 1 else (parts[0], None)

#unicode dashes were causing errors
def _opt_int(s: str):
    """
    Return int(s) if s is digits; otherwise None (handles '—', '–', '-', '').
    used for Move.power
    """
    s = s.strip().replace("—", "-").replace("–", "-")
    return int(s) if s.isdigit() else None

#needed to be able to parse the infinity symbol in acc which is not used in power
def _opt_acc(s: str):
    """
    return None for always hit moves ('—', '–', '-', '', '∞'), else an int percent
    no interpretation of None done here, handled in battle loop in battle.py
    """
    s = s.strip().lower().replace("—", "-").replace("–", "-")
    if s in {"-", "", "∞"}:
        return None
    return int(s)


#========================
#loading functions
#========================

def load_monsters(path: str) -> Dict[str, Monster]:
    """parse gen1_monsters.txt -> dictionary of {'#001': Monster(...)}, text file derived from https://pokemondb.net/pokedex/stats/gen1"""
    monsters: Dict[str, Monster] = {}

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            m = CRE_RE_NUM.match(line) or CRE_RE_NO.match(line)

            #ignores and skips unknown line format instead of raising error
            if not m:
                continue

            g = m.groupdict()
            t1, t2 = _split_types(g["types"])
            dex = f"#{g['dex']}"

            monsters[dex] = Monster(
                dex = dex, 
                name = g["name"].strip(), 
                type1 = t1, 
                type2 = t2, 
                hp = int(g["hp"]), 
                atk = int(g["atk"]), 
                dfn = int(g["dfn"]), 
                sp_atk = int(g["spa"]), 
                sp_dfn = int(g["spd"]), 
                speed = int(g["spe"]), 
            )

    return monsters

def load_moves(path: str) -> Dict[str, Move]:
    """parse gen1_moves.txt -> dict of {'Ember': Move(...)}, text file derived from https://pokemondb.net/move/generation/1 and linked pages"""
    moves: Dict[str, Move] = {}

    with open(path, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()

            if not line or line.startswith("#"):
                continue

            m = MOVE_RE.match(line)

            #ignores and skips unknown line format instead of raising error
            if not m:
                continue

            #iterates over dict pairs and removes leading and trailing spaces 
            # (leaves internal spaces) to create a cleaned dictionary 
            #{
            # "name": "Ember",
            # "type": "Fire",
            # "cat": "Special",
            # "power": "40",
            # "acc": "100",
            # "pp": "25",
            # "effect": "May burn target."
            #}
            g = {k: v.strip() for k, v in m.groupdict().items()}

            power = _opt_int(g["power"])    #must be digits (int) - now handles all forms of dashes properly as None values
            acc = _opt_acc(g["acc"])        #must be digits (int) - now handles all forms of dashes properly and the infinity symbol

            #power = None if g["power"] in ("-", "") else int(g["power"])
            #acc = None if g["acc"] in ("-", "") else int(g["acc"])
            pp = int(g["pp"]) if g["pp"].isdigit() else 0   #must be digits, otherwise 0

            moves[g["name"]] = Move(
                name = g["name"], 
                type = g["type"], 
                category = g["cat"], 
                power = power, 
                accuracy = acc, 
                pp = pp, 
                effect = g["effect"], 
            )

    return moves

def load_move_learners(path: str) -> Dict[str, List[str]]:
    """parse move_learners.json -> dict of {move_name: ['#004', '#007', ...]}"""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    normalized: Dict[str, List[str]] = {}

    for mv, dexes in data.items():
        fixed = []

        for d in dexes:
            s = str(d).strip()
            fixed.append(s if s.startswith("#") else "#" + s.zfill(3))
        #deduped, numeric sort by the int portion of #NNN
        normalized[mv] = sorted(set(fixed), key=lambda x: int(x[1:]))

    return normalized