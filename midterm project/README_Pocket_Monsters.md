# CIS 314 — Gen-1 Battle Simulator (Midterm Project)

A lightweight, text-mode Pokémon-style battle simulator written in Python for CIS 314. It loads Gen-1-style monster stats and move data from plain-text / JSON files, builds legal move sets per Pokémon, then runs a deterministic turn-based battle with accuracy, STAB, limited type effectiveness, PP, and logging.

---

## Quick Start

### Requirements
- Python 3.10+ (tested with 3.13 on Windows)
- No external packages required

### Project Structure
```
midterm project/
├─ data/
│  ├─ gen1_monsters.txt
│  ├─ gen1_moves.txt
│  └─ move_learners.json
├─ saves/
│  ├─ battles/        # timestamped JSON + .log per battle
│  └─ slots/          # autosave slot(s)
├─ src/
│  ├─ __init__.py
│  ├─ battle.py       # battle loop & move choosers
│  ├─ damage.py       # damage formula, type chart helpers
│  ├─ loaders.py      # parsers for data files
│  ├─ models.py       # dataclasses: Monster, Move
│  └─ persist.py      # SaveManager (autosaves + logs)
└─ main.py            # entry point
```

### Run
From the project root (the folder containing main.py), run:
```bash
python main.py
```
You’ll see a pre-battle Battle Lineup with each Pokémon’s types, stats, and the 1–4 moves selected for this battle. Press Enter to start. On each of your turns, choose a move by number (or press Enter to use the first move with PP).

At the end, the program writes:
- A human-readable log in saves/battles/YYYYMMDD_HHMMSS_battle_A_vs_B.log
- A structured JSON with summary + events in the same folder

Autosaves are stored in saves/slots/autosave.json before and after a battle.

---

## How It Works

### Data Loading (loaders.py)
- Monsters are parsed from data/gen1_monsters.txt lines like:
  ```
  Monster: No.006 Charizard | Type: Fire/Flying | HP: 78 | ATK: 84 | DEF: 78 | SP.ATK: 109 | SP.DEF: 85 | SPD: 100
  ```
- Moves are parsed from data/gen1_moves.txt lines like:
  ```
  Move: Ember | Type: Fire | Cat: Special | Power: 40 | Acc: 100 | PP: 25 | Effect: May burn target.
  ```
  - Power: - and Acc: - are treated as no power and N/A accuracy (status/utility moves).
  - Acc: ∞ (in data) means always hits (e.g., Swift).
- Move Learners come from data/move_learners.json, mapping move name → list of Pokédex IDs ("#004", "#025", …). IDs are normalized and deduplicated.

### Domain Models (models.py)
- Move: name, type, category, power, accuracy, pp, effect
- Monster: dex, name, types, combat stats, and a list of Move objects

### Battle Flow (battle.py)
1. Move pool building: for each Pokémon, pick up to k legal moves (choose_rand_legal_moves), default k=4.
2. Pre-battle lineup: show both Pokémon, their stats, and their moves for this battle.
3. Initiative: higher Speed acts first; Player (A) wins ties.
4. Turns:
   - Player selects a move from the menu (only runs once per turn).
   - Accuracy is rolled once in do_battle() (always-hit moves skip the roll).
   - compute_damage() applies power, STAB, simplified type effect, and a small random variance (0.85–1.00). Status moves deal 0 direct damage.
   - On hit, the console shows damage dealt and the defender’s remaining HP.
   - PP decreases on attempt (hit or miss).
5. Win condition: prints a clear result line using the winner’s name (“Pidgeotto is the winner!”), and appends a full recap.

### Damage & Effectiveness (damage.py)
- Special vs Physical: by Gen-1 special types (Fire, Water, Grass, Electric, Ice, Psychic, Dragon).
- STAB: 1.5× if the move’s type matches the attacker’s type.
- Type chart: focused subset (extensible), with immunities respected.
- Status: power=None → 0 direct damage.
- Optional fixed-damage support (off by default): add small rules for Seismic Toss, Night Shade (level-based; here level=50), Dragon Rage (40), Sonic Boom (20).

### Persistence (persist.py)
- Creates saves/slots and saves/battles on first run.
- Writes Windows-safe filenames with YYYYMMDD_HHMMSS timestamps.
- Keeps the most recent N battle logs (configurable) via rotate_battles().

---

## Configuration (in main.py)
```python
MAX_REPICKS = 50      # attempts to find a pair where both have ≥1 legal moves
MOVE_CAP    = 4       # max moves per Pokémon (1–4)
EXCLUDE_UNDER_FOUR = False  # True to skip Pokémon with <3 legal moves
```
Paths for data files are set relative to the project root:

```python
MONSTERS_PATH = ROOT / "data/gen1_monsters.txt"
MOVES_PATH    = ROOT / "data/gen1_moves.txt"
LEARNERS_PATH = ROOT / "data/move_learners.json"
```

---

## Project Reflection 

- Did the project achieve its goals?  
  Yes—while the final result differs from the earliest vision, the core “Goal 1” functionality was achieved: a working battle framework with data loading, legal move selection, and a turn loop.

- Did the goals shift during development?  
  They did. Time constraints made clean user selection of a Pokémon/team impractical in the CLI, so the project pivoted to random player selection to focus on stabilizing the battle engine and debugging.

- Future plans envisioned during the report:  
  - Move beyond CLI to a GUI (more visual/engaging), with simple animations tied to move types.  
  - Support player-selected teams (e.g., a 6‑mon party) and two‑player battles.  
  - Add deeper mechanics (stat stages, effects with reciprocal costs, switching).  
  - Keep the game offline/self‑contained so it’s easy for kids to play.

- Process takeaways:  
  Increased comfort using GitHub for tracking and iteration across modules.

---

## Sample Session

```
=== Battle Lineup ===

Player: #100 Voltorb (Type: Electric)
  HP:40  ATK:30  DEF:50  SP.ATK:55  SP.DEF:55  SPD:100
  Moves for this battle:
1. Swift  [Normal/Physical]  Pow:60  Acc:∞  PP:20
2. Light Screen  [Psychic/Special]  Pow:-  Acc:-  PP:30
3. Tackle  [Normal/Physical]  Pow:40  Acc:100  PP:35
4. Screech  [Normal/Physical]  Pow:-  Acc:85  PP:40

Computer: #015 Beedrill (Type: Bug/Poison)
  HP:65  ATK:90  DEF:40  SP.ATK:45  SP.DEF:80  SPD:75
  Moves for this battle:
1. Focus Energy  [Normal/Physical]  Pow:-  Acc:-  PP:30
2. Agility  [Psychic/Special]  Pow:-  Acc:-  PP:30
3. Rage  [Normal/Physical]  Pow:20  Acc:100  PP:20
4. Fury Attack  [Normal/Physical]  Pow:15  Acc:85  PP:20

Press enter to begin the battle...


Voltorb (Player) will act first — higher Speed 100 vs 75.

=== Turn 1: Voltorb's move ===
1. Swift  [Normal/Physical]  Pow:60  Acc:∞  PP:20 
2. Light Screen  [Psychic/Special]  Pow:-  Acc:-  PP:30 
3. Tackle  [Normal/Physical]  Pow:40  Acc:100  PP:35 
4. Screech  [Normal/Physical]  Pow:-  Acc:85  PP:40 
Choose a move by number (press enter for first available): 1
Voltorb used Swift! It dealt 20 damage. Beedrill has 45 HP remaining
Beedrill used Focus Energy! It dealt 0 damage. Voltorb has 40 HP remaining

=== Turn 2: Voltorb's move ===
1. Swift  [Normal/Physical]  Pow:60  Acc:∞  PP:19 
2. Light Screen  [Psychic/Special]  Pow:-  Acc:-  PP:30
3. Tackle  [Normal/Physical]  Pow:40  Acc:100  PP:35
4. Screech  [Normal/Physical]  Pow:-  Acc:85  PP:40
Choose a move by number (press enter for first available):
Voltorb used Swift! It dealt 19 damage. Beedrill has 26 HP remaining
Beedrill used Fury Attack, but it missed!

=== Turn 3: Voltorb's move ===
1. Swift  [Normal/Physical]  Pow:60  Acc:∞  PP:18
2. Light Screen  [Psychic/Special]  Pow:-  Acc:-  PP:30
3. Tackle  [Normal/Physical]  Pow:40  Acc:100  PP:35
4. Screech  [Normal/Physical]  Pow:-  Acc:85  PP:40
Choose a move by number (press enter for first available):
Voltorb used Swift! It dealt 20 damage. Beedrill has 6 HP remaining
Beedrill used Focus Energy! It dealt 0 damage. Voltorb has 40 HP remaining

=== Turn 4: Voltorb's move ===
1. Swift  [Normal/Physical]  Pow:60  Acc:∞  PP:17
2. Light Screen  [Psychic/Special]  Pow:-  Acc:-  PP:30
3. Tackle  [Normal/Physical]  Pow:40  Acc:100  PP:35
4. Screech  [Normal/Physical]  Pow:-  Acc:85  PP:40
Choose a move by number (press enter for first available):
Voltorb used Swift! It dealt 19 damage. Beedrill has 0 HP remaining
Result: Voltorb HP 40 vs Beedrill HP 0 -> Voltorb is the winner!

=== Battle Recap ===
Voltorb (Player) will act first — higher Speed 100 vs 75.
---Turn 1 ---
Voltorb used Swift! It dealt 20 damage. Beedrill has 45 HP remaining
Beedrill used Focus Energy! It dealt 0 damage. Voltorb has 40 HP remaining
---Turn 2 ---
Voltorb used Swift! It dealt 19 damage. Beedrill has 26 HP remaining
Beedrill used Fury Attack, but it missed!
---Turn 3 ---
Voltorb used Swift! It dealt 20 damage. Beedrill has 6 HP remaining
Beedrill used Focus Energy! It dealt 0 damage. Voltorb has 40 HP remaining
---Turn 4 ---
Voltorb used Swift! It dealt 19 damage. Beedrill has 0 HP remaining
Result: Voltorb HP 40 vs Beedrill HP 0 -> Voltorb is the winner!

Saved battle:
  JSON: C:\Users\flyga\OneDrive\Desktop\folders & files\lynda stuff\Shepherd\CIS314\midterm project\saves\battles\20251010_023209_battle_100_vs_015.json
  LOG: C:\Users\flyga\OneDrive\Desktop\folders & files\lynda stuff\Shepherd\CIS314\midterm project\saves\battles\20251010_023209_battle_100_vs_015.log

```

*(Your actual damage will vary slightly due to the 0.85–1.00 variance.)*

---

## Limitations & Known Issues

- Stalemate if neither side can deal direct damage  
  In rare matchups, both randomly selected move sets can be purely non-damaging (e.g., all status/utility) or effectively neutered by immunities/resistances. The only way the battle ends is by hitting the max turn count.  
  *Workarounds:* increase MOVE_CAP, disable EXCLUDE_UNDER_FOUR=False to widen the move pool, or pre-filter out status-only move sets before starting a battle.

- PP exhaustion loop  
  There’s currently no explicit “no-moves-left” early-termination. If both sides eventually exhaust PP on all moves, the battle will still proceed with skip turns until the max turn count ends it.  
  *Potential fix (future work):* detect “both actors have zero PP for all moves” and declare a draw immediately.

---

## Roadmap / Future Work

- From the Post‑Project Report goals
  - Build a GUI with simple, offline animations mapped to move categories/types.
  - Support user-chosen teams (party of 6), switching, and a two‑player mode.
  - Deepen mechanics: stat stages, status conditions, reciprocal effects, proper level scaling.
- Engine / data
  - Expand the type chart to full Gen‑1 coverage.
  - Implement fixed-damage moves (Seismic Toss, Night Shade, Dragon Rage, Sonic Boom).
  - Add an early‑draw rule when both sides have no damaging options or no PP.

