"""
Author: L. Flygare
Description: implements simplified pokemon style damage calculations based on types and effectiveness
            -type_chart lookup for move effectiveness multiplier
            -supports multiplier for dual type defenders
            -determines special type moves
            -returns total damage
"""

import random
from .models import Monster, Move

#currently minimal chart with the possibility to extend with time pending future goals
#chart information derived from https://pokemondb.net/type/dual
#format is (move_type, monster_used_against_type): effectiveness
#2.0 = super effective, 0.5 = not very effective, 0.0 = immune, any pairing not listed will default to 1.0
#moves against dual-types will currently be handled in a function instead of being listed in this chart
TYPE_CHART = {
    ("Fire","Grass"): 2.0, ("Fire","Ice"): 2.0, ("Fire","Bug"): 2.0, ("Fire","Steel"): 2.0,
    ("Fire","Water"): 0.5, ("Fire","Fire"): 0.5, ("Fire","Rock"): 0.5, ("Fire","Dragon"): 0.5,

    ("Water","Fire"): 2.0, ("Water","Ground"): 2.0, ("Water","Rock"): 2.0,
    ("Water","Water"): 0.5, ("Water","Grass"): 0.5, ("Water","Dragon"): 0.5,

    ("Grass","Water"): 2.0, ("Grass","Ground"): 2.0, ("Grass","Rock"): 2.0,
    ("Grass","Fire"): 0.5, ("Grass","Grass"): 0.5, ("Grass","Poison"): 0.5, ("Grass","Flying"): 0.5,
    ("Grass","Bug"): 0.5, ("Grass","Dragon"): 0.5, ("Grass","Steel"): 0.5,

    ("Electric","Water"): 2.0, ("Electric","Flying"): 2.0,
    ("Electric","Electric"): 0.5, ("Electric","Grass"): 0.5, ("Electric","Dragon"): 0.5,
    ("Electric","Ground"): 0.0,

    ("Ground","Electric"): 2.0, ("Ground","Fire"): 2.0, ("Ground","Poison"): 2.0,
    ("Ground","Rock"): 2.0, ("Ground","Steel"): 2.0,
    ("Ground","Grass"): 0.5, ("Ground","Bug"): 0.5, ("Ground","Flying"): 0.0,
}


def type_multiplier(move_type: str, defender: Monster) -> float:
    """computes total effectivenss for single/dual type defenders by multiplying per-type modifiers in accordance with the above referenced source"""
    mult = 1.0
    for t in (defender.type1, defender.type2):
        if not t:
            continue
        mult *= TYPE_CHART.get((move_type, t), 1.0)
    return mult

def is_special(move_type: str) -> bool: 
    """returns True for the seven special types of gen1 moves to determine which stats to use"""
    return move_type in {"Fire", "Water", "Grass", "Electric", "Ice", "Psychic", "Dragon"}

def _hits(move: Move, rnd: random.Random | None = None) -> bool:
    """returns true if the move hits based on its accuracy (None always hits, never fails)"""
    if move.accuracy is None:   #represented by '—' in data
        return True
    
    #randomly determine accuracy if not an 'awlays hits' move
    r = (rnd or random).Random()
    return r <= (move.accuracy / 100.0)

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
    
    if not _hits(move, rnd = rnd):
        return 0    #move misses
    
    #rolls a random style variance in damage like in gen1 ~.85-1.00
    #gives the same move a range of HP dealt to simulate not every landed strike always being exactly the same
    if rng is None:
        rng = random.uniform(0.85, 1.00)
  
    atk = attacker.sp_atk if is_special(move.type) else attacker.atk
    dfn = defender.sp_dfn if is_special(move.type) else defender.dfn
    base = (((2 * 50 / 5 + 2) * move.power * (atk / max(1, dfn))) / 50) + 2
    stab = 1.5 if move.type in (attacker.type1, attacker.type2) else 1.0
    eff = type_multiplier(move.type, defender)

    total = base * stab * eff * rng
    #ensures immunities are recognized 
    if eff == 0.0:
        return 0
    
    #ensures non-immune hits do at least 1 Hp of damage
    return max(1, int(total))