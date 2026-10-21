from typing import Any, Dict, List
import random
import logging
from database import Database


class QuestBoard:
    """
    A settlement's text-based side quests: short D&D-flavored errands
    resolved on the spot as a single ability check (real SRD mechanic - a
    d20 roll plus the relevant ability modifier against a DC), rather than
    a tracked objective spanning multiple screens. A fresh board is drawn
    each time a settlement is entered.
    """
    def __init__(self, count: int = 3):
        self._db = Database()
        pool = self._db.get_all_quests()
        self.quests: List[Dict[str, Any]] = random.sample(pool, k=min(count, len(pool)))
        self._completed: set = set()

    def is_completed(self, quest: Dict[str, Any]) -> bool:
        return quest['id'] in self._completed

    def attempt(self, character: Any, quest: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve a quest attempt. Each quest can only be attempted once per
        board (win or lose) - returns the roll breakdown, the outcome text,
        and whatever was actually rewarded (zero on failure).
        """
        roll = random.randint(1, 20)
        modifier = character.ability_modifier(quest['ability'])
        total = roll + modifier
        success = total >= quest['dc']
        self._completed.add(quest['id'])

        result = {
            'success': success,
            'roll': roll,
            'modifier': modifier,
            'total': total,
            'text': quest['success_text'] if success else quest['failure_text'],
            'copper': 0,
            'xp': 0,
        }

        if success:
            result['copper'] = quest['reward_copper']
            result['xp'] = quest['reward_xp']
            character.money += quest['reward_copper']
            character.add_xp(quest['reward_xp'])

        logging.info(f"Quest '{quest['id']}' attempted by {character.name}: "
                     f"roll {roll}+{modifier}={total} vs DC {quest['dc']} -> {'success' if success else 'failure'}")
        return result
