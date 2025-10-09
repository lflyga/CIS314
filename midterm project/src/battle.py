"""
Author: L. Flygare
Description: runs a simple turn-based battle between two pokemon
            -builds up to k(4) learnable moves for a pokemno based on dex num
            -allows user to choose move/computer randomly chooses move for defender
            -simulates the fight with speed based turn order, accuracy checks, damage, PP reduction, and win conditions
            -returns battle logs, events, and summary stats at battle end
"""

import random
from dataclasses import replace
from typing import List, Dict, Optional, Callable
from .models import Monster, Move
from .damage import compute_damage

MoveChooser = Callable[[Monster, List[Move], int], Optional[Move]]

def choose_rand_legal_moves(dex: str, move_bank: Dict[str, Move], move_learners: Dict[str, List[str]], k: int = 4) -> List[Move]:
    """ pick up to k learneable moves for a given pokemon from the allowable move bank"""
    legal = [mv for mv, dexes in move_learners.items() if dex in dexes and mv in move_bank]
    random.shuffle(legal)
    return [move_bank[mv] for mv in legal[:k]]

def choose_move_random(_: Monster, moves: List[Move], __: int) -> Optional[Move]:
    """computer picks a random move with PP > 0, None if noe available"""
    available = [m for m in moves if m.pp > 0]
    return random.choice(available) if available else None

def choose_move_user(actor: Monster, moves: List[Move], turn: int) -> Optional[Move]:
    """prompts the user to select a move by index, returns None if no moves with PP available"""
    available = [m for m in moves if m.pp > 0]
    if not available:
        print(f"{actor.name} has no PP left! Skips turn.")
        return None
    
    #shows move menu with stats
    print(f"\n=== Turn {turn}: {actor.name}'s move ===")
    for i, m in enumerate(moves, start = 1):
        tag = "" if m.pp > 0 else "(NO PP)"
        pow_txt = "-" if m.power is None else str(m.power)
        acc_txt = "∞" if m.accuracy is None else str(m.accuracy)
        print(f"{i}. {m.name}  [{m.type}/{m.category}]  Pow:{pow_txt}  Acc:{acc_txt}  PP:{m.pp} {tag}")

    #user input loop
    while True:
        raw = input("Choose a move by number (press enter for first available): ").strip()

        if raw =="":
            #picks first move with available PP
            for m in moves:
                if m.pp > 0:
                    return m
            return None
        
        if not raw.isdigit():
            print("Please enter a number.")
            continue

        idx = int(raw)

        if not (1 <= idx <= len(moves)):
            print(f"Enter a number 1-{len(moves)}.")
            continue

        mv = moves[idx - 1]

        if mv.pp <= 0:
            print("That move has no remaining PP. Choose another.")
            continue
        return mv

def do_battle( 
        a: Monster, b: Monster, 
        moves_a: List[Move], moves_b: List[Move], 
        chooose_a: MoveChooser = choose_move_user, choose_b: MoveChooser = choose_move_random, 
        rnd: Optional[random.Random] = None, 
        copy_moves: bool = True,
        ):
    """
    simulate a simple pokemon battle
    -turn order by Monster.speed, descending
    -accuracy roll per move (None always hits)
    -damage with STAB, type effectiveness, and variability
    -PP increase per use
    """

    r = rnd or random

    #shallow copy moves so PP changes do not leak across battles with persistence
    if copy_moves:
        moves_a = [replace(m) for m in moves_a]
        moves_b = [replace(m) for m in moves_b]

    hp_a, hp_b = a.hp, b.hp
    turn = 1
    log: List[str] = []
    events: List[Dict] = []

    while hp_a > 0 and hp_b > 0 and turn < 100:
        log.append(f"---Turn {turn} ---")

        order = [(a, moves_a, "A", chooose_a), (b, moves_b, "B", choose_b)]
        order.sort(key=lambda x: x[0].speed, reverse = True)

        for actor, actor_moves, tag, chooser in order:
            #skip if this pokemon fainted earlier in the same turn
            if (tag == "A" and hp_a <= 0) or (tag == "B" and hp_b <= 0):
                continue

            defender = b if tag == "A" else a

            #determine move, user or computer
            mv = chooser(actor, actor_moves, turn)
            if mv is None:
                msg = f"{actor.name} has no PP left! Skips turn."
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, "move": None, "hit": False, "damage": 0, "hp_a": hp_a, "hp_b": hp_b, "note": "no-pp"})
                continue

            #check accuracy
            if mv.accuracy is None:
                will_hit = True
            else: 
                will_hit = (r.randint(1, 100) <= mv.accuracy)

            if not will_hit:
                msg = f"{actor.name} used {mv.name}, but it missed!"
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, "move": mv.name, "hit": False, "damage": 0, "hp_a": hp_a, "hp_b": hp_b})
            else:
                dmg = compute_damage(actor, defender, mv, rng = r.uniform(0.85, 1.00))
                if tag == "A":
                    hp_b -= dmg
                else:
                    hp_a -= dmg
                
                msg = f"{actor.name} used {mv.name}! It dealt {dmg} damage."
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, "move": mv.name, "hit": True, "damage": 0, "hp_a": hp_a, "hp_b": hp_b})

            #deplete PP after attempting a move, even if it misses
            mv.pp = max(0, mv.pp - 1)

            #stop midturn if either pokemon faints
            if hp_a <= 0 or hp_b <= 0:
                break

        turn += 1

    #win conditions
    winner = "A" if hp_b <= 0 else ("B" if hp_a <= 0 else "Draw")
    endline = f"Result: {a.name} HP {max(0, hp_a)} vs {b.name} HP {max(0, hp_b)} -> {winner}"
    print(endline)
    log.append(endline)

    summary = {
        "winner": {winner}, 
        "a_name": a.name, "a_dex": a.dex, 
        "b_name": b.name, "b_dex": b.dex, 
        "final_hp_a": max(0, hp_a), "final_hp_b": max(0, hp_b), 
        "turns":  turn - 1, 
    }

    return log, events, summary

    
