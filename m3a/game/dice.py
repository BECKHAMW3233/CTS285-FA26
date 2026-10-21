# dice.py - shared dice notation parser/roller (e.g. "1d8", "2d6", "1d4+1").
import random
import re
from typing import Tuple

_PATTERN = re.compile(r"^(\d+)d(\d+)([+-]\d+)?$")


def parse(dice_str: str) -> Tuple[int, int, int]:
    """Parse 'NdM+K' into (count, sides, modifier)."""
    match = _PATTERN.match(dice_str.strip())
    if not match:
        raise ValueError(f"Invalid dice notation: {dice_str}")
    count, sides, modifier = match.groups()
    return int(count), int(sides), int(modifier) if modifier else 0


def roll(dice_str: str) -> int:
    """Roll dice notation like '2d6+1' and return the total."""
    count, sides, modifier = parse(dice_str)
    return sum(random.randint(1, sides) for _ in range(count)) + modifier


def average(dice_str: str) -> int:
    """The fixed/average result for dice notation (the SRD's 'fixed hit
    points per level' option instead of rolling: d6=4, d8=5, d10=6, d12=7)."""
    count, sides, modifier = parse(dice_str)
    return count * (sides // 2 + 1) + modifier


def max_value(dice_str: str) -> int:
    """The maximum possible result (used for level-1 hit points)."""
    count, sides, modifier = parse(dice_str)
    return count * sides + modifier
