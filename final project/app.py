"""
Author: L. Flygare
Description: the streamlit front-end for pokebattle final project
             -provides a complete web-based user interface for a gen1 pokemon battle simulator
             - this module is responsible for:
                -loading preprocessed pokemon data from json files
                -providing an interactive team builder (up to 6 pokemon per team)
                -acting as an entry points into the battle engine
                -displaying pokemon sprites, stats, hp bars, move lsits, team statuses, and battle logs
                -routing between team builder and battle pages
             -all game logic is inside:
                core/
                    battle_engine.py    -turn flow, pp, KO logic
                    damage.py           -actual damage calculations
                    models.py           -Monster and Move dataclasses
"""

import random
import streamlit as st
from core.json_loaders import (
    load_monsters_json,
    load_moves_json, 
    load_move_learners_json, 
)
from core.battle_engine import BattleState, start_battle, apply_move


#-----------------------------
# data loading with caching
#-----------------------------
@st.cache_data
def load_data():
    """
    load all static json data and memoize it so streamlit does not reload from disk every run

    streamlit caching ensures that json files are read only once per application session
        -improves performance during UI reruns

    returns:
        monsters  : dict[str, Monster]
        moves     : dict[str, Move]
        learners  : dict[str, list[str]]
    """
    monsters = load_monsters_json()
    moves = load_moves_json()
    learners = load_move_learners_json()

    return monsters, moves, learners


#-----------------------------
# session state initialization
#-----------------------------
def init_session_state():
    """
    create required session variables if they do not exist

    ensures persistent team selections, abttle state, and mode across streamlit reruns
    """
    if "team_p1" not in st.session_state:
        st.session_state.team_p1 = []

    if "team_p2" not in st.session_state:
        st.session_state.team_p2 = []

    if "battle_mode" not in st.session_state:
        st.session_state.battle_mode = "CPU"    #default to CPU opponent

    if "battle" not in st.session_state:
        st.session_state.battle = None


#-----------------------------
# team builder page and helper functions
#-----------------------------
def set_preview_from_p1():
    """
    update preview panel to show currently selected p1 pokemon
    """
    st.session_state.preview_dex = st.session_state.get("p1_selector")

def set_preview_from_p2():
    """
    update preview panel to show currently selected p2 pokemon
    """
    st.session_state.preview_dex = st.session_state.get("p2_selector")

def team_builder_page(monsters, moves, learners):
    """
    display the team builder interface

    features:
        -build teams for both players
        -view stats and sprites and moves
        -add/remove from teams (teams limited to 6 total pokemon)
        -preview pokemon details without adding them to a team

    behavior:
        -player 1 always builds team manually
        -if battle_mode == "PVP", player 2 manually builds their team
        -if battle_mode == "CPU", player 2 team generated randomly  from pokemon not already selected by p1
    """
    st.header("Team Builder")

    dex_list = sorted(monsters.keys())  
    name_map = {dex: monsters[dex].name for dex in dex_list}

    #default preview to the first pokemon in the dex at load
    if "preview_dex" not in st.session_state:
        st.session_state.preview_dex = dex_list[0]

    mode = st.session_state.battle_mode     #CPU or PVP

    #3-column layout
    #P1 builder | Pokémon preview | P2 builder
    col_p1, col_info, col_p2 = st.columns([1.5, 1.2, 1.5])

    #player 1 team builder
    with col_p1:
        st.subheader("Player 1 Team")

        p1_choice = st.selectbox(
            "Choose Pokemon for Player 1", 
            dex_list, 
            format_func = lambda d: f"{d} {name_map[d]}", 
            key = "p1_selector", 
            on_change = set_preview_from_p1, 
        )

        if st.button("Add to Player 1 Team"):
            if p1_choice in st.session_state.team_p1:
                st.info("That Pokémon is already on Player 1's team.")
            elif len(st.session_state.team_p1) >= 6:
                st.warning("Player 1 team is full (max 6).")
            else:
                st.session_state.team_p1.append(p1_choice)

        #show p1 team list with remove buttons
        if not st.session_state.team_p1:
            st.write("Player 1 has no Pokemon selected yet.")
        else:
            for i, dex in enumerate(st.session_state.team_p1):
                mon = monsters[dex]
                cols = st.columns([4, 1])
                cols[0].write(f"{i + 1}. {dex} {mon.name}")
                if cols[1].button("Remove", key = f"p1_rm_{i}"):
                    st.session_state.team_p1.pop(i)
                    st.rerun()

    #pokemon preview panel
    with col_info:
        st.subheader("Pokemon Info")

        #determine which pokemon to preview
        #priority = whichever selector was last changed
        preview_dex = st.session_state.get("preview_dex")

        if preview_dex:
            mon = monsters[preview_dex]
            st.subheader(f"{mon.dex} {mon.name}")

            #sprite
            if hasattr(mon, "sprite") and mon.sprite:
                st.image(mon.sprite, width = 120)

            #type(s)
            type_text = mon.type1 if not mon.type2 else f"{mon.type1}/{mon.type2}"
            st.write(f"Type: **{type_text}**")

            #base stats
            st.write(
                f"HP: {mon.hp} | "
                f"ATK: {mon.atk} | DEF: {mon.dfn} | "
                f"SP.ATK: {mon.sp_atk} | SP.DEF: {mon.sp_dfn} | SPD: {mon.speed}"
            )

            moves_for_mon = learners.get(preview_dex, [])

            if moves_for_mon:
                st.markdown("### Possible Level-up Moves: \n### Gen 1/Red-Blue")
                for mv_name in moves_for_mon[:15]:  #up to 15 moves shown, allows a buffer so all moves shold be shown for all pokemon
                    mv = moves.get(mv_name)
                    if mv is not None:
                        pow_txt = "-" if mv.power is None else str(mv.power)
                        acc_txt = "-" if mv.accuracy is None else str(mv.accuracy)
                        st.write(
                            f"- **{mv.name}** "
                            f"(Type: {mv.type}, Pow: {pow_txt}, Acc: {acc_txt}, PP: {mv.pp})"
                        )
                    else:
                        #fallback if something exists in learners but not in moves.json
                        st.write(f"- **{mv_name}**")
            else:
                st.markdown("### Possible Level-up Moves")
                st.write("No moves found for this Pokemon.")
        else:
            st.write("Select a Pokemon to view its information.")

    #player 2/CPU team builder
    with col_p2:
        if mode == "PVP":
            st.subheader("Player 2 Team")

            p2_choice = st.selectbox(
                "Choose Pokemon for Player 2", 
                dex_list, 
                format_func = lambda d: f"{d} {name_map[d]}", 
                key = "p2_selector", 
                on_change = set_preview_from_p2, 
            )
            
            if st.button("Add to Player 2 Team"):
                if p2_choice in st.session_state.team_p2:
                    st.info("That Pokémon is already on Player 2's team.")
                elif len(st.session_state.team_p2) >= 6:
                    st.warning("Player 2 team is full (max 6).")
                else:
                    st.session_state.team_p2.append(p2_choice)

            #show p2 team list with remove buttons
            if not st.session_state.team_p2:
                st.write("Player 2 has no Pokemon selected yet.")
            else:
                for i, dex in enumerate(st.session_state.team_p2):
                    mon = monsters[dex]
                    cols = st.columns([4, 1])
                    cols[0].write(f"{i + 1}. {dex} {mon.name}")
                    if cols[1].button("Remove", key = f"p2_rm_{i}"):
                        st.session_state.team_p2.pop(i)
                        st.rerun()

        #mode == "CPU"
        else:   
            st.subheader("Computer Team")

            #show current CPU team
            if not st.session_state.team_p2:
                st.write("Computer team not generated yet.")
            else:
                for i, dex in enumerate(st.session_state.team_p2):
                    mon = monsters[dex]
                    st.write(f"{i + 1}. {dex} {mon.name}")

            #random CPU team that does not share members with p1 team, dependent composition at time of roll
            if st.button("Randomize Computer Team"):
                available = [d for d in dex_list if d not in st.session_state.team_p1]
                if not available:
                    st.warning("No Pokemon available to build a CPU team.")
                else:
                    team_size = min(6, len(available))
                    st.session_state.team_p2 = random.sample(available, k = team_size)
                    st.rerun()

    #guidance at bottom of screen
    st.write("---")
    if mode == "PVP":
        st.caption("Both players should have at least one Pokémon before starting a battle.")
    else:
        st.caption("Player 1 should have at least one Pokémon.")
        st.caption("Computer team can be randomized to not share the same Pokemon as Player 1. If you wish to have the same Pokemon as the Computer, roll for the Computer and then select your team.")


#-----------------------------
# battle page and helper functions 
#-----------------------------
def _render_team_status(title: str, team: list, hp_list: list[int], active_idx: int):
    """
    render a team status panel in the sidebar
    
    displays:
        -active pokemon highlighted
        -fainted pokemon grayed out and marked as FNT
        -remaining hp shown as current/max
    """
    st.sidebar.subheader(title)

    for i, mon in enumerate(team):
        curr_hp = hp_list[i]
        max_hp = mon.hp

        is_active = (i == active_idx)
        is_fainted = (curr_hp <= 0)

        #build label for active pokemon
        arrow = "▶ " if is_active else "  "
        hp_text = f"{curr_hp}/{max_hp}"

        #simple html to make fainted pokemon appear grayed out
        if is_fainted:
            st.sidebar.markdown(
                f"<span style='color:#888;'>{arrow}{mon.name}  {hp_text}  (FNT)</span>",
                unsafe_allow_html = True
            )
        elif is_active:
            st.sidebar.markdown(f"**{arrow}{mon.name}  {hp_text}**")
        else:
            st.sidebar.write(f"{arrow}{mon.name}  {hp_text}")

    st.sidebar.write("")    #for spacing

def build_default_moves_for_dex(dex: str, moves: dict, learners:dict, max_moves: int = 4):
    """
    build a default moveset for a pokemon

    rules:
        -include at least one dex legal damaging move if possible
        -fill remaining slots with any other dex legal moves
        -limit move set to maximum of 'max_moves'

    helps prevent battles where neither side can deal damage
        -allows fallback to Struggle when needed
    """
    move_names = learners.get(dex, [])
    #resolve to Move objects (skip any missing from moves.json)
    resolved = [moves[m] for m in move_names if m in moves]

    damaging = [m for m in resolved if m.power is not None]
    status = [m for m in resolved if m.power is None]

    chosen: list = []

    #guarantee at least one damaging move, if pokemon has one, to mitigate stalemates
    if damaging:
        chosen.append(damaging[0])

    #fill remaining slots (prefer damaging first, then status)
    for m in damaging[1:]:
        if len(chosen) >= max_moves:
            break
        chosen.append(m)

    return chosen

def battle_page(monsters, moves, learners):
    """
    display the battle interface

    features:
        -use full teams for each player (up to 6 pokemon per side)
        -auto switching when pokemon faints
        -CPU controlled opponent in CPU mode
        -dispays active pokemon's sprites, hp bars, and move options
        -real-time battle log

    battle ends when one side has no remaining pokemon with hp > 0 
    """
    st.header("Battle")
    mode = st.session_state.battle_mode     #CPU or PVP 
    
    #validate both teams have at least one pokemon
    if not st.session_state.team_p1:
        st.warning("Player 1 needs at least one Pokemon on their team.")
        return
    
    if not st.session_state.team_p2:
        if mode == "CPU":
            st.warning("Computer team not generated. Go to Team Builder and click 'Randomize Computer Team'.")
        else: 
            st.warning("Player 2 needs at least one Pokemon on their team.")
        return

    #initialize a new battle if one does not exist
    if st.session_state.battle is None:
        #build full temas from selected dex numbers
        team_a = [monsters[d] for d in st.session_state.team_p1]
        team_b = [monsters[d] for d in st.session_state.team_p2]

        #up to 4 moves per pokemon, per team member
        moves_a = []
        moves_b = []

        for dex in st.session_state.team_p1:
            moves_a.append(build_default_moves_for_dex(dex, moves, learners))

        for dex in st.session_state.team_p2:
            moves_b.append(build_default_moves_for_dex(dex, moves, learners))

        st.session_state.battle = start_battle(team_a, team_b, moves_a, moves_b)

    battle: BattleState = st.session_state.battle

    #show both teams in a sidebar
    p2_label = "Player 2 Team" if mode == "PVP" else "Computer Team"
    _render_team_status("Player 1 Team", battle.team_a, battle.hp_a, battle.active_a)
    _render_team_status(p2_label, battle.team_b, battle.hp_b, battle.active_b)

    #CPU autoturn logic - for active B pokemon
    #if playing against computer and its computer's turn, automatically picka random move (with pp remaining) and us it
    if mode == "CPU" and battle.winner is None and battle.next_actor == "B":
        current_moves = battle.moves_b[battle.active_b]
        #choose from moves with remaining pp
        available_indices = [
            i for i, mv in enumerate(current_moves)
            if mv.pp is None or mv.pp > 0
        ]
        if not available_indices:
            chosen_index = 0    #fallback (not likely but just in case)
        else:
            chosen_index = random.choice(available_indices)

        battle = apply_move(battle, chosen_index)
        st.session_state.battle = battle

    #display pokemon info, sprites, and hp bars
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Player 1: {battle.a.name}")
        if getattr(battle.a, "sprite", None):
            st.image(battle.a.sprite, width = 120)
        st.progress(battle.hp_current_a / battle.a.hp)
        st.write(f"{battle.hp_current_a}/{battle.a.hp} HP")

    with col2:
        label_p2 = "Player 2" if mode == "PVP" else "Computer"
        st.subheader(f"{label_p2}: {battle.b.name}")
        if getattr(battle.b, "sprite", None):
            st.image(battle.b.sprite, width = 120)
        st.progress(battle.hp_current_b / battle.b.hp)
        st.write(f"{battle.hp_current_b}/{battle.b.hp} HP")

    st.write("---")

    #if battle is ongoing, show move options for the active (human) player
    if battle.winner is None:
        actor_tag = battle.next_actor   #A or B
        if actor_tag == "A":
            actor = battle.a
            actor_moves = battle.moves_a[battle.active_a]
            label = "Player 1"
        else:
            actor = battle.b
            actor_moves = battle.moves_b[battle.active_b]
            label = "Player 2" if mode == "PVP" else "Computer"

        st.subheader(f"{label}'s Turn: {actor.name}")

        cols = st.columns(4)

        for idx, mv in enumerate(actor_moves):
            pow_txt = "-" if mv.power is None else str(mv.power)
            acc_txt = "-" if mv.accuracy is None else str(mv.accuracy)
            pp_txt = "-" if mv.pp is None else str(mv.pp)

            button_label = (
                f"{mv.name}\n"
                f"Pow: {pow_txt}  Acc: {acc_txt}\n"
                f"PP: {pp_txt}"
            )

            #utilize a unique key to avoid button collisions between turns
            if cols[idx].button(button_label, key = f"mv_{battle.turn}_{actor_tag}_{idx}"):
                st.session_state.battle = apply_move(battle, idx)
                st.rerun()

    #if battle has ended, show result and reset option
    else:
        if battle.winner == "Draw":
            st.success("Battle Over - It's a draw!")
        elif battle.winner == "A":
            st.success(f"Battle Over - {battle.a.name} (Player 1) wins!")
        else:
            label_p2 = "Player 2" if mode == "PVP" else "Computer"
            st.success(f"Battle Over - {battle.b.name} ({label_p2}) wins!")

        if st.button("Start New Battle"):
            st.session_state.battle = None
            st.rerun()

    #battle log
    st.write("---")
    st.subheader("Battle Log")

    for line in battle.log:
        st.write(line)


#-----------------------------
# app entry point
#-----------------------------
def main():
    """
    entry point for streamlit application

    initializes session state, loads data, and routes between the Team Builder and Battle pages.
    """
    st.set_page_config(page_title = "PokeBattle (Gen 1)", layout = "wide")

    init_session_state()
    monsters, moves, learners = load_data()

    #sidebar nav and mode selection
    st.sidebar.title("PokeBattle Menu")

    st.sidebar.subheader("Battle Mode")
    mode_label = st.sidebar.radio("Mode: ", ["vs Computer", "vs Player 2"])
    st.session_state.battle_mode = "CPU" if mode_label == "vs Computer" else "PVP"

    page = st.sidebar.radio("Go to: ", ["Team Builder", "Battle"])

    if page == "Team Builder":
        #reset any existing battle if teams are being changed
        st.session_state.battle = None
        team_builder_page(monsters, moves, learners)
    else:
        battle_page(monsters, moves, learners)



if __name__ == "__main__":
    main()