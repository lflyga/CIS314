#!/usr/bin/env python3
"""
helpers/random_moves_for_dex.py
Example usage inside your game:
  from helpers.random_moves_for_dex import get_random_moves_for_dex
  mv = get_random_moves_for_dex("#006", 4, "data/gen1_moves.txt", "data/move_learners.json")
"""
import json, random, re

MOVE_LINE = re.compile(r"^Move:\s*(?P<name>[^|]+)\s*\|\s*Type:\s*(?P<type>[^|]+)\s*\|\s*Cat:\s*(?P<cat>[^|]+)\s*\|\s*Power:\s*(?P<power>[^|]+)\s*\|\s*Acc:\s*(?P<acc>[^|]+)\s*\|\s*PP:\s*(?P<pp>[^|]+)\s*\|\s*Effect:\s*(?P<effect>.+)$")

def load_moves_txt(path_txt: str):
    moves = {}
    with open(path_txt, "r", encoding="utf-8") as f:
        for line in f:
            m = MOVE_LINE.match(line.strip())
            if not m: 
                continue
            d = m.groupdict()
            name = d["name"].strip()
            moves[name] = {
                "name": name,
                "type": d["type"].strip(),
                "category": d["cat"].strip(),
                "power": d["power"].strip(),
                "accuracy": d["acc"].strip(),
                "pp": d["pp"].strip(),
                "effect": d["effect"].strip(),
            }
    return moves

def get_random_moves_for_dex(dex: str, k: int, moves_txt="data/gen1_moves.txt", learners_json="data/move_learners.json"):
    with open(learners_json, "r", encoding="utf-8") as jf:
        learners = json.load(jf)
    moves = load_moves_txt(moves_txt)
    legal = [name for name, dexes in learners.items() if dex in dexes and name in moves]
    if not legal:
        return []
    k = min(k, len(legal))
    return [moves[n] for n in random.sample(legal, k)]
