# database.py
import json
import os
import random
from typing import Dict, List, Optional, Any
from config import DATA_DIR
import logging


class Database:
    _instance = None

    def __new__(cls) -> 'Database':
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.initialize()
        return cls._instance

    def initialize(self) -> None:
        self.data_files = {
            'items': os.path.join(DATA_DIR, 'items.json'),
            'enemies': os.path.join(DATA_DIR, 'enemies.json'),
            'skills': os.path.join(DATA_DIR, 'skills.json'),
            'classes': os.path.join(DATA_DIR, 'classes.json'),
            'spells': os.path.join(DATA_DIR, 'spells.json'),
            'magic_bonus': os.path.join(DATA_DIR, 'magic_bonus.json'),
            'quests': os.path.join(DATA_DIR, 'quests.json'),
        }
        self._verify_data_files()
        self._cache: Dict[str, Any] = {}

    def _verify_data_files(self) -> None:
        for file_name, file_path in self.data_files.items():
            if not os.path.exists(file_path):
                logging.error(f"Missing data file: {file_path}")
                raise FileNotFoundError(f"Required data file missing: {file_name}")

    def load_data(self, table_name: str) -> Any:
        """Load a JSON data table, caching it after the first read."""
        if table_name in self._cache:
            return self._cache[table_name]
        try:
            with open(self.data_files[table_name], encoding='utf-8') as f:
                data = json.load(f)
            self._cache[table_name] = data
            return data
        except Exception as e:
            logging.error(f"Error loading {table_name}: {str(e)}")
            return []

    def save_data(self, table_name: str, data: Any) -> None:
        try:
            with open(self.data_files[table_name], 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            self._cache[table_name] = data
            logging.info(f"Successfully saved data to {table_name}")
        except Exception as e:
            logging.error(f"Error saving {table_name}: {str(e)}")
            raise

    # ------------------------------------------------------------------
    # Items
    # ------------------------------------------------------------------
    def get_item_template(self, item_name: str) -> Optional[Dict[str, Any]]:
        """Get the raw (non-magical) item template by name."""
        for item in self.load_data('items'):
            if item['name'] == item_name:
                return item
        logging.warning(f"Item template not found: {item_name}")
        return None

    def roll_magic_bonus(self, eligible: bool) -> str:
        """Roll a magic bonus tier ('+0'..'+3'), weighted by data/magic_bonus.json."""
        if not eligible:
            return '+0'
        data = self.load_data('magic_bonus')
        tiers = data.get('tiers', {})
        order = data.get('order', ['+0'])
        weights = [tiers[name]['weight'] for name in order]
        return random.choices(order, weights=weights, k=1)[0]

    def instantiate_item(self, item_name: str, magic_bonus: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Build a concrete item instance from a template, optionally rolling a
        magic bonus (+0/+1/+2/+3, real D&D style - a flat bonus to attack and
        damage rolls for weapons, or to AC for armor/shields, not a stat
        multiplier). Consumables and tools are never magical.
        """
        template = self.get_item_template(item_name)
        if not template:
            return None

        eligible = bool(template.get('magic_eligible', False))
        chosen = magic_bonus if magic_bonus else self.roll_magic_bonus(eligible)
        if not eligible:
            chosen = '+0'

        bonus_data = self.load_data('magic_bonus')
        tier_info = bonus_data.get('tiers', {}).get(chosen, {'bonus': 0, 'label': '', 'price_multiplier': 1})
        bonus = tier_info['bonus']

        item = dict(template)
        item['magic_bonus'] = bonus
        item['name'] = f"{tier_info['label']}{template['name']}" if bonus else template['name']
        item['base_name'] = template['name']
        # A rolled magic bonus is a real (if rare) power jump - the price
        # has to reflect that, or a lucky +3 roll costs the same as a +0
        # and the whole bonus system is invisible to the economy.
        item['price_copper'] = int(item['price_copper'] * tier_info.get('price_multiplier', 1))
        return item

    def get_item(self, item_name: str, magic_bonus: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a concrete item instance by template name."""
        return self.instantiate_item(item_name, magic_bonus=magic_bonus)

    def get_all_items_by_tier(self, tier: int) -> List[Dict[str, Any]]:
        """Get all item templates available at or below a tier."""
        return [item for item in self.load_data('items') if item.get('tier', 1) <= tier]

    def get_max_item_tier(self) -> int:
        return max((item.get('tier', 1) for item in self.load_data('items')), default=1)

    # ------------------------------------------------------------------
    # Enemies
    # ------------------------------------------------------------------
    def get_enemy(self, enemy_name: str) -> Optional[Dict[str, Any]]:
        """Get complete enemy data by name."""
        for enemy in self.load_data('enemies'):
            if enemy['name'] == enemy_name:
                return dict(enemy)
        logging.warning(f"Enemy not found: {enemy_name}")
        return None

    def get_all_enemies_by_tier(self, tier: int) -> List[Dict[str, Any]]:
        """Get all non-boss enemies that can appear in a specific tier."""
        return [e for e in self.load_data('enemies') if e.get('tier', 1) <= tier and not e.get('is_boss', False)]

    def get_boss_for_tier(self, tier: int) -> Optional[Dict[str, Any]]:
        """Get the boss enemy defined for an exact tier."""
        for enemy in self.load_data('enemies'):
            if enemy.get('is_boss', False) and enemy.get('tier') == tier:
                return dict(enemy)
        logging.warning(f"No boss defined for tier {tier}")
        return None

    def get_max_enemy_tier(self) -> int:
        return max((e.get('tier', 1) for e in self.load_data('enemies')), default=1)

    # ------------------------------------------------------------------
    # Classes
    # ------------------------------------------------------------------
    def get_class(self, class_key: str) -> Optional[Dict[str, Any]]:
        return self.load_data('classes').get(class_key.lower())

    def get_all_classes(self) -> Dict[str, Dict[str, Any]]:
        return self.load_data('classes')

    # ------------------------------------------------------------------
    # Spells
    # ------------------------------------------------------------------
    def get_spell(self, spell_name: str) -> Optional[Dict[str, Any]]:
        for spell in self.load_data('spells'):
            if spell['name'] == spell_name:
                return spell
        return None

    def get_spells_for_class(self, class_key: str) -> List[Dict[str, Any]]:
        return [s for s in self.load_data('spells') if class_key.lower() in s.get('classes', [])]

    # ------------------------------------------------------------------
    # Skills (the bonus homebrew tree, separate from real class features)
    # ------------------------------------------------------------------
    def get_all_skills(self) -> Dict[str, Dict[str, Any]]:
        branches = self.load_data('skills')
        flat = {}
        for nodes in branches.values():
            for node in nodes:
                flat[node['id']] = node
        return flat

    def get_skill_branches(self) -> Dict[str, List[Dict[str, Any]]]:
        return self.load_data('skills')

    def get_skill(self, skill_id: str) -> Optional[Dict[str, Any]]:
        return self.get_all_skills().get(skill_id)

    # ------------------------------------------------------------------
    # Quests (text-based town side quests, resolved as an ability check)
    # ------------------------------------------------------------------
    def get_all_quests(self) -> List[Dict[str, Any]]:
        return self.load_data('quests')
