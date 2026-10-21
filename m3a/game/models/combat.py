from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any, List
import random
import logging
from config import CRITICAL_HIT_MULTIPLIER
from database import Database
import dice

DOT_STATUSES = {
    'bleed': {'turns': 2},
    'burn': {'turns': 2},
    'poison': {'turns': 3},
}
# Per-turn damage as a fraction of the triggering hit's damage, not a flat
# number - a flat DOT goes stale every time weapon damage grows (4.1.13).
# Burn kept 1.5x bleed's rate, preserving their original 3:2 ratio.
DOT_DAMAGE_FRACTION = {
    'bleed': 0.10,
    'burn': 0.15,
    'poison': 0.20,
}
STUN_CHANCE = 0.5
# Drain (weapon effect) heals the attacker on every hit, same as Vampiric
# Strikes (skill) - matched to the same fraction so neither one is the
# obviously-better choice just because of how it's delivered.
DRAIN_HEAL_FRACTION = 0.15


@dataclass
class CombatAction:
    """
    Represents a combat action.
    """
    type: str  # 'attack', 'cast_spell', 'flee', 'move'
    target: Optional[str] = None
    spell_name: Optional[str] = None
    distance_delta: int = 0  # for 'move': +1 retreats, -1 advances


class CombatSystem:
    """
    Represents the combat system. Players roll d20 + ability modifier +
    proficiency bonus against the target's AC (real D&D 5e SRD math);
    enemies use their flat statblock the way SRD monsters do.
    """

    def roll_d20(self) -> int:
        return random.randint(1, 20)

    def calculate_hit(self, attacker: Any, defender: Any, attack_bonus: int) -> Tuple[bool, int, bool]:
        """
        Calculate if an attack hits using the D20 system. `attack_bonus` is
        supplied by the caller (not read off `attacker` directly) because it
        depends on which weapon - melee or ranged - is actually usable at
        the current combat distance. A primed Power Strike (homebrew skill)
        guarantees a hit and skips the dodge check below - it's meant to be
        an unavoidable blow. Natural 20 always hits and crits; natural 1
        always misses.
        """
        roll = self.roll_d20()

        if getattr(attacker, 'pending_power_strike', False):
            return True, roll, (roll == 20)

        if roll == 20:
            hit, is_crit = True, True
        elif roll == 1:
            return False, roll, False
        else:
            target_ac = 10 + defender.calculate_total_defense()
            hit, is_crit = (roll + attack_bonus >= target_ac), False

        if hit and self._defender_dodges(defender):
            return False, roll, False
        return hit, roll, is_crit

    def _defender_dodges(self, defender: Any) -> bool:
        """Evasion (homebrew skill): a flat chance to avoid an attack
        entirely, checked after the normal hit roll succeeds."""
        dodge_chance = getattr(defender, 'dodge_chance', 0)
        return bool(dodge_chance) and random.random() < dodge_chance

    def process_turn(self, attacker: Any, defender: Any, action: CombatAction, distance: int = 0) -> Dict[str, Any]:
        result = {
            'success': True,
            'damage_dealt': 0,
            'fled': False,
            'messages': [],
            'roll_info': {}
        }

        dot_messages, stunned = self._tick_status(attacker)
        result['messages'].extend(dot_messages)
        if stunned:
            result['success'] = False
            result['messages'].append(f"{attacker.name} is stunned and can't act!")
            return result

        # A primed Power Strike only pays off on the attack it was meant for -
        # any other action (spell, flee, move) burns it for nothing instead
        # of letting it sit banked indefinitely for a later swing.
        if action.type != 'attack' and getattr(attacker, 'pending_power_strike', False):
            attacker.pending_power_strike = False
            result['messages'].append(f"{attacker.name}'s readied Power Strike fizzles, unused.")

        if action.type == 'attack':
            self._resolve_attacks(attacker, defender, result, distance)
        elif action.type == 'cast_spell':
            self._resolve_spell(attacker, defender, action.spell_name, result)
        elif action.type == 'flee':
            self._resolve_flee(attacker, result, distance)

        return result

    def _resolve_attacks(self, attacker: Any, defender: Any, result: Dict[str, Any], distance: int = 0) -> None:
        """Resolve one Attack action, including a Fighter's Extra Attack
        (multiple attack rolls per action at level 5/11/20). `distance`
        (0 = melee range, >0 = too far for melee) picks which equipped
        weapon - melee or ranged - the attack actually uses; enemies have
        no weapon/range concept at all and always just fight with their
        flat statblock regardless of distance."""
        swings = attacker.attacks_per_action() if hasattr(attacker, 'attacks_per_action') else 1
        any_hit = False

        weapon = None
        has_ranged_support = hasattr(attacker, 'weapon_for_range')
        if has_ranged_support:
            weapon = attacker.weapon_for_range(distance == 0)
            # At melee range (distance 0), weapon_for_range() falls back to
            # a ranged weapon if no melee weapon is equipped, so it's only
            # None here with distance > 0 and no ranged weapon equipped -
            # too far to reach with whatever's in hand.
            if weapon is None and attacker.equipped_melee_weapon:
                result['success'] = False
                result['messages'].append(
                    f"{attacker.name} has no ranged weapon equipped and can't reach the enemy from here!")
                return

        for _ in range(swings):
            if defender.current_health <= 0:
                break

            attack_bonus = attacker.calculate_attack_bonus(weapon) if has_ranged_support \
                else attacker.calculate_total_attack()
            hit_success, roll, is_crit = self.calculate_hit(attacker, defender, attack_bonus)
            target_ac = 10 + defender.calculate_total_defense()

            power_strike = getattr(attacker, 'pending_power_strike', False)
            if hasattr(attacker, 'pending_power_strike'):
                attacker.pending_power_strike = False

            if hit_success:
                any_hit = True
                damage = self._calculate_melee_damage(attacker, defender, is_crit, power_strike, weapon)
                defender.take_damage(damage)
                result['damage_dealt'] += damage

                crit_text = " **CRITICAL HIT!**" if is_crit else ""
                power_text = " **POWER STRIKE!**" if power_strike else ""
                weapon_text = f" with {weapon['name']}" if weapon else ""
                message = (f"{attacker.name} attacks {defender.name}{weapon_text}{crit_text}{power_text}! "
                           f"[Roll: {roll} + {attack_bonus} vs AC {target_ac}] "
                           f"Dealing {damage} damage!")
                result['messages'].append(message)

                weapon_for_effect = weapon if has_ranged_support else getattr(attacker, 'equipped_weapon', None)
                effect = weapon_for_effect.get('effect') if weapon_for_effect else None
                if effect and effect not in ('none', None):
                    effect_message = self._apply_weapon_effect(attacker, defender, effect, damage)
                    if effect_message:
                        result['messages'].append(effect_message)

                lifesteal_message = self._apply_lifesteal(attacker, damage)
                if lifesteal_message:
                    result['messages'].append(lifesteal_message)

                poison_message = self._apply_poison_chance(attacker, defender, damage)
                if poison_message:
                    result['messages'].append(poison_message)
            else:
                miss_reason = "Critical Miss!" if roll == 1 else "Miss!"
                message = (f"{attacker.name}'s attack missed! {miss_reason} "
                           f"[Roll: {roll} + {attack_bonus} vs AC {target_ac}]")
                result['messages'].append(message)

        result['success'] = any_hit

    def _resolve_spell(self, attacker: Any, defender: Any, spell_name: str, result: Dict[str, Any]) -> None:
        db = Database()
        spell = db.get_spell(spell_name)
        if not spell or not hasattr(attacker, 'can_cast') or not attacker.can_cast(spell_name):
            result['success'] = False
            result['messages'].append(f"{attacker.name} can't cast {spell_name} right now.")
            return

        level = spell['level']
        if level > 0:
            attacker.spend_spell_slot(level)

        character_level = getattr(attacker, 'level', 1)

        if spell['cast_type'] == 'attack':
            roll = self.roll_d20()
            spell_bonus = attacker.spell_attack_bonus()
            target_ac = 10 + defender.calculate_total_defense()
            is_crit = roll == 20
            hit = is_crit or (roll != 1 and roll + spell_bonus >= target_ac)
            if hit:
                damage = self._scaled_cantrip_damage(spell, character_level)
                if is_crit:
                    crit_multiplier = getattr(attacker, 'crit_multiplier', CRITICAL_HIT_MULTIPLIER)
                    damage = int(damage * crit_multiplier)
                defender.take_damage(damage)
                result['damage_dealt'] += damage
                result['messages'].append(
                    f"{attacker.name} casts {spell_name}! [Roll: {roll} + {spell_bonus} vs AC {target_ac}] "
                    f"Dealing {damage} {spell.get('damage_type', '')} damage!")
            else:
                result['success'] = False
                result['messages'].append(
                    f"{attacker.name} casts {spell_name}, but it misses! "
                    f"[Roll: {roll} + {spell_bonus} vs AC {target_ac}]")

        elif spell['cast_type'] == 'save':
            save_dc = attacker.spell_save_dc()
            save_roll = self.roll_d20()
            defender_mod = 0
            if hasattr(defender, 'ability_modifier'):
                defender_mod = defender.ability_modifier(spell['save_ability'])
            saved = (save_roll + defender_mod) >= save_dc
            damage = self._scaled_cantrip_damage(spell, character_level)
            if saved:
                damage //= 2
                result['messages'].append(
                    f"{attacker.name} casts {spell_name}! {defender.name} succeeds on a DC {save_dc} save "
                    f"(half damage).")
            else:
                result['messages'].append(
                    f"{attacker.name} casts {spell_name}! {defender.name} fails a DC {save_dc} save!")
            defender.take_damage(damage)
            result['damage_dealt'] += damage
            result['messages'][-1] += f" Dealing {damage} {spell.get('damage_type', '')} damage!"

        elif spell['cast_type'] == 'auto_hit_multi':
            num_darts = spell.get('base_darts', 3)
            total = sum(dice.roll(spell['dart_dice']) for _ in range(num_darts))
            defender.take_damage(total)
            result['damage_dealt'] += total
            result['messages'].append(
                f"{attacker.name} casts {spell_name}! {num_darts} darts strike {defender.name} "
                f"automatically for {total} {spell.get('damage_type', '')} damage!")

        elif spell['cast_type'] == 'heal':
            heal_mod = attacker.ability_modifier(attacker.spellcasting_ability())
            healed = attacker.heal(dice.roll(spell['heal_dice']) + heal_mod)
            result['messages'].append(f"{attacker.name} casts {spell_name} and recovers {healed} HP!")

    def _scaled_cantrip_damage(self, spell: Dict[str, Any], character_level: int) -> int:
        """Cantrips scale with character level, not spell slots (SRD rule)."""
        if spell['level'] != 0:
            return dice.roll(spell['damage_dice'])
        scale_levels = spell.get('cantrip_scale_levels', [1])
        multiplier = sum(1 for lvl in scale_levels if character_level >= lvl)
        count, sides, modifier = dice.parse(spell['damage_dice'])
        return sum(random.randint(1, sides) for _ in range(count * max(1, multiplier))) + modifier

    def _resolve_flee(self, attacker: Any, result: Dict[str, Any], distance: int = 0) -> None:
        flee_roll = self.roll_d20()
        flee_dc = 10
        # Easier to run when you're not already toe-to-toe with the enemy.
        flee_bonus = 2 + getattr(attacker, 'flee_bonus', 0) + distance if hasattr(attacker, 'title') else 0

        if flee_roll + flee_bonus >= flee_dc:
            result['fled'] = True
            result['messages'].append(f"{attacker.name} successfully fled! [Roll: {flee_roll} + {flee_bonus} vs DC {flee_dc}]")
        else:
            result['success'] = False
            result['messages'].append(f"{attacker.name} failed to flee! [Roll: {flee_roll} + {flee_bonus} vs DC {flee_dc}]")

    def _tick_status(self, character: Any) -> Tuple[List[str], bool]:
        messages: List[str] = []
        statuses = getattr(character, 'status_effects', None)
        if not statuses:
            return messages, False

        stunned = False
        for name in list(statuses.keys()):
            data = statuses[name]
            if name == 'stunned':
                stunned = True
                del statuses[name]
                continue
            damage = data.get('damage', 0)
            if damage:
                character.take_damage(damage)
                messages.append(f"{character.name} suffers {damage} {name} damage!")
            data['turns'] -= 1
            if data['turns'] <= 0:
                del statuses[name]
            else:
                statuses[name] = data

        return messages, stunned

    def _apply_weapon_effect(self, attacker: Any, defender: Any, effect: str, damage: int) -> Optional[str]:
        if effect in DOT_STATUSES and hasattr(defender, 'status_effects'):
            per_turn = max(1, round(damage * DOT_DAMAGE_FRACTION[effect]))
            defender.status_effects[effect] = {'damage': per_turn, 'turns': DOT_STATUSES[effect]['turns']}
            return f"{defender.name} is afflicted with {effect}! ({per_turn} damage/turn)"
        if effect == 'stun' and hasattr(defender, 'status_effects'):
            if random.random() < STUN_CHANCE:
                defender.status_effects['stunned'] = {'turns': 1}
                return f"{defender.name} is stunned!"
            return None
        if effect == 'drain':
            # Scaled off this hit's damage, same basis as Vampiric Strikes'
            # lifesteal (0.15 * damage) - it was 5% of the attacker's own max
            # HP, which at endgame healed 20x more than lifesteal would on
            # the identical swing and more than the hit itself dealt.
            heal_amount = max(1, int(damage * DRAIN_HEAL_FRACTION))
            if hasattr(attacker, 'heal'):
                attacker.heal(heal_amount)
                return f"{attacker.name} drains {heal_amount} HP from the hit!"
        return None

    def _apply_lifesteal(self, attacker: Any, damage: int) -> Optional[str]:
        """Vampiric Strikes (homebrew skill): heal a fraction of damage dealt."""
        fraction = getattr(attacker, 'lifesteal_fraction', 0)
        if not fraction or not hasattr(attacker, 'heal'):
            return None
        healed = attacker.heal(max(1, int(damage * fraction)))
        if healed:
            return f"{attacker.name} drains {healed} HP from the strike!"
        return None

    def _apply_poison_chance(self, attacker: Any, defender: Any, damage: int) -> Optional[str]:
        """Venomous Strikes (homebrew skill): a chance to poison on hit, scaled
        to the triggering hit's damage rather than a flat number - a flat DOT
        went stale every time weapon damage grew (same issue 4.1.11 fixed for
        weapons vs. enemy HP). Per-turn damage is set so the 25%-chance,
        3-turn poison lands at the same expected value per hit as Vampiric
        Strikes' 100%-chance 15% lifesteal: 0.25 * (3 * per_turn) == 0.15 *
        damage  =>  per_turn == 0.2 * damage."""
        chance = getattr(attacker, 'poison_chance', 0)
        if not chance or not hasattr(defender, 'status_effects') or random.random() >= chance:
            return None
        per_turn = max(1, round(damage * DOT_DAMAGE_FRACTION['poison']))
        defender.status_effects['poison'] = {'damage': per_turn, 'turns': DOT_STATUSES['poison']['turns']}
        return f"{defender.name} is poisoned! ({per_turn} damage/turn)"

    def _calculate_melee_damage(self, attacker: Any, defender: Any, is_crit: bool, power_strike: bool,
                                 weapon: Optional[Dict] = None) -> int:
        """
        Real D&D damage: weapon die + ability modifier (AC only decides
        hit/miss, it does not reduce damage further). Enemies without the
        SRD character math fall back to a simple attack-stat-based roll.
        """
        if hasattr(attacker, 'roll_weapon_damage'):
            damage = attacker.roll_weapon_damage(weapon)
            if hasattr(attacker, 'sneak_attack_dice'):
                sneak_dice = attacker.sneak_attack_dice()
                if sneak_dice:
                    damage += sum(random.randint(1, 6) for _ in range(sneak_dice))
        else:
            damage = dice.roll('1d6') + (getattr(attacker, 'attack', 0) // 2)

        crit_multiplier = getattr(attacker, 'crit_multiplier', CRITICAL_HIT_MULTIPLIER)
        if is_crit:
            damage = int(damage * crit_multiplier)
        if power_strike:
            damage = int(damage * 1.5)

        return max(1, int(damage))

    def check_combat_status(self, character: Any, enemy: Any) -> Tuple[bool, str]:
        if character.current_health <= 0:
            return True, 'defeat'
        if enemy.current_health <= 0:
            return True, 'victory'
        return False, ''

    def distribute_rewards(self, character: Any, enemy: Any) -> Dict[str, Any]:
        db = Database()
        rewards = {'xp': enemy.xp_value, 'items': [], 'copper': 0}

        drops = enemy.get_drops(character)
        for drop_type, value in drops:
            if drop_type == 'copper':
                rewards['copper'] = value
                character.money += value
            elif drop_type == 'item':
                item_data = db.get_item(value)
                if item_data:
                    rewards['items'].append(item_data['name'])
                    character.add_item(item_data)
                else:
                    logging.error(f"Failed to load item data for drop: {value}")

        character.add_xp(rewards['xp'])
        logging.info(f"Combat rewards distributed: {rewards}")
        return rewards
