"""
Author: L. Flygare
Description: runs a self-contained battle and saves results
            -loads daat/ using loaders
            -picks two random pokemon and their move banks
            -pre saves battle states, runs battle, writes battle history, and saves post-battle summary
"""

from pathlib import Path
from typing import Tuple, List
from src.loaders import load_monsters, load_moves, load_move_learners
from src.battle import choose_rand_legal_moves, do_battle
from src.persist import SaveManager
import random

#========================
#settings
#========================

ROOT = Path(__file__).resolve().parent

#data file location relative to project root
MONSTERS_PATH = ROOT / "data/gen1_monsters.txt"
MOVES_PATH = ROOT / "data/gen1_moves.txt"
LEARNERS_PATH = ROOT / "data/move_learners.json"

MAX_REPICKS = 50    #how many times to attempt finding a random pair where both have >= 1 legal moves
MOVE_CAP = 4        #per pokemon cap (eg pokemon has 7 legal learnable moves but only 4 will be chosen for the battle)

EXCLUDE_UNDER_FOUR = False #option to exclude pokemon with only 1 learnable move from battles, set to True to exclude

#========================
#helpers
#========================

def pick_two_rand(monsters_dict: dict) -> Tuple:
    """returns two distint random monster objects"""
    a, b = random.sample(list(monsters_dict.values()), 2)
    return a, b

def count_legal_moves(dex: str, move_learners: dict) -> int:
    """count how many legal moves a pokemon can learn"""
    n = 0 
    for mv, dexes in move_learners.items():
        if dex in dexes:
            n += 1
    return n

def show_lineup(monster, moves, label: str):
    """print a pokemon's stats and moves chosen for this battle, only displays - does not manipulate the state of anything"""
    t2 = f"/{monster.type2}" if monster.type2 else ""
    print(f"\n{label}: {monster.dex} {monster.name} (Type: {monster.type1}{t2})")
    print(f"  HP:{monster.hp}  ATK:{monster.atk}  DEF:{monster.dfn}  SP.ATK:{monster.sp_atk}  SP.DEF:{monster.sp_dfn}  SPD:{monster.speed}")
    if moves:
        print("  Moves for this battle:")
        for i, m in enumerate(moves, start = 1):
            pow_txt = "-" if m.power is None else m.power
            acc_txt = (
                "∞" if (m.accuracy is None and m.power is not None) #currently only applies to Swift
                else "-" if m.accuracy is None
                else m.accuracy
            )
            print(f"{i}. {m.name}  [{m.type}/{m.category}]  Pow:{pow_txt}  Acc:{acc_txt}  PP:{m.pp}")

#========================
#main
#========================

def main():
    #create SaveManager
    sm = SaveManager(ROOT)

    #load data
    monsters = load_monsters(str(MONSTERS_PATH))
    move_bank = load_moves(str(MOVES_PATH))
    learners = load_move_learners(str(LEARNERS_PATH))

    #find a valid pair where both have at least one legal learnable move
    #if EXCLUDE_UNDER_FOUR = True in settings, can exclude pokemon with <3 total learnable moves
    for attempt in range (1, MAX_REPICKS +1):
        a, b = pick_two_rand(monsters)

        #tally total legal learnable moves per randomly chosen pokemon
        total_a = count_legal_moves(a.dex, learners)
        total_b = count_legal_moves(b.dex, learners)

        if total_a == 0 or total_b == 0:
            continue    #will repick a new random pair in the event either pokemon does not have at least one legal move

        if EXCLUDE_UNDER_FOUR and (total_a < 3 or total_b < 3):
            continue    #will repick if either has less than 3 legal moves (set to True in settings above to exclude "boring" Pokemon in this version)

        #building move lists, capacity based on MOVE_CAP
        moves_a = choose_rand_legal_moves(a.dex, move_bank, learners, k = MOVE_CAP)
        moves_b = choose_rand_legal_moves(b.dex, move_bank, learners, k = MOVE_CAP)

        #will repick pair if by some chance there is a metadata mixup and either list ends up empty, data may have been changed and now mismatched
        if moves_a and moves_b:
            break
    
    else:
        #despite all attempts a pair could not be created, check information in files to ensure current and valid
        raise RuntimeError(
            "Could not find a valid random pair satisfying the constraints." \
            "Check that your move_learners.json and gen1_move.txt cover the same move names."
        )

    #autosave before start of battle with monsters adn chosen moves
    sm.save_slot(
        "autosave", 
        {
            "a": {"dex": a.dex, "name": a.name, "moves": [m.name for m in moves_a]}, 
            "b": {"dex": b.dex, "name": b.name, "moves": [m.name for m in moves_b]}, 
            "settings": {
                "move_cap": MOVE_CAP, 
                "exclude_under_four": EXCLUDE_UNDER_FOUR, 
                "max_repicks": MAX_REPICKS,
            },
        },
    )

    #show user the battle lineup
    print("\n=== Battle Lineup ===")
    show_lineup(a, moves_a, "Player")
    show_lineup(b, moves_b, "Computer")
    print("\nPress enter to begin the battle...")
    input()

    #run battle, returns text log + structures events + summary
    #passes shallow copies of moves so PP reduction does not premanently alter the bank
    log, events, summary = do_battle(a, b, [m for m in moves_a], [m for m in moves_b])

    #prints log to console as recap
    for line in log:
        print(line)

    #save battle log (json + .log) and rotate old logs for deletion
    meta = {
        "a_dex": a.dex, "a_name": a.name, 
        "b_dex": b.dex, "b_name": b.name, 
        **summary, 
        "chosen_moves_a": [m.name for m in moves_a], 
        "chosen_moves_b": [m.name for m in moves_b], 
        "constraints": {
           "move_cap": MOVE_CAP, 
           "exclude_under_four": EXCLUDE_UNDER_FOUR,  
        },
    }
    paths = sm.write_battle_log(meta, log, events)
    sm.rotate_battles(keep_last = 200)

    print(f"\nSaved battle:\n  JSON: {paths['json']}\n  LOG: {paths['log']}")

    #autosave post-battle summary
    sm.save_slot("autosave", {"last_battle": meta})


if __name__ == "__main__":
    main()
