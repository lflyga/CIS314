# PokéBattle — Gen 1 Team Battle Simulator

**Author:** Lynda Flygare  
**Course:** CIS 314 – Shepherd University  
**Project Type:** Final Project  

---

## Overview

**PokéBattle** is a Generation 1 Pokémon team battle simulator built in Python with a Streamlit-based graphical interface.  
The application allows users to build teams, preview Pokémon stats and moves, and conduct turn-based battles that follow classic Pokémon mechanics.

The project emphasizes clean architecture, data-driven design using PokeAPI, and robust battle logic that avoids deadlock scenarios.

---

## Features

### Team Builder
- Build teams of up to **6 Pokémon per side**
- Supports **Player vs Player** and **Player vs CPU**
- Preview Pokémon stats, typing, and legal Gen 1 moves before selection
- CPU teams are generated automatically from available Pokémon

### Battle System
- **Full team battles** (not single 1v1 fights)
- One Pokémon per team is active at a time
- Automatic switching when a Pokémon faints
- Battle ends when one team has no remaining Pokémon with HP > 0
- Turn order determined by Speed (Gen 1 rules)

### Move Handling
- Each Pokémon is guaranteed **at least one damaging move** when possible
- Move PP is tracked **per battle**, isolated from global data
- **Struggle fallback** prevents infinite battles when no damaging moves remain
- Recoil damage ensures battles always conclude

### Damage Calculation
- Gen 1 physical vs special rules (type-based)
- Same-Type Attack Bonus (STAB)
- Type effectiveness for single- and dual-type Pokémon
- Type chart derived from **PokeAPI**
- Randomized damage variance similar to Gen 1 games

---

## Project Structure

```
final_project/
│
├── app.py                     # Streamlit UI and routing
│
├── core/
│   ├── battle_engine.py       # Battle flow, PP tracking, fainting logic
│   ├── damage.py              # Damage calculations and type effectiveness
│   ├── json_loaders.py        # Load JSON into Monster/Move objects
│   ├── models.py              # Dataclasses for Monster and Move
│
├── utils/
│   └── pokeapi_loader.py      # One-time PokeAPI data extraction script
│
├── data/
│   ├── monsters.json          # Pokémon stats and metadata
│   ├── moves.json             # Move definitions
│   ├── move_learners.json     # Legal moves per Pokémon
│   └── type_chart.json        # Type effectiveness chart
│
├── venv/                      # Virtual environment (not committed)
│
├── README.md
├── LICENSE
└── pyproject.toml
```

---

## Data Source: PokeAPI

This project uses **PokeAPI (https://pokeapi.co)** as the authoritative data source for:

- Pokémon species and stats
- Move definitions (power, accuracy, PP)
- Pokémon typing
- Type effectiveness relationships

### Data Workflow
1. `utils/pokeapi_loader.py` queries PokeAPI and filters Pokémon by generation
2. Relevant data is normalized and saved to JSON files
3. Runtime code loads JSON only (no live API calls during gameplay)

---

## Installation & Setup

### 1. Create and activate a virtual environment

```bash
python -m venv venv
```

**Windows**
```bash
venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install streamlit requests
```

---

## Data Generation (Optional)

This project includes pre-generated Pokémon data files located in the `data/`
directory. These files are sufficient to run the application as-is, and users
do **not** need to make any live API requests.

If desired, the data can be regenerated using the PokeAPI loader script:

```bash
python -m utils.pokeapi_loader
```

---

## Running the Application

From the project root directory:

```bash
streamlit run app.py
```

---

## Battle Rules & Design Decisions

### Generation 1 Rules
- Move category (Physical/Special) determined by move type
- Fixed battle level (Level 50)
- Accuracy and PP enforced
- Status moves deal no damage

### Struggle Implementation
To prevent infinite battles:
- If a Pokémon has no usable damaging moves, it is forced to use **Struggle**
- Struggle always hits and deals damage
- Recoil damage equals ¼ of the user’s max HP
- Guarantees all battles eventually end

### Separation of Concerns
- `app.py` handles UI only
- `battle_engine.py` handles battle flow and state
- `damage.py` handles numeric damage calculations
- `models.py` defines core data structures
- `json_loaders.py` bridges JSON data to runtime objects

---

## Limitations and Known Issues

While PokéBattle implements a complete and functional Gen 1–style team battle system, the current version includes several intentional simplifications and known limitations:

### Battle Mechanics
- **No status conditions implemented**: Non-damaging moves (e.g., Growl, Sleep Powder, Poison Gas) do not apply persistent effects such as sleep, paralysis, poison, burn, confusion, or stat stage changes. These moves currently consume PP without altering battle state.
- **Simplified damage model**: Damage calculations follow Gen 1–inspired rules but are not a perfect replica. Critical hits, multi-hit behavior, fixed-damage moves, and certain edge-case mechanics are not implemented.
- **Simplified Struggle behavior**: Struggle is implemented as a fallback when no damaging moves remain, with simplified recoil logic to guarantee battle resolution. Exact canonical behavior is not fully reproduced.
- **Basic AI decision-making**: CPU-controlled opponents select moves randomly from available options and do not perform strategic evaluation.

### Data Accuracy
- **Approximate move legality**: Legal move lists are derived from PokeAPI data filtered to Generation 1 assumptions. Some edge cases (version-specific learnsets or special acquisition methods) may not be perfectly represented.
- **Type effectiveness accuracy depends on generated data**: The type chart is derived from external data sources and assumes Generation 1 effectiveness rules.

### User Interface
- **Streamlit rerun behavior**: Because Streamlit reruns the script on interaction, some UI state may reset if session state variables are not preserved in all scenarios.
- **Caching during development**: Cached JSON loading may require restarting the app to reflect regenerated data files.
- **Limited battle configuration**: Users cannot manually customize move sets beyond the automatically generated selections.

### Project Constraints
- **No live API usage during gameplay**: All Pokémon data must be pre-generated using the PokeAPI loader script. The application does not fetch data dynamically at runtime.
- **Local execution only**: Multiplayer functionality is local only (same browser session). Networked multiplayer is not supported.

These limitations reflect deliberate scope choices made to prioritize correctness, clarity, and architectural separation within the constraints of the course project.

---

## License & Attribution

This project incorporates data derived from **PokeAPI**, licensed under the **BSD 3-Clause License**.

Pokémon and Pokémon character names are trademarks of Nintendo.

---

## Educational Disclaimer

This project is intended for **educational use only**.  
Pokémon names, sprites, and related intellectual property belong to Nintendo, Game Freak, and The Pokémon Company.