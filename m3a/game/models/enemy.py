from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any, Tuple
from database import Database
import random
import logging


@dataclass
class Enemy:
    """
    Represents an enemy character.
    """
    name: str
    tier: int
    current_health: Optional[int] = None
    attack: int = 0
    defense: int = 0
    health: int = 0
    xp_value: int = 0
    min_copper: int = 0
    max_copper: int = 0
    common_drops: List[str] = None
    rare_drops: List[str] = None
    is_boss: bool = False
    is_player: bool = False  # Added to identify non-player characters
    status_effects: Dict[str, Dict] = field(default_factory=dict)

    def __post_init__(self):
        """
        Initialize enemy stats after creation.
        """
        self._load_stats()
        if self.current_health is None:
            self.current_health = self.health
        if self.common_drops is None:
            self.common_drops = []
        if self.rare_drops is None:
            self.rare_drops = []

    def _load_stats(self) -> None:
        """
        Load enemy stats from the database.
        """
        db = Database()
        enemy_data = db.get_enemy(self.name)
        if not enemy_data:
            logging.error(f"Failed to load enemy data for {self.name}")
            raise ValueError(f"Invalid enemy: {self.name}")

        self.attack = enemy_data['attack']
        self.defense = enemy_data['defense']
        self.health = enemy_data['health']
        self.xp_value = enemy_data['xp_value']
        self.min_copper = enemy_data['min_copper']
        self.max_copper = enemy_data['max_copper']
        self.common_drops = list(enemy_data.get('common_drops') or [])
        self.rare_drops = list(enemy_data.get('rare_drops') or [])
        self.is_boss = bool(enemy_data.get('is_boss', False))

    def take_damage(self, damage: int) -> bool:
        """
        Take damage and return whether still alive.

        Args:
            damage: The amount of damage to take.

        Returns:
            True if the enemy is still alive, False otherwise.
        """
        self.current_health = max(0, self.current_health - damage)
        logging.info(f"{self.name} took {damage} damage. Health: {self.current_health}/{self.health}")
        return self.current_health > 0

    def is_defeated(self) -> bool:
        """
        Check if the enemy is defeated.

        Returns:
            True if the enemy is defeated, False otherwise.
        """
        return self.current_health <= 0

    def get_drops(self, character: Any = None) -> List[Tuple[str, Any]]:
        """
        Generate loot drops with improved variety and chances. A character with
        the Treasure Hunter skill gets an extra bonus-drop roll.

        Args:
            character: The player character that defeated this enemy (optional,
                       used to apply loot-bonus skills).

        Returns:
            A list of loot drops as tuples (drop_type, value).
        """
        drops = []
        db = Database()

        # Base money drops with bonus chance
        base_copper = random.randint(self.min_copper, self.max_copper)
        if random.random() < 0.2:  # 20% chance for bonus money
            bonus_multiplier = random.uniform(1.5, 3.0)
            base_copper = int(base_copper * bonus_multiplier)
        drops.append(('copper', base_copper))

        max_tier = db.get_max_item_tier()

        # Legendary-tier drop chance (top item tier)
        if random.random() < 0.02:  # 2% chance for a top-tier item
            legendary_items = db.get_all_items_by_tier(max_tier)
            top_tier_items = [i for i in legendary_items if i['tier'] == max_tier]
            if top_tier_items:
                item = random.choice(top_tier_items)
                drops.append(('item', item['name']))
                logging.info(f"Top-tier item dropped: {item['name']}")

        # Rare drop chance - prefer this enemy's own curated signature item
        # (data/enemies.json's rare_drops) over a generic higher-tier roll,
        # so e.g. a Lich has a real shot at dropping its Flame Blade instead
        # of some unrelated item from two tiers up.
        if random.random() < 0.10:  # 10% chance for rare item
            if self.rare_drops:
                item_name = random.choice(self.rare_drops)
                drops.append(('item', item_name))
                logging.info(f"Rare item dropped: {item_name}")
            else:
                rare_tier = min(self.tier + 2, max_tier)
                rare_items = db.get_all_items_by_tier(rare_tier)
                if rare_items:
                    item = random.choice(rare_items)
                    drops.append(('item', item['name']))
                    logging.info(f"Rare item dropped: {item['name']}")

        # Common drops with improved variety
        common_chance = 0.6
        if character is not None:
            common_chance += getattr(character, 'loot_bonus', 0)
        if random.random() < common_chance:
            drop_pool = []

            # Add tier-appropriate items
            tier_items = db.get_all_items_by_tier(self.tier)
            if tier_items:
                drop_pool.extend(item['name'] for item in tier_items)

            # Add specific common drops
            if self.common_drops:
                drop_pool.extend(self.common_drops)

            if drop_pool:
                item_name = random.choice(drop_pool)
                drops.append(('item', item_name))
                logging.info(f"Common item dropped: {item_name}")

        # Extra drops based on enemy tier
        extra_drop_chance = 0.1 * self.tier  # Higher tier = more chances
        while random.random() < extra_drop_chance and extra_drop_chance > 0:
            tier_items = db.get_all_items_by_tier(self.tier)
            if tier_items:
                item = random.choice(tier_items)
                drops.append(('item', item['name']))
                logging.info(f"Extra item dropped: {item['name']}")
            extra_drop_chance -= 0.1

        logging.info(f"{self.name} dropped: {drops}")
        return drops

    def calculate_total_attack(self) -> int:
        """
        Calculate total attack (for combat system compatibility).

        Returns:
            The total attack value.
        """
        return self.attack

    def calculate_total_defense(self) -> int:
        """
        Calculate total defense (for combat system compatibility).

        Returns:
            The total defense value.
        """
        return self.defense

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert enemy data to a dictionary for saving.

        Returns:
            The enemy data as a dictionary.
        """
        return {
            'name': self.name,
            'tier': self.tier,
            'current_health': self.current_health,
            'attack': self.attack,
            'defense': self.defense,
            'health': self.health,
            'xp_value': self.xp_value,
            'min_copper': self.min_copper,
            'max_copper': self.max_copper,
            'common_drops': self.common_drops,
            'rare_drops': self.rare_drops,
            'is_boss': self.is_boss,
        }

    @staticmethod
    def get_random_enemy(tier: int) -> 'Enemy':
        """
        Create a random (non-boss) enemy of the specified tier, weighted by spawn_chance.

        Args:
            tier: The tier of the enemy.

        Returns:
            A random enemy of the specified tier.
        """
        db = Database()
        tier_enemies = db.get_all_enemies_by_tier(tier)
        if not tier_enemies:
            raise ValueError(f"No enemies found for tier {tier}")

        weights = [e.get('spawn_chance', 0.1) for e in tier_enemies]
        chosen = random.choices(tier_enemies, weights=weights, k=1)[0]
        return Enemy(name=chosen['name'], tier=chosen['tier'])

    @staticmethod
    def get_boss(tier: int) -> 'Enemy':
        """
        Create the boss enemy defined for a tier.

        Args:
            tier: The tier of the boss.

        Returns:
            The boss enemy for that tier.
        """
        db = Database()
        boss_data = db.get_boss_for_tier(tier)
        if not boss_data:
            raise ValueError(f"No boss found for tier {tier}")
        return Enemy(name=boss_data['name'], tier=boss_data['tier'])
