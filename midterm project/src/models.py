from dataclasses import dataclass
from typing import Optional #built in module for type hints that allows a field to be 'x' or 'None'

#importing dataclass and using it here auto-generates __init__, __repr__, __eq__ from the given fields
@dataclass
class Move:
    name: str
    type: str
    category: str           #Physical/Special
    power: Optional[int]    #None is '-' or a fixed damage amount
    accuracy: Optional[int] #None => move never misses
    pp: int
    effect: str

    #default __repr__ class defined by @dataclass is too verbose
    def __repr__(self):
        pow_text = f"<Power: {self.power}>" if self.power is not None else ""       #show power if present otherwise nothing added to line
        return f"<Move: {self.name}, {pow.text}, Type/Cat: ({self.type}/{self.category})>"

@dataclass
class Creature:
    dex: str                #pokedex number, gen1 pokemon, ex. 'No.001'
    name: str
    type1: str
    type2: Optional[str]
    hp: int
    atk: int
    dfn: int
    sp_atk: int
    sp_dfn: int
    speed: int
    moves: List[Move] = field(default_factory=list) #calls list() each time a new creature is created with its own empty move list

    #default __repr__ class defined by @dataclass is too verbose
    def __repr__(self):
        t2 = f"/{self.type2}" if self.type2 else ""                     #to include dual type if present
        return f"<Creature: {self.dex} {self.name}, Type: ({self.type1}{t2})>"


    