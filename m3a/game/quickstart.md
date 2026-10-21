# Dungeon RPG - Manual & Quick Start Guide

This covers the game as it actually works right now. If something here doesn't
match what you see in-game, the game is right and this doc is stale - say so.

---

## 1. Starting a Character

Launch the game, then **File > New Game** (or `Ctrl+N`). Enter a name and age
(1-100), pick a class, click Create.

### Classes

| Class | Hit Die | Primary Ability | Role |
|---|---|---|---|
| Fighter | d10 | Strength | Melee, best HP, Extra Attack at 5/11/20 (up to 4 attacks/turn) |
| Rogue | d8 | Dexterity | Finesse melee, Sneak Attack damage dice scale with level (up to 10d6 at 20+) |
| Wizard | d6 | Intelligence | Spellcaster, fire/cold/lightning blast spells |
| Cleric | d8 | Wisdom | Spellcaster, healing plus radiant/fire damage spells |

Ability scores are rolled (4d6, drop lowest, six times) and assigned by each
class's priority order - you don't choose where they go.

Starting kit: your class's starting weapon, armor, and shield (if any), 3
Potions of Healing, Thieves' Tools, a Torch, and 1500 copper (15 gold).

---

## 2. Controls

| Key | Action |
|---|---|
| W / A / S / D | Move (north/west/south/east) |
| I | Inventory |
| E | Interact (loot, merchant, vault, leave a dungeon) |
| K | Skills |
| C | Camp (world map only) |
| R | Scout (world map only) |
| Esc | Pause menu |
| Ctrl+N | New Game |
| Ctrl+S | Save |
| Ctrl+L | Load |
| Ctrl + / Ctrl - / Ctrl 0 | Zoom UI in / out / reset |

Every one of these is also in the menu bar (**File**, **View**, **Actions**) or
as a sidebar button, so you don't have to memorize the keys.

The window auto-sizes to your screen on launch, and text auto-scales up on
wide screens. If anything's cramped, every sidebar column and the combat
window can be dragged wider/resized by hand.

---

## 3. The World Map

You start on an open world map (32x32), not a fixed dungeon. Walk onto a tile
to interact with it:

| Tile | What happens |
|---|---|
| **V** / **T** (village/town) | Full heal + spell slot restore, opens the Merchant (with a Quests tab) |
| **D** (dungeon, purple) | Enters that dungeon instance. Shows a recommended level ("Tier 3 (Lv15+)") before you commit |
| **?** (encounter) | Random event - about half the time a fight, otherwise flavor text |
| plain terrain | Nothing - just texture (plains/forest/road; water blocks movement) |

Dungeon tiers run 1-8 and roughly track distance from your starting point.
Recommended level scales with tier (tier 1 -> level 1, tier 8 -> level 50) -
it's a guideline, not a hard gate; nothing stops you from walking in early.

**Camp (C)**: heals ~50% of missing HP on the spot, anywhere on the world
map. Doesn't restore spell slots or skill cooldowns - that needs a real bed
at a village/town.

**Scout (R)**: reveals the tier of any unresolved `?` tiles within 3 tiles of
you, without walking into them - they'll show "Tier N" on the map instead of
a blank `?` once scouted.

---

## 4. Dungeons

Each dungeon is its own maze, generated fresh, with:
- Rooms containing enemies, treasure, or nothing
- One merchant room
- A locked vault at the far end, guarded by that tier's boss - you need
  Thieves' Tools to pick the lock, then fight the boss for a real loot haul

Press **E** in a room to loot treasure, talk to the merchant, pick the vault
lock, or fight the boss, depending on what's there.

**Leaving a dungeon**: walk back to the entrance room (where you started,
marked "EXIT" on the map) and press **E** - it'll ask to confirm before
sending you back to the world map. This is the only way out besides dying.

If you're defeated, you're healed to full and bounced back to the world map
automatically - there's no permadeath or game-over screen.

---

## 5. Combat

Combat is real d20-based: **roll + modifier vs. a target number** (AC to
hit, DC to save), natural 20 always hits and crits, natural 1 always misses.
Nothing in this session's changes touched that core roll - distance, dodge,
lifesteal, and poison are all additional checks layered around it, not
replacements for it.

### Range

Every fight starts at **Far** range and has 3 bands: Melee / Mid / Far.
- Enemies have no ranged attacks at all - every enemy turn spent above Melee
  range is spent closing the distance instead of attacking.
- **Melee weapons only work at Melee range.** **Ranged weapons work at any
  range** (and are used automatically at Melee range too if that's all you
  have equipped).
- You can equip both a melee and a ranged weapon at once - whichever fits
  the current range is used automatically when you hit Attack.
- **Advance** closes the distance by one band; **Retreat** opens it by one -
  both cost your turn, same as attacking. The enemy still closes in on its
  own turn, so Retreat alone doesn't create lasting distance unless you keep
  doing it every round.
- Fleeing is easier the farther away you are.

### Actions
- **Attack** - swings whichever weapon fits the current range
- **Use Item** - potions, etc.
- **Abilities** - your unlocked active skills (see Skills below)
- **Cast Spell** - if your class can cast
- **Flee** - d20 + bonus vs DC 10 (~65% base, better with Swift
  Feet/Pathfinder skills or more distance)
- **Advance / Retreat** - see Range above

### Status effects
Some weapons/skills inflict **bleed** (2 dmg/turn, 2 turns), **burn** (3
dmg/turn, 2 turns), **poison** (2 dmg/turn, 3 turns), or **stun** (skip your
next turn, 50% chance on hit from a stunning weapon). A Potion of Healing
cures bleed/burn/poison (not stun) as a side effect when drunk via the
Antidote item.

---

## 6. Equipment

10 slots: **Melee Weapon**, **Ranged Weapon**, **Head**, **Chest**, **Hands**,
**Legs**, **Shield**, **Ring L**, **Ring R**, **Necklace**. The sidebar shows
a body diagram - boxes light up gold when filled - plus a full text list
below it.

- Armor comes in **light / medium / heavy**. Only the **Chest** slot's
  category affects your DEX bonus to AC (light = full DEX, medium = DEX
  capped at +2, heavy = no DEX) - that's the real SRD rule. Head/Hands/Legs
  are a homebrew extension on top: each just adds its own flat AC bonus,
  regardless of category.
- **Rings and Necklace** grant a flat bonus to one (or two) ability scores,
  which flows into everything that stat touches - attack, AC, spell DC, all
  of it.
- Weapons/armor can roll a magic bonus when found or bought: +0 (70% of the
  time), +1 (20%), +2 (8%), +3 (2%) - a flat bonus to attack/damage or AC.
- Open Inventory (**I**), click **Equip** on anything equippable. The old
  item in that slot goes back to your inventory automatically.

---

## 7. Leveling

The level cap is **50**, not the SRD's usual 20. XP required curves smoothly
(roughly quadratic) - level 2 takes about 8 kills, level 3 about 30 total;
it gets meaningfully longer at each step after that, the way a real
long-term progression should, but never requires the absurd grinding a
flat SRD table would at this low an XP-per-kill rate.

Each level: HP goes up (your class's hit die + CON modifier), and
proficiency bonus increases every 4 levels (+2 at level 1, up to +14 at
level 49-50, continuing the SRD's own pattern past its normal level-20 stop).

**Spellcasters** (Wizard/Cleric) learn a new spell automatically the moment
they get a slot of that level - nothing to pick or manage, it just appears
in your known spells.

---

## 8. Skills (homebrew bonus tree)

Skill points come at levels 4, 8, 12, ... up to 48 (12 points total,
explicitly **not** official D&D - this is extra player choice layered on
top). Open with **K**. Three branches, 5 tiers deep each, one path per
branch (each node requires the one before it):

- **Offense**: Power Strike (active, guaranteed hit + bonus dmg) -> Weapon
  Mastery (+2 attack) -> Executioner (bigger crits) -> Vampiric Strikes
  (lifesteal) -> Death's Precision (even bigger crits)
- **Defense**: Second Wind (active heal) -> Iron Skin (+2 AC) -> Last Stand
  (survive a lethal hit at 1 HP, once/combat) -> Evasion (10% dodge chance)
  -> Phoenix Heart (second active heal)
- **Utility**: Swift Feet (+flee chance) -> Treasure Hunter (+loot chance)
  -> Battle Focus (+10% XP) -> Venomous Strikes (poison on hit) -> Fortune's
  Favor (+15% more XP)

---

## 9. Quests

Every village/town visit draws 3 random quests, shown in a **Quests** tab
inside the Merchant window. Each is a short errand resolved immediately as
one ability check (d20 + the relevant ability modifier vs. a DC) - no
tracking, no travel, just click Attempt and see what happens. Success pays
copper and XP; each quest can only be attempted once per visit.

---

## 10. Saving

**Ctrl+S** / File menu / sidebar button to save, **Ctrl+L** to load. Saves
are per-character-name, timestamped files - loading asks you to pick one by
filename.

**Known issue:** very old saves (before equipment slots were added) will
fail to load. There's no migration for that - just start a new character.

---

## 11. A note on what's *not* implemented

A couple of things are listed in the game's own data files but don't
actually do anything yet - flagging this so the manual doesn't promise
something that isn't real:
- Rogue's "Cunning Action" and "Uncanny Dodge" and Fighter's "Second Wind"
  *class feature* are named in `classes.json` but no code reads them. (The
  Defense skill tree's "Second Wind" is a different, working thing - a
  skill point unlock, not a class feature.)
- Only Wizard and Cleric can cast spells; Fighter and Rogue have no spell
  list at all, by design.

Good luck out there.
