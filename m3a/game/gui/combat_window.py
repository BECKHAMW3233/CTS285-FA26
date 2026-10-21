# gui/combat_window.py
from tkinter import ttk
import tkinter as tk
from typing import Any, Callable, Dict
import logging
from models.combat import CombatAction
from gui.layout import fit_window, scaled_font
from config import COMBAT_DISTANCE_BANDS, COMBAT_START_DISTANCE, COMBAT_MAX_DISTANCE, dungeon_recommended_level

class CombatWindow(tk.Toplevel):
    def __init__(self, master: tk.Tk, character: Any, enemy: Any, combat_system: Any, on_combat_end: Callable):
        super().__init__(master)
        self.title("Combat")
        # Resizable now (was locked) - on a wide-but-short screen the
        # auto-detected UI scale can make the three action-button rows
        # taller than 90% of screen height leaves room for, and a locked
        # window gave the player no way to recover from that.
        self.resizable(True, True)
        self.minsize(480, 520)
        fit_window(self, 560, 760, parent=master)

        # Make window modal and force it to stay on top
        self.transient(master)
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.disable_close)
        self.lift()
        self.focus_force()

        self.character = character
        self.enemy = enemy
        self.combat_system = combat_system
        self.on_combat_end = on_combat_end
        self.combat_ended = False
        self._ended_outcome = None
        # Homebrew per-turn positioning: 0 = melee range, higher = farther.
        # Enemies have no ranged capability, so every enemy turn spent at
        # distance > 0 is spent closing in instead of attacking.
        self.distance = COMBAT_START_DISTANCE

        # Store button references
        self.attack_button = None
        self.item_button = None
        self.ability_button = None
        self.flee_button = None
        self.advance_button = None
        self.retreat_button = None

        self.setup_ui()
        self.update_stats()
        self.enable_buttons()

        # Start with a combat initiation message
        self.log_message(f"Combat initiated between {self.character.name} and {self.enemy.name}!")
        self.log_message("-" * 50)
        if self.distance > 0:
            self.log_message(f"You start at {COMBAT_DISTANCE_BANDS[self.distance]} range - "
                              f"Advance to close the gap or stay back and use a ranged weapon.")

    def disable_close(self):
        """Block the native close button while the fight is still live (no
        dodging a loss by closing the window) - once it's over, treat it
        the same as clicking the in-window Close button, so the window is
        never permanently stuck with no way out."""
        if self.combat_ended:
            self.end_combat(self._ended_outcome)

    def setup_ui(self):
        # Main container with padding
        main_container = ttk.Frame(self, padding="5")
        main_container.pack(fill='both', expand=True)
        
        # Stats Frame
        self.stats_frame = ttk.LabelFrame(main_container, text="Combat Stats", padding="5")
        self.stats_frame.pack(fill='x', pady=(0, 5))
        
        # Character stats
        char_frame = ttk.Frame(self.stats_frame)
        char_frame.pack(fill='x', pady=2)
        ttk.Label(char_frame, text="Player:", width=10).pack(side='left')
        self.character_stats = ttk.Label(char_frame, text="")
        self.character_stats.pack(side='left', fill='x', expand=True)
        
        # Enemy stats
        enemy_frame = ttk.Frame(self.stats_frame)
        enemy_frame.pack(fill='x', pady=2)
        ttk.Label(enemy_frame, text="Enemy:", width=10).pack(side='left')
        self.enemy_stats = ttk.Label(enemy_frame, text="")
        self.enemy_stats.pack(side='left', fill='x', expand=True)

        # Range
        range_frame = ttk.Frame(self.stats_frame)
        range_frame.pack(fill='x', pady=2)
        ttk.Label(range_frame, text="Range:", width=10).pack(side='left')
        self.range_stats = ttk.Label(range_frame, text="")
        self.range_stats.pack(side='left', fill='x', expand=True)

        # Combat Log Frame with Scrollbar
        self.log_frame = ttk.LabelFrame(main_container, text="Combat Log", padding="5")
        self.log_frame.pack(fill='both', expand=True, pady=(0, 5))
        
        log_scroll = ttk.Scrollbar(self.log_frame)
        log_scroll.pack(side='right', fill='y')
        
        self.combat_log = tk.Text(
            self.log_frame,
            height=14,
            wrap='word',
            yscrollcommand=log_scroll.set,
            background='white',
            font=scaled_font(self, 10, 'Courier')
        )
        self.combat_log.pack(fill='both', expand=True)
        log_scroll.config(command=self.combat_log.yview)
        
        # Action Buttons Frame
        self.actions_frame = ttk.LabelFrame(main_container, text="Actions", padding="5")
        self.actions_frame.pack(fill='x')
        
        # Action buttons, split across two rows - five buttons at width=20
        # in one row don't fit this window's 500px width; ttk.pack silently
        # squeezes the overflow down to a few pixels instead of clipping
        # visibly, which made Cast Spell and Flee effectively unclickable.
        button_frame = ttk.Frame(self.actions_frame)
        button_frame.pack(fill='x', expand=True)

        button_row1 = ttk.Frame(button_frame)
        button_row1.pack(fill='x')
        button_row2 = ttk.Frame(button_frame)
        button_row2.pack(fill='x', pady=(5, 0))
        button_row3 = ttk.Frame(button_frame)
        button_row3.pack(fill='x', pady=(5, 0))

        self.attack_button = ttk.Button(
            button_row1,
            text="Attack",
            command=self.handle_attack,
            width=20
        )
        self.attack_button.pack(side='left', padx=5)

        self.item_button = ttk.Button(
            button_row1,
            text="Use Item",
            command=self.show_item_selection,
            width=20
        )
        self.item_button.pack(side='left', padx=5)

        self.ability_button = ttk.Button(
            button_row1,
            text="Abilities",
            command=self.show_ability_selection,
            width=20
        )
        self.ability_button.pack(side='left', padx=5)
        if not self.character.get_active_skills():
            self.ability_button.config(state='disabled')

        self.spell_button = ttk.Button(
            button_row2,
            text="Cast Spell",
            command=self.show_spell_selection,
            width=20
        )
        self.spell_button.pack(side='left', padx=5)
        if not (hasattr(self.character, 'is_caster') and self.character.is_caster()):
            self.spell_button.config(state='disabled')

        self.flee_button = ttk.Button(
            button_row2,
            text="Flee",
            command=self.handle_flee,
            width=20
        )
        self.flee_button.pack(side='left', padx=5)

        self.advance_button = ttk.Button(
            button_row3,
            text="Advance",
            command=self.handle_advance,
            width=20
        )
        self.advance_button.pack(side='left', padx=5)

        self.retreat_button = ttk.Button(
            button_row3,
            text="Retreat",
            command=self.handle_retreat,
            width=20
        )
        self.retreat_button.pack(side='left', padx=5)

    def _weapon_at_current_range(self):
        """The weapon this character would actually swing with right now,
        given the current distance - None if nothing equipped reaches, or
        if unarmed (which is always usable regardless of distance)."""
        if not hasattr(self.character, 'weapon_for_range'):
            return None
        return self.character.weapon_for_range(self.distance == 0)

    def _attack_blocked(self) -> bool:
        """True only for the one real stuck case - a melee weapon equipped,
        no ranged weapon, and too far away to swing the melee one. Mirrors
        CombatSystem._resolve_attacks()'s own guard exactly; a fully
        unarmed character can always still throw a punch at any range."""
        if not hasattr(self.character, 'weapon_for_range'):
            return False
        weapon = self.character.weapon_for_range(self.distance == 0)
        return weapon is None and bool(self.character.equipped_melee_weapon)

    def update_stats(self):
        weapon = self._weapon_at_current_range()
        char_attack = self.character.calculate_attack_bonus(weapon) if hasattr(self.character, 'calculate_attack_bonus') \
            else self.character.calculate_total_attack()
        char_ac = self.character.calculate_ac() if hasattr(self.character, 'calculate_ac') else (10 + self.character.calculate_total_defense())
        char_status = self._status_text(self.character)
        weapon_text = f" [{weapon['name']}]" if weapon else (" [no weapon in range!]" if hasattr(self.character, 'weapon_for_range') else "")
        self.character_stats.config(
            text=f"Lv {self.character.level} - "
                 f"HP: {self.character.current_health}/{self.character.max_health} "
                 f"ATK: +{char_attack} AC: {char_ac}{char_status}{weapon_text}"
        )

        enemy_status = self._status_text(self.enemy)
        enemy_level = dungeon_recommended_level(self.enemy.tier)
        self.enemy_stats.config(
            text=f"Lv {enemy_level} (Tier {self.enemy.tier}) - "
                 f"HP: {self.enemy.current_health}/{self.enemy.health} "
                 f"ATK: +{self.enemy.attack} AC: {10 + self.enemy.defense}{enemy_status}"
        )

        band_name = COMBAT_DISTANCE_BANDS[self.distance]
        self.range_stats.config(text=f"{band_name} ({self.distance}/{COMBAT_MAX_DISTANCE})")

    def _status_text(self, combatant: Any) -> str:
        effects = list(getattr(combatant, 'status_effects', {}).keys())
        return f" [{', '.join(effects)}]" if effects else ""
        
    def log_message(self, message: str):
        self.combat_log.insert('end', f"{message}\n")
        self.combat_log.see('end')
        
    def disable_buttons(self):
        self.attack_button.config(state='disabled')
        self.item_button.config(state='disabled')
        self.ability_button.config(state='disabled')
        self.spell_button.config(state='disabled')
        self.flee_button.config(state='disabled')
        self.advance_button.config(state='disabled')
        self.retreat_button.config(state='disabled')

    def enable_buttons(self):
        if not self.combat_ended:
            self.attack_button.config(state='disabled' if self._attack_blocked() else 'normal')
            self.item_button.config(state='normal')
            self.flee_button.config(state='normal')
            if self.character.get_active_skills():
                self.ability_button.config(state='normal')
            if hasattr(self.character, 'is_caster') and self.character.is_caster():
                self.spell_button.config(state='normal')
            self.advance_button.config(state='normal' if self.distance > 0 else 'disabled')
            self.retreat_button.config(state='normal' if self.distance < COMBAT_MAX_DISTANCE else 'disabled')

    def show_spell_selection(self):
        known = getattr(self.character, 'known_spells', [])
        if not known:
            self.log_message("\nNo spells known!")
            return

        from database import Database
        db = Database()
        spell_window = tk.Toplevel(self)
        spell_window.title("Cast Spell")
        spell_window.transient(self)
        fit_window(spell_window, 380, 320, parent=self)
        spell_window.grab_set()

        for spell_name in known:
            spell = db.get_spell(spell_name)
            if not spell:
                continue
            row = ttk.Frame(spell_window)
            row.pack(fill='x', padx=8, pady=4)
            level_text = "Cantrip" if spell['level'] == 0 else f"Level {spell['level']}"
            slots_left = "" if spell['level'] == 0 else f" ({self.character.spell_slots.get(spell['level'], 0)} slots left)"
            ttk.Label(row, text=f"{spell['name']} [{level_text}]{slots_left}", wraplength=260).pack(side='left')
            cast_button = ttk.Button(
                row,
                text="Cast",
                command=lambda s=spell_name: self.use_selected_spell(s, spell_window)
            )
            cast_button.pack(side='right')
            if not self.character.can_cast(spell_name):
                cast_button.config(state='disabled')

    def use_selected_spell(self, spell_name: str, window: tk.Toplevel):
        window.destroy()
        self.disable_buttons()

        result = self.combat_system.process_turn(
            self.character, self.enemy, CombatAction(type='cast_spell', spell_name=spell_name)
        )
        self.log_message("\n=== Spell Cast ===")
        for message in result['messages']:
            self.log_message(message)
        self.update_stats()

        is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
        if is_ended:
            self.handle_combat_end(outcome)
        else:
            self.after(1000, self.process_enemy_turn)

    def show_ability_selection(self):
        active_skills = self.character.get_active_skills()
        if not active_skills:
            self.log_message("\nNo usable abilities!")
            return

        ability_window = tk.Toplevel(self)
        ability_window.title("Select Ability")
        ability_window.transient(self)
        fit_window(ability_window, 340, 300, parent=self)
        ability_window.grab_set()

        for skill in active_skills:
            row = ttk.Frame(ability_window)
            row.pack(fill='x', padx=8, pady=4)
            ttk.Label(row, text=f"{skill['name']}: {skill['description']}", wraplength=220).pack(side='left')
            use_button = ttk.Button(
                row,
                text="Used" if skill['used_this_combat'] else "Use",
                command=lambda s=skill: self.use_selected_ability(s, ability_window)
            )
            use_button.pack(side='right')
            if skill['used_this_combat']:
                use_button.config(state='disabled')

    def use_selected_ability(self, skill: Dict, window: tk.Toplevel):
        window.destroy()
        had_pending_power_strike = getattr(self.character, 'pending_power_strike', False)
        result = self.character.use_active_skill(skill['id'])
        self.log_message(f"\n{result['message']}")

        # A Power Strike primed on an earlier turn fizzles if a different
        # active skill is used instead of attacking with it.
        if result['success'] and had_pending_power_strike and skill['effect'].get('type') != 'active_power_strike':
            self.character.pending_power_strike = False
            self.log_message(f"{self.character.name}'s readied Power Strike fizzles, unused.")

        self.update_stats()

        if not result['success']:
            return

        if skill['effect'].get('type') == 'active_heal_percent':
            self.disable_buttons()
            self.after(1000, self.process_enemy_turn)

    def show_item_selection(self):
        usable_items = [
            item for item in self.character.inventory 
            if item['type'] == 'consumable'
        ]
        
        if not usable_items:
            self.log_message("\nNo usable items in inventory!")
            return
            
        # Create item selection window
        item_window = tk.Toplevel(self)
        item_window.title("Select Item")
        item_window.transient(self)
        fit_window(item_window, 300, 400, parent=self)
        item_window.grab_set()
        
        # Create scrollable frame for items
        canvas = tk.Canvas(item_window)
        scrollbar = ttk.Scrollbar(item_window, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Add items to scrollable frame
        for item in usable_items:
            item_frame = ttk.Frame(scrollable_frame)
            item_frame.pack(fill='x', padx=5, pady=2)
            
            effect_desc = ""
            if 'effect' in item and item['effect'].startswith('heal_'):
                effect_desc = f" (Heals {item['effect'][len('heal_'):]} HP)"
            
            item_info = f"{item['name']}{effect_desc}"
            ttk.Label(item_frame, text=item_info).pack(side='left', padx=5)
            ttk.Button(
                item_frame,
                text="Use",
                command=lambda i=item: self.use_selected_item(i, item_window)
            ).pack(side='right', padx=5)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def use_selected_item(self, item: Dict, window: tk.Toplevel):
        window.destroy()
        self.disable_buttons()

        if getattr(self.character, 'pending_power_strike', False):
            self.character.pending_power_strike = False
            self.log_message(f"\n{self.character.name}'s readied Power Strike fizzles, unused.")

        success = False
        if item['type'] == 'consumable':
            health_before = self.character.current_health
            success = self.character.use_healing_potion(item)

            if success:
                heal_amount = self.character.current_health - health_before
                self.log_message(f"\n{self.character.name} used {item['name']} and healed for {heal_amount} HP!")
                self.update_stats()
                # Process enemy turn after using item
                self.after(1000, self.process_enemy_turn)
            else:
                self.log_message(f"\nFailed to use {item['name']}!")
                self.enable_buttons()
        
        # Log the attempt
        logging.info(f"Combat item use attempt - Item: {item['name']}, Success: {success}")
        
        # Check combat status
        is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
        if is_ended:
            self.handle_combat_end(outcome)
        elif not success:
            self.enable_buttons()
        
    def handle_attack(self):
        self.disable_buttons()

        # Process player's attack
        result = self.combat_system.process_turn(
            self.character,
            self.enemy,
            CombatAction(type='attack'),
            distance=self.distance
        )

        # Log all messages from the combat system
        self.log_message("\n=== Player Turn ===")
        for message in result['messages']:
            self.log_message(message)

        self.update_stats()

        # Check if enemy is defeated
        is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
        if is_ended:
            self.handle_combat_end(outcome)
            return

        # Process enemy's turn after a short delay
        self.after(1000, self.process_enemy_turn)

    def _handle_move(self, delta: int, verb: str):
        """Shared by Advance/Retreat: routes through process_turn() first so
        a stunned character can't move either, and poison/bleed/burn still
        ticks on a movement turn the same as any other action."""
        self.disable_buttons()
        self.log_message("\n=== Move ===")
        result = self.combat_system.process_turn(self.character, self.enemy, CombatAction(type='move'))
        for message in result['messages']:
            self.log_message(message)

        if result['success']:
            self.distance = max(0, min(COMBAT_MAX_DISTANCE, self.distance + delta))
            self.log_message(f"{self.character.name} {verb}s - now at {COMBAT_DISTANCE_BANDS[self.distance]} range.")

        self.update_stats()

        is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
        if is_ended:
            self.handle_combat_end(outcome)
        else:
            self.after(1000, self.process_enemy_turn)

    def handle_advance(self):
        """Spend the turn closing the distance instead of attacking."""
        self._handle_move(-1, "advance")

    def handle_retreat(self):
        """Spend the turn falling back instead of attacking - the enemy
        still closes in on its own turn, so this only buys real distance if
        kept up every round."""
        self._handle_move(1, "retreat")

    def process_enemy_turn(self):
        self.log_message("\n=== Enemy Turn ===")

        if self.distance > 0:
            move_result = self.combat_system.process_turn(self.enemy, self.character, CombatAction(type='move'))
            for message in move_result['messages']:
                self.log_message(message)
            if move_result['success']:
                self.distance -= 1
                self.log_message(f"{self.enemy.name} closes in - now at {COMBAT_DISTANCE_BANDS[self.distance]} range.")
            self.update_stats()

            is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
            if is_ended:
                self.handle_combat_end(outcome)
            else:
                self.enable_buttons()
            return

        result = self.combat_system.process_turn(
            self.enemy,
            self.character,
            CombatAction(type='attack')
        )

        for message in result['messages']:
            self.log_message(message)

        self.update_stats()

        # Check combat status after enemy turn
        is_ended, outcome = self.combat_system.check_combat_status(self.character, self.enemy)
        if is_ended:
            self.handle_combat_end(outcome)
        else:
            self.enable_buttons()

    def handle_flee(self):
        self.disable_buttons()
        
        self.log_message("\n=== Flee Attempt ===")
        result = self.combat_system.process_turn(
            self.character,
            self.enemy,
            CombatAction(type='flee'),
            distance=self.distance
        )
        
        for message in result['messages']:
            self.log_message(message)
            
        if result['fled']:
            self.log_message("\nEscaped successfully!")
            self.after(1500, lambda: self.handle_combat_end('fled'))
        else:
            self.log_message("\nFailed to escape!")
            self.after(1000, self.process_enemy_turn)
            
    def handle_combat_end(self, outcome: str):
        self.combat_ended = True
        self._ended_outcome = outcome
        self.disable_buttons()
        self.log_message("\n" + "=" * 50)
        
        if outcome == 'victory':
            rewards = self.combat_system.distribute_rewards(self.character, self.enemy)
            self.log_message("\nVictory!")
            self.log_message(f"Gained {rewards['xp']} XP and {rewards['copper']} copper")
            for item in rewards['items']:
                self.log_message(f"Received item: {item}")
        elif outcome == 'defeat':
            self.log_message("\nDefeat... You have been slain!")
        elif outcome == 'fled':
            self.log_message("\nYou have escaped from combat!")
            
        # Add a close button
        ttk.Button(
            self.actions_frame,
            text="Close",
            command=lambda: self.end_combat(outcome)
        ).pack(pady=10)
            
    def end_combat(self, outcome: str):
        self.grab_release()
        self.on_combat_end(outcome)
        self.destroy()