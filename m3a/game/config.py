import os
import logging
from datetime import datetime
from typing import Final

# Directory Configuration
BASE_DIR: Final = os.path.dirname(os.path.abspath(__file__))
DATA_DIR: Final = os.path.join(BASE_DIR, 'data')
SAVE_DIR: Final = os.path.join(BASE_DIR, 'saves')
LOG_DIR: Final = os.path.join(BASE_DIR, 'logs')

# Initialize directories
for directory in [DATA_DIR, SAVE_DIR, LOG_DIR]:
    os.makedirs(directory, exist_ok=True)

# Window Configuration
# 800 (fixed-size dungeon/world canvas) + 740 (three-column sidebar: paper-
# doll equipment diagram, character/ability stats, inventory+actions) + margin
WINDOW_WIDTH: Final = 1600
WINDOW_HEIGHT: Final = 1000
WINDOW_TITLE: Final = "Dungeon RPG"

# Game Constants
VISIBLE_RANGE: Final = 4
CRITICAL_HIT_MULTIPLIER: Final = 2.0
STARTING_GOLD_COPPER: Final = 1500  # 15 gp

# Per-turn combat distance (homebrew): 0 is melee range, higher bands are
# farther away. Melee weapons only work at band 0; ranged weapons work at
# any band. Enemies have no ranged capability at all, so every fight is
# "the enemy closes in while you decide whether to meet them or keep
# shooting" - every enemy turn spent at band > 0 advances instead of
# attacking, rather than tracking real distance in feet.
COMBAT_DISTANCE_BANDS: Final = ['Melee', 'Mid', 'Far']
COMBAT_START_DISTANCE: Final = 2
COMBAT_MAX_DISTANCE: Final = len(COMBAT_DISTANCE_BANDS) - 1

# Enemy spawn rates
ENEMY_SPAWN_CHANCE: Final = 0.4

# --- D&D 5e SRD tables (System Reference Document 5.1, OGL/CC - open for
# public/derivative use), extended past the SRD's native 1-20 cap to a
# 50-level arc. The real SRD XP table (300/900/2700/.../355000) assumes a
# 4-person party splitting real SRD monster XP (tens to hundreds per kill);
# this game is solo and the old enemy xp_value scale was 1-8 per kill, so the
# unmodified SRD thresholds meant ~300 kills just to reach level 2. This
# curve (quadratic, 150*(level-1)^2) targets level 2 in under 10 kills and
# scales up smoothly from there - data/enemies.json's xp_value was rescaled
# to match (see its comment). Proficiency bonus keeps the SRD's "+1 every 4
# levels" pattern past level 20 instead of stopping at +6.

# XP required to REACH each level. Index 0 = level 1 (0 xp), index 49 = level 50.
XP_BY_LEVEL: Final = [
    0, 150, 600, 1350, 2400, 3750, 5400, 7350, 9600, 12150,
    15000, 18150, 21600, 25350, 29400, 33750, 38400, 43350, 48600, 54150,
    60000, 66150, 72600, 79350, 86400, 93750, 101400, 109350, 117600, 126150,
    135000, 144150, 153600, 163350, 173400, 183750, 194400, 205350, 216600, 228150,
    240000, 252150, 264600, 277350, 290400, 303750, 317400, 331350, 345600, 360150,
]

# Proficiency bonus by character level (1-indexed list, same layout as XP_BY_LEVEL).
PROFICIENCY_BONUS_BY_LEVEL: Final = [
    2, 2, 2, 2, 3, 3, 3, 3, 4, 4,
    4, 4, 5, 5, 5, 5, 6, 6, 6, 6,
    7, 7, 7, 7, 8, 8, 8, 8, 9, 9,
    9, 9, 10, 10, 10, 10, 11, 11, 11, 11,
    12, 12, 12, 12, 13, 13, 13, 13, 14, 14,
]

# Full-caster spell slot table: SPELL_SLOTS_BY_LEVEL[level-1] = [1st,2nd,...,9th] slot counts.
# The SRD has no official slots past level 20 - Character._refresh_spell_slots
# clamps to this table's last row for any higher level rather than guessing.
SPELL_SLOTS_BY_LEVEL: Final = [
    [2, 0, 0, 0, 0, 0, 0, 0, 0],
    [3, 0, 0, 0, 0, 0, 0, 0, 0],
    [4, 2, 0, 0, 0, 0, 0, 0, 0],
    [4, 3, 0, 0, 0, 0, 0, 0, 0],
    [4, 3, 2, 0, 0, 0, 0, 0, 0],
    [4, 3, 3, 0, 0, 0, 0, 0, 0],
    [4, 3, 3, 1, 0, 0, 0, 0, 0],
    [4, 3, 3, 2, 0, 0, 0, 0, 0],
    [4, 3, 3, 3, 1, 0, 0, 0, 0],
    [4, 3, 3, 3, 2, 0, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 0, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 0, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 0],
    [4, 3, 3, 3, 2, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 1, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 1, 1, 1],
    [4, 3, 3, 3, 3, 2, 2, 1, 1],
]

def dungeon_recommended_level(tier: int) -> int:
    """Rough guideline level for a dungeon tier, spread evenly across the
    8 enemy tiers over the full 1-50 level range (tier 1 -> level 1,
    tier 8 -> level 50)."""
    return min(50, 1 + (tier - 1) * 7)

# Logging Configuration
LOG_FILE = os.path.join(LOG_DIR, f'game_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)