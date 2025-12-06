"""
Author: L. Flygare
Description: this script pulls gen1 pokemon dat afrom pokeapi and generates htree json files under the project
                'data/' directory:
                * monsters.json         - keyed by dex number (e.g., "#001")
                                        - each entry contains name, types, base stats, and a front sprite URL
                * moves.json            - keyed by move name (alphabetically sorted)
                                        - each entry contains move type, power, accuracy, and pp
                * move_learners.json    - maps each Pokédex number (ex #001) to a sorted list of all gen1 legal 
                                          level-up moves that pokemon can learn in the red/blue version group
"""

import json
import requests
from pathlib import Path

#-----------------------------
# API configuration
#-----------------------------

#base URL for all pokeapi endpoints used in project
API_BASE = "https://pokeapi.co/api/v2/"

#gen1 endpoint - what will be used to iterate over
GEN_ENDPOINT = "generation/1/"

#filtering out moves used in later generations to keep all moves limited to gen1 legal moves
VERSION_GROUP = "red-blue"  #only moves from pokemon red/blue

#-----------------------------
# output paths
#-----------------------------

#points to project root - one directory above this file (final project)
ROOT = Path(__file__).resolve().parents[1]

#all genrated files will live under ROOT/data
OUT_DIR = ROOT / "data"
OUT_DIR.mkdir(exist_ok=True)

#individual json file outputs - will be derived from pokeapi data unlike previous version
MON_OUT = OUT_DIR / "monsters.json"
MOVE_OUT = OUT_DIR / "moves.json"
LEARN_OUT = OUT_DIR / "move_learners.json"



def fetch(url: str) -> dict:
    """
    perform a GET request to the given url and return decoded json
    """
    resp = requests.get(url, timeout = 15)
    resp.raise_for_status()
    return resp.json()

def get_gen1_species_names() -> list[str]:
    """
    fetch all gen1 pokemon species names from pokeapi

    returns a sorted list of species names which are then used with 
    the /pokemon/ endpoint to get detailed data
    """
    data = fetch(API_BASE + GEN_ENDPOINT)
    #"pokemon_species" is a list of objects, each having a "name" field
    species = [s["name"] for s in data["pokemon_species"]]
    #sorting ensures consistent order from run-to-run
    return sorted(species)

def extract_stats(pokemon_json: dict) -> dict:
    """
    extract the base stats from a pokeapi json object

    given pokemon_json (the full pokemon data from /pokemon/{name}/), returns
    a dict mapping shortened stat labels to integer base stats
    """
    #pokeapi stores stats as a list of objects with "stat" and "base_stat"
    stat_map = {s["stat"]["name"]: s["base_stat"] for s in pokemon_json["stats"]}
    return{
        "hp": stat_map["hp"], 
        "atk": stat_map["attack"], 
        "dfn": stat_map["defense"], 
        "sp_atk": stat_map["special-attack"], 
        "sp_dfn": stat_map["special-defense"], 
        "speed": stat_map["speed"], 
    }

def extract_types(pokemon_json: dict) -> tuple[str, str | None]:
    """
    extract primary and secondary(optional) types from the pokemon json

    given pokemon_json (the full pokemon data from /pokemon/{name}/), returns
    (type1, type2) string name of the primary and secondary types (or None 
    for type2 if non-applicable)
    """
    #sorted by slot (1 or 2) to keep order consistent 
    types = sorted(pokemon_json["types"], key = lambda t: t["slot"])
    t1 = types[0]["type"]["name"].title()
    t2 = types[1]["type"]["name"].title() if len(types) > 1 else None
    return t1, t2

def extract_legal_gen1_moves(pokemon_json: dict) -> dict[str, dict]:
    """
    extract all legal gen1 level-up moves for red/blue pokemon
        -only keeps moves where version_group == "red-blue" AND 
         move_learn_method == "level-up"

    given pokemon_json (the full pokemon data from /pokemon/{name}/), returns
    a dict mapping move names to the slug and minimum level learned

    removes need for slugify def (made extra work there) and allows to show 
    title case in the json/interface while still talking to the endpoiunt using 
    the pokeapi slug (instead of going from slug->title->slug)
    """
    legal: dict[str, dict] = {}

    for mv in pokemon_json["moves"]:
        #fetch raw move slug from pokeapi
        slug = mv["move"]["name"]                   #ex wing-attack
        #convert to human readable display name
        display = slug.replace("-", " ").title()    #ex Wing Attack
        # move_name = mv["move"]["name"].replace("-", " ").title()

        #includes all the contexts in which a pokemon learns a move
        for vgd in mv["version_group_details"]:
            #only moves learned in red/blue by level-up
            if vgd["version_group"]["name"] == VERSION_GROUP and \
               vgd["move_learn_method"]["name"] == "level-up":
                level = vgd["level_learned_at"]
                #if the move already exists, keeps whichever level is lower
                #since some pokemon learn same move at varying levels depending on version
                if display not in legal or level < legal[display]["level"]:
                    legal[display] = {"slug": slug, "level": level}
    return legal

# def slugify_move_name(move_name: str) -> str:
#     """
#     convert a human readable move name (ex 'Wing Attack')
#     into the pokeapi move slug (ex 'wing-attack')
#     """

#     slug = move_name.lower().strip()
#     #basic cleanup for gen1 moves with noted issues:
#     slug = slug.replace(" ", "-")
#     slug = slug.replace("'", "")
#     slug = slug.replace(".", "")
#     slug = slug.replace(":", "")

#     return slug 

def fetch_move_details(display_name: str, slug: str):
    """
    fetch detailed move data from pokeapi using the exact move slug

    given display_name and slug, returns a dict to be stored in move.json
    """
    # slug = slugify_move_name(move_name)
    #builds the fill move endpoint using the slug
    url = API_BASE + "move/" + slug + "/"
    #pulls the json for the move
    data = fetch(url)

    return {
        "name": display_name, 
        "type": data["type"]["name"].title(), 
        "power": data["power"],                 #may be None (status moves)
        "accuracy": data["accuracy"],           #may be None
        "pp": data["pp"], 
    }

def main():
    """
    main driver for generating all three json files the rest of the program will rely on

    1. fetch gen1 species list
    2. for each pokemon:
        -pull detailed pokemon data
        -extract stats, types, sprite
        -extract legal gen1 level-up moves, with slug and level
        -store pokemon in monsters.json
        -store readable move list for move_learners.json
        -ensure each move has detailed entry in moves.json
    3. sort all final dictionaries (dex order for monsters/learners, alphabetical for moves)
    4. write json output files to the /data directory
        * monsters.json         - keyed by dex number (e.g., "#001"), with stats/types/sprite
        * moves.json            - keyed by move name (alphabetically sorted)
        * move_learners.json    - mapping each dex number to the list of moves it can learn
    """
    #get all gen1 species names from generation endpoint
    species_names = get_gen1_species_names()

    monsters: dict[str, dict] = {}
    all_moves: dict[str, dict] = {}
    move_learners: dict[str, list[str]] = {}

    for name in species_names:
        #fetch detailed pokemon data by species name
        pokemon_json = fetch(API_BASE + "pokemon/" + name)

        #formats the dex number (1-151 for gen1) as #001-#151
        dex = pokemon_json["id"]
        dex_str = f"#{dex:03d}"

        #extracts types, stats, and the front sprite url
        t1, t2 = extract_types(pokemon_json)
        stats = extract_stats(pokemon_json)
        sprite = pokemon_json["sprites"]["front_default"]

        #get all legal level-up moves for red/blue
        legal_moves = extract_legal_gen1_moves(pokemon_json)

        #build the monster entry to be stored in monsters.json
        monsters[dex_str] = {
            "dex": dex_str, 
            "name": pokemon_json["name"].title(), 
            "type1": t1, 
            "type2": t2, 
            "sprite": sprite, 
            **stats, 
        }

        #store only the move names for this pokemon in move_learners.json
        move_learners[dex_str] = sorted(legal_moves.keys())

        #for each move this pokemon can learn, ensure detailed move data
        for display_name, info in legal_moves.items():
            slug = info["slug"]

            if display_name not in all_moves:
                try:
                    all_moves[display_name] = fetch_move_details(display_name, slug)
                #gives warning if move does not map properly but will output the rest of the JSON file
                except requests.HTTPError as e:
                    print(f"!!! FAILED TO FETCH '{display_name}' (slug '{slug}'): {e}")
                #catch-all to avoid aborting entire run for one bad move
                except Exception as e:
                    print(f"!!! UNEXPECTED ERROR for move '{display_name}' (slug '{slug}'): {e}")                

        #insicates progress to user, shows which pokemon have been loaded
        print(f"Loaded {dex_str} {pokemon_json['name'].title()}")

    #sort monsters and move learners json files numerically (dex order rather than alphabetical name order)
    monsters_sorted = dict(sorted(monsters.items(), key = lambda x: x[0]))
    learners_sorted = dict(sorted(move_learners.items(), key = lambda x: x[0]))

    #sort moves json alphabetically
    moves_sorted = dict(sorted(all_moves.items(), key = lambda x: x[0].lower()))

    #write out json files
    MON_OUT.write_text(json.dumps(monsters_sorted, indent = 2), encoding = "utf-8")
    MOVE_OUT.write_text(json.dumps(moves_sorted, indent = 2), encoding = "utf-8")
    LEARN_OUT.write_text(json.dumps(learners_sorted, indent = 2), encoding = "utf-8")

    #final confirmation to user in terminal 
    print("\nGenerated files: ")
    print("•", MON_OUT)
    print("•", MOVE_OUT)
    print("•", LEARN_OUT)


if __name__ == "__main__":
    #running this file directly (python -m utils.pokeapi_loader) will execute the full data generation pipeline
    main()