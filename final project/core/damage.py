"""
Author: L. Flygare
Description: implements simplified pokemon style damage calculations based on types and effectiveness
            -type_chart lookup for move effectiveness multiplier (now derived instead of hardcoded)
            -supports multiplier for dual type defenders
            -determines special type moves
            -returns total damage
"""

import json
from pathlib import Path
from .models import Monster, Move
import random

TYPE_CHART_PATH = Path(__file__).resolve().parents[1] / "data" / "type_chart.json"
TYPE_CHART: dict[str, dict[str, float]] = json.loads(TYPE_CHART_PATH.read_text(encoding = "utf-8"))

#currently minimal chart with the possibility to extend with time pending future goals
#chart information derived from https://pokemondb.net/type/dual
#format is (move_type, monster_used_against_type): effectiveness
#2.0 = super effective, 0.5 = not very effective, 0.0 = immune, any pairing not listed will default to 1.0
#moves against dual-types will currently be handled in a function instead of being listed in this chart
# TYPE_CHART = {
#     ("Fire","Grass"): 2.0, ("Fire","Ice"): 2.0, ("Fire","Bug"): 2.0, ("Fire","Steel"): 2.0,
#     ("Fire","Water"): 0.5, ("Fire","Fire"): 0.5, ("Fire","Rock"): 0.5, ("Fire","Dragon"): 0.5,

#     ("Water","Fire"): 2.0, ("Water","Ground"): 2.0, ("Water","Rock"): 2.0,
#     ("Water","Water"): 0.5, ("Water","Grass"): 0.5, ("Water","Dragon"): 0.5,

#     ("Grass","Water"): 2.0, ("Grass","Ground"): 2.0, ("Grass","Rock"): 2.0,
#     ("Grass","Fire"): 0.5, ("Grass","Grass"): 0.5, ("Grass","Poison"): 0.5, ("Grass","Flying"): 0.5,
#     ("Grass","Bug"): 0.5, ("Grass","Dragon"): 0.5, ("Grass","Steel"): 0.5,

#     ("Electric","Water"): 2.0, ("Electric","Flying"): 2.0,
#     ("Electric","Electric"): 0.5, ("Electric","Grass"): 0.5, ("Electric","Dragon"): 0.5,
#     ("Electric","Ground"): 0.0,

#     ("Ground","Electric"): 2.0, ("Ground","Fire"): 2.0, ("Ground","Poison"): 2.0,
#     ("Ground","Rock"): 2.0, ("Ground","Steel"): 2.0,
#     ("Ground","Grass"): 0.5, ("Ground","Bug"): 0.5, ("Ground","Flying"): 0.0,
# }


def type_multiplier(move_type: str, defender: Monster) -> float:
    """
    computes total effectivenss for single/dual type defenders by multiplying per-type modifiers in accordance with the above referenced source
    dual type examples:
    - Fire vs (Grass/Poison):
        Fire -> Grass = 2.0, Fire -> Poison (not listed) = 1.0 -> total = 2.0
    - Electric vs (Flying/Ground):
        Electric -> Flying = 2.0, Electric -> Ground = 0.0 -> total = 0.0 (immune)
    """
    mult = 1.0  #if no matching type pairing in type chart, defaults to 1.0 (neutral) effectivness multiplier
    atk_row = TYPE_CHART.get(move_type, {})

    for t in (defender.type1, defender.type2):
        if not t:
            continue
        mult *= atk_row.get(t, 1.0)
    return mult     #returns the combined effectiveness multiplier, moves can be significantly more or less effective than their baseline

def is_special(move_type: str) -> bool: 
    """returns True for the seven special types of gen1 moves to determine which stats to use"""
    return move_type in {"Fire", "Water", "Grass", "Electric", "Ice", "Psychic", "Dragon"}

def compute_damage(attacker: Monster, defender: Monster, move: Move, rng: float | None = None, rnd: random.Random | None = None) -> int:
    """
    returns final int damage using a simplified formula that fixes the level at 50
    -category check with no damage for Status (power=None)
    -checks accuracy before computing damage
    -correct attacking/defending stats (normal or special base don move type)
    -same-type attack bonus (eg fire-type pokemon uses fire-type move) if types match
    -type effectiveness, taking into account immunities
    -random variance via rng to simulate a range of effectiveness in moves
    -minimum damage will be 1 unless there is immunity, ensuring weak but non-immune hits
     deal at least 1 HP
    """
    if move.category == "Status" or move.power is None:
        return 0    #no damage
    
    #type-effectiveness
    eff = type_multiplier(move.type, defender)
    
    #ensures immunities are recognized
    #bails before calculations and other determinations if defender will be immune to damage from hit
    if eff == 0.0:
        return 0
        
    #determine atk/dfn use vs sp_atk/sp_dfn use
    use_special = is_special(move.type)
    atk = attacker.sp_atk if use_special else attacker.atk
    dfn = defender.sp_dfn if use_special else defender.dfn

    #base damage calc
    base = (((2 * 50 / 5 + 2) * move.power * (atk / max(1, dfn))) / 50) + 2

    #same-type attack bonus
    stab = 1.5 if move.type in (attacker.type1, attacker.type2) else 1.0
    
    #rolls a random style variance in damage like in gen1 ~.85-1.00
    #gives the same move a range of HP dealt to simulate not every landed strike always being exactly the same
    if rng is None:
        rng = random.uniform(0.85, 1.00)
    
    #final damage calc
    total = base * stab * eff * rng
    
    #ensures non-immune hits do at least 1 Hp of damage
    return max(1, int(total))