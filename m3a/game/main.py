# main.py
import tkinter as tk
from tkinter import ttk, simpledialog
from gui import dialogs as messagebox
import logging
import json
import os
import random
from datetime import datetime
from typing import Optional, Dict, Any

from config import WINDOW_WIDTH, WINDOW_HEIGHT, SAVE_DIR
from database import Database
from models.character import Character
from models.enemy import Enemy
from models.dungeon import Dungeon
from models.world_map import WorldMap
from models.merchant import Merchant
from models.quests import QuestBoard
from models.combat import CombatSystem
from gui.main_window import GameWindow
from gui.combat_window import CombatWindow
from gui.skill_window import SkillWindow
from gui.layout import fit_window

WORLD_ENCOUNTER_FLAVOR = [
    "You find a quiet clearing and rest a moment. Nothing happens, but it's peaceful.",
    "A merchant's lost coin purse is half-buried in the dirt.",
    "You stumble into brambles. It's not fun, but it's not dangerous either.",
    "Wind carries the sound of distant battle. You press on.",
]


class Game:
    """
    Top-level game controller. The player starts on the world map and travels
    between dungeon, village, and random-encounter instances from there.
    """
    def __init__(self):
        self.db = Database()
        self.window: Optional[GameWindow] = None
        self.player: Optional[Character] = None
        self.world_map: Optional[WorldMap] = None
        self.current_dungeon: Optional[Dungeon] = None
        self.merchant: Optional[Merchant] = None
        self.quest_board: Optional[QuestBoard] = None
        # 'menu', 'world_map', 'dungeon', 'combat', 'inventory', 'skills'
        self.game_state = 'menu'
        self.combat_system = CombatSystem()
        self.combat_context: Optional[str] = None  # 'dungeon', 'vault_boss', or 'encounter'

    def start(self):
        self.window = GameWindow()
        self.setup_menu()
        self.bind_keys()
        self.window.mainloop()

    def bind_keys(self):
        self.window.bind('<w>', lambda e: self.handle_movement('north'))
        self.window.bind('<s>', lambda e: self.handle_movement('south'))
        self.window.bind('<a>', lambda e: self.handle_movement('west'))
        self.window.bind('<d>', lambda e: self.handle_movement('east'))
        self.window.bind('<i>', lambda e: self.handle_inventory())
        self.window.bind('<e>', lambda e: self.handle_interact())
        self.window.bind('<k>', lambda e: self.handle_skills())
        self.window.bind('<c>', lambda e: self.handle_camp())
        self.window.bind('<r>', lambda e: self.handle_scout())
        self.window.bind('<Escape>', lambda e: self.handle_pause())
        self.window.bind('<Control-s>', lambda e: self.save_game())
        self.window.bind('<Control-l>', lambda e: self.load_game())
        self.window.bind('<Control-n>', lambda e: self.new_game())

        # Virtual events fired by the sidebar buttons and the File menu
        self.window.bind('<<NewGame>>', lambda e: self.new_game())
        self.window.bind('<<SaveGame>>', lambda e: self.save_game())
        self.window.bind('<<LoadGame>>', lambda e: self.load_game())
        self.window.bind('<<QuitGame>>', lambda e: self.window.quit())
        self.window.bind('<<ToggleInventory>>', lambda e: self.handle_inventory())
        self.window.bind('<<Interact>>', lambda e: self.handle_interact())
        self.window.bind('<<ToggleSkills>>', lambda e: self.handle_skills())
        self.window.bind('<<Camp>>', lambda e: self.handle_camp())
        self.window.bind('<<Scout>>', lambda e: self.handle_scout())

    def setup_menu(self):
        self.window.setup_start_screen()

    def new_game(self):
        dialog = tk.Toplevel(self.window)
        dialog.title("Create Character")
        dialog.transient(self.window)
        fit_window(dialog, 320, 320, parent=self.window)
        dialog.grab_set()

        ttk.Label(dialog, text="Character Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)

        ttk.Label(dialog, text="Age:").pack(pady=5)
        age_entry = ttk.Entry(dialog)
        age_entry.pack(pady=5)

        ttk.Label(dialog, text="Class:").pack(pady=5)
        class_keys = list(self.db.get_all_classes().keys())
        class_var = tk.StringVar(value=class_keys[0])
        class_menu = ttk.OptionMenu(dialog, class_var, class_keys[0], *class_keys)
        class_menu.pack(pady=5)

        def create_character():
            name = name_entry.get()
            try:
                age = int(age_entry.get())
                if 1 <= age <= 100:
                    dialog.destroy()
                    self.player = Character(name=name, age=age, class_key=class_var.get())
                    self.world_map = WorldMap()
                    self.current_dungeon = None
                    self.game_state = 'world_map'
                    self.start_game()
                else:
                    messagebox.showerror("Error", "Age must be between 1 and 100")
            except ValueError:
                messagebox.showerror("Error", "Age must be a number")

        ttk.Button(dialog, text="Create", command=create_character).pack(pady=20)

    def load_game(self):
        try:
            save_files = [f for f in os.listdir(SAVE_DIR) if f.endswith('.json')]
            if not save_files:
                messagebox.showinfo("Load Game", "No saved games found.")
                return

            save_file = simpledialog.askstring(
                "Load Game",
                "Enter save file name:",
                initialvalue=save_files[0]
            )

            if not save_file:
                return

            with open(os.path.join(SAVE_DIR, save_file), 'r') as f:
                save_data = json.load(f)

            if not self.validate_save_data(save_data):
                raise ValueError("Invalid save file format")

            self.player = Character(**save_data['player'])
            self.world_map = WorldMap(**save_data['world_map'])
            self.current_dungeon = Dungeon(**save_data['dungeon']) if save_data.get('dungeon') else None
            self.game_state = save_data.get('game_state', 'world_map')
            self.start_game()

        except Exception as e:
            logging.error(f"Error loading game: {str(e)}")
            messagebox.showerror("Error", f"Failed to load game: {str(e)}")

    def validate_save_data(self, save_data: Dict[str, Any]) -> bool:
        required_keys = {'player', 'world_map'}
        player_keys = {'name', 'age', 'class_key', 'level', 'xp', 'current_health', 'inventory'}

        if not all(key in save_data for key in required_keys):
            return False
        if not all(key in save_data['player'] for key in player_keys):
            return False
        if not all(key in save_data['world_map'] for key in {'size', 'player_pos', 'nodes'}):
            return False
        return True

    def save_game(self):
        try:
            if not self.player or not self.world_map:
                raise ValueError("No active game to save")

            save_data = {
                'player': self.player.to_dict(),
                'game_state': self.game_state,
                'world_map': self.world_map.to_dict(),
                'dungeon': self.current_dungeon.to_dict() if self.current_dungeon else None,
            }

            filename = f"{self.player.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(os.path.join(SAVE_DIR, filename), 'w') as f:
                json.dump(save_data, f, indent=2)

            logging.info(f"Game saved: {filename}")
            messagebox.showinfo("Save Game", "Game saved successfully!")

        except Exception as e:
            logging.error(f"Error saving game: {str(e)}")
            messagebox.showerror("Error", f"Failed to save game: {str(e)}")

    def start_game(self):
        self.window.clear_menu()
        self.window.setup_game_ui()
        self.update_display()

    def update_display(self):
        if not self.window or not self.player:
            return
        if self.game_state == 'dungeon' and self.current_dungeon:
            self.current_dungeon.view_range = self._effective_view_range()
            self.window.update_game_view(self.current_dungeon, self.player)
        elif self.world_map:
            self.window.update_world_view(self.world_map, self.player)
        self.window.update_stats_view(self.player)

    def _effective_view_range(self) -> int:
        from config import VISIBLE_RANGE
        bonus = 2 if self.player.has_item_named('Torch') else 0
        return VISIBLE_RANGE + bonus

    # ------------------------------------------------------------------
    # Movement and interaction
    # ------------------------------------------------------------------
    def handle_movement(self, direction: str):
        if self.game_state == 'world_map' and self.world_map:
            if self.world_map.move_player(direction):
                self.update_display()
                self._on_world_node_entered()
        elif self.game_state == 'dungeon' and self.current_dungeon:
            if self.current_dungeon.move_player(direction):
                current_room = self.current_dungeon.get_current_room()
                if current_room.enemies and not current_room.is_cleared:
                    self.combat_context = 'dungeon'
                    self.start_combat(current_room.enemies[0])
                self.update_display()

    def _on_world_node_entered(self):
        node = self.world_map.get_current_node()
        if node.kind in ('village', 'town'):
            self.enter_settlement(node.kind)
        elif node.kind == 'dungeon' and not node.cleared:
            self.enter_dungeon(node.tier)
        elif node.kind == 'encounter' and not node.cleared:
            self.trigger_world_encounter(node.tier)

    def enter_settlement(self, kind: str):
        if not self.player:
            return
        was_hurt = self.player.current_health < self.player.max_health
        self.player.long_rest()
        self.merchant = Merchant()
        self.quest_board = QuestBoard()
        self.window.show_merchant_ui(self.player, self.merchant, quest_board=self.quest_board)
        label = "town" if kind == 'town' else "village"
        if was_hurt:
            messagebox.showinfo(label.title(), f"You rest at the {label} - HP and spell slots fully restored.")

    def enter_dungeon(self, tier: int):
        self.current_dungeon = Dungeon(tier=tier)
        self.current_dungeon.view_range = self._effective_view_range()
        self.game_state = 'dungeon'
        self.update_display()

    def leave_dungeon(self):
        """Return to the world map, abandoning the current dungeon instance."""
        self.current_dungeon = None
        self.game_state = 'world_map'
        self.update_display()

    def trigger_world_encounter(self, tier: int):
        if self.world_map.roll_encounter_is_fight():
            enemy = Enemy.get_random_enemy(tier)
            self.combat_context = 'encounter'
            messagebox.showinfo("Encounter", f"A {enemy.name} ambushes you on the road!")
            self.start_combat(enemy)
        else:
            messagebox.showinfo("Encounter", random.choice(WORLD_ENCOUNTER_FLAVOR))
            self.world_map.get_current_node().cleared = True

    def handle_interact(self):
        if self.game_state != 'dungeon' or not self.current_dungeon:
            return
        room = self.current_dungeon.get_current_room()

        if self.current_dungeon.player_pos == (0, 0):
            if messagebox.askyesno("Leave Dungeon", "Leave the dungeon and return to the world map?"):
                self.leave_dungeon()
        elif room.has_treasure and not room.treasure_looted:
            loot = self.current_dungeon.get_treasure_loot()
            loot_lines = self._apply_loot(loot)
            room.treasure_looted = True
            self.update_display()
            messagebox.showinfo("Treasure", "You found treasure!\n\n" + "\n".join(loot_lines))
        elif room.has_merchant and not room.merchant_visited:
            self.merchant = Merchant(max_tier=self.current_dungeon.tier)
            self.window.show_merchant_ui(self.player, self.merchant)
        elif room.is_end_room and room.is_locked:
            if self.current_dungeon.try_unlock_vault(self.player):
                messagebox.showinfo("Vault", "You pick the lock with your Thieves' Tools. The vault creaks open!")
                self.update_display()
            else:
                messagebox.showwarning("Vault", "This vault is locked. You need Thieves' Tools.")
        elif room.is_end_room and not room.boss_defeated:
            boss = self.current_dungeon.get_vault_boss()
            self.combat_context = 'vault_boss'
            messagebox.showinfo("Vault", f"{boss.name} rises to guard the vault!")
            self.start_combat(boss)
        elif room.is_end_room and room.boss_defeated:
            messagebox.showinfo("Vault", "The vault lies empty, its guardian already defeated.")
        else:
            messagebox.showinfo("Interact", "There's nothing to interact with here.")

    def handle_camp(self):
        if self.game_state != 'world_map' or not self.player:
            messagebox.showinfo("Camp", "You can only make camp out in the open world.")
            return
        if self.player.current_health >= self.player.max_health:
            messagebox.showinfo("Camp", "You're already at full health.")
            return
        healed = self.player.camp_rest()
        self.update_display()
        messagebox.showinfo(
            "Camp",
            f"You make camp for the night and recover {healed} HP "
            f"({self.player.current_health}/{self.player.max_health}).\n"
            "A proper bed at a village or town will restore you fully."
        )

    def handle_scout(self):
        if self.game_state != 'world_map' or not self.world_map:
            messagebox.showinfo("Scout", "You can only scout the surrounding area out in the open world.")
            return
        found = self.world_map.scout_nearby()
        self.update_display()
        if not found:
            messagebox.showinfo("Scout", "You survey the surrounding area and find nothing new of note.")
            return
        tiers = ", ".join(f"Tier {node.tier}" for node in found)
        messagebox.showinfo(
            "Scout",
            f"You spot {len(found)} potential encounter site(s) nearby: {tiers}."
        )

    def _apply_loot(self, loot):
        lines = []
        for drop_type, value in loot:
            if drop_type == 'copper':
                self.player.money += value
                lines.append(f"+ {value} copper")
            else:
                item = self.db.get_item(value)
                if item:
                    self.player.add_item(item)
                    lines.append(f"+ {item['name']}")
        return lines

    def handle_pause(self):
        if self.game_state not in ('world_map', 'dungeon'):
            return
        self.window.show_pause_menu()

    def handle_inventory(self):
        if self.game_state == 'combat' or not self.window or not self.player:
            return
        self.window.show_inventory_ui(self.player)

    def handle_skills(self):
        if self.game_state == 'combat' or not self.player:
            return
        SkillWindow(self.window, self.player, on_change=self.update_display)

    # ------------------------------------------------------------------
    # Combat
    # ------------------------------------------------------------------
    def start_combat(self, enemy: Enemy):
        if not self.window or not self.player:
            return

        self.player.reset_combat_flags()
        self._previous_state = self.game_state
        self.game_state = 'combat'
        CombatWindow(
            self.window,
            self.player,
            enemy,
            self.combat_system,
            self.handle_combat_end
        )

    def handle_combat_end(self, outcome: str):
        context = self.combat_context
        self.combat_context = None
        self.game_state = getattr(self, '_previous_state', 'world_map')

        if context == 'vault_boss' and outcome == 'victory' and self.current_dungeon:
            room = self.current_dungeon.get_current_room()
            room.boss_defeated = True
            room.is_cleared = True
            bonus_loot = self.current_dungeon.get_treasure_loot()
            loot_lines = self._apply_loot(bonus_loot)
            messagebox.showinfo(
                "Victory",
                "The vault's guardian falls! The dungeon is cleared.\n\n" + "\n".join(loot_lines)
            )
            self._mark_current_dungeon_node_cleared()
        elif context == 'dungeon' and self.current_dungeon:
            current_room = self.current_dungeon.get_current_room()
            if outcome == 'victory':
                current_room.is_cleared = True
                current_room.enemies = []
            elif outcome == 'fled':
                self.current_dungeon.move_player_random_adjacent()
        elif context == 'encounter' and self.world_map:
            self.world_map.get_current_node().cleared = True

        if outcome == 'defeat':
            messagebox.showinfo("Defeat", "You have fallen in battle. Returning to the village to recover.")
            self.player.current_health = self.player.max_health
            self.leave_dungeon()

        self.update_display()

    def _mark_current_dungeon_node_cleared(self):
        if not self.world_map:
            return
        node = self.world_map.get_current_node()
        if node.kind == 'dungeon':
            node.cleared = True


def main():
    try:
        game = Game()
        game.start()
    except Exception as e:
        logging.critical(f"Critical error in main game loop: {str(e)}")
        messagebox.showerror("Critical Error", f"A critical error occurred: {str(e)}")


if __name__ == "__main__":
    main()
