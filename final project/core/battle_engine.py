"""
Author: L. Flygare
Description: ui-agnostic battle controller for the overall project
                
             this module owns *battle flow and state* (turn order, move selection, PP usage,
                fainting, team progression, and win conditions) while delegating all numeric
                damage math to damage.compute_damage()

             key features:
                -full team battles
                -pp isolation
                -struggle fallback (stalemate prevention)

             damage rules:
                -all type effectiveness, STAB and physical/special handling are delegated to 
                 damage.compute_damage, which now uses pokeapi backed data rather than being 
                 hardcoded into the module
"""
from dataclasses import dataclass, field, replace
from typing import List, Optional
import random

from .models import Monster, Move
from .damage import compute_damage

@dataclass
class BattleState:
    """
    represents a full multi-pokemon team battle
    each side has a list of pokemon and an active index
    """
    #full teams
    team_a: List[Monster]
    team_b: List[Monster]
    
    #which pokemon is active
    active_a: int = 0
    active_b: int = 0

    #hp pools
    hp_a: List[int] = field(default_factory = list)
    hp_b: List[int] = field(default_factory = list)
    
    #move lists per team member (typically 1-4 moves each)
    moves_a: List[List[Move]] = field(default_factory = list)
    moves_b: List[List[Move]] = field(default_factory = list)

    #turn and flow control
    turn: int = 1
    next_actor: str = "A"   #A or B to indicate whose turn it is

    #text log of events     ("Pikachu used Thunderbolt! It dealt 32 damage.")
    log: List[str] = field(default_factory = list)

    #winner flag of A, B, Draw or None if battle still inprogress
    winner: Optional[str] = None    #A, B, Draw, or None

    @property
    def a(self):
        return self.team_a[self.active_a]
    
    @property
    def b(self):
        return self.team_b[self.active_b]
    
    @property
    def hp_current_a(self):
        return self.hp_a[self.active_a]
    
    @property
    def hp_current_b(self):
        return self.hp_b[self.active_b]


def start_battle(team_a: List[Monster], team_b: List[Monster], moves_a: List[List[Move]], moves_b: List[List[Move]]) -> BattleState:
    """
    initialize a new BattleState for a full team battle
    """
    #make shallow copies of moves to keep pp usage isolated to this battle
    moves_a = [[replace(m) for m in mv_list] for mv_list in moves_a]
    moves_b = [[replace(m) for m in mv_list] for mv_list in moves_b]

    state = BattleState(
        team_a = team_a, 
        team_b = team_b, 
        active_a = 0, 
        active_b = 0, 
        hp_a = [m.hp for m in team_a], 
        hp_b = [m.hp for m in team_b], 
        moves_a = moves_a, 
        moves_b = moves_b, 
    )

    #simple speed check for first turn
    #decide who acts first based on speed
    if team_a[0].speed > team_b[0].speed:
        state.next_actor = "A"
        state.log.append(
            f"{team_a[0].name} (Player 1) will act first (Speed {team_a[0].speed} vs {team_b[0].speed})."
        )
    elif team_b[0].speed > team_a[0].speed:
        state.next_actor = "B"
        state.log.append(
            f"{team_b[0].name} (Player 2) will act first (Speed {team_b[0].speed} vs {team_a[0].speed})."
        )
    else:
        #on speed tie, default to player 1 going first
        state.next_actor = "A"
        state.log.append(
            f"Speeds tie at {team_a[0].speed}. Player 1 acts first."
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

def _flip_turn(state, actor_tag):
    """
    advances battle flow to the next actor
    """
    #increment turn only after B acts
    if actor_tag == "B":
        state.turn += 1

    state.next_actor = "B" if actor_tag == "A" else "A"
    return state

def make_struggle_move():
    """
    simplified Struggle implementation, to aid in battles that would be stalemates for all status moves
        -treated as normal physical move that always hits
        -implemented when a pokemon only has status type legal moves
         -prevents both battling pokemon from only having non-damaging status moves
    """
    return Move(
        name = "Struggle", 
        type = "Normal", 
        power = 50, 
        accuracy = None,    #always hits
        pp = 999,           #effectively unlimited for this purpose
        category = "Physical", 
        effect = "Fallback move when no damaging moves available."
    )

def apply_move(state: BattleState, move_index: int, rnd: random.Random | None = None) -> BattleState:
    """
    resolve one action for the current actor - A or B

    Flow:
        1) Identify actor/defender and fetch the actor's move list for their
           currently active Pokémon.
        2) If the actor has no usable damaging moves, force Struggle.
        3) Validate the chosen move index (if not forced Struggle) and ensure PP remains.
        4) Roll accuracy; on miss, decrement PP (if applicable) and end the action.
        5) Compute damage via damage.compute_damage() and apply it to defender HP.
        6) Decrement PP (if applicable).
        7) If Struggle was forced, apply recoil to the actor.
        8) Handle defender fainting and auto-send the next available Pokémon.
        9) Handle actor fainting from recoil and auto-send the next available Pokémon.
       10) Flip turn to the next actor.

    Notes:
        -this function mutates the BattleState in place and returns it for convenience.
        -win condition: when one side has no team member with HP > 0.
        -any numeric damage math (STAB, type effectiveness, physical/special) is
          delegated to damage.compute_damage().
    """
    #if we have a winner already, do nothing further
    if state.winner is not None:
        return state    
    
    rnd = rnd or random

    #identify current actor and defender
    actor_tag = state.next_actor
    if actor_tag == "A":
        actor = state.a
        defender = state.b
        # actor_hp = state.hp_a
        # defender_hp = state.hp_b
        actor_moves = state.moves_a[state.active_a]
        # def_team = state.team_b
        # def_moves = state.moves_b
    else:
        actor = state.b
        defender = state.a
        # actor_hp = state.hp_b
        # defender_hp = state.hp_a
        actor_moves = state.moves_b[state.active_b]
        # def_team = state.team_a
        # def_moves = state.moves_a

    #struggle check
    usable_moves = [m for m in actor_moves if (m.pp is None or m.pp > 0)]
    usable_damaging = [m for m in usable_moves if m.power is not None]

    forced_struggle = False

    if not usable_damaging:
        mv = make_struggle_move()
        forced_struggle = True
    else:
        #basic move index validation
        if move_index < 0 or move_index >= len(actor_moves):
            state.log.append(f"{actor.name} acted but chose an invalid move.")
            return state
        
        mv = actor_moves[move_index]

        #check pp before attempting the move
        if mv.pp is not None and mv.pp <= 0:
            state.log.append(f"{actor.name} tried {mv.name}, but no PP left!")
            return state
    
    #accuracy roll
    if not _roll_hit(mv, rnd = rnd):
        state.log.append(f"{actor.name} used {mv.name}, but it missed!")
        if mv.pp is not None:
            mv.pp -= 1
        return _flip_turn(state, actor_tag)
    

    #defer to damage.compute_damage for move damage
    dmg = compute_damage(attacker = actor, defender = defender, move = mv)

    #apply damage to correct side
    if actor_tag == "A":
        state.hp_b[state.active_b] = max(0, state.hp_b[state.active_b] - dmg)
        remaining = state.hp_b[state.active_b]
    else:
        state.hp_a[state.active_a] = max(0, state.hp_a[state.active_a] - dmg)
        remaining = state.hp_a[state.active_a]

    state.log.append(
        f"{actor.name} used {mv.name}! It dealt {dmg} damage. "
        f"{defender.name} has {remaining} HP left."
    )

    if mv.pp is not None:
        mv.pp -= 1

    #recoil damage from Struggle implementation
    if forced_struggle:
        recoil = max(1, actor.hp // 4)
        if actor_tag == "A":
            state.hp_a[state.active_a] = max(0, state.hp_a[state.active_a] - recoil)
            state.log.append(f"{actor.name} is hurt by recoil! (-{recoil} HP)")
        else:
            state.hp_b[state.active_b] = max(0, state.hp_b[state.active_b] - recoil)
            state.log.append(f"{actor.name} is hurt by recoil! (-{recoil} HP)")

    #KO checks  and logic 
    if remaining <= 0:
        state.log.append(f"{defender.name} fainted!")

        #find next pokemon
        next_idx = None
        if actor_tag == "A":
            #B fainted
            for i, hp in enumerate(state.hp_b):
                if hp > 0:
                    next_idx = i
                    break
            if next_idx is None:
                state.winner = "A"
                state.log.append("Player 1 wins the battle!")
                return state
            else:
                state.active_b = next_idx
                state.log.append(f"{state.team_b[next_idx].name} was sent out!")
        else:
            #A fainted
            for i, hp in enumerate(state.hp_a):
                if hp > 0:
                    next_idx = i
                    break
            if next_idx is None:
                state.winner = "B"
                state.log.append("Player 2 wins the battle!")
                return state
            else:
                state.active_a = next_idx
                state.log.append(f"{state.team_a[next_idx].name} was sent out!")

    #if Struggle recoil KO'd attacker
    if forced_struggle:
        if actor_tag == "A" and state.hp_a[state.active_a] <= 0:
            state.log.append(f"{actor.name} fainted from recoil!")
            #switch in next A if possible
            next_idx = None
            for i, hp in enumerate(state.hp_a):
                if hp > 0:
                    next_idx = i
                    break
            if next_idx is None:
                state.winner = "B"
                state.log.append("Player 2 wins the battle!")
                return state
            else:
                state.active_a = next_idx
                state.log.append(f"{state.team_a[next_idx].name} was sent out!")

        elif actor_tag == "B" and state.hp_b[state.active_b] <= 0:
            state.log.append(f"{actor.name} fainted from recoil!")
            #switch in next B if possible
            next_idx = None
            for i, hp in enumerate(state.hp_b):
                if hp > 0:
                    next_idx = i
                    break
            if next_idx is None:
                state.winner = "A"
                state.log.append("Player 1 wins the battle!")
                return state
            else:
                state.active_b = next_idx
                state.log.append(f"{state.team_b[next_idx].name} was sent out!")

    return _flip_turn(state, actor_tag)