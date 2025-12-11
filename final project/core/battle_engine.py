"""
Author: L. Flygare
Description: provides a ui-agnostic wrapper around core damage logic so that the rest of the project can run 
                battles without knowing/handling any of the math details
                -BattleState tracks both pokemon, their hp, move lists, turn number, whose turn it is, a text 
                 log, and the winner once decided
                -start_battle initializes a fresh BattleState from two monsters and their chosen move lists
                -apply_move executes one move selection for the current actor, calls compute_damage from 
                 damage.py, and updates HO, log, and winner
             all type effectiveness, STAB and physical/special handling are delegated to damage.compute_damage, 
             which now uses pokeapi backed data rather than being hardcoded into the file
"""
from dataclasses import dataclass, field, replace
from typing import List, Optional
import random

from .models import Monster, Move
from .damage import compute_damage

@dataclass
class BattleState:
    """
    represents the full state of one-on-one battle
    """
    #two combatants
    a: Monster
    b: Monster
    
    #move lists (typically 1-4 moves)
    moves_a: List[Move]
    moves_b: List[Move]

    #current hp for each pokemon, starting at their base hp
    hp_a: int
    hp_b: int

    #turn and flow control
    turn: int = 1
    next_actor: str = "A"   #A or B to indicate whose turn it is

    #text log of events     ("Pikachu used Thunderbolt! It dealt 32 damage.")
    log: List[str] = field(default_factory = list)

    #winner flag of A, B, Draw or None if battle still inprogress
    winner: Optional[str] = None    #A, B, Draw, or None


def start_battle(a: Monster, b: Monster, moves_a: List[Move], moves_b: List[Move], copy_moves: bool = True ) -> BattleState:
    """
    initialize a new BattleState from two monsters and the sets of moves they will use in this battle
    """
    #make shallow copies of moves to keep pp usage isolated to this battle
    if copy_moves:
        moves_a = [replace(m) for m in moves_a]
        moves_b = [replace(m) for m in moves_b]

    state = BattleState(
        a = a, 
        b = b, 
        moves_a = moves_a, 
        moves_b = moves_b, 
        hp_a = a.hp, 
        hp_b = b.hp, 
    )

    #simple speed check
    #decide who acts first based on speed
    if a.speed > b.speed:
        state.next_actor = "A"
        state.log.append(
            f"{a.name} (Player 1) will act first (Speed {a.speed} vs {b.speed})."
        )
    elif b.speed > a.speed:
        state.next_actor = "B"
        state.log.append(
            f"{b.name} (Player 2) will act first (Speed {b.speed} vs {a.speed})."
        )
    else:
        #on speed tie, default to player 1 going first
        state.next_actor = "A"
        state.log.append(
            f"Speeds tie at {a.speed}. Player 1 acts first."
        )
    
    return state

def _roll_hit(move: Move, rnd: random.Random | None = None) -> bool:
    """
    determine whether a move hit based on its accuracy

    returns True if move hits, false if it misses

    if accuracy is None, move is treated as always hitting
    """
    if move.accuracy is None:
        return True
    
    r = rnd or random
    return r.randint(1, 100) <= move.accuracy

def apply_move(state: BattleState, move_index: int, rnd: random.Random | None = None) -> BattleState:
    #if we have a winner already, do nothing further
    if state.winner is not None:
        return state    
    
    rnd = rnd or random

    #identify current actor and defender
    actor_tag = state.next_actor
    actor = state.a if actor_tag == "A" else state.b
    defender = state.b if actor_tag =="A" else state.a

    #select correct moves list
    actor_moves = state.moves_a if actor_tag == "A" else state.moves_b

    #basic move index validation
    if not (0 <= move_index < len(actor_moves)):
        state.log.append(f"{actor.name} tried to act, but chose an invalid move.")
        return state
    
    mv = actor_moves[move_index]

    #check pp before attempting the move
    if mv.pp is not None and mv.pp <= 0:
        state.log.append(f"{actor.name} tried to use {mv.name}, but it has no PP left!")
        return state
    
    #accuracy roll
    if not _roll_hit(mv, rnd = rnd):
        state.log.append(f"{actor.name} used {mv.name}, but it missed!")
        if mv.pp is not None:
            mv.pp -= 1
    else:
        #defer to damage.compute_damage for move damage
        dmg = compute_damage(attacker = actor, defender = defender, move = mv)

        #apply damage to correct side
        if actor_tag == "A":
            state.hp_b = max(0, state.hp_b - dmg)
            def_name, def_hp = state.b.name, state.hp_b
        else:
            state.hp_a = max(0, state.hp_a - dmg)
            def_name, def_hp = state.a.name, state.hp_a

        state.log.append(
            f"{actor.name} used {mv.name}! It dealt {dmg} damage. "
            f"{def_name} has {def_hp} HP left."
        )

        if mv.pp is not None:
            mv.pp -= 1

        #KO checks - double KOs are possible
        if state.hp_a <=0 and state.hp_b <= 0:
            state.winner = "Draw"
            state.log.append("Both Pokémon fainted. It's a draw!")
            return state
        elif state.hp_b <= 0:
            state.winner = "A"
            state.log.append(f"{state.b.name} fainted. Player 1 wins!")
            return state
        elif state.hp_a <= 0:
            state.winner = "B"
            state.log.append(f"{state.a.name} fainted. Player 2 wins!")
            return state
        
    #if make it to here, battle continues
    #flip who the actor is, increment turn after player 2 acts
    if actor_tag == "B":
        state.turn += 1

    state.next_actor = "B" if actor_tag == "A" else "A"

    return state