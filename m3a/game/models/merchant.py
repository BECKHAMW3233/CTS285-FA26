from typing import List, Dict, Any
from database import Database
import random
import logging


class Merchant:
    """
    Represents a merchant in the game.
    """
    def __init__(self, max_tier: int = None):
        """
        Initialize the merchant.

        Args:
            max_tier: The highest item tier this merchant can stock. Defaults
                      to the game's highest defined tier.
        """
        self._db = Database()
        self._max_tier = max_tier if max_tier is not None else self._db.get_max_item_tier()
        self._inventory = self._generate_inventory()
        self._refresh_timer = 0  # For periodic inventory refresh

    def _generate_inventory(self) -> List[Dict]:
        """
        Generate the merchant's inventory with varied items and rolled rarities.

        Returns:
            The generated inventory as a list of item dictionaries.
        """
        inventory = []
        try:
            all_templates = self._db.get_all_items_by_tier(self._max_tier)
            if not all_templates:
                logging.error("No items found in database for merchant")
                return inventory

            for item_type in ['weapon', 'ranged', 'armor', 'shield', 'ring', 'necklace', 'consumable', 'tool']:
                type_templates = [t for t in all_templates if t['type'] == item_type]
                num_items = 5 if item_type in ('consumable', 'tool') else 3
                selected = random.sample(type_templates, k=min(num_items, len(type_templates)))
                for template in selected:
                    inventory.append(self._db.instantiate_item(template['name']))

            logging.info(f"Generated merchant inventory with {len(inventory)} items")
            return inventory

        except Exception as e:
            logging.error(f"Error generating merchant inventory: {str(e)}")
            return []

    def refresh_inventory(self) -> None:
        """
        Refresh the merchant's inventory.
        """
        self._inventory = self._generate_inventory()
        self._refresh_timer = 0
        logging.info("Merchant inventory refreshed")

    def buy_item(self, player: Any, item_name: str) -> bool:
        """
        Handle the player buying an item from the merchant.

        Args:
            player: The player character.
            item_name: The name of the item to buy.

        Returns:
            True if the item was bought successfully, False otherwise.
        """
        try:
            item = next((i for i in self._inventory if i['name'] == item_name), None)

            if not item:
                logging.warning(f"Item not found in merchant inventory: {item_name}")
                return False

            if player.money < item['price_copper']:
                logging.info(f"Player cannot afford item: {item_name}")
                return False

            player.money -= item['price_copper']
            player.add_item(item)
            self._inventory.remove(item)

            logging.info(f"Player bought {item_name} for {item['price_copper']} copper")
            return True

        except Exception as e:
            logging.error(f"Error processing buy transaction: {str(e)}")
            return False

    def sell_item(self, player: Any, item: Dict) -> bool:
        """
        Handle the player selling an item to the merchant.

        Args:
            player: The player character.
            item: The item to sell.

        Returns:
            True if the item was sold successfully, False otherwise.
        """
        try:
            if item not in player.inventory:
                logging.warning(f"Item not found in player inventory: {item['name']}")
                return False

            sell_price = int(item['price_copper'] * 0.5)

            player.money += sell_price
            player.remove_item(item)

            logging.info(f"Player sold {item['name']} for {sell_price} copper")
            return True

        except Exception as e:
            logging.error(f"Error processing sell transaction: {str(e)}")
            return False

    def get_item_value(self, item: Dict) -> int:
        """
        Calculate the sell value of an item.

        Args:
            item: The item to calculate the value for.

        Returns:
            The sell value of the item.
        """
        return int(item['price_copper'] * 0.5)

    def get_inventory_by_type(self, item_type: str) -> List[Dict]:
        """
        Get filtered inventory by item type.

        Args:
            item_type: The type of items to retrieve.

        Returns:
            A list of items of the specified type.
        """
        return [item for item in self._inventory if item['type'] == item_type]

    def get_available_types(self) -> List[str]:
        """
        Get a list of available item types in the inventory.

        Returns:
            A list of available item types.
        """
        return sorted(list(set(item['type'] for item in self._inventory)))
