# Dungeon RPG - Full Manual

This is the complete reference: every mechanic, every formula, every number,
as the game actually implements them right now. For a short on-ramp instead,
see [`quickstart.md`](../quickstart.md) in the project root. For the full
item catalog, see [`items_reference.md`](items_reference.md) in this folder.

If something here disagrees with what you see in-game, the game is correct
and this doc is stale - that's a documentation bug, say so.

---

## Contents

1. [Character Creation](#1-character-creation)
2. [Ability Scores & Modifiers](#2-ability-scores--modifiers)
3. [Combat](#3-combat)
4. [Equipment](#4-equipment)
5. [Leveling](#5-leveling)
6. [Skills (Homebrew)](#6-skills-homebrew)
7. [Spells](#7-spells)
8. [The World Map](#8-the-world-map)
9. [Dungeons](#9-dungeons)
10. [The Economy](#10-the-economy)
11. [Quests](#11-quests)
12. [Camp & Scout](#12-camp--scout)
13. [Status Effects](#13-status-effects)
14. [Interface](#14-interface)
15. [Saving](#15-saving)
16. [What's Not Implemented](#16-whats-not-implemented)

---

## 1. Character Creation

**File > New Game** (`Ctrl+N`). You provide a name and an age (1-100); the
rest is generated or chosen.

**Ability scores** are rolled with the real SRD method: roll 4d6, drop the
lowest die, six times, giving six scores typically in the 8-18 range. Scores
are then assigned to the six abilities in the order your class's
`ability_priority` list specifies - you don't choose which score goes where.

**Classes:**

| Class | Hit Die | Primary | Saves | Starting Weapon | Starting Armor | Starting Shield | Caster |
|---|---|---|---|---|---|---|---|
| Fighter | d10 | STR | STR, CON | Longsword | Chain Mail | Shield | No |
| Rogue | d8 | DEX | DEX, INT | Rapier | Studded Leather | - | No |
| Wizard | d6 | INT | INT, WIS | Quarterstaff | - | - | Yes (INT) |
| Cleric | d8 | WIS | WIS, CHA | Mace | Chain Shirt | Shield | Yes (WIS) |

**Starting kit** (all classes): class weapon/armor/shield above, 3x Potion
of Healing, 1x Thieves' Tools, 1x Torch, 1500 copper (15 gold).

---

## 2. Ability Scores & Modifiers

Standard SRD formula: `modifier = (score - 10) // 2` (integer division,
rounds toward negative infinity - a score of 9 gives -1, not 0).

Equipped **rings and a necklace** add directly to the score used in this
formula before the modifier is computed, so a +2 Ring of Strength raises
your effective STR score by 2, which can push you across a modifier
breakpoint (e.g. 18 -> 20 raises the modifier from +4 to +5).

The modifier feeds into: attack rolls, damage rolls, AC (via DEX), saving
throws (spell saves against you), spell attack bonus, spell save DC, and
flee rolls indirectly through skills.

---

## 3. Combat

Every roll is a d20. Natural 20 always hits and crits; natural 1 always
misses. Otherwise: `roll + modifier >= target number` (AC to hit, DC to
save).

### Range

Combat has a homebrew 3-band distance system: **Melee / Mid / Far**
(`config.COMBAT_DISTANCE_BANDS`). Every fight starts at **Far**
(`COMBAT_START_DISTANCE = 2`).

- Enemies have no ranged attacks. Any enemy turn spent above Melee range is
  spent closing the distance by one band instead of attacking.
- **Melee weapons only work at Melee range.** **Ranged weapons work at any
  range**, and are used automatically at Melee range too if you have no
  melee weapon equipped (`Character.weapon_for_range()` prefers melee at
  Melee range, falls back to ranged).
- If you have a melee weapon but no ranged weapon and the enemy isn't at
  Melee range yet, Attack is disabled - Advance first, or wait for the
  enemy to close in.
- **Advance** (-1 band) and **Retreat** (+1 band) cost your turn, same as
  Attack. Both route through the same turn-processing as any other action,
  so a stunned character can't move either, and poison/bleed/burn still
  ticks on a movement turn.
- The enemy closes in on its own turn regardless of what you do, so
  Retreat alone doesn't create lasting distance unless repeated every round.
- Fleeing gets `+distance` added to the roll - easier to escape the farther
  away you already are.

### Attack resolution

1. Roll d20.
2. Natural 20: auto-hit, crit. Natural 1: auto-miss. Otherwise, hit if
   `roll + attack_bonus >= target AC`.
3. If it would hit, the **defender's Evasion** skill (if unlocked) gets a
   flat chance (10%) to negate it entirely - checked after the roll, so
   even a crit can be dodged (a primed Power Strike skips this check
   entirely, since it's meant to be unavoidable).
4. Damage = weapon die roll + ability modifier + weapon's magic bonus,
   minimum 1. A confirmed critical multiplies this by `crit_multiplier`
   (2.0 base, overridden to 2.5/3.0 by the Executioner/Death's Precision
   skills). A Power Strike multiplies by 1.5 on top of that.
5. Any weapon `effect` (bleed/burn/stun/drain - see
   [items_reference.md](items_reference.md) for which items carry one)
   applies after a hit, independent of skill-driven lifesteal/poison below.
6. **Vampiric Strikes** (skill): heals the attacker for a percentage of
   the damage just dealt.
7. **Venomous Strikes** (skill): 25% chance to apply poison, dealing 20% of
   that hit's damage per turn for 3 turns - see [Status Effects](#13-status-effects).

**Attack bonus** = ability modifier (STR normally, DEX for ranged weapons
or finesse weapons where DEX is better) + proficiency bonus + weapon's
magic bonus + any `passive_attack` skill total.

**AC** = see [Equipment](#4-equipment) below.

### Extra Attack / Sneak Attack

- **Fighter**: 1 attack normally, 2 at level 5+, 3 at level 11+, 4 at level
  20+ (caps there - `Character.attacks_per_action()`).
- **Rogue**: Sneak Attack adds `(min(level, 20) + 1) // 2` d6 to one hit's
  damage, capped at 10d6 (the real SRD level-20 value - there's no official
  continuation past that, so it's clamped rather than scaling further).

### Flee

`d20 + 2 + distance + flee_bonus skill total >= DC 10`. Base ~65% even at
Melee range (roll 8+ with the flat +2); Swift Feet/Pathfinder and higher
distance both improve it further.

---

## 4. Equipment

10 slots: **Melee Weapon, Ranged Weapon, Head, Chest, Hands, Legs, Shield,
Ring L, Ring R, Necklace**. See [items_reference.md](items_reference.md)
for every item that can fill them.

### AC formula

```
if Chest is equipped:
    category = chest's armor_category (light/medium/heavy)
    base = chest base_ac + chest magic_bonus
    if light:  AC = base + full DEX modifier
    if medium: AC = base + min(DEX modifier, 2)
    if heavy:  AC = base + 0  (no DEX)
else:
    AC = 10 + DEX modifier

AC += Head.base_ac + Head.magic_bonus   (if equipped)
AC += Hands.base_ac + Hands.magic_bonus (if equipped)
AC += Legs.base_ac + Legs.magic_bonus   (if equipped)
AC += Shield.base_ac + Shield.magic_bonus (if equipped)
AC += total of any passive_defense skill bonuses
```

The light/medium/heavy DEX rule is the real SRD rule and only applies to
**Chest** - that's the one slot the SRD actually models. Head/Hands/Legs
are a homebrew extension on top: each is just a flat AC add, regardless of
category, since there's no SRD precedent for separate head/hand/leg armor
slots at all.

### Magic bonus

Any `magic_eligible` item (every weapon, every piece of armor, both
shields - never rings, necklaces, consumables, or tools) rolls a bonus
when it's created (bought, looted, or starting gear forced to +0):

| Roll | Chance | Bonus | Price multiplier |
|---|---|---|---|
| +0 | 70% | +0 | 1x |
| +1 | 20% | +1 to attack/damage or AC | 3x |
| +2 | 8% | +2 | 8x |
| +3 | 2% | +3 | 20x |

The price multiplier (`data/magic_bonus.json`) applies to `price_copper`
at creation time, so a lucky +3 roll costs noticeably more to buy and sells
for noticeably more too - it's not just a name prefix.

### Rings & Necklace

`ability_bonus` (e.g. `{"strength": 2}`) adds directly to that ability
score, which flows through every modifier that reads it (attack, AC via
DEX, spell DC, etc. - see [Ability Scores](#2-ability-scores--modifiers)).
Never roll a magic bonus; their stated bonus is fixed.

---

## 5. Leveling

Level cap is **50**. XP required to reach each level follows
`XP_BY_LEVEL` in `config.py` - roughly quadratic (`150 * (level-1)^2`),
reaching level 2 at 150 XP (about 8 tier-1 kills), level 10 at 12,150,
level 25 at 93,750, level 50 at 360,150 total.

Per level: HP increases by your class's hit die (average value, not a
fresh roll) plus your CON modifier; **proficiency bonus** increases every 4
levels, from +2 at level 1 up to +14 at level 49-50 (continuing the SRD's
own "+1 every 4 levels" pattern past where the real SRD stops at level 20).

**Spellcasters** (Wizard/Cleric) learn their class's designated spell for a
given spell level automatically, the instant they have a slot of that
level (`Character._learn_available_spells()`) - nothing to choose, it just
appears in your known spells.

---

## 6. Skills (Homebrew)

Explicitly **not** official D&D - a bonus layer of player choice on top.
Skill points arrive at levels 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48
(12 total). Each node costs 1 point (`node['cost']`, enforced - a node
could in principle cost more, nothing currently does). Unlocking a node
requires its prerequisite already unlocked; each branch is a single
5-deep chain (no branching choice within a branch, but 12 points against
15 total nodes means you can't max everything - real tradeoffs across the
3 branches).

| Tier | Offense | Defense | Utility |
|---|---|---|---|
| 1 | **Power Strike** (active) - next attack auto-hits, +50% damage | **Second Wind** (active) - heal 20% max HP | **Swift Feet** - +3 flee rolls |
| 2 | **Weapon Mastery** - +2 attack | **Iron Skin** - +2 AC | **Treasure Hunter** - +10% bonus loot chance |
| 3 | **Executioner** - crits deal 2.5x | **Last Stand** - survive a lethal hit at 1 HP, once/combat | **Battle Focus** - +10% XP |
| 4 | **Vampiric Strikes** - heal 15% of damage dealt, on hit | **Evasion** - 10% chance to dodge any attack | **Venomous Strikes** - 25% chance to poison on hit |
| 5 | **Death's Precision** - crits deal 3.0x | **Phoenix Heart** (active) - heal 35% max HP, separate from Second Wind | **Fortune's Favor** - +15% XP (stacks with Battle Focus, +25% total) |

Open with **K**.

---

## 7. Spells

Only Wizard and Cleric have a spell list. Each has 2 cantrips (known from
level 1) and one spell at every character level 1-9 corresponding to that
spell level, granted automatically. Four mechanical types exist in the
engine (`cast_type`):

- **attack**: spell attack roll (`proficiency + spellcasting ability mod`)
  vs. target AC.
- **save**: target rolls `d20 + their relevant ability mod` vs. your spell
  save DC (`8 + proficiency + spellcasting ability mod`); failure takes
  full damage, success takes half.
- **auto_hit_multi**: always hits, rolls N instances of a die ("darts").
- **heal**: rolls healing dice + your spellcasting ability modifier.

### Wizard (INT)

Cantrips: Fire Bolt, Ray of Frost. Leveled: Magic Missile (1st) ->
Scorching Ray (2nd) -> Fireball (3rd) -> Ice Storm (4th) -> Cone of Cold
(5th) -> Chain Lightning (6th) -> Prismatic Spray (7th) -> Sunburst (8th)
-> Meteor Swarm (9th).

### Cleric (WIS)

Cantrips: Sacred Flame, Toll the Dead. Leveled: Cure Wounds (1st) ->
Prayer of Healing (2nd) -> Spirit Guardians (3rd) -> Guardian of Faith
(4th) -> Flame Strike (5th) -> Heal (6th) -> Fire Storm (7th) -> Divine
Wrath (8th) -> Mass Heal (9th).

Casting a leveled spell spends one slot of that spell's level
(`spell_slots`, refreshed by `long_rest()` at a village/town, not by
`camp_rest()`). Cantrips never cost a slot.

---

## 8. The World Map

Generated once per new game: a 32x32 open grid (every tile connects to
every neighbor - no maze walls, unlike dungeons). Terrain is grown as
organic blobs (lakes, forests) rather than scattered randomly; water
blocks movement, everything else is just visual texture, with roads
pathed between every settlement and its nearest neighbor.

Node counts (`WorldMap._generate_world`): up to 8 villages
(`max(6, size//4)`), 5 towns (`max(4, size//6)`), 10 dungeons
(`max(8, size//3)`), 32 random encounters (`max(20, size)`) - scaled by
map size, currently fixed at 32.

| Tile | Trigger |
|---|---|
| Village / Town | Full heal + spell slot restore (`long_rest()`), opens Merchant with a Quests tab |
| Dungeon | Enters a new `Dungeon` instance at that tile's tier; shows "Tier N (Lv M+)" before you commit |
| Encounter (`?`) | ~50% chance of a fight (tier-appropriate enemy), else a flavor-text moment; resolved once, then marked cleared |
| Empty | Nothing |

**Dungeon tier -> recommended level**: `min(50, 1 + (tier-1) * 7)` -
tier 1 recommends level 1, tier 8 recommends level 50, spread evenly
across the 8 tiers. It's a guideline shown on the map, not an enforced
gate.

**Scout** (see [Camp & Scout](#12-camp--scout)) reveals a nearby
encounter tile's tier without triggering it.

---

## 9. Dungeons

Each dungeon is a freshly generated 10x10 single-path maze (unlike the
open world map - this is deliberately a maze, since a dungeon is an
enclosed space). Contains:

- Enemies scattered with `ENEMY_SPAWN_CHANCE` (40%) per room, tier-weighted
  by `spawn_chance` in `data/enemies.json`
- 1 to `tier` treasure rooms
- Exactly one merchant room
- One locked vault (the room farthest from the entrance), holding that
  tier's boss - locked until you spend a Thieves' Tools to pick it
  (`try_unlock_vault`), then the boss spawns on your next Interact

**Leaving**: walk back to the entrance room (always at `(0,0)`, marked
"EXIT" on the dungeon canvas, and guaranteed never to contain
treasure/merchant/vault by construction) and press **E** - confirms before
sending you back to the world map. Dying also returns you to the world map
automatically (healed to full), with no permadeath.

---

## 10. The Economy

All figures below are averages; see
[items_reference.md](items_reference.md) for exact per-item prices.

| Source | Formula | Tier 1 avg | Tier 8 avg |
|---|---|---|---|
| Enemy kill (trash) | `random(min_copper, max_copper)` per enemy in `data/enemies.json` | ~150 copper | ~1800 copper |
| Enemy kill (boss) | same, boss-specific range | ~675 copper | ~13,500 copper |
| Dungeon treasure room | `800*tier + random(0, 800*tier)` | ~1,200 copper | ~9,600 copper |
| Quest (settlement) | fixed per quest, 160-480 copper | - | - |
| Merchant sell-back | 50% of the item's current `price_copper` (post magic-bonus) | - | - |

A treasure room averages roughly **3-8x** a single kill at its tier - a
real bonus find, not a coin-flip with a kill. Quest rewards sit comfortably
above a tier-1 kill regardless of where you find the settlement, since
quests aren't tier-gated the way dungeons are.

---

## 11. Quests

Every village/town visit draws **3 random quests** from a 48-quest pool
(`data/quests.json`, 8 per ability score) into a **Quests** tab inside the
Merchant window. Each is a single ability check:
`d20 + relevant ability modifier >= quest's DC`. Success pays the quest's
`reward_copper`/`reward_xp` immediately; failure pays nothing. Each quest
can only be attempted once per board (win or lose) - buying/selling at the
same merchant visit doesn't reset the board or regenerate new quests.

---

## 12. Camp & Scout

Both world-map only (not usable in a dungeon or during combat).

- **Camp** (`C`): `Character.camp_rest()` heals `max(1, max_health // 2)`
  HP - about half your missing HP, floor of 1. Does **not** restore spell
  slots or reset skill cooldowns (only a real `long_rest()` at a
  village/town does that). No-ops if already at full HP.
- **Scout** (`R`): `WorldMap.scout_nearby(radius=3)` reveals the tier of
  any unresolved `?` tiles within 3 tiles, marking them `scouted` so the
  map shows "Tier N" instead of a blank `?`. Doesn't trigger the
  encounter, doesn't re-scout an already-scouted or already-resolved tile.

---

## 13. Status Effects

| Effect | Damage/turn | Duration | How it's applied |
|---|---|---|---|
| Bleed | 10% of the triggering hit's damage | 2 turns | Weapon `effect: "bleed"` on hit (100% chance) |
| Burn | 15% of the triggering hit's damage | 2 turns | Weapon `effect: "burn"` on hit (100% chance) |
| Poison | 20% of the triggering hit's damage | 3 turns | 25% chance from the Venomous Strikes skill (no weapon currently carries `effect: "poison"`) |
| Stun | skips your next turn | 1 turn | 50% chance from a weapon with `effect: "stun"` |

All three DOTs scale with the hit that applied them rather than a flat
number, so they keep pace with weapon upgrades instead of going stale the
way a fixed number would once bigger weapons exist (changelog 4.1.13/4.1.14).
Burn's rate is 1.5x bleed's, preserving their original ratio. Poison's 20%
at a 25% proc chance lands at the same expected damage per hit as Vampiric
Strikes' 100%-chance 15% lifesteal, since it's a skill-tree sibling to it
rather than a weapon effect.

A Potion of Healing-adjacent item, the **Antidote**, cures bleed/burn/poison
(not stun) when used. Reapplying any DOT effect refreshes its duration
rather than stacking damage.

---

## 14. Interface

- **File** menu: New Game, Load Game, Save Game (greyed out until a
  character exists), Exit - mirrors `Ctrl+N`/`Ctrl+L`/`Ctrl+S`.
- **View** menu: Zoom In/Out/Reset (`Ctrl +`/`Ctrl -`/`Ctrl 0`) - scales
  all UI text and widgets via Tk's shared named fonts. Deliberately does
  **not** resize the world-map/dungeon canvas tiles - that's a fixed size
  regardless of zoom.
- **Actions** menu: mirrors every sidebar button (Save, Inventory,
  Interact, Skills, Camp, Scout) as menu commands.
- The main window auto-sizes to 90% of your screen on launch and
  auto-scales text up on screens wider than 1920px (never scales text down
  below normal). Every panel - the 3-column sidebar, the combat window -
  can be dragged wider/taller by hand if anything looks cramped.
- The sidebar shows a body-diagram (silhouette with 10 labeled slot boxes,
  gold when filled) above the full equipment text list.

---

## 15. Saving

`Ctrl+S` / File menu / sidebar button to save; `Ctrl+L` to load. Save files
are named `{character_name}_{timestamp}.json` in `game/saves/`; loading
prompts you to type the filename.

**Known limitation:** saves from before the 10-slot equipment system
(pre-4.0.0) will fail to load - `Character.__init__()` no longer accepts
the old `equipped_weapon`/`equipped_armor` field names those saves used.
There's no migration path. Start a new character.

---

## 16. What's Not Implemented

Listed here so this manual never promises something that isn't real:

- **Rogue's Cunning Action and Uncanny Dodge**, and **Fighter's "Second
  Wind" class feature**, are all named in `data/classes.json`'s `features`
  dict but no code reads that dict at all - they do nothing. (The Defense
  skill tree's "Second Wind" is unrelated and fully functional - a skill
  point unlock, not a class feature.)
- **Fighter and Rogue cannot cast spells** at all - only Wizard and Cleric
  have a spell list, by design, not as a gap.
- Combat balance (enemy stats vs. an on-level character) was modeled
  analytically against a "normally-equipped" character, not verified
  against every possible build - see the 4.1.5 changelog entry for the
  exact method and its limits.
