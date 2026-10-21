# Changelog

All notable changes to Dungeon RPG will be documented in this file.

---

## Original project history (preserved from `csc-121/game-beta/changelog.md`)

## [1.0.0] - 2024-12-08

### Added
- Initial release of the game
- Character creation and progression system with 6 tiers
- D20-based combat system
- Procedurally generated dungeons
- Equipment and inventory system
- Merchant trading system
- Save/load functionality
- Complete dungeon completion system with rewards
- GUI interface with game view and stats display

### Features
- Character progression from Farmer to King
- Dynamic combat with critical hits
- Procedural dungeon generation
- Equipment system with weapons, armor, and shields
- Merchant system with dynamic pricing
- Treasure rooms and loot system
- Enemy encounters with varied difficulty
- Dungeon completion rewards based on tier

### Technical
- Implemented logging system
- Added error handling throughout the application
- Created save/load system using JSON
- Implemented database system for game data
- Added configuration system

## [0.9.0] - 2024-12-07

### Added
- Combat system implementation
- Enemy AI and behavior
- Basic item system
- Initial GUI framework

### Changed
- Improved dungeon generation algorithm
- Enhanced character stats calculation
- Updated room visibility system

### Fixed
- Room connection issues in dungeon generation
- Character stat calculation bugs
- Item equipping inconsistencies

## [0.8.0] - 2024-12-06

### Added
- Basic game structure
- Character class implementation
- Initial dungeon generation
- Simple inventory system

### Changed
- Updated project structure
- Improved data management
- Enhanced error handling

### Originally planned, never built under the old system
- Multiple character classes (listed as planned v1.2.0) - delivered in 3.0.0 below, via real D&D classes instead of the originally-imagined system
- Quest system, achievement system - not yet built
- Additional enemy types, new item effects - delivered in 2.0.0/3.0.0 below

---

## [2.0.0] - 2026-10-12 - World map, skill tree, and real itemization

Built as the engine underneath an M3A (CTS-285) story assignment, then kept expanding on request. This pass moved the game off the original's flat 6-tier stat-block system onto a homebrew skill tree, while fixing a number of features that existed in code but were never actually reachable from gameplay.

### Added
- World map (`models/world_map.py`, new file): overworld with village/dungeon/encounter nodes, separate from the dungeon instances
- Locked vault + boss fight at the end of every dungeon (Lockpick-gated, one boss per tier)
- Homebrew skill tree (`data/skills.json`): 3 branches (Offense/Defense/Utility), 9 nodes, skill points earned on level-up
- Status effects actually applied: weapon effects (stun/bleed/burn/drain) now tick and matter, instead of being unused flavor strings
- Item rarity system (Common -> Legendary, stat multipliers) - later replaced in 3.0.0 by real D&D magic bonuses
- Expanded roster to 8 tiers (was 6), ~30 items, ~30 enemies including 8 bosses
- `requirements.txt`, `.gitignore`

### Changed
- Migrated all data from CSV/pandas to JSON (items, enemies, player tiers); dropped the `pandas` dependency entirely
- `database.py` rewritten around plain JSON reads instead of DataFrame queries

### Fixed (real bugs found while wiring up previously-dead features)
- `Dungeon` only exposed private `_player_pos`/`_size`/`_rooms`; the GUI read `dungeon.player_pos`/`.size`/`.rooms` - would have crashed the first time a dungeon view rendered. Added the missing public properties.
- Ranged weapons (bow/crossbow/throwing knives) could not be equipped at all - fixed in `Character.equip_item`.
- Merchant-window close handler referenced a nonexistent `self.master.current_frame.master.current_dungeon` path - would crash on closing any shop. Replaced with an explicit callback.
- Save/Quit/Inventory sidebar buttons and the Game menu fired virtual events (`<<SaveGame>>` etc.) that nothing listened for - wired them up.
- `Dungeon.get_treasure_loot()` returned bare item-name strings mixed with `('copper', amount)` tuples; every caller unpacked entries as `(drop_type, value)` - crashed the instant a treasure room was actually looted (this method was never called anywhere in the original code, so the bug was latent until this session wired up the Interact action).
- Removed dead code: an unreachable combat item-use path, an unused duplicate key-binding method, and the inert `special_ability` tier field (now real flavor text, not dead-looking "mechanics").
- Deleted `game.py` - an orphaned, syntactically-broken, never-imported duplicate of the Game controller left over from the original project.

---

## [3.0.0] - 2026-10-13 - Real D&D 5e SRD rules and an actual open world

Full replacement of the homebrew tier/rarity system with the real D&D 5e SRD (System Reference Document 5.1, OGL/CC - open for derivative use): six ability scores, proficiency bonus, hit-die HP, real AC, and four real classes with spellcasting. Also fixed the world map, which turned out to be structurally a maze (single path, no loops) instead of an open world.

### Added
- Real ability scores (STR/DEX/CON/INT/WIS/CHA, rolled 4d6-drop-lowest) with SRD modifiers
- Real classes (`data/classes.json`): Fighter (d10, Extra Attack at 5/11/20), Rogue (d8, Sneak Attack scaling by level), Wizard (d6, INT caster), Cleric (d8, WIS caster)
- Real spellcasting: spell slots by level (full 1-20 SRD table), 4 real spells (Fire Bolt, Sacred Flame, Magic Missile, Cure Wounds) with correct SRD mechanics (attack roll / saving throw / auto-hit / heal)
- Real XP table and proficiency bonus table, levels 1-20 (`config.py`)
- Real AC formula (10 + DEX, armor base + capped DEX for medium, no DEX for heavy, +2 shields)
- Magic weapon bonus system (+0/+1/+2/+3, flat bonus to hit/damage) replacing the old stat-multiplier rarity system
- `dice.py` (new file): shared dice-notation parser/roller used throughout combat and HP calculation
- Class selection at character creation (`story.py` and `main.py`'s New Game dialog)
- Real SRD equipment roster replacing invented fantasy items: Longsword, Rapier, Dagger, real armor categories (light/medium/heavy) with real AC values, real Potion of Healing variants (2d4+2, 4d4+4, etc.)
- `town` as a second settlement type alongside `village` (distinct flavor/marker)
- Terrain on the world map: `plains`/`forest`/`water`/`road`, grown as organic blobs, not scattered single tiles
- Roads connecting every settlement to its nearest neighbor via a water-avoiding pathfind

### Changed
- World map default size 7x7 (49 tiles) -> 32x32 (1,024 tiles)
- World map topology: was a single-path maze (same algorithm as the dungeon's corridors) with exactly one route between any two points - rebuilt as a fully open grid so the player can walk any direction, backtrack, and approach anything from any side
- World-view rendering: no longer draws dungeon-style walls/doors; tiles are colored by actual terrain, with a POI marker drawn on top only where something exists
- `story.py` restructured so the player starts outside in the wild on the world map and discovers villages/dungeons by walking, instead of a hardcoded single dungeon behind a text menu
- Village/town visits now call `long_rest()` (restores HP *and* spell slots) instead of only healing HP - casters were never getting spell slots back on rest before this fix
- `player_tiers.json` deleted outright - superseded by `classes.json` + the SRD tables in `config.py`
- `Character.tier` renamed to `Character.level` throughout (dungeon/enemy/item "tier" is a separate, unrelated concept and was left alone)

### Fixed
- `story.py` never bound K (skills) or I (inventory) during the dungeon crawl, so skill points earned mid-run had nowhere to go - added
- `Dungeon.try_unlock_vault` / inventory checks still referenced the old item name `Lockpick` after it was renamed to `Thieves' Tools` during the SRD item-roster rewrite - vault could never be unlocked until this was caught and fixed
- `Character.spell_slots` dict keys silently became strings after a JSON save/load round-trip (JSON has no int keys), breaking spell casting after a reload - normalized back to int on load

### Testing
- 62-check headless smoke test covering ability scores, HP/AC/proficiency math, class features (Extra Attack, Sneak Attack), real spellcasting, magic bonuses, status effects, vault/boss, world map topology and terrain, water blocking, and save/load round-trips - all passing
- Automated GUI playthrough driver (scripted player driving real Tkinter widgets, not a mock) used to catch integration bugs the unit-level smoke test couldn't reach

---

## [3.0.1] - 2026-10-13 - Playtesting pass: bug found via automated exploration

Found while running an automated playthrough driver that actually walks the real world map, not just the model layer.

### Fixed
- `WorldMap` generation had no guarantee that the start tile could reach anything: `_connect_open_grid()` makes every tile topologically adjacent, but water is a *separate* movement-time obstacle checked only in `move_player`. A large enough lake (or several) could fully enclose the spawn point, leaving the player stuck at (0, 0) with nowhere walkable to go - reproduced directly via an automated playthrough that got stuck at the start tile for the entire run. Fixed by flood-filling from the start tile after terrain generation and draining any water outside the reachable region back to plains. Stress-tested across 200 random map generations with zero trapped starts after the fix (previously reproducible).

---

## [3.1.0] - 2026-10-13 - File menu, UI scale, and two more playtesting bugs

### Added
- Persistent `File` menu (`gui/main_window.py`), present from the start screen onward: New Game, Load Game, Save Game (greyed out until a character exists), Exit - replaces the always-on-screen New Game/Load Game/Quit buttons that used to sit in the middle of the start screen permanently
- `View` menu with Zoom In / Zoom Out / Reset Zoom (`Ctrl +`/`Ctrl -`/`Ctrl 0`), scaling all ttk/tk text and widget sizes (sidebar, menus, dialogs) via Tk's shared named fonts - deliberately does *not* resize the world-map/dungeon canvas tiles, which stay a fixed size regardless of UI scale (a separate map-zoom feature, if wanted later, is a different concern)
- `Ctrl+N` accelerator for New Game, matching the existing `Ctrl+S`/`Ctrl+L`

### Changed
- `GameWindow.setup_start_screen()` (new) replaces the old `Game.setup_menu()` button frame; the returned frame is now tracked as `_current_frame` like the in-game view is, so `clear_menu()` actually cleans it up on transition (previously the start-screen frame was never tracked and was left to sit, unpacked-but-undestroyed, behind the game UI once a game started)

### Fixed (found via test playthrough)
- Treasure rooms and the vault-boss kill showed a flat "You found treasure!" with no indication of what was actually looted - `_apply_loot` now returns a description of every copper/item drop and both messageboxes list it
- World-map encounter (`?`) tiles could never trigger: `WorldMap.move_player` marks the destination tile `visited = True` the instant you step onto it, but `_on_world_node_entered` was gating the encounter roll on `not node.visited` - already `False` by the time it checked, so the branch was dead code and `?` tiles did nothing, forever, including on first entry. Regated on a `cleared` flag instead (set only once the encounter actually resolves), matching how dungeon/vault completion is tracked elsewhere.

### Testing
- Headless smoke tests: File-menu Save-Game enable/disable across the menu-screen -> start_game() transition, zoom in/out/reset changing shared Tk font sizes without touching canvas draw sizes, encounter tile now flips `cleared` after being walked onto, treasure-loot messagebox text contains the actual drops

---

## [3.2.0] - 2026-10-13 - Combat window layout, scalable popups, screen-aware sizing

### Added
- `gui/dialogs.py` (new): drop-in replacement for `tkinter.messagebox` (`showinfo`/`showwarning`/`showerror`/`askyesno`, same `(title, message)` call signature - every call site just swapped its import). On Windows, `messagebox.*` shells out to the native OS dialog, which Tk cannot theme, font-scale, or resize; these are plain ttk Toplevels instead, so they finally respond to the View > Zoom setting and auto-size to their actual message text
- `gui/layout.py` (new): `fit_window()` sizes a Toplevel from a base design size, the current zoom level, and the real screen resolution (`winfo_screenwidth/height`), clamped to 90% of the screen and centered over its parent - applied to every window in the app (main window, combat, inventory, merchant, skills, pause menu, character creation, and the three in-combat sub-dialogs), replacing fixed `.geometry("WxH")` calls that didn't adapt to the machine actually running the game. Also `scaled_font()` for the handful of widgets using an explicit font tuple instead of the shared named fonts (skill tree labels, merchant money label, combat log, start-screen title) - those were invisible to the zoom feature in 3.1.0 since explicit font tuples don't follow `TkDefaultFont`
- Sidebar (`gui/main_window.py`) split into two side-by-side columns (Equipment/Stats/Abilities on the left, Inventory/Actions on the right) instead of one long vertical stack - at higher zoom levels the single column could grow taller than the window with no scrollbar, pushing the action buttons below the visible area

### Fixed
- Combat window packed 5 action buttons in a single row inside a fixed 500px-wide, non-resizable window; `Attack`/`Use Item`/`Abilities` fit, but `Cast Spell` and `Flee` got squeezed down to 46px and 1px respectively by the packer - effectively invisible and unclickable. This is why there was "no way to flee a fight": the button existed and worked, it just had no clickable area. Split into two rows of buttons instead.
- Combat window's native close button (`WM_DELETE_WINDOW`) was unconditionally a no-op, by design, to stop the player dodging a loss mid-fight - but that remained true even after the fight ended, so if a player didn't notice the small in-log "Close" button after a defeat, there was no way to close the window at all. Now defers to the same close path once the fight is actually over.
- `WINDOW_WIDTH` (1000) was already tighter than the dungeon/world canvas (a fixed 800px-wide widget) plus a sidebar; the new two-column sidebar (440px) made this concrete - the packer was starving the sidebar down to ~196px regardless of its configured width, because the canvas, packed first, claimed its full 800px before the sidebar got a share of what was left. Widened to 1300.

### Testing
- Headless Tk smoke tests: combat button widths after the row split (all 130px, none squeezed), a simulated defeat closed via the native X button path (not just the in-log Close button) correctly returns to world_map, dialog reqwidth/reqheight grow with zoom (423x99 -> 542x138 at 1.3x), sidebar column widths confirmed correct with real dungeon/world canvas content drawn (not just the empty frame)

---

## [3.3.0] - 2026-10-13 - Camp and Scout

### Added
- `Camp` action (`C` / sidebar button, world map only): `Character.camp_rest()` recovers about half of missing HP, but - unlike a village/town's `long_rest()` - doesn't restore spell slots or reset skill cooldowns, so it's a real but lesser alternative to traveling to a settlement. `config.CAMP_HEAL_RATE` had existed, unused, since the original project; this replaces it with a percentage-of-missing-HP heal rather than wiring up the old flat constant, which would have been a trivial 5 HP against a modern SRD character's HP pool
- `Scout` action (`R` / sidebar button, world map only): `WorldMap.scout_nearby(radius=3)` reveals the tier of any unresolved encounter (`?`) tiles near the player without having to walk onto them - the world-map view already drew every nearby tile's kind regardless of a fog mechanic, but encounter tiles gave no hint of their tier (unlike dungeon tiles, which always show theirs) until you committed to triggering them blind. A new `WorldNode.scouted` flag (persisted in save/load) gates a `Tier N` label on scouted-but-unresolved encounter tiles, replaced by `Explored` once actually resolved

### Changed
- The world-map `Explored` label on encounter tiles now keys off `node.cleared` (encounter actually resolved) instead of `node.visited` (merely stepped on once, which - since `move_player` sets it immediately on arrival - could be true before the encounter had even triggered)

### Testing
- Headless smoke tests: camp heals when hurt and no-ops at full HP, refused outside the world map (e.g. mid-dungeon), scout reveals nearby unresolved encounter tiers and doesn't re-scout the same tile twice, `scouted` survives a `to_dict()`/reload round-trip, world-map canvas renders both a scouted (`Tier N`) and a resolved (`Explored`) encounter tile without error

---

## [3.3.1] - 2026-10-13 - Auto-scale text to the screen on launch

### Changed
- `GameWindow` now picks its starting zoom level from the actual screen resolution (`winfo_screenwidth()`) instead of always launching at 1.0 and leaving high-resolution displays with small text until the player manually zoomed in. Baseline is a 1920px-wide screen; anything wider scales text up proportionally (capped at the existing `MAX_UI_SCALE`), and anything at or under 1920px still gets the normal 1.0 size - this never makes text *smaller* than before, only bigger where the screen has the room for it. `_set_ui_scale`'s font-resizing logic was pulled out into `_apply_font_scale()` so both the manual zoom controls and this startup auto-scale share the same code path.

---

## [3.4.0] - 2026-10-13 - Town side quests

### Added
- `data/quests.json` (new): 12 short, D&D-flavored side quests (one or two per ability score - hauling barrels, chasing a pickpocket, untangling a merchant's ledger, mediating a land dispute, etc.), each resolved as a single real SRD ability check (d20 + ability modifier vs. a DC) rather than a tracked multi-step objective
- `models/quests.py` (new): `QuestBoard` draws 3 random quests on settlement entry and resolves an attempt in one call - rolls the check, pays out copper/XP through the player's existing `add_xp`/`money` on success, and marks the quest used either way so it can't be retried on the same board
- `database.get_all_quests()` - same load/cache pattern as items/enemies/skills
- A `Quests` tab in the merchant window (only shown when a settlement's QuestBoard is passed in - the in-dungeon merchant has none), listing each quest's flavor text, ability/DC, and reward, with an `Attempt` button that rolls immediately and reports the roll breakdown and outcome

### Changed
- `enter_settlement()` now generates a `QuestBoard` alongside the `Merchant` each time a village/town is entered; `show_merchant_ui`/`_handle_buy`/`_handle_sell` thread the same `quest_board` instance through every window refresh (buying or selling an item no longer drops the Quests tab or resets which quests were already attempted this visit)

---

## [3.5.0] - 2026-10-16 - Actions menu, resizable sidebar

### Added
- `Actions` menu on the main menu bar, mirroring every sidebar action button (Save, Inventory, Interact, Skills, Camp, Scout) as menu commands firing the same virtual events - greyed out alongside Save Game in the `File` menu until a character exists (`set_game_active` now toggles both)

### Changed
- The game-view/sidebar split, and the sidebar's own Equipment+Stats / Inventory+Actions split, are now `tk.PanedWindow` sashes instead of fixed-width frames - the player can drag either boundary to resize, e.g. widening the Inventory list (it was getting truncated - "Potion of Healing" clipping off-screen - at the old fixed ~200px column width). Each pane has a `minsize` so dragging can't collapse one to nothing; `stretch` is set so the canvas side holds its size and the inventory column is the one that grows when the window itself is resized.

---

## [3.6.0] - 2026-10-16 - 50-level progression, dungeon entry/exit

Root cause of "leveling feels slow": `XP_BY_LEVEL` was the unmodified real SRD table (300 XP for level 2, designed around a 4-person party splitting real SRD monster XP in the tens-to-hundreds), while `data/enemies.json`'s `xp_value` was a leftover 1-8 homebrew scale from before the SRD rewrite. At 1 XP/kill, level 2 needed 300 kills.

### Changed
- Extended the character arc from 20 to 50 levels. `XP_BY_LEVEL` (`config.py`) is a new quadratic curve (`150 * (level-1)^2`) instead of the raw SRD thresholds - reaches level 2 in ~8 kills and level 3 in ~30 total, instead of hundreds, while still stretching to a genuine long-term 50-level arc (360,150 cumulative XP at level 50, in the same ballpark as the original SRD's level-20 max, just spread much further and reachable at a sane pace throughout)
- Rescaled every `xp_value` in `data/enemies.json` from the old 1-8/10-300 homebrew scale to 20-230 (trash) / 100-1150 (boss), tiered to match the new curve
- `PROFICIENCY_BONUS_BY_LEVEL` extended to 50 levels, continuing the SRD's own "+1 every 4 levels" pattern past the point the SRD stops (level 20 was +6, level 50 is now +14)
- `Character._refresh_spell_slots` and `.sneak_attack_dice()` now clamp to the SRD's level-20 values for any higher level, instead of indexing past the end of `SPELL_SLOTS_BY_LEVEL` (would have crashed at level 21) or letting Sneak Attack scale unbounded past the real 10d6 cap (would have hit 25d6 at level 50)
- World-map dungeon tiles now show a recommended level alongside their tier (`config.dungeon_recommended_level()`, spread evenly 1->50 across the 8 enemy tiers) instead of just "Tier N", so you can tell before walking in whether a dungeon is over your head
- Dungeons can now be left from the entrance room (always (0,0), never a treasure/merchant/vault room by construction): standing there and pressing Interact asks to leave back to the world map. Previously the only way out was dying. The entrance room is now also marked "EXIT" on the dungeon canvas so it's discoverable without reading this changelog.

## [3.7.0] - 2026-10-16 - Item roster and loot tables were mostly broken

Found while investigating a complaint that the item list felt thin. It was worse than thin: cross-checking `data/enemies.json`'s drop tables against `data/items.json` showed **24 of 27** referenced item names didn't exist (e.g. "Flame Blade", "Short Sword" vs. the real "Shortsword", "Health Potion" vs. the real "Potion of Healing") - `_apply_loot` silently no-ops on an unknown name, so these drops had been invisibly failing. Separately, `Enemy.rare_drops` turned out to be dead data entirely: loaded, saved, and never once read by `get_drops()`, which rolled its "rare item" chance from a generic tier-based pool instead - no boss's named signature item was ever actually obtainable.

### Added
- `data/items.json` expanded from 27 to 65 items: the real SRD simple+martial weapon and ranged weapon tables (Club, Handaxe, Javelin, Scimitar, Flail, Glaive, Maul, Sling, Hand Crossbow, etc. - previously only ~14 weapons existed total), a fuller armor spread (Hide, Scale Mail, Ring Mail added), a second shield (Tower Shield), and 10 new named tier 5-8 "legendary" items (Flame Blade, Soul Reaper, Runed Greatsword, Hunter's Longbow, Dragonfang Blade, Stormcaller Bow, Titan's Maul, Dragonscale Armour, Worldbreaker, Legendary Blade) - these are the first items in the game to actually carry the `bleed`/`burn`/`stun`/`drain` weapon effects combat.py has supported since 3.0.0 but nothing ever used

### Fixed
- Every `common_drops`/`rare_drops` name in `data/enemies.json` rewritten to reference a real item (typo fixes like "Short Sword"->"Shortsword" and "War Hammer"->"Warhammer", renames like the four fictional "X Health Potion" tiers -> the real `Potion of Healing`/`Greater`/`Superior` names, and real substitutes for placeholder armor names like "Med Plate Armour"->"Half Plate")
- `Enemy.get_drops()`'s rare-item roll now picks from the enemy's own `rare_drops` when it has any (falling back to the old generic tier-pool roll only if empty), so a Lich can now actually drop its Flame Blade instead of a random unrelated item

---

## [3.8.0] - 2026-10-16 - Full spell list and a real skill tree

Asked to assess the data files for content depth after the items/enemies pass. Two were genuinely thin: `spells.json` had 4 spells total (1 cantrip + 1 first-level spell per caster class) against a slot table that goes up to 9th level - a caster would accumulate 2nd-9th level slots with nothing to ever cast in them. `skills.json` had 9 nodes in 3 straight 3-deep lines, capped at level 20 skill points even after the level cap moved to 50.

### Added
- `data/spells.json`: 4 -> 22 spells. Wizard and Cleric each get a second cantrip plus one spell at every level 1-9 (Wizard: Scorching Ray, Fireball, Ice Storm, Cone of Cold, Chain Lightning, Prismatic Spray, Sunburst, Meteor Swarm; Cleric: Prayer of Healing, Spirit Guardians, Guardian of Faith, Flame Strike, Heal, Fire Storm, Divine Wrath, Mass Heal), all built from the engine's existing 4 cast types (attack/save/auto_hit_multi/heal) rather than inventing new spell mechanics
- `Character._learn_available_spells()` (new): grants a class's designated spell(s) for a spell level the moment the character has a slot of that level, called on creation and every level-up. Without this, adding spells to the data file alone would have done nothing - nothing previously added anything past the starting 1st-level spell to `known_spells` as a character leveled
- `data/skills.json`: 9 -> 15 nodes - each of the 3 branches (Offense/Defense/Utility) extended from a 3-deep chain to 5-deep, all new nodes reusing effect types the engine already consumes (`passive_attack`/`passive_defense`/`crit_multiplier`/`flee_bonus`/`xp_bonus`/a second `active_heal_percent` skill) rather than adding effect types nothing would read
- `SKILL_POINT_LEVELS` extended from `(4, 8, 12, 16, 20)` to continue every 4 levels through 48 (12 points total), matching both the new 5-deep branches and the 50-level arc - it previously stopped granting points at level 20 entirely

### Fixed
- `Character.take_damage()`'s Last Stand check was hardcoded to the specific skill id `'last_stand'` instead of checking generically for the `survive_lethal` effect type the way every other skill effect is checked (`_skill_effect_total`, `crit_multiplier`) - harmless with only one such node, but would have silently ignored a second one. Generalized before adding content that could have hit exactly that trap.

### Testing
- Verified every spell name in `classes.json`'s `cantrips_known_at_1`/`spells_by_level` resolves to a real `spells.json` entry, and every skill's `requires` resolves to a real node id in the same file - both checked programmatically, not by inspection

---

## [3.9.0] - 2026-10-16 - Three new skill mechanics: lifesteal, poison, dodge

Asked what's actually stopping a "proper" skill tree. Answer: the tier-4 nodes added in 3.8.0 (Relentless Assault, Fortified Resolve, Pathfinder) were just the tier-2 node's number again - same lever, not a new ability. A node with a genuinely new effect type does nothing unless combat.py is taught to read it, same trap as the dead `rare_drops` field from 3.7.0. So this is a code change, not a data-only one.

### Added
- `CombatSystem._apply_lifesteal()`: heals the attacker for a fraction of damage dealt on a successful hit
- `CombatSystem._apply_poison_chance()` + `poison` added to `DOT_STATUSES`: a flat chance on hit to poison the target (2 damage/turn for 3 turns, same shape as the existing bleed/burn)
- `CombatSystem._defender_dodges()`, called from `calculate_hit()`: a flat chance for the defender to avoid an attack entirely after the normal roll would have hit - skipped by a primed Power Strike, which is meant to be unavoidable
- `Character.lifesteal_fraction` / `.poison_chance` / `.dodge_chance` properties, same `_skill_effect_total()` pattern as the existing skill-driven stats

### Changed
- `data/skills.json`: replaced the three weakest "bigger number of a stat you already have" tier-4 nodes with the three new mechanics - Vampiric Strikes (lifesteal, Offense), Evasion (dodge, Defense), Venomous Strikes (poison, Utility) - node count stays at 15, it's a quality swap, not padding

---

## [4.0.0] - 2026-10-18 - Multi-slot equipment and per-turn combat positioning

Requested: head/chest/hands/legs/ring/necklace equipment slots, dual-wielding a melee and ranged weapon at once with the character using whichever fits the fight, and asked for the harder of two options on how deep to take it - full per-turn positioning rather than a simple per-encounter range roll. This touches the equipment model, the attack-resolution math, and the combat UI; it's the largest single change this project has had.

### Added
- **Equipment**: `Character` now has 10 equip slots instead of 3 - `equipped_melee_weapon`, `equipped_ranged_weapon` (both can be equipped at once), `equipped_head`/`chest`/`hands`/`legs` (armor now carries a `slot` field; `chest` keeps the real SRD light/medium/heavy DEX-cap rule, the other three are flat AC bonuses since the SRD has no rule for them at all), `equipped_shield`, and `equipped_ring_left`/`ring_right`/`necklace`. Rings/necklaces grant a flat ability-score bonus (`item['ability_bonus']`) that now flows through `ability_modifier()` into every stat that reads it - attack, AC, saves, spell DC
- `data/items.json`: +19 items for the new slots - 9 head/hands/legs armor pieces and 10 rings/necklaces (one per ability score, plus a tier-6 Ring of Power and three necklaces)
- **Combat positioning**: a homebrew 3-band distance system (`Melee`/`Mid`/`Far`, `config.COMBAT_DISTANCE_BANDS`). Every fight starts at Far. Enemies have no ranged capability, so an enemy turn spent at distance > 0 is spent closing in instead of attacking - matching `process_turn(type='move')` so it still respects stun and still ticks poison/bleed/burn, the same as any other turn. The player gets `Advance`/`Retreat` buttons (also routed through `process_turn`) alongside Attack; melee weapons only work at Melee range, ranged weapons work at any range (falling back to ranged automatically if no melee weapon is equipped at Melee range too) - `Character.weapon_for_range(in_melee)` picks which equipped weapon an attack actually uses
- Fleeing is now easier the farther away you are (`+distance` on the flee roll) - the one place "being far away" was already meaningful before this change, now reinforced by it

### Changed
- `CombatSystem.calculate_hit()`/`_resolve_attacks()`/`_calculate_melee_damage()` all take an explicit `weapon`/`attack_bonus` now instead of reading a single `attacker.equipped_weapon` - needed so the same attack-resolution code works whether the attacker just has one weapon (Enemy, unaffected) or is choosing between two based on distance (Character)
- Merchant inventory generation, the sidebar equipment display, the inventory window, and `_describe_item()` all extended to the new slots/types

### Fixed (caught during my own review, before you'd have hit them)
- `weapon_for_range()`'s first draft only checked the ranged slot at non-melee distance and the melee slot at melee distance, which meant a character carrying *only* a ranged weapon could never attack once an enemy closed to melee range - contradicted my own stated design (ranged works at any range). Fixed to fall back to the ranged weapon at melee range when no melee weapon is equipped.
- Advance/Retreat originally mutated `self.distance` directly in the UI layer, bypassing `process_turn()` entirely - meaning a stunned character could still freely reposition, and poison/bleed/burn wouldn't tick on a movement turn. Routed through `process_turn(type='move')` instead, so movement gets the same stun-check and DOT-tick every other action gets.
- A leftover dead branch in `_resolve_attacks` ("no melee weapon equipped" at distance 0) became literally unreachable after the `weapon_for_range()` fix above - removed rather than left as confusing dead code.

### Known limitation
- Old save files (pre-4.0.0) will fail to load - `Character.__init__()` no longer accepts the old `equipped_weapon`/`equipped_armor` keys those saves were written with. No migration path was written; this is a dev-build breaking change, not a bug. Start a new character.

---

## [4.0.1] - 2026-10-18 - Head/hands/legs armor were a token gesture, not an expansion

The 4.0.0 pass gave `chest` a real progression (13 items across light/medium/heavy, tiers 1-7) but gave `head`/`hands`/`legs` exactly one item per category (3 each) - a placeholder, not content, and inconsistent with the slot it was supposed to match.

### Changed
- `data/items.json`: head/hands/legs expanded from 3 items each to 9 each (84 -> 102 total), mirroring chest's actual structure - 3 light + 3 medium + 3 heavy per slot, spanning tiers 1-5 the same way chest does, plus a tier-7 legendary piece in each (Dragonskull Helm, Dragonclaw Gauntlets, Dragonscale Greaves) matching Dragonscale Armour's role on chest

---

## [4.0.2] - 2026-10-18 - Armor slots pushed to 18 each

Benchmarked against Diablo 2 (~56 unique helms, ~24 unique gloves, ~23 unique boots) and Baldur's Gate 3 (~50+ gloves) before deciding scope - neither game gets there by hand-authoring that many templates per slot; the bulk of their apparent variety is procedural (affix/rarity systems) on top of a much smaller base-type count, which this project already has via the +0/+1/+2/+3 magic bonus roll. Agreed target: push base templates to 15-20 per slot, not chase the full procedural-scale number.

### Changed
- `data/items.json`: all four armor slots (chest/head/hands/legs) now have exactly 18 items each (6 light + 6 medium + 6 heavy, 102 -> 134 total) - chest went from an uneven 13 to match the other three exactly, instead of being the one slot left ahead
- Matching "armor set" naming across slots at the same tier (Iron/Warhost/Titan-prefixed heavy pieces, Duelist's/Shadowweave-prefixed light pieces, Bronze/Knight's/Champion's-prefixed medium pieces) so a themed set reads as a set across head/hands/legs/chest, the way named armor sets work in the games above
- Fixed a duplicate `Dragonscale Armour` entry introduced while merging the legendary-items tail section into the main chest list

---

## [4.0.3] - 2026-10-18 - Paper-doll equipment diagram; combat window too short on some screens

### Added
- A body-diagram canvas above the Equipment text list (`gui/main_window.py`): a humanoid silhouette with 10 labeled slot boxes (Head/Necklace/Shield/Ring L flanking the left, Melee/Ranged/Ring R flanking the right, Chest/Hands/Legs overlaid on the figure) that highlight gold when filled, gray when empty. The existing text list stays underneath for actual item names - the boxes only show slot labels, there wasn't room to fit full item names legibly inside them. Widened the sidebar's left column (200->280px) and the window (1300->1360) to fit it.

### Fixed
- Combat window was locked non-resizable, and on a screen that's wide-but-not-tall the auto-detected UI scale (driven off screen *width*) could make its three action-button rows taller than 90% of screen *height* leaves room for - with no way for the player to recover, since it couldn't be resized. Made it resizable, gave it a `minsize`, and shrank the combat log's default height (20 lines -> 14) so it needs less room by default in the first place.

---

## [4.0.4] - 2026-10-18 - Sidebar split into 3 columns

The body-diagram addition in 4.0.3 made the Equipment section tall enough (diagram + text list) that Character Stats/Ability Scores, stacked below it in the same column, were getting pushed off the bottom of the window - invisible, not just scrolled.

### Changed
- Sidebar is now 3 draggable columns instead of 2: Equipment (diagram + list), Character Stats + Ability Scores, Inventory + Actions - `_sidebar_left` split into `_sidebar_equipment` and `_sidebar_stats`, each sized to fit its own content instead of competing for one column's height
- Window width 1360 -> 1600 to fit the extra column (800 canvas + 740 sidebar + margin)

---

## [4.1.0] - 2026-10-18 - Documentation, and the quest pool quadrupled

### Added
- `quickstart.md` rewritten from scratch - the old version predated the entire SRD rewrite (mentioned "Lesser Health Potions" and a homebrew "+2 to hit" combat system that hasn't existed since 3.0.0). Now covers character creation, the world map, dungeons, the real d20 combat system plus this session's range/positioning mechanic, all 10 equipment slots, the 50-level arc, the skill tree, quests, and saving - as the game actually works today. Explicitly calls out that Rogue's Cunning Action/Uncanny Dodge and Fighter's "Second Wind" *class feature* are named in `classes.json` but never implemented, so the manual doesn't promise something that isn't real.
- `docs/items_reference.md` (new) - every one of the 134 items in a table, generated directly from `data/items.json` rather than hand-transcribed, so it can't drift from the real data by copying mistakes.

### Changed
- `data/quests.json`: 12 -> 48 quests (8 per ability score instead of 1-2), each with its own flavor text and DC - the draw stays at 3 per settlement visit (kept as-is, that part was working as intended), but the pool behind it is 4x deeper so the same handful of errands don't show up every single visit

---

## [4.1.1] - 2026-10-18 - Enemy copper drops were still on the pre-rewrite scale

Same bug shape as the `xp_value` fix in 3.6.0, just on gold instead of XP: `min_copper`/`max_copper` on every enemy was never touched when the leveling rescale happened, while item prices are largely real SRD gold values (Plate Armor really is 1500gp in the SRD). At the old rate, affording a Plate Armor took ~1,300 kills even at the best possible (tier-8) kill rate - the item prices and the earning rate were never checked against each other.

### Changed
- `data/enemies.json`: every enemy's `min_copper`/`max_copper` scaled up 15x (tier 1 trash: ~10 -> ~150 copper/kill average; tier 8: ~120 -> ~1800). Mid-tier gear (e.g. Scale Mail, 50gp) now costs about 14 kills at the appropriate tier instead of ~200; top-tier legendary armor (1500-2200gp) is 50-120 kills at the toughest tier - a real grind for best-in-slot gear, not an unreachable one

---

## [4.1.2] - 2026-10-18 - Magic bonus rolls never changed the price

Asked to also check merchant buy prices. Found a second pricing bug: `Database.instantiate_item()` rolls a +0/+1/+2/+3 magic bonus and renames the item ("+3 Legendary Blade"), but copied `price_copper` straight from the template and never adjusted it - a +3 roll (2% chance, a real combat power jump) cost exactly the same as a +0 of the same base item, buying or selling. The bonus system was invisible to the economy.

### Changed
- `data/magic_bonus.json`: each tier now carries a `price_multiplier` (+0: 1x, +1: 3x, +2: 8x, +3: 20x)
- `Database.instantiate_item()` applies it to `price_copper` when the bonus is rolled - `Legendary Blade` (50000c) becomes 150000c/400000c/1000000c at +1/+2/+3. Applies everywhere an item gets instantiated (merchant stock, loot drops, treasure), since it's all the same code path.

---

## [4.1.3] - 2026-10-18 - Skill point cost wasn't actually read

Asked to check skill point costs too. Every skill node has carried a `cost` field since 3.8.0 (and the UI's "Unlock (cost N)" button label already reads it correctly), but `Character.unlock_skill()` hardcoded `self.skill_points -= 1` regardless of the node's actual cost, and `can_unlock_skill()` only checked `skill_points > 0`, not `>= cost`. Harmless today only because every node's cost happens to be 1 - the moment any node were priced higher (a 2-point capstone, say), it would've silently undercharged.

### Fixed
- `can_unlock_skill()` now checks `skill_points >= node['cost']`; `unlock_skill()` deducts the node's real cost instead of a hardcoded 1
- Verified with a simulated 2-cost node: correctly blocked at 1 point, correctly allowed and deducted 2 at 2 points - current 15-node tree is unaffected since every real cost is still 1

---

## [4.1.4] - 2026-10-18 - Treasure rooms and quests hadn't caught up to the copper rescale

Asked to check other merchant/reward values. Found two more casualties of 4.1.1's enemy-copper rescale, which only touched enemy drops: dungeon treasure rooms and quest rewards were both designed against the old copper scale and never revisited, so fixing kills made them *relatively* worse - a dedicated treasure room now paid as little as 0.35x a single kill (tier 6), and a quest paid less than half of one tier-1 kill (20-60 copper vs ~150).

### Changed
- `Dungeon.get_treasure_loot()`: base money 100/tier -> 800/tier (average payout now 2.8x-8x a single kill at that tier, instead of 0.35x-1x)
- `data/quests.json`: `reward_copper` x8 (now 160-480, comfortably above a tier-1 kill), `reward_xp` x2 (now 15-50 - a smaller bump on purpose, since quest XP needs to stay well under what a real level-up costs rather than match copper's jump)

---

## [4.1.5] - 2026-10-18 - Enemy combat stats were never rescaled for the 50-level arc

Asked to check enemy stats and HP too. This was the biggest one: `attack`/`defense`/`health` on every enemy are untouched since the original pre-SRD project - they were never revisited when the level cap went from 20 to 50, when Fighter's Extra Attack was confirmed to cap at 4 attacks/turn, or when 10 equipment slots replaced 3. Modeled it out against a normal on-level character at each tier's recommended level (`config.dungeon_recommended_level()`): the player's hit chance climbed from a reasonable "needs 10+" at tier 1 to "needs 2+" (95%, functionally guaranteed) by tier 3 and stayed there through tier 8, while enemy HP grew only ~5x (10 -> 50) across a range where player damage output grows far faster, especially once Extra Attack multiplies every hit by up to 4.

### Changed
- `data/enemies.json`: every enemy's `attack`/`defense`/`health` rescaled per-tier so an on-level character needs roughly 10+ to hit (about 55%) at every tier 1-8, not just tier 1 - each enemy's stat was scaled proportionally from its tier's old average to the new target, so individual flavor differences within a tier (Rat weaker than Bandit, etc.) are preserved rather than flattened. Boss stats scaled using the existing boss:trash ratios (~1.8x defense, ~2x attack, ~3x HP) rather than invented from scratch.

### Known limitation
- The player-side half of this model (attack bonus, AC) is an estimate of a "normally-equipped on-level character," not a simulation of every build - a heavily-optimized or heavily-neglected character will see different numbers than modeled. This needed real design judgment, not just a formula, the same way the original XP curve did - it's a strong correction over the old numbers, not a guarantee of perfect tuning. Treat it as the next thing to verify by actually playing a dungeon run at a couple of different tiers.

---

## [4.1.6] - 2026-10-18 - A full game manual, not just a quickstart

Told that `quickstart.md` is a quick-start guide, not a full manual - it doesn't explain all the game mechanics. Added a separate, deeper reference document alongside it rather than rewriting quickstart into something it isn't meant to be.

### Added
- `docs/manual.md`: a comprehensive mechanics reference with real numbers pulled fresh from `config.py` and the data files - ability scores and modifiers, the full attack-resolution sequence (including crit/dodge/vampiric/poison ordering), the range-band system, the exact AC formula per armor slot, the full magic-bonus odds/price-multiplier table, the 50-level XP/proficiency progression, all 15 skill nodes, all 22 spells, world-map and dungeon generation parameters (node counts, treasure/merchant/vault placement, maze generation), the full economy (enemy copper by tier, treasure room formula, quest rewards, merchant sell rate), camp/scout, exact status-effect numbers, and the interface/saving sections. Closes with an explicit "What's Not Implemented" section (classes.json's dead `features` dict - Cunning Action, Uncanny Dodge, Fighter's class-level Second Wind) so the manual never claims something the code doesn't actually do.

---

## [4.1.7] - 2026-10-18 - Levels shown in combat and on the quest board

Asked for the combat window to show what level the enemy and player are, not just HP/ATK/AC - and then to show it on the Quests tab too.

### Added
- `CombatWindow.update_stats()`: the Player and Enemy stat lines now lead with `Lv N`. The player's is just `character.level`; enemies only carry a `tier` in the data, not a level, so the enemy line shows `Lv N (Tier M)` using the same `config.dungeon_recommended_level(tier)` conversion already used to label dungeon tiles on the world map - one consistent tier-to-level number across the game instead of two different scales.
- Merchant window's Quests tab: added a `"{name} - Level {level}"` header above the quest list. Quests have no enemy/tier to pair it against like combat does, so this just surfaces the player's current level next to the quest DCs so the odds are easier to judge at a glance.

---

## [4.1.8] - 2026-10-18 - Tier-1 enemy HP was still 2-6x the player's own HP

Reported: a level-1 character runs into tier-1 enemies with way more HP than they have - as much as ~3x for a Wizard against a Bandit. Right call; this was the one real miss in 4.1.5's rescale.

4.1.5 sized every tier's HP by modeling hit chance only, never by checking it against the player's *own* HP pool. Checking that now (player HP from `Character`'s actual level-up formula: `max_value(1d{hit_die}) + CON mod` at level 1, `+= average(1d{hit_die}) + CON mod` per level after, using a representative +2 CON mod) against each tier's recommended level (`config.dungeon_recommended_level()`) shows tiers 2-8 already land at a smooth, sane ratio - trash at 0.54x-0.68x of player HP, bosses at 1.6x-2.0x. Tier 1 is the one break in that curve: trash averaged **2.0x** player HP and the tier-1 boss averaged **6.0x** - because a level-1 character has only one hit die roll to its name and no accumulated level-ups, so it's the one point on the curve where an eyeballed HP target (instead of a checked one) was actually wrong, not just imprecise. Every other tier's recommended level had leveled up enough times that the same mistake happened to land in a plausible-looking range anyway.

### Changed
- `data/enemies.json`: tier-1 health rescaled to match the ratio tiers 2-8 already hold - Goblin 21->7, Rat 16->6, Bandit 25->9, Wolf 18->6, Goblin Chieftain (boss) 60->21. `attack`/`defense` untouched - the to-hit math for tier 1 was already reasonable, this was specifically an HP-pool problem.

---

## [4.1.9] - 2026-10-18 - Head/hands/legs AC was stacking enemies out of relevance

Asked to check enemy attack/defense scaling too, after the tier-1 HP fix. Modeled both directions (player-hits-enemy and enemy-hits-player) using real gear values from `items.json`, real proficiency growth, and simulated ability-score rolls, for a Fighter (heavy+shield), Cleric (medium+shield), and Rogue (light, no shield).

Player-hits-enemy was fine (40-57%, close to the ~55% 4.1.5 targeted). Enemy-hits-player was broken: by tier 3, a Fighter or Cleric sat at a flat 5% (nat-20-only) for the rest of the game - functionally unhittable by trash. Root cause: 4.0.0 added four separate flat-AC slots (head/hands/legs on top of chest) plus a shield, stacking a heavy+shield build to AC 35-39 by mid-game - stacking real 5e doesn't have, since 5e has one armor slot. `enemies.json`'s `attack` stat (retuned in 4.1.5) was only ever checked against the *other* direction, and a flat +1-2/tier growth was never going to keep pace with AC compounding across 5 separate slots.

Asked which way to fix it: scale enemy attack way up (which would make unarmored/light builds nearly unplayable), or shrink the homebrew slots back down toward a 5e-reasonable AC range (closer to the actual root cause, since enemy attack was already tuned for that range). Went with the second.

### Changed
- `data/items.json`: every head/hands/legs armor piece's `base_ac` halved (`ceil(old/2)` - 1 stays 1, 2->1, 3->2, 4->2, 5->3) across all 45 affected items. Chest/shield untouched - they're the real 5e-modeled slots and were already correctly scaled.

### Verified
- Re-ran the same model against the edited data: enemy-hits-Fighter went from a flat 5% at tiers 3-8 to a range that actually moves with tier again (5-25%); Cleric similarly (5-35%); Rogue stayed in a sane 27-57% band throughout. No longer a dead flat line for the whole second half of the game.

---

## [4.1.10] - 2026-10-18 - Head/hands/legs prices never followed the AC cut

Asked to check merchant prices against the 4.1.9 AC change. They hadn't - 4.1.9 only touched `base_ac`, so every head/hands/legs item's price-per-point-of-AC doubled (e.g. Great Helm: AC 4 for 18000 copper before, AC 2 for the same 18000 after - twice the price for the same armor piece now sells for half the protection).

### Changed
- `data/items.json`: halved `price_copper` on the same 45 items whose `base_ac` changed in 4.1.9, restoring their original price-per-AC ratio (unchanged, just priced in line with their now-smaller stat).

### Fixed (self-caught before it shipped)
- First pass halved price on all 54 head/hands/legs items, but 9 of them (`Leather Cap`, `Cloth Hood`, `Hooded Cowl`, `Leather Gloves`, `Cloth Wraps`, `Fingerless Gloves`, `Leather Leggings`, `Cloth Trousers`, `Traveler's Breeches`) had `base_ac` of 1 both before and after 4.1.9 (`ceil(1/2)` stays 1) - their stat never changed, so halving their price was wrong. Caught by cross-checking against the exact 45-item list from 4.1.9's own output rather than re-deriving which items changed from their current AC value alone; reverted those 9 back to their original price.

---

## [4.1.11] - 2026-10-18 - Weapon damage plateaued while enemy HP kept climbing

Asked to check weapon damage scaling. Melee weapon dice stop improving after tier 4 (`Maul`, 2d6) - there was no tier-5 or tier-6 weapon with a bigger die at all, and the tier-7/8 "legendary" weapons (Dragonfang Blade, Soul Reaper, Worldbreaker, etc.) were built around special on-hit effects (bleed/burn/stun/drain), not raw damage, so several of them actually hit *softer* than the plain tier-4 Maul. Ranged was worse - Heavy Crossbow's 1d10 (tier 4) was still the best ranged die all the way through tier 7, with no tier-5 or tier-8 ranged weapon existing at all. Modeled turns-to-kill using real damage dice, real hit chance, and Extra Attack: trash kills climbed from 1.8 turns at tier 1 to 9.1 turns by tier 8, bosses from 5.3 to 27.3 - fights got steadily more grindy instead of staying paced, because enemy HP (fixed in 4.1.8) kept growing while weapon damage didn't.

Asked whether to add bigger tier-5/6/8 weapons or ease off enemy HP instead - went with adding weapons, so gear progression stays meaningful instead of flattening late-game difficulty.

### Added
- `data/items.json`: new pure-damage (no special effect) weapons at the three gap tiers - `War Maul` (3d6, tier 5, melee), `Behemoth Axe` (3d8, tier 6, melee), `Ragnarok Edge` (3d10, tier 8, melee), `War Crossbow` (2d6, tier 5, ranged), `Doomwhisper Bow` (2d10, tier 8, ranged). Priced in line with the existing price-per-average-damage ratio of their nearest mundane neighbor (Greatsword, Heavy Crossbow), cheaper per point than the effect-carrying legendaries since they trade utility for raw numbers.

### Changed
- `data/items.json`: `Hunter's Longbow` (tier 6, ranged) buffed from 1d10 to 2d8 - it was the one existing item sitting exactly on the tier-4 plateau. Price scaled from 18000 to 29500 to preserve its original price-per-average-damage ratio exactly (same mistake as 4.1.9/4.1.10 otherwise).

### Verified
- Re-ran the turns-to-kill model: melee trash kills now hold flat at 5.3-6.2 turns across all 8 tiers (was 1.8-9.1), bosses flat at 15.8-18.6 (was 5.3-27.3). Ranged improved from an open-ended climb to 5.5-8.5 turns. Side effect: tier 6's Behemoth Axe (3d8) outdamages tier 7's existing Titan's Maul (2d8), so a tier-7 character naturally keeps using it instead of "downgrading" - the one tier-7 soft spot flagged when this was first reported ends up covered without needing to touch tier 7 directly.

---

## [4.1.12] - 2026-10-18 - Leveling up gave casters a free full spell-slot refill

Asked to check spell slot usage. Spell damage scaling itself checked out fine (climbs smoothly with each new spell level, no plateau like weapons had), but found a real bug in how slots are tracked across a level-up.

`_level_up()` called `_refresh_spell_slots()` unconditionally - the same full-reset method `long_rest()` uses - every time a caster leveled up, regardless of whether they'd actually rested. A tier-1 dungeon run has ~40 enemy encounters worth up to 800 XP total, and a level-1 character only needs 150 XP to reach level 2 and 600 for level 3 - so a caster routinely levels up once or twice mid-dungeon, and each time was getting every spell slot fully refilled for free, with no rest required. That silently erased the entire "slots don't recover until you reach a village/town" resource constraint for most of the early game.

### Fixed
- `models/character.py`: added `_grant_new_spell_slots()`, called from `_level_up()` in place of `_refresh_spell_slots()`. It diffs the old level's slot table against the new one and adds only the newly-unlocked capacity (a bigger count at an already-known spell level, or a brand-new level unlocking) to whatever's currently remaining - already-spent slots stay spent. `long_rest()` is untouched and still does the real full reset.
- Verified directly: spend 1 of 2 level-1 slots, level up (1st-level max 2->3) - remaining went 1->2 (gained exactly the +1 new capacity), not reset to 3. Leveling again into a brand-new 2nd-level slot (max 0->2) correctly added 2 fresh 2nd-level slots while the 1st-level pool kept its already-spent state plus its own +1 delta.

---

## [4.1.13] - 2026-10-18 - Venomous Strikes' poison was a flat number next to scaling weapons

Asked to re-check skill point costs after the recent fixes - the `cost` field itself was unaffected (nothing links it to HP/AC/weapon/spell changes), but flagged that Venomous Strikes' poison (flat 2 damage/turn for 3 turns = 6 total) had gone stale relative to Vampiric Strikes (15% of damage dealt, which scales automatically) now that 4.1.11 added weapons hitting for 15-20+ per swing - same "flat value next to a system that grew" shape as the weapon-vs-enemy-HP and AC-vs-attack bugs earlier in this session, just in a skill effect instead of a data table. Asked whether to rebalance it - yes.

### Changed
- `models/combat.py`: `_apply_poison_chance()` now takes the triggering hit's `damage` and scales poison's per-turn damage to `max(1, round(damage * 0.2))` instead of a flat 2, over the same 3 turns. The 0.2 factor is derived, not guessed: Vampiric Strikes lands `0.15 * damage` every hit (100% proc); matching that expected value at poison's 25% proc rate needs `0.25 * (3 * per_turn) = 0.15 * damage`, which solves to `per_turn = 0.2 * damage` - the two tier-4 skills (one per branch) now carry the same expected value per hit instead of one quietly decaying as gear improves.
- `data/skills.json`, `docs/manual.md`: updated Venomous Strikes' description and the status-effects table to describe the new scaling instead of the old flat "2 damage/turn."

### Verified
- Live-tested `_apply_poison_chance` directly: a 20-damage hit (tier-8 scale) now poisons for 4/turn (12 total); a 3-damage hit still gets the `max(1, ...)` floor rather than rounding to 0.

---

## [4.1.14] - 2026-10-18 - Bleed and burn had the exact same flat-DOT problem as poison

Asked to check bleed and burn too, right after the poison fix. Same bug, same shape: `_apply_weapon_effect()` applies bleed/burn unconditionally (100% of the time a weapon with that effect lands a hit, no chance roll at all) using the flat `DOT_STATUSES` values (bleed 2/turn x2=4 total, burn 3/turn x2=6 total) set back when weapons topped out around 7-9 avg damage. Now that 4.1.11 added weapons hitting for up to ~20, that same fixed 4-6 total damage shrank from being a meaningful bonus (~58% of one hit's damage at tier 1) to a minor afterthought (~20-30% by tier 8) - and it's worse than poison's version of this bug, since bleed/burn are tied to specific legendary weapons (Dragonfang Blade, Hunter's Longbow, Flame Blade, Runed Greatsword, Legendary Blade), not a skill choice, so a decaying rider effect quietly undermines the reason to pick those items over a plain high-damage weapon at all.

### Changed
- `models/combat.py`: `DOT_STATUSES` now only holds each effect's `turns` (duration); a new `DOT_DAMAGE_FRACTION` dict (`bleed: 0.10, burn: 0.15, poison: 0.20`) holds the per-turn damage as a fraction of the triggering hit instead. `_apply_weapon_effect()` takes `damage` and computes `max(1, round(damage * DOT_DAMAGE_FRACTION[effect]))` the same way 4.1.13 did for poison; `_apply_poison_chance()` switched to read from the same shared table instead of its own hardcoded `0.2` literal, so there's one source of truth for all three DOTs. Burn kept at 1.5x bleed's rate, preserving their original 3:2 ratio exactly.

### Verified
- Live-tested `_apply_weapon_effect` directly: a 20-damage hit gives bleed 2/turn, burn 3/turn (matches the old flat values exactly at the damage level they were originally tuned for); a 7-damage hit gives both 1/turn (floor applied, ratio no longer distinguishable at that small a hit, which is expected and fine). Confirmed `stun` and `drain` - the two non-DOT weapon effects - are unaffected by the signature change.

---

## [4.1.15] - 2026-10-18 - Drain healed 20x more than lifesteal on the identical hit

Asked to check lifesteal and drain too. Lifesteal (Vampiric Strikes) had nothing to fix - it already scales with the triggering hit's damage (`0.15 * damage`), and was the reference value every other effect in 4.1.13/4.1.14 was calibrated against. Drain (Worldbreaker, Soul Reaper) was a different, pre-existing problem unrelated to anything changed earlier today: it healed `5% of the attacker's own max HP` per hit, not a fraction of the hit's damage. At level 50 that's 20 HP on a hit that deals ~12 - the wielder heals for more than they damage the enemy, every single swing, and 20x more than Vampiric Strikes would give on the identical hit. Not something that decayed over time like the DOT bug - more likely always this disproportionate, just surfaced by checking this family of effects together.

### Changed
- `models/combat.py`: drain's heal changed from `max(1, int(attacker.max_health * 0.05))` to `max(1, int(damage * DRAIN_HEAL_FRACTION))` with `DRAIN_HEAL_FRACTION = 0.15` - the same fraction and the same `int()` truncation Vampiric Strikes already uses, so a drain weapon and the lifesteal skill are now mechanically equivalent, just delivered through different sources (an item vs. a skill point), rather than one trivializing the other.

### Verified
- Live-tested both directly on the same 12-damage hit: drain and `_apply_lifesteal` now return the identical result (1 HP) where drain previously would have given 20 on a level-50 character regardless of the hit's size.

---

## [4.1.16] - 2026-10-18 - Spell crits ignored Executioner/Death's Precision entirely

Asked to check critical hit multiplier scaling. The multiplier itself is fine for melee - it's a ratio, not a flat number, so it scales with whatever damage it's applied to automatically, and `_calculate_melee_damage()` already reads the character's real `crit_multiplier` property (2.0 base, 2.5/3.0 once Executioner/Death's Precision are unlocked). Spell crits didn't: `_resolve_spell()`'s `attack`-type branch (the one used by Guardian of Faith, the lone `attack`-type spell) hardcoded `damage *= 2` instead of reading `attacker.crit_multiplier` at all - a caster who spent two skill points climbing the Offense tree to Death's Precision got zero benefit from it the one time their own spell crit.

### Fixed
- `models/combat.py`: `_resolve_spell()`'s crit branch now reads `getattr(attacker, 'crit_multiplier', CRITICAL_HIT_MULTIPLIER)`, the same pattern melee already uses, instead of the hardcoded `*2`.

### Verified
- Live-tested `_resolve_spell` directly with a forced nat-20 crit and `crit_multiplier = 3.0`: an 18-damage roll now deals 54 (18*3.0), where the old hardcoded path would have given 36 (18*2) regardless of any skill investment.

### Removed
- `config.CRITICAL_HIT_CHANCE = 0.15` - dead data, confirmed via grep that nothing in the codebase read it. Asked whether to wire it in (would've tripled crit chance from 5% to 15%) or delete it to match the nat-20-only design that's actually implemented and documented; told to delete and keep crit at 5%. Removed the constant; `CRITICAL_HIT_MULTIPLIER` is untouched.

---

## [4.1.17] - 2026-10-18 - Two more dead config constants, and a rare-drop mismatch

Asked to check flee chance and loot bonus scaling. `Character.flee_bonus`/`loot_bonus` themselves had nothing to fix - both are flat adds to a probability/roll (+3 to a flee roll, +10% to a drop chance), not an absolute number compared against a growing stat, so there's nothing for them to decay relative to, same reasoning as Evasion's dodge chance. But checking them turned up the same dead-constant pattern as `CRITICAL_HIT_CHANCE` twice more, plus a real mismatch:

- `config.FLEE_BASE_CHANCE = 0.3` - never read anywhere; the real flee formula in `combat.py` has its own hardcoded `flee_dc = 10` and `+2` baseline, unrelated to this constant.
- `config.COMMON_DROP_CHANCE = 0.6` - never read; `enemy.py` hardcodes `0.6` directly. Matched by coincidence, but still dead - changing the config constant would have silently done nothing.
- `config.RARE_DROP_CHANCE = 0.1` - never read; `enemy.py` hardcoded `0.15` instead, a different number entirely, not just unread.

Asked whether to delete the dead constants and which rare-drop number to keep; told to delete and wire the real behavior to the stated 10%.

### Changed
- `models/enemy.py`: rare-item drop chance `0.15` -> `0.10`, matching the config constant's stated value rather than the number the code happened to have.

### Removed
- `config.FLEE_BASE_CHANCE` and `config.COMMON_DROP_CHANCE` - dead, deleted outright (the code they'd have matched is unchanged). `config.RARE_DROP_CHANCE` also deleted after its value was folded into the actual code above.

---

## [4.1.18] - 2026-10-18 - The rest of the skill tree checked out; Power Strike could be banked across spells

Asked to check the other skill effects (Power Strike, Weapon Mastery, Second Wind, Last Stand, Phoenix Heart, Battle Focus, Fortune's Favor - the ones not already covered by the lifesteal/poison/drain/crit/dodge/flee/loot checks). None had a scaling bug - they all fall into categories already established as immune to the "flat number vs. growing stat" problem this whole family of checks was hunting: percentage multipliers on damage/healing (Power Strike's 1.5x, Second Wind/Phoenix Heart's % of max HP, which itself grows every level), flat adds to a roll rather than a damage number (Weapon Mastery's +2 attack, same category as Iron Skin), flat XP percentages (Battle Focus/Fortune's Favor), and a binary survive-once effect with no number at all (Last Stand).

One real gap turned up anyway, not a scaling issue but a missing interaction: `pending_power_strike` was only ever read or cleared in the melee attack path (`calculate_hit()`, `_resolve_attacks()`). Priming Power Strike and then casting a spell, using an item, or using a different active skill instead of attacking left the flag neither applied nor cleared - it just sat there, banked indefinitely for whatever melee attack eventually came next, with no downside to delaying it. Asked how to handle it (burn it on any other action, apply it to spells too, or leave it); told to burn it.

### Fixed
- `models/combat.py`: `process_turn()` now clears `pending_power_strike` (with a "fizzles, unused" message) whenever the action type isn't `'attack'`, covering spell casts and flee/move.
- `gui/combat_window.py`: `use_selected_item()` and `use_selected_ability()` - the two paths that bypass `process_turn()` entirely - got the same check, since using a potion or a different active skill (e.g. Second Wind) while Power Strike was already primed from an earlier turn needed the same fizzle, not just casting a spell.

### Verified
- Live-tested `process_turn()` directly: a primed Power Strike correctly clears (with the fizzle message) when the action is `'flee'`, and is correctly consumed (not double-cleared, `**POWER STRIKE!**` tag present, auto-hit landed) when the action is the real `'attack'` it was meant for.

---

## [4.1.19] - 2026-10-19 - General sweep: two more dead constants, a stale doc, clean cross-references

Asked if there were any other issues, after the long chain of targeted checks (HP, AC, weapons, spells, skills, drain, crit, dodge, flee, loot). Did a broader pass instead of guessing: re-checked every remaining `config.py` constant for the same dead-code pattern already found four times, verified every cross-reference between the data files (enemy drops -> items, class spell lists -> spells, class starting gear -> items, skill `requires` chains, quest/spell ability-name fields), and checked whether the generated docs had drifted from the data they describe.

### Removed
- `config.CAMP_HEAL_RATE` and `config.ABILITY_NAMES` - both confirmed dead via grep (zero references anywhere outside their own definition line), same pattern as the four constants removed in 4.1.16/4.1.17. `CAMP_HEAL_RATE` was already flagged as superseded by `Character.camp_rest()`'s percentage formula back when camp/scout was added (3.3.0); it just hadn't been deleted until now.

### Fixed
- `docs/items_reference.md` regenerated from the current `data/items.json` - it was still showing pre-4.1.9/4.1.10 AC and price values (e.g. Great Helm listed as AC 4 / 180gp, actually AC 2 / 90gp) and was missing the five weapons 4.1.11 added. Now current at 139 items (was 134).

### Checked, nothing broken
- Every enemy `common_drops`/`rare_drops` name resolves to a real item in `items.json`.
- Every class's `cantrips_known_at_1`, `spells_by_level`, and starting weapon/armor/shield resolve to real entries in `spells.json`/`items.json`.
- Every skill's `requires` resolves to a real skill id; every quest's `ability` and spell's `save_ability` is a valid ability name.

### Found, not fixed (cosmetic, not broken)
- `Thieves' Tools` and `Torch` carry `effect: "unlock_vault"`/`"light_radius"` in `items.json`, but nothing reads those specific string values - `Dungeon.try_unlock_vault()` and `_effective_view_range()` both check the item by *name* instead (`consume_item_named("Thieves' Tools")`, `has_item_named('Torch')`). Both items work correctly through the name-based path; the `effect` field on these two is just decorative dead data, not a functional bug, so left alone rather than touching working code without being asked.

---

## [4.1.20] - 2026-10-19 - story.py's dead encounter trigger and generic treasure message, finally fixed

Asked to check `story.py` (the project-root CTS-285 passage file, separate from `game/main.py`) - this was reported as a finding much earlier in the session ("is this a complete game") but explicitly never fixed at the time. Checked it now with the same lens as everything else this session, and it had the exact bugs flagged back then, still untouched.

- `run_world_map_gui`'s `handle_world_encounter`/`on_move` gated the random-encounter trigger on `not node.visited`, but `WorldMap.move_player()` sets `.visited = True` on arrival *before* that check runs - the identical dead-code shape `game/main.py`'s own version of this had (fixed in this session's early 3.x work by switching to a separate `.cleared` field gated only on actual resolution). Walking onto a `?` tile in `story.py` did nothing, silently, every time.
- `on_interact()`'s treasure pickup said only "You found treasure!" with no breakdown of what was actually found - `main.py`'s `_apply_loot()` already solved this with itemized `+ N copper` / `+ Item Name` lines; `story.py` never got the same treatment.
- Found one more while in there: `passage_vault_door()` called `_dungeon.try_unlock_vault(_player)` and printed "The lock clicks open" unconditionally, never checking the method's own return value - if the unlock ever failed, the message would still claim success.

### Fixed
- `story.py`: `handle_world_encounter` and `on_move` switched from `.visited` to `.cleared`, matching `main.py`'s fix exactly.
- `story.py`: `on_interact()`'s treasure branch now builds the same itemized loot lines `main.py` does instead of a flat "You found treasure!".
- `story.py`: `passage_vault_door()` now branches on `try_unlock_vault()`'s actual return value - success keeps the existing "lock clicks open" line into the boss fight, failure prints a miss and sends the player back to `passage_find_key()` (a link the passage graph already had, so no new dead ends).

### Verified
- `python story_check.py story.py --map` (the assignment's own structural checker) still reports "OK: no orphans, no dead ends, no broken links, no traps" after the edits - 10 passages, 14 links, unchanged graph shape.

### Not done (feature gap, not a bug - flagged, not touched)
- `story.py` still has no Camp, Scout, or Quests - `game/main.py` has all three. That's missing functionality, not broken behavior, so it wasn't added without being asked first.

---

## [4.1.21] - 2026-10-19 - Camp, Scout, and Quests ported to story.py

Asked to port Camp/Scout/Quests into `story.py` too, closing the feature gap flagged in 4.1.20.

### Added
- `story.py` imports `QuestBoard` from `models.quests`.
- `run_world_map_gui()`: `on_camp`/`on_scout` handlers mirroring `main.py`'s `handle_camp`/`handle_scout` exactly (same full-health guard, same `camp_rest()`/`scout_nearby()` calls, same message wording), bound to `C`/`R`. The "The Wild" instructions popup now lists all six controls instead of four.
- `passage_village()`: creates a `QuestBoard()` and passes it into `show_merchant_ui(..., quest_board=quest_board)`, giving the village/town merchant window the same Quests tab `main.py`'s settlements already have.

### Verified
- `python story_check.py story.py --map` still reports the same 10 passages, 14 links, no orphans/dead ends/broken links - camp/scout/quests are GUI helpers, not passages, so the story graph is unaffected.

---

## [4.1.22] - 2026-10-19 - World map was still 32x32, not the requested 500x500

The world map was supposed to be 500x500 from an earlier request that got missed while this session's attention was on the balance-audit chain. Fixed directly.

### Changed
- `models/world_map.py`: `WorldMap.__init__`'s default `size` changed from `32` to `500`. Both `main.py` and `story.py` create a new map with `WorldMap()` (no explicit size), so this one default covers a new game in either entry point; loading an existing save still passes its own saved `size` through unchanged, so old saves keep their original map rather than being silently resized.

### Verified
- Timed `WorldMap(size=500)` generation directly (data generation, not the GUI) at 0.77-0.81s - the road-building step does a BFS per settlement, which could have been a real risk at 125x more tiles, but it's not; no change needed there.
- Confirmed no other code hardcodes the old `32` (grepped `models/world_map.py`, `gui/main_window.py`, `main.py`) - rendering was already viewport-limited to `VISIBLE_RANGE` around the player, not drawing the whole grid, so it was never a rendering concern either.
- Resulting default map: 250,000 tiles, 125 villages, 83 towns, 166 dungeons, 500 encounters (the existing `size`-scaled formulas from 3.0.0 apply automatically - not re-tuned here, since only the size itself was reported wrong, not the density).
- Save/load round-trip (`to_dict()` -> `WorldMap(**dict)`) confirmed intact at the new size.

---

## [4.1.23] - 2026-10-19 - Village/town/dungeon/encounter counts only scaled with side length, not area

Pointed out right after 4.1.22: more tiles should mean more villages, towns, etc. It didn't, fully - `num_villages`/`num_towns`/`num_dungeons`/`num_encounters` were `max(N, self._size // K)`, scaling with the map's *side length*, not its tile *area*. Going from 32x32 to 500x500 is a 244x increase in tiles but only a 15.6x increase in side length, so those counts only grew 15.6x - the world got 244x bigger while only getting 15.6x more content, making it 15.6x sparser than the original map rather than just bigger.

### Changed
- `models/world_map.py`: all four counts now scale off `area = self._size * self._size` instead of `self._size` directly, with ratios chosen to reproduce the *exact* original density (8/5/10/32 per 1024 tiles) rather than picking a new number - `area * 8 // 1024`, `area * 5 // 1024`, `area * 10 // 1024`, `area * 32 // 1024`.

### Verified
- `WorldMap(size=32)` reproduces the exact original counts (8 villages, 5 towns, 10 dungeons, 32 encounters) - confirms the new formula is a strict generalization, not a behavior change at the old size.
- Default `WorldMap()` (size=500) now generates 1,953 villages, 1,220 towns, 2,441 dungeons, 7,812 encounters - same 5.37% density as the original map, just spread across 244x the tiles. Generation time 2.33s (up from 0.81s with the old under-scaled counts, still well within reason).

## Not yet done / known gaps

- No full manual playthrough of the 3.0.0+ changes has been done yet (smoke-tested at the model/data layer only as of this entry) - this is especially true of 4.0.0, which is large enough that I'd treat a real playthrough as necessary before trusting it, not optional
