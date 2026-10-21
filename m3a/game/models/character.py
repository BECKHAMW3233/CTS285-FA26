from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Any
import logging
import random
from database import Database
from config import XP_BY_LEVEL, PROFICIENCY_BONUS_BY_LEVEL, SPELL_SLOTS_BY_LEVEL, STARTING_GOLD_COPPER
import dice

# Homebrew bonus-skill points, on top of real class features - every 4
# levels through 48, matching the skill tree's 5-tier-deep branches (see
# data/skills.json) now that the level cap is 50, not the old 20.
SKILL_POINT_LEVELS = (4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48)


def roll_ability_scores() -> List[int]:
    """4d6, drop the lowest, six times - the SRD's standard random generation method."""
    scores = []
    for _ in range(6):
        rolls = sorted((random.randint(1, 6) for _ in range(4)), reverse=True)
        scores.append(sum(rolls[:3]))
    return scores


@dataclass
class Character:
    """
    A player character built on the real D&D 5e SRD rules: six rolled
    ability scores, a class (Fighter/Rogue/Wizard/Cleric) with its own hit
    die and features, proficiency bonus and XP table extended to a 50-level
    arc (see config.py), and real spellcasting for the two caster classes
    (capped at the SRD's level-20 slot table, since the SRD has nothing
    past that). A small homebrew skill tree (see data/skills.json) sits on
    top as a bonus layer - it is explicitly not official D&D, just extra
    player choice.
    """
    name: str
    age: int
    class_key: str = 'fighter'
    level: int = 1
    xp: int = 0
    ability_scores: Dict[str, int] = field(default_factory=dict)
    current_health: Optional[int] = None
    inventory: List[Dict] = field(default_factory=list)
    equipped_melee_weapon: Optional[Dict] = None
    equipped_ranged_weapon: Optional[Dict] = None
    equipped_head: Optional[Dict] = None
    equipped_chest: Optional[Dict] = None
    equipped_hands: Optional[Dict] = None
    equipped_legs: Optional[Dict] = None
    equipped_shield: Optional[Dict] = None
    equipped_ring_left: Optional[Dict] = None
    equipped_ring_right: Optional[Dict] = None
    equipped_necklace: Optional[Dict] = None
    money: int = 0
    is_player: bool = True
    skill_points: int = 0
    unlocked_skills: List[str] = field(default_factory=list)
    status_effects: Dict[str, Dict] = field(default_factory=dict)
    pending_power_strike: bool = False
    spell_slots: Dict[int, int] = field(default_factory=dict)
    known_spells: List[str] = field(default_factory=list)
    _skills_used_this_combat: Set[str] = field(default_factory=set)

    def __post_init__(self):
        db = Database()
        self.class_data = db.get_class(self.class_key)
        if not self.class_data:
            raise ValueError(f"Unknown class: {self.class_key}")
        self.title = self.class_data['name']
        self.hit_die = self.class_data['hit_die']

        is_new_character = not self.ability_scores
        if is_new_character:
            self._generate_ability_scores()

        self._recalculate_derived_stats()
        if self.current_health is None:
            self.current_health = self.max_health
        # JSON round-trips turn dict int keys into strings - normalize back.
        self.spell_slots = {int(k): v for k, v in self.spell_slots.items()}

        if is_new_character:
            self._initialize_starting_equipment()
            self._initialize_spells()

    # ------------------------------------------------------------------
    # Ability scores and derived stats
    # ------------------------------------------------------------------
    def _generate_ability_scores(self) -> None:
        rolled = sorted(roll_ability_scores(), reverse=True)
        priority = self.class_data['ability_priority']
        self.ability_scores = {ability: rolled[i] for i, ability in enumerate(priority)}
        logging.info(f"{self.name} rolled ability scores: {self.ability_scores}")

    def ability_modifier(self, ability: str) -> int:
        score = self.ability_scores[ability] + self._accessory_ability_bonus(ability)
        return (score - 10) // 2

    def _accessory_ability_bonus(self, ability: str) -> int:
        """Rings/necklace can grant a flat bonus to one ability score each
        (item field 'ability_bonus': {"strength": 2}), which ripples into
        every modifier that reads from here - attack, AC, saves, spell DC."""
        total = 0
        for item in (self.equipped_ring_left, self.equipped_ring_right, self.equipped_necklace):
            if item:
                total += item.get('ability_bonus', {}).get(ability, 0)
        return total

    def _recalculate_derived_stats(self) -> None:
        con_mod = self.ability_modifier('constitution')
        max_health = dice.max_value(f"1d{self.hit_die}") + con_mod
        for _ in range(2, self.level + 1):
            max_health += dice.average(f"1d{self.hit_die}") + con_mod
        self.max_health = max(1, max_health)
        self.proficiency_bonus = PROFICIENCY_BONUS_BY_LEVEL[self.level - 1]

    def _initialize_starting_equipment(self) -> None:
        db = Database()
        self.money = STARTING_GOLD_COPPER

        for _ in range(3):
            potion = db.get_item("Potion of Healing")
            if potion:
                self.inventory.append(potion.copy())

        tools = db.get_item("Thieves' Tools")
        if tools:
            self.inventory.append(tools)
        torch = db.get_item("Torch")
        if torch:
            self.inventory.append(torch)

        weapon_name = self.class_data.get('starting_weapon')
        if weapon_name:
            weapon = db.get_item(weapon_name, magic_bonus='+0')
            if weapon:
                self.equipped_melee_weapon = weapon

        armor_name = self.class_data.get('starting_armor')
        if armor_name:
            armor = db.get_item(armor_name, magic_bonus='+0')
            if armor:
                self.equipped_chest = armor

        shield_name = self.class_data.get('starting_shield')
        if shield_name:
            shield = db.get_item(shield_name, magic_bonus='+0')
            if shield:
                self.equipped_shield = shield

    def _initialize_spells(self) -> None:
        if not self.class_data.get('is_caster'):
            return
        self.known_spells = list(self.class_data.get('cantrips_known_at_1', []))
        self._refresh_spell_slots()
        self._learn_available_spells()

    def _learn_available_spells(self) -> None:
        """
        Grant the class's designated spell(s) for every spell level the
        character currently has at least one slot for, once each - without
        this, a caster accumulates 2nd-9th level slots (SPELL_SLOTS_BY_LEVEL
        goes up to 9th) with nothing in spells.json to ever fill them.
        """
        spells_by_level = self.class_data.get('spells_by_level', {})
        for spell_level_str, names in spells_by_level.items():
            if self.spell_slots.get(int(spell_level_str), 0) <= 0:
                continue
            for name in names:
                if name not in self.known_spells:
                    self.known_spells.append(name)

    # ------------------------------------------------------------------
    # Leveling
    # ------------------------------------------------------------------
    def add_xp(self, xp_amount: int) -> None:
        bonus = self._skill_effect_total('xp_bonus')
        total = int(round(xp_amount * (1 + bonus)))
        self.xp += total
        logging.info(f"{self.name} gained {total} XP. Total: {self.xp}")
        self._check_level_up()

    def _check_level_up(self) -> None:
        while self.level < len(XP_BY_LEVEL) and self.xp >= XP_BY_LEVEL[self.level]:
            self._level_up()

    def _level_up(self) -> None:
        self.level += 1
        old_max = self.max_health
        health_percent = self.current_health / old_max
        self._recalculate_derived_stats()
        self.current_health = int(self.max_health * health_percent)
        if self.class_data.get('is_caster'):
            self._grant_new_spell_slots()
            self._learn_available_spells()
        if self.level in SKILL_POINT_LEVELS:
            self.skill_points += 1
        logging.info(f"{self.name} reached level {self.level} ({self.title})")

    # ------------------------------------------------------------------
    # Class features
    # ------------------------------------------------------------------
    def attacks_per_action(self) -> int:
        """Fighter's Extra Attack (SRD): 2 attacks at 5th, 3 at 11th, 4 at 20th."""
        if self.class_key != 'fighter':
            return 1
        if self.level >= 20:
            return 4
        if self.level >= 11:
            return 3
        if self.level >= 5:
            return 2
        return 1

    def sneak_attack_dice(self) -> int:
        """Rogue's Sneak Attack dice count (SRD progression, 1d6 per 2
        levels, capped at the SRD's level-20 value of 10d6 - there's no
        official continuation past level 20)."""
        if self.class_key != 'rogue' or self.level < 1:
            return 0
        return (min(self.level, 20) + 1) // 2

    # ------------------------------------------------------------------
    # Spellcasting
    # ------------------------------------------------------------------
    def is_caster(self) -> bool:
        return bool(self.class_data.get('is_caster'))

    def spellcasting_ability(self) -> Optional[str]:
        return self.class_data.get('spellcasting_ability')

    def spell_save_dc(self) -> int:
        return 8 + self.proficiency_bonus + self.ability_modifier(self.spellcasting_ability())

    def spell_attack_bonus(self) -> int:
        return self.proficiency_bonus + self.ability_modifier(self.spellcasting_ability())

    def _refresh_spell_slots(self) -> None:
        # No official SRD slots past level 20 - hold at the level-20 row.
        table = SPELL_SLOTS_BY_LEVEL[min(self.level, len(SPELL_SLOTS_BY_LEVEL)) - 1]
        self.spell_slots = {i + 1: count for i, count in enumerate(table) if count > 0}

    def _grant_new_spell_slots(self) -> None:
        """Leveling up unlocks new slot capacity but must not refill slots
        already spent - only long_rest() does a full reset. Adds just the
        newly-unlocked capacity (this level's max minus last level's max)
        to whatever's currently remaining, so a caster can't level up
        mid-dungeon for a free full slot refresh."""
        old_table = SPELL_SLOTS_BY_LEVEL[min(self.level - 1, len(SPELL_SLOTS_BY_LEVEL)) - 1]
        new_table = SPELL_SLOTS_BY_LEVEL[min(self.level, len(SPELL_SLOTS_BY_LEVEL)) - 1]
        for i, new_count in enumerate(new_table):
            delta = new_count - old_table[i]
            if delta > 0:
                spell_level = i + 1
                self.spell_slots[spell_level] = self.spell_slots.get(spell_level, 0) + delta

    def can_cast(self, spell_name: str) -> bool:
        db = Database()
        spell = db.get_spell(spell_name)
        if not spell or spell_name not in self.known_spells:
            return False
        if spell['level'] == 0:
            return True
        return self.spell_slots.get(spell['level'], 0) > 0

    def spend_spell_slot(self, level: int) -> bool:
        if self.spell_slots.get(level, 0) <= 0:
            return False
        self.spell_slots[level] -= 1
        return True

    def long_rest(self) -> None:
        """Full heal, spell slots restored, once-per-combat skills reset."""
        self.current_health = self.max_health
        self._refresh_spell_slots()
        self._skills_used_this_combat = set()

    def camp_rest(self) -> int:
        """
        A rough overnight camp out in the wild, away from any settlement's
        bed: recovers about half of missing HP, but - unlike long_rest() at
        a village/town - doesn't restore spell slots or reset skill
        cooldowns. Returns the HP actually recovered.
        """
        return self.heal(max(1, self.max_health // 2))

    # ------------------------------------------------------------------
    # Homebrew bonus skill tree (see data/skills.json - explicitly NOT
    # official D&D, just an extra layer of player choice)
    # ------------------------------------------------------------------
    def _skill_effect_total(self, effect_type: str) -> float:
        db = Database()
        total = 0.0
        for skill_id in self.unlocked_skills:
            node = db.get_skill(skill_id)
            if node and node['effect'].get('type') == effect_type:
                total += node['effect'].get('amount', 0)
        return total

    def has_skill(self, skill_id: str) -> bool:
        return skill_id in self.unlocked_skills

    def can_unlock_skill(self, skill_id: str) -> bool:
        if skill_id in self.unlocked_skills:
            return False
        db = Database()
        node = db.get_skill(skill_id)
        if not node:
            return False
        if self.skill_points < node.get('cost', 1):
            return False
        if node['requires'] and node['requires'] not in self.unlocked_skills:
            return False
        return True

    def unlock_skill(self, skill_id: str) -> bool:
        if not self.can_unlock_skill(skill_id):
            return False
        db = Database()
        node = db.get_skill(skill_id)
        self.unlocked_skills.append(skill_id)
        self.skill_points -= node.get('cost', 1)
        logging.info(f"{self.name} unlocked skill: {skill_id} for {node.get('cost', 1)} point(s)")
        return True

    def reset_combat_flags(self) -> None:
        self._skills_used_this_combat = set()
        self.pending_power_strike = False

    def get_active_skills(self) -> List[Dict]:
        db = Database()
        result = []
        for skill_id in self.unlocked_skills:
            node = db.get_skill(skill_id)
            if node and node['kind'] == 'active':
                result.append({**node, 'used_this_combat': skill_id in self._skills_used_this_combat})
        return result

    def use_active_skill(self, skill_id: str) -> Dict[str, str]:
        if skill_id not in self.unlocked_skills:
            return {'success': False, 'message': f"{self.name} has not unlocked that skill."}
        if skill_id in self._skills_used_this_combat:
            return {'success': False, 'message': "Already used this combat."}

        db = Database()
        node = db.get_skill(skill_id)
        if not node:
            return {'success': False, 'message': 'Unknown skill.'}

        effect = node['effect']
        if effect['type'] == 'active_power_strike':
            self.pending_power_strike = True
            message = f"{self.name} readies a Power Strike! The next attack will land hard."
        elif effect['type'] == 'active_heal_percent':
            heal_amount = int(self.max_health * effect['amount'])
            healed = self.heal(heal_amount)
            message = f"{self.name} uses Second Wind and recovers {healed} HP!"
        else:
            return {'success': False, 'message': 'This skill has no combat effect yet.'}

        self._skills_used_this_combat.add(skill_id)
        return {'success': True, 'message': message}

    @property
    def flee_bonus(self) -> int:
        return int(self._skill_effect_total('flee_bonus'))

    @property
    def loot_bonus(self) -> float:
        return self._skill_effect_total('loot_bonus')

    @property
    def lifesteal_fraction(self) -> float:
        return self._skill_effect_total('passive_lifesteal')

    @property
    def poison_chance(self) -> float:
        return self._skill_effect_total('passive_poison_chance')

    @property
    def dodge_chance(self) -> float:
        return self._skill_effect_total('passive_dodge_chance')

    @property
    def crit_multiplier(self) -> float:
        from config import CRITICAL_HIT_MULTIPLIER
        override = None
        db = Database()
        for skill_id in self.unlocked_skills:
            node = db.get_skill(skill_id)
            if node and node['effect'].get('type') == 'crit_multiplier':
                override = node['effect']['amount']
        return override if override is not None else CRITICAL_HIT_MULTIPLIER

    # ------------------------------------------------------------------
    # Combat stats (real D&D math)
    # ------------------------------------------------------------------
    def active_weapon(self) -> Optional[Dict]:
        """The weapon to show/use outside combat (no distance context) -
        prefers melee. Combat itself always calls weapon_for_range()
        instead, since which weapon is usable depends on the fight's
        current distance, not a fixed preference."""
        return self.equipped_melee_weapon or self.equipped_ranged_weapon

    def weapon_for_range(self, in_melee: bool) -> Optional[Dict]:
        """The equipped weapon usable at the current combat distance.
        Ranged weapons work at any distance, melee weapons only work
        adjacent to the enemy - so at melee range prefer the melee weapon
        but fall back to a ranged one if that's all that's equipped; at any
        other range only the ranged weapon reaches. None if nothing
        equipped fits (e.g. only a melee weapon while still far away)."""
        if in_melee:
            return self.equipped_melee_weapon or self.equipped_ranged_weapon
        return self.equipped_ranged_weapon

    def weapon_ability(self, weapon: Optional[Dict] = None) -> str:
        """STR for most weapons; DEX for ranged weapons, or for a finesse
        weapon when DEX is the better modifier (SRD finesse rule)."""
        if weapon is None:
            weapon = self.active_weapon()
        if not weapon:
            return 'strength'
        if weapon['type'] == 'ranged':
            return 'dexterity'
        if weapon.get('finesse') and self.ability_modifier('dexterity') > self.ability_modifier('strength'):
            return 'dexterity'
        return 'strength'

    def calculate_attack_bonus(self, weapon: Optional[Dict] = None) -> int:
        if weapon is None:
            weapon = self.active_weapon()
        ability = self.weapon_ability(weapon)
        bonus = self.ability_modifier(ability) + self.proficiency_bonus
        if weapon:
            bonus += weapon.get('magic_bonus', 0)
        bonus += int(self._skill_effect_total('passive_attack'))
        return int(bonus)

    # Kept as an alias - combat.py and the GUI read "total attack" generically
    # for both players and enemies.
    def calculate_total_attack(self) -> int:
        return self.calculate_attack_bonus()

    def roll_weapon_damage(self, weapon: Optional[Dict] = None) -> int:
        if weapon is None:
            weapon = self.active_weapon()
        ability = self.weapon_ability(weapon)
        mod = self.ability_modifier(ability)
        if weapon:
            base = dice.roll(weapon['damage_dice']) + weapon.get('magic_bonus', 0)
        else:
            base = 1  # unarmed strike
        return max(1, base + mod)

    def calculate_ac(self) -> int:
        dex_mod = self.ability_modifier('dexterity')
        if self.equipped_chest:
            category = self.equipped_chest.get('armor_category', 'light')
            base = self.equipped_chest.get('base_ac', 10) + self.equipped_chest.get('magic_bonus', 0)
            if category == 'light':
                ac = base + dex_mod
            elif category == 'medium':
                ac = base + min(dex_mod, 2)
            else:  # heavy armor: no DEX bonus
                ac = base
        else:
            ac = 10 + dex_mod
        # Head/hands/legs are a homebrew extension past the SRD's single
        # body-armor slot - each just adds its flat AC, no DEX interaction
        # (that rule is specifically about body armor category).
        for slot in (self.equipped_head, self.equipped_hands, self.equipped_legs):
            if slot:
                ac += slot.get('base_ac', 0) + slot.get('magic_bonus', 0)
        if self.equipped_shield:
            ac += self.equipped_shield.get('base_ac', 2) + self.equipped_shield.get('magic_bonus', 0)
        ac += int(self._skill_effect_total('passive_defense'))
        return int(ac)

    def calculate_total_defense(self) -> int:
        """Alias kept so combat.py's shared attacker/defender code paths work
        for both Character and Enemy without branching on type."""
        return self.calculate_ac() - 10

    def take_damage(self, damage: int) -> bool:
        new_health = self.current_health - damage
        if new_health <= 0:
            db = Database()
            for skill_id in self.unlocked_skills:
                if skill_id in self._skills_used_this_combat:
                    continue
                node = db.get_skill(skill_id)
                if node and node['effect'].get('type') == 'survive_lethal':
                    self._skills_used_this_combat.add(skill_id)
                    self.current_health = 1
                    logging.info(f"{self.name}'s {node['name']} triggers! Survives at 1 HP.")
                    return True

        self.current_health = max(0, new_health)
        logging.info(f"{self.name} took {damage} damage. Health: {self.current_health}/{self.max_health}")
        return self.current_health > 0

    def heal(self, amount: int) -> int:
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        actual_heal = self.current_health - old_health
        logging.info(f"{self.name} healed for {actual_heal}. Health: {self.current_health}/{self.max_health}")
        return actual_heal

    def use_healing_potion(self, potion: Dict) -> bool:
        if potion['type'] != 'consumable':
            logging.warning(f"Attempted to use non-consumable item as potion: {potion['name']}")
            return False

        effect = potion['effect']
        if effect == 'cure_ailment':
            cured = [name for name in ('poison', 'bleed', 'burn') if name in self.status_effects]
            for name in cured:
                del self.status_effects[name]
            self.remove_item(potion)
            logging.info(f"{self.name} used {potion['name']} and cured: {cured or 'nothing'}")
            return True

        if effect.startswith('heal_'):
            heal_dice = effect[len('heal_'):]
            heal_amount = dice.roll(heal_dice)
            self.heal(heal_amount)
            self.remove_item(potion)
            logging.info(f"{self.name} used {potion['name']} and healed for {heal_amount}")
            return True

        logging.warning(f"Consumable has no recognized effect: {potion['name']} ({effect})")
        return False

    def add_item(self, item: Dict) -> None:
        if isinstance(item, str):
            db = Database()
            item_data = db.get_item(item)
            if item_data:
                self.inventory.append(item_data)
                logging.info(f"{self.name} acquired {item_data['name']}")
            else:
                logging.error(f"Failed to load item data for: {item}")
        else:
            self.inventory.append(item)
            logging.info(f"{self.name} acquired {item['name']}")

    def remove_item(self, item: Dict) -> bool:
        try:
            self.inventory.remove(item)
            logging.info(f"{self.name} removed {item['name']} from inventory")
            return True
        except ValueError:
            logging.warning(f"Failed to remove {item['name']} from {self.name}'s inventory - item not found")
            return False

    # type -> equip-slot attribute name. 'armor' resolves to one of several
    # chest/head/hands/legs attributes via item['slot'] instead (see below) -
    # it's the one type that doesn't map to a single fixed slot.
    _WEAPON_SLOTS = {'weapon': 'equipped_melee_weapon', 'ranged': 'equipped_ranged_weapon'}
    _ARMOR_SLOTS = {'head': 'equipped_head', 'chest': 'equipped_chest',
                    'hands': 'equipped_hands', 'legs': 'equipped_legs'}

    def equip_item(self, item: Dict) -> bool:
        slot_attr = None
        if item['type'] in self._WEAPON_SLOTS:
            slot_attr = self._WEAPON_SLOTS[item['type']]
        elif item['type'] == 'armor':
            slot_attr = self._ARMOR_SLOTS.get(item.get('slot', 'chest'), 'equipped_chest')
        elif item['type'] == 'shield':
            slot_attr = 'equipped_shield'
        elif item['type'] == 'necklace':
            slot_attr = 'equipped_necklace'
        elif item['type'] == 'ring':
            # Fill the first open ring slot; if both are full, replace the left.
            slot_attr = 'equipped_ring_left' if not self.equipped_ring_left else (
                'equipped_ring_right' if not self.equipped_ring_right else 'equipped_ring_left')
        else:
            return False

        previous = getattr(self, slot_attr)
        if previous:
            self.inventory.append(previous)
        setattr(self, slot_attr, item)
        logging.info(f"{self.name} equipped {item['type']}: {item['name']} ({slot_attr})")

        self.inventory.remove(item)
        return True

    def has_item_named(self, item_name: str) -> bool:
        return any(i['name'] == item_name or i.get('base_name') == item_name for i in self.inventory)

    def consume_item_named(self, item_name: str) -> bool:
        for item in self.inventory:
            if item['name'] == item_name or item.get('base_name') == item_name:
                return self.remove_item(item)
        return False

    def _describe_equipped(self, item: Optional[Dict]) -> str:
        if not item:
            return "None"
        if item['type'] in ('weapon', 'ranged'):
            return f"{item['name']} ({item['damage_dice']} {item.get('damage_type', '')})"
        if item['type'] in ('armor', 'shield'):
            return f"{item['name']} (AC {item.get('base_ac', 0)})"
        if item['type'] in ('ring', 'necklace') and item.get('ability_bonus'):
            bonuses = ", ".join(f"+{v} {k[:3].upper()}" for k, v in item['ability_bonus'].items())
            return f"{item['name']} ({bonuses})"
        return item['name']

    def get_equipment_display(self) -> Dict[str, str]:
        return {
            'melee_weapon': self._describe_equipped(self.equipped_melee_weapon),
            'ranged_weapon': self._describe_equipped(self.equipped_ranged_weapon),
            'head': self._describe_equipped(self.equipped_head),
            'chest': self._describe_equipped(self.equipped_chest),
            'hands': self._describe_equipped(self.equipped_hands),
            'legs': self._describe_equipped(self.equipped_legs),
            'shield': self._describe_equipped(self.equipped_shield),
            'ring_left': self._describe_equipped(self.equipped_ring_left),
            'ring_right': self._describe_equipped(self.equipped_ring_right),
            'necklace': self._describe_equipped(self.equipped_necklace),
        }

    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'age': self.age,
            'class_key': self.class_key,
            'level': self.level,
            'xp': self.xp,
            'ability_scores': self.ability_scores,
            'current_health': self.current_health,
            'inventory': self.inventory,
            'equipped_melee_weapon': self.equipped_melee_weapon,
            'equipped_ranged_weapon': self.equipped_ranged_weapon,
            'equipped_head': self.equipped_head,
            'equipped_chest': self.equipped_chest,
            'equipped_hands': self.equipped_hands,
            'equipped_legs': self.equipped_legs,
            'equipped_shield': self.equipped_shield,
            'equipped_ring_left': self.equipped_ring_left,
            'equipped_ring_right': self.equipped_ring_right,
            'equipped_necklace': self.equipped_necklace,
            'money': self.money,
            'skill_points': self.skill_points,
            'unlocked_skills': self.unlocked_skills,
            'spell_slots': self.spell_slots,
            'known_spells': self.known_spells,
        }

    def get_status_effects(self) -> List[str]:
        return list(self.status_effects.keys())

    def can_afford(self, price: int) -> bool:
        return self.money >= price
