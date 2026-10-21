"""
story.py - THE SEALED VAULT (M3A story file, Python)

Run it:   python story.py
Check it: python story_check.py story.py --map

RULES FOR THIS FILE
- One function = one passage.
- A passage function starts with  passage_  (example: passage_start).
- An ending function starts with  ending_   (example: ending_victory).
- A passage ends by calling the next passage. Endings call nothing.
- story_check.py reads these names. Keep the prefixes.

WHAT THIS STORY ACTUALLY DOES
This is the narrative layer on top of the Dungeon RPG in game/, which now
runs on real D&D 5e SRD rules (ability scores, proficiency bonus, hit dice,
AC, levels 1-20, real classes and spellcasting - see game/database.py and
game/models/character.py). You create a character (name, age, class) and
start outside in the wild on the world map - no menu, you actually walk
around with WASD and discover a village or a dungeon by exploring, same as
the dungeon crawl and boss fight later: those are real Tkinter windows, not
simulated text. See brief.md Part 6 for why this is split the way it is.
"""

import os
import sys
import tkinter as tk
from tkinter import messagebox
import random

GAME_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game')
sys.path.insert(0, GAME_DIR)

from database import Database  # noqa: E402
from models.character import Character  # noqa: E402
from models.dungeon import Dungeon  # noqa: E402
from models.world_map import WorldMap  # noqa: E402
from models.enemy import Enemy  # noqa: E402
from models.merchant import Merchant  # noqa: E402
from models.quests import QuestBoard  # noqa: E402
from models.combat import CombatSystem  # noqa: E402
from gui.main_window import GameWindow  # noqa: E402
from gui.combat_window import CombatWindow  # noqa: E402
from gui.skill_window import SkillWindow  # noqa: E402

WORLD_ENCOUNTER_FLAVOR = [
    "You find a quiet clearing and rest a moment. Nothing happens, but it's peaceful.",
    "A merchant's lost coin purse is half-buried in the dirt.",
    "You stumble into brambles. It's not fun, but it's not dangerous either.",
    "Wind carries the sound of distant battle. You press on.",
]

# ---------------------------------------------------------------
# Story-session state. _player/_world_map/_dungeon carry across passages.
# "has a key" is realized as "has Thieves' Tools in inventory" (H1 state
# hook - see brief.md Part 6) rather than a second, separate flag.
# ---------------------------------------------------------------
_window = None
_player = None
_world_map = None
_dungeon = None


# ---------------------------------------------------------------
# Tool (provided): ask()
# Shows numbered options. Repeats until the player enters a valid
# number. Returns the number the player chose (1, 2, 3, ...).
# ---------------------------------------------------------------
def ask(prompt, options):
    while True:
        print()
        print(prompt)
        for number, text in enumerate(options, start=1):
            print(f"  {number}. {text}")
        try:
            raw = input("> ").strip()
        except EOFError:
            raise SystemExit  # input closed: stop the program
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw)
        print(f"Enter a number from 1 to {len(options)}.")


# ---------------------------------------------------------------
# GUI helpers (not passages - story_check.py only looks at functions
# named passage_... / ending_..., so these are invisible to it).
# ---------------------------------------------------------------
def _get_window():
    global _window
    if _window is None:
        _window = GameWindow()
        _window.setup_game_ui()
    return _window


def run_world_map_gui(player, world_map):
    """
    Let the player actually wander the wild (WASD, I for inventory, K for
    skills, Esc to stop exploring) in a real window until they walk into a
    village or town, an uncleared dungeon, or give up. Random-encounter
    nodes trigger a real fight or a flavor moment right there, then
    exploring continues. Returns 'entered_settlement', 'entered_dungeon',
    or 'gave_up'.
    """
    window = _get_window()
    done = tk.BooleanVar(value=False)
    outcome = {'result': 'gave_up'}

    def refresh():
        window.update_world_view(world_map, player)
        window.update_stats_view(player)

    def finish(result):
        outcome['result'] = result
        done.set(True)

    def handle_world_encounter(node):
        if world_map.roll_encounter_is_fight():
            enemy = Enemy.get_random_enemy(node.tier)
            player.reset_combat_flags()
            combat_system = CombatSystem()
            messagebox.showinfo("Encounter", f"A {enemy.name} ambushes you on the road!")

            def on_combat_end(result):
                node.cleared = True
                refresh()

            CombatWindow(window, player, enemy, combat_system, on_combat_end)
        else:
            node.cleared = True
            messagebox.showinfo("Encounter", random.choice(WORLD_ENCOUNTER_FLAVOR))

    def on_move(direction):
        if not world_map.move_player(direction):
            return
        refresh()
        node = world_map.get_current_node()
        if node.kind in ('village', 'town'):
            finish('entered_settlement')
        elif node.kind == 'dungeon' and not node.cleared:
            finish('entered_dungeon')
        elif node.kind == 'encounter' and not node.cleared:
            handle_world_encounter(node)

    def on_inventory(_event=None):
        window.show_inventory_ui(player)

    def on_skills(_event=None):
        SkillWindow(window, player, on_change=refresh)

    def on_camp(_event=None):
        if player.current_health >= player.max_health:
            messagebox.showinfo("Camp", "You're already at full health.")
            return
        healed = player.camp_rest()
        refresh()
        messagebox.showinfo(
            "Camp",
            f"You make camp for the night and recover {healed} HP "
            f"({player.current_health}/{player.max_health}).\n"
            "A proper bed at a village or town will restore you fully."
        )

    def on_scout(_event=None):
        found = world_map.scout_nearby()
        refresh()
        if not found:
            messagebox.showinfo("Scout", "You survey the surrounding area and find nothing new of note.")
            return
        tiers = ", ".join(f"Tier {node.tier}" for node in found)
        messagebox.showinfo("Scout", f"You spot {len(found)} potential encounter site(s) nearby: {tiers}.")

    def on_give_up(_event=None):
        if messagebox.askyesno("Stop Exploring", "End your journey here?"):
            finish('gave_up')

    bindings = {
        '<w>': lambda e: on_move('north'),
        '<s>': lambda e: on_move('south'),
        '<a>': lambda e: on_move('west'),
        '<d>': lambda e: on_move('east'),
        '<i>': on_inventory,
        '<k>': on_skills,
        '<c>': on_camp,
        '<r>': on_scout,
        '<Escape>': on_give_up,
    }
    for seq, handler in bindings.items():
        window.bind(seq, handler)

    messagebox.showinfo(
        "The Wild",
        "WASD to walk, I for inventory, K for skills, C to camp, R to scout, Esc to stop exploring."
    )
    refresh()
    window.wait_variable(done)

    for seq in bindings:
        window.unbind(seq)

    return outcome['result']


def run_dungeon_gui(player, dungeon):
    """
    Let the player actually walk the dungeon (WASD, E to interact, Esc to
    leave) in a real window until they reach the locked vault, die, or
    leave. Returns 'reached_vault', 'defeated', or 'fled'.
    """
    window = _get_window()
    combat_system = CombatSystem()
    done = tk.BooleanVar(value=False)
    outcome = {'result': 'fled'}

    def refresh():
        window.update_game_view(dungeon, player)
        window.update_stats_view(player)

    def finish(result):
        outcome['result'] = result
        done.set(True)

    def start_fight(enemy):
        player.reset_combat_flags()

        def on_combat_end(result):
            room = dungeon.get_current_room()
            if result == 'victory':
                room.is_cleared = True
                room.enemies = []
            elif result == 'fled':
                dungeon.move_player_random_adjacent()
            refresh()
            if result == 'defeat':
                finish('defeated')

        CombatWindow(window, player, enemy, combat_system, on_combat_end)

    def on_move(direction):
        if dungeon.move_player(direction):
            room = dungeon.get_current_room()
            if room.enemies and not room.is_cleared:
                start_fight(room.enemies[0])
            refresh()

    def on_interact():
        room = dungeon.get_current_room()
        if room.has_treasure and not room.treasure_looted:
            db = Database()
            loot_lines = []
            for drop_type, value in dungeon.get_treasure_loot():
                if drop_type == 'copper':
                    player.money += value
                    loot_lines.append(f"+ {value} copper")
                else:
                    item = db.get_item(value)
                    if item:
                        player.add_item(item)
                        loot_lines.append(f"+ {item['name']}")
            room.treasure_looted = True
            refresh()
            messagebox.showinfo("Treasure", "You found treasure!\n\n" + "\n".join(loot_lines))
        elif room.has_merchant and not room.merchant_visited:
            merchant = Merchant(max_tier=dungeon.tier)
            window.show_merchant_ui(player, merchant, on_close=lambda: setattr(room, 'merchant_visited', True))
        elif room.is_end_room:
            finish('reached_vault')
        else:
            messagebox.showinfo("Interact", "There's nothing to interact with here.")

    def on_inventory(_event=None):
        window.show_inventory_ui(player)

    def on_skills(_event=None):
        SkillWindow(window, player, on_change=refresh)

    def on_leave(_event=None):
        if messagebox.askyesno("Leave Dungeon", "Climb back to the surface?"):
            finish('fled')

    bindings = {
        '<w>': lambda e: on_move('north'),
        '<s>': lambda e: on_move('south'),
        '<a>': lambda e: on_move('west'),
        '<d>': lambda e: on_move('east'),
        '<e>': lambda e: on_interact(),
        '<i>': on_inventory,
        '<k>': on_skills,
        '<Escape>': on_leave,
    }
    for seq, handler in bindings.items():
        window.bind(seq, handler)

    messagebox.showinfo("Dungeon", "WASD to move, E to interact, I for inventory, K for skills, Esc to leave.")
    refresh()
    window.wait_variable(done)

    for seq in bindings:
        window.unbind(seq)

    return outcome['result']


def run_boss_fight_gui(player, enemy):
    """
    Run one real combat window against a boss. Returns 'victory', 'defeat',
    or 'fled'.
    """
    window = _get_window()
    combat_system = CombatSystem()
    player.reset_combat_flags()
    done = tk.BooleanVar(value=False)
    outcome = {'result': 'fled'}

    def on_combat_end(result):
        outcome['result'] = result
        done.set(True)

    CombatWindow(window, player, enemy, combat_system, on_combat_end)
    window.wait_variable(done)
    return outcome['result']


def choose_class():
    db = Database()
    classes = db.get_all_classes()
    keys = list(classes.keys())
    blurbs = {
        'fighter': "Fighter - tough, armored, and gets extra attacks as you level. No spells.",
        'rogue': "Rogue - fast and sneaky, Sneak Attack adds bonus damage. No spells.",
        'wizard': "Wizard - fragile but casts Fire Bolt and Magic Missile with real spell slots.",
        'cleric': "Cleric - sturdy and casts Sacred Flame and Cure Wounds with real spell slots.",
    }
    choice = ask("Choose your class:", [blurbs.get(k, k) for k in keys])
    return keys[choice - 1]


# ---------------------------------------------------------------
# Passages
# ---------------------------------------------------------------
def passage_start():
    global _player, _world_map
    print("=== THE SEALED VAULT ===")
    name = input("\nWhat is your name, adventurer? > ").strip() or "Adventurer"
    class_key = choose_class()
    _player = Character(name=name, age=20, class_key=class_key)

    print(f"\n{_player.name} the {_player.title}, level 1.")
    scores = ", ".join(f"{k[:3].upper()} {v}" for k, v in _player.ability_scores.items())
    print(f"Ability scores: {scores}")
    print(f"\nYou wake up alone in the wild, miles from anywhere, with nothing")
    print("but your gear and stories of a vault that's never been opened.")

    _world_map = WorldMap()
    passage_explore()


def passage_explore():
    outcome = run_world_map_gui(_player, _world_map)
    if outcome == 'entered_settlement':
        passage_village()
    elif outcome == 'entered_dungeon':
        passage_dungeon_level()
    else:
        ending_fled()


def passage_village():
    node = _world_map.get_current_node()
    was_hurt = _player.current_health < _player.max_health
    if node.kind == 'town':
        print("\nYou find a proper town - a market square, an inn, a healer's tent.")
    else:
        print("\nYou find a small village. A merchant waves you over to look at their wares.")
    _player.long_rest()
    if was_hurt:
        print("You rest here - HP and spell slots fully restored.")

    window = _get_window()
    merchant = Merchant()
    quest_board = QuestBoard()
    done = tk.BooleanVar(value=False)
    window.show_merchant_ui(_player, merchant, on_close=lambda: done.set(True), quest_board=quest_board)
    window.update_stats_view(_player)
    window.wait_variable(done)

    print("\nYou shoulder your gear and head back out into the wild.")
    passage_explore()


def passage_dungeon_level():
    global _dungeon
    node = _world_map.get_current_node()
    print(f"\nYou find a dungeon entrance (tier {node.tier}) and descend. Torchlight")
    print("flickers over damp stone and old bones.")
    _dungeon = Dungeon(tier=node.tier)
    outcome = run_dungeon_gui(_player, _dungeon)
    if outcome == 'reached_vault':
        passage_vault_door()
    elif outcome == 'defeated':
        ending_defeat()
    else:
        ending_fled()


def passage_vault_door():
    print("\nA vault door blocks the way, etched with old warnings. It's locked tight.")
    if _player.has_item_named("Thieves' Tools"):
        choice = ask("What do you do?", [
            "Pick the lock with your Thieves' Tools",
            "Search the dungeon for another way in",
        ])
        if choice == 1:
            if _dungeon.try_unlock_vault(_player):
                print("\nThe lock clicks open. Cold air breathes out from the dark inside.")
                passage_boss_fight()
            else:
                print("\nYour tools slip and snap in the lock. That way's blocked now.")
                passage_find_key()
        else:
            passage_find_key()
    else:
        print("\nYou have no lockpicking tools. This door won't budge without some.")
        passage_find_key()


def passage_find_key():
    print("\nYou backtrack through the dungeon, checking side passages for tools.")
    if not _player.has_item_named("Thieves' Tools"):
        tools = Database().get_item("Thieves' Tools")
        if tools:
            _player.add_item(tools)
    print("You find a set of thieves' tools wedged behind a loose stone!")
    passage_vault_door()


def passage_boss_fight():
    print("\nThe vault's guardian rises to meet you. This is the final fight.")
    boss = _dungeon.get_vault_boss()
    outcome = run_boss_fight_gui(_player, boss)
    if outcome == 'victory':
        ending_victory()
    elif outcome == 'defeat':
        ending_defeat()
    else:
        ending_fled()


# ---------------------------------------------------------------
# Endings
# ---------------------------------------------------------------
def ending_victory():
    print(f"\n{_player.name} stands over the fallen guardian, vault treasure in hand.")
    print(f"The dungeon is cleared. You are victorious, at level {_player.level}!")


def ending_defeat():
    print(f"\n{_player.name} falls in the dark below the vault door.")
    print("The dungeon claims another adventurer.")


def ending_fled():
    print(f"\n{_player.name} walks away into the wild, breathing hard.")
    print("The vault's secrets will have to wait for another day.")


# ---------------------------------------------------------------
# Main
# ---------------------------------------------------------------
def main():
    playing = True
    while playing:
        passage_start()
        print("\nThe end.")
        choice = ask("Play again?", ["Yes", "No"])
        if choice == 2:
            playing = False

    if _window is not None:
        _window.destroy()


if __name__ == "__main__":
    main()
