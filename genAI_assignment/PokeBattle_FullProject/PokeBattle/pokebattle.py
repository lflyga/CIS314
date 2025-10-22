#!/usr/bin/env python3
import json, os, random, datetime
from poke_engine import BattleEngine, CreatureInstance
from data_parser import parse_creatures_file, parse_moves_file

CONFIG_DIR = "configs"
SAVES_DIR = "saves"
LOGS_DIR = "logs"

def ensure_dirs():
    for d in (SAVES_DIR, LOGS_DIR):
        os.makedirs(d, exist_ok=True)

def pick_team(creatures, prompt="Pick 3 creatures by number (comma separated): "):
    print("\nAvailable creatures:")
    for i, c in enumerate(creatures):
        print(f"{i+1}. {c['Name']} (HP={c.get('HP')}, Atk={c.get('Attack')}, Def={c.get('Defense')}, Spd={c.get('Speed')}) Moves: {', '.join(c.get('Moves', []))}")
    while True:
        choice = input(prompt).strip()
        try:
            indexes = [int(x.strip())-1 for x in choice.split(",") if x.strip()]
            if not indexes or any(i < 0 or i >= len(creatures) for i in indexes):
                raise ValueError
            team = [CreatureInstance.from_dict(creatures[i]) for i in indexes]
            return team
        except Exception:
            print("Invalid selection. Enter numbers separated by commas, e.g. 1,3,4")

def main():
    ensure_dirs()
    print("PokeBattle CLI — Turn-based battle simulator\n")
    moves = parse_moves_file(os.path.join(CONFIG_DIR, "moves.cfg"))
    creatures = parse_creatures_file(os.path.join(CONFIG_DIR, "creatures.cfg"))

    action = input("Start (N)ew battle or (L)oad saved team? [N/L]: ").strip().lower()
    if action == "l":
        saves = [f for f in os.listdir(SAVES_DIR) if f.endswith(".json")]
        if not saves:
            print("No saves found. Starting new battle.")
            action = "n"
        else:
            print("Saves:")
            for i, s in enumerate(saves):
                print(f"{i+1}. {s}")
            idx = int(input("Pick save number: ").strip()) - 1
            with open(os.path.join(SAVES_DIR, saves[idx]), "r") as fh:
                saved = json.load(fh)
            team = [CreatureInstance.from_dict(c) for c in saved["team"]]
    if action != "l":
        team = pick_team(creatures)
        if input("Save this team for later? [y/N]: ").strip().lower() == "y":
            name = input("Save filename (no extension): ").strip() or "team"
            savepath = os.path.join(SAVES_DIR, f"{name}.json")
            with open(savepath, "w") as fh:
                json.dump({"team": [c.to_dict() for c in team], "created": str(datetime.datetime.now())}, fh, indent=2)
            print(f"Saved to {savepath}")

    opponent = [CreatureInstance.from_dict(c) for c in random.sample(creatures, k=min(3, len(creatures)))]
    print("\nYour team:")
    for c in team: print(" -", c.name)
    print("\nOpponent team:")
    for c in opponent: print(" -", c.name)

    engine = BattleEngine(team, opponent)
    engine.run_cli_battle()

if __name__ == "__main__":
    main()
