"""
Author: L. Flygare
Description: defines core data structures used througout the project
            -contains dataclasses for Monster and Move representing pokemon and their attributes
            -each class includes a readable __repr__ for debugging and logging output cleanly
"""

from dataclasses import dataclass, field    #field lets you configure how a field behaves when the dataclass is created
from typing import Optional, List #Optional = built in module for type hints that allows a field to be 'x' or 'None'

#importing dataclass and using it here auto-generates __init__, __repr__, __eq__ from the given fields
@dataclass
class Move:
    """represents a move available in battle"""
    name: str               #disply name of the move (eg Hydro Pump)
    type: str               #elemental type of move (eg Water, Fire Ice, etc)
    
    power: Optional[int]    #base power for damaging moves, None is '-' = non-damaging/Status
    accuracy: Optional[int] #accuracy as a percentage (eg 100 for 100%), None => move never misses ('-', '∞')
    pp: int                 #remaining power points for a move in the current battle
    category: str = "Physical"      #Physical/Special (gen1 does not use Status, accuracy is used to determine Status moves not cat) - physical default
    effect: str = ""        #free-form text describing move effects, only used for display/logging purposes (no calculations this version)

    #default __repr__ class auto defined by @dataclass is too verbose
    def __repr__(self):
        pow_text = f"<Power: {self.power}>" if self.power is not None else ""       #show power if present otherwise nothing added to line
        return f"<Move: {self.name}, {pow_text}, Type/Cat: ({self.type}/{self.category})>"

@dataclass
class Monster:
    """represents a pokemon with base stats and an optional move list"""
    dex: str                #pokedex number, gen1 pokemon, ex. 'No.001'
    name: str               #display name (eg Charizard)
    type1: str              #primary type of pokemon
    type2: Optional[str]    #secondary type for dual-type pokemon, None for mono-types
    hp: int                 #battle stat - health points
    atk: int                #battle stat - attack
    dfn: int                #battle stat - defense
    sp_atk: int             #battle stat - special attack
    sp_dfn: int             #battle stat - special defense
    speed: int              #battle stat - speed
    sprite: Optional[str] = None    #url/path for front sprite image
    moves: List[Move] = field(default_factory=list) #calls list() each time a new monster is created with its own empty move list

    #default __repr__ class defined by @dataclass is too verbose
    def __repr__(self):
        """concise stat representation of a single pokemon (eg <Monster: #006 Charizard, Type: (Fire/Flying)>)"""
        t2 = f"/{self.type2}" if self.type2 else ""                     #to include dual type if present
        return f"<Monster: {self.dex} {self.name}, Type: ({self.type1}{t2})>"


    