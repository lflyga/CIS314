"""
Author: L. Flygare
Description: runs a simple turn-based battle between two pokemon
            -builds up to k(4) learnable moves for a pokemon based on dex num
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
    #filters move names from move_learners.json that include this pokemon
    legal_names = [mv for mv, dexes in move_learners.items() if dex in dexes and mv in move_bank]

    #return empty list if no legal moves, dealt with in main.py main() loop
    if not legal_names:
        return []   #caller decides what to do if no legal moves for randomly chosen pokemon
    
    #shuffles and slices for variation
    random.shuffle(legal_names)
    chosen = legal_names[:min(k, len(legal_names))] 

    #provides a legal move bank for a given pokemon
    return [move_bank[name] for name in chosen]

def choose_move_random(_: Monster, moves: List[Move], __: int) -> Optional[Move]:
    """computer picks a random move with PP > 0, None if none available and skips turn"""
    available = [m for m in moves if m.pp > 0]
    return random.choice(available) if available else None

def choose_move_user(actor: Monster, moves: List[Move], turn: int) -> Optional[Move]:
    """prompts the user to select a move by index, returns None if no moves with PP available and skips turn"""
    available = [m for m in moves if m.pp > 0]
    if not available:
        print(f"{actor.name} has no PP left! Skips turn.")
        return None
    
    #shows move menu with stats in clean, easy to read format
    print(f"\n=== Turn {turn}: {actor.name}'s move ===")
    for i, m in enumerate(moves, start = 1):
        tag = "" if m.pp > 0 else "(NO PP)"
        pow_txt = "-" if m.power is None else str(m.power)
        acc_txt = (
            "∞" if (m.accuracy is None and m.power is not None)
            else "-" if m.accuracy is None
            else str(m.accuracy)
        )
        print(f"{i}. {m.name}  [{m.type}/{m.category}]  Pow:{pow_txt}  Acc:{acc_txt}  PP:{m.pp} {tag}")

    #user input loop for move selection per turn, validates input and prompts for valid int input if not an int or enter
    while True:
        raw = input("Choose a move by number (press enter for first available): ").strip()

        if raw =="":
            #picks first move with available PP when enter is presses instead of int 1-4
            for m in moves:
                if m.pp > 0:
                    return m
            return None
        
        #prompts for int input if anything but an int
        if not raw.isdigit():
            print("Please enter a number.")
            continue

        idx = int(raw)

        #prompts for int in valid range of move index if outside range
        if not (1 <= idx <= len(moves)):
            print(f"Enter a number 1-{len(moves)}.")
            continue

        mv = moves[idx - 1]

        #new moves selection if current selection has no remaining PP
        if mv.pp <= 0:
            print("That move has no remaining PP. Choose another.")
            continue

        return mv

def do_battle( 
        a: Monster, b: Monster, 
        moves_a: List[Move], moves_b: List[Move], 
        choose_a: MoveChooser = choose_move_user, choose_b: MoveChooser = choose_move_random, 
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

    #starting states
    hp_a, hp_b = a.hp, b.hp
    turn = 1
    log: List[str] = []
    events: List[Dict] = []

    #inform user of turn order and log
    if a.speed > b.speed:
        msg = f"{a.name} (Player) will act first — higher Speed {a.speed} vs {b.speed}."
    elif a.speed < b.speed:
        msg = f"{b.name} (Computer) will act first — higher Speed {b.speed} vs {a.speed}."
    else:
        msg = f"Speeds are tied at {a.speed}. Player (A) acts first on tie."
    print("\n" + msg)
    log.append(msg)

    #turn order
    while hp_a > 0 and hp_b > 0 and turn < 100:
        log.append(f"---Turn {turn} ---")

        #determine turn order based on speed, re-evaluate each turn (important to remember for later version implementation plans)
        order = [(a, moves_a, "A", choose_a), (b, moves_b, "B", choose_b)]
        order.sort(key=lambda x: x[0].speed, reverse = True)

        #setting up to make sure player's chooser only runs once per turn
        #was getting duplication of moves in move options each turn
        #resets at start of each full new turn
        player_acted_this_turn = False

        for actor, actor_moves, tag, chooser in order:
            #ensuring player's chooser can only run once per turn to prevent duplication in output
            if tag == "A" and chooser is choose_move_user and player_acted_this_turn:
                continue

            #skip if this pokemon fainted earlier in the same turn
            if (tag == "A" and hp_a <= 0) or (tag == "B" and hp_b <= 0):
                continue

            #set defender role
            defender = b if tag == "A" else a

            #determine move, user or computer, and log
            mv = chooser(actor, actor_moves, turn)
            if mv is None:
                msg = f"{actor.name} has no PP left! Skips turn."
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, "move": None, "hit": False, "damage": 0, "hp_a": hp_a, "hp_b": hp_b, "note": "no-pp"})
                continue

            #check accuracy (None always hits)
            if mv.accuracy is None:
                will_hit = True
            else: 
                will_hit = (r.randint(1, 100) <= mv.accuracy)

            #if move attempted but missed, output to user, log
            if not will_hit:
                msg = f"{actor.name} used {mv.name}, but it missed!"
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, "move": mv.name, "hit": False, "damage": 0, "hp_a": hp_a, "hp_b": hp_b})
            #if move hits and inflicts damage, output to user, log
            else:
                dmg = compute_damage(actor, defender, mv, rng = r.uniform(0.85, 1.00))
                if tag == "A":
                    hp_b -= dmg
                    def_name = b.name
                    def_hp = max(0, hp_b)
                else:
                    hp_a -= dmg
                    def_name = a.name
                    def_hp = max(0, hp_a)
                
                msg = f"{actor.name} used {mv.name}! It dealt {dmg} damage. {def_name} has {def_hp} HP remaining"
                print(msg)
                log.append(msg)
                events.append({"turn": turn, "actor": tag, 
                               "move": mv.name, "hit": True, "damage": dmg, 
                               "hp_a": hp_a, "hp_b": hp_b, "defender_hp_remaining": def_hp
                })

            #deplete PP after attempting a move, even if it misses
            mv.pp = max(0, mv.pp - 1)

            #setting to true so that player menu does not run again during the same turn and show duplicate values
            if tag == "A" and chooser is choose_move_user:
                player_acted_this_turn = True

            #stop midturn if either pokemon faints
            if hp_a <= 0 or hp_b <= 0:
                break

        #increase turn count
        turn += 1

    #win conditions, determine and declare winner to user, log
    if hp_a <= 0 and hp_b <= 0:
        winner_tag = "Draw"
        winner_name = None
        endline = (f"Result: {a.name} HP {max(0, hp_a)} vs {b.name} HP {max(0, hp_b)} -> It's a draw!")
    else:
        winner_tag = "A" if hp_b <= 0 else "B"
        winner_monster = a if winner_tag =="A" else b
        loser_monster = b if winner_tag == "A" else a
        winner_name = winner_monster.name
        endline = (f"Result: {a.name} HP {max(0, hp_a)} vs {b.name} HP {max(0, hp_b)} -> {winner_name} is the winner!")
    print(endline)
    log.append(endline)

    #build summary 
    summary = {
        "winner": winner_tag, "winner_name": winner_name, 
        "a_name": a.name, "a_dex": a.dex, 
        "b_name": b.name, "b_dex": b.dex, 
        "final_hp_a": max(0, hp_a), "final_hp_b": max(0, hp_b), 
        "turns":  turn - 1, 
    }

    #header for post battle recap
    print("\n=== Battle Recap ===")

    return log, events, summary

    
