"""Display-string helpers, including the 8-character VFD width limit
(RESEARCH.md §2, Itron FG105H1) that every display string in this app
is run through."""

from .config import OP_DISPLAY, DISPLAY_WIDTH


def format_display(s):
    """Enforce the real unit's 8-character VFD width.

    The manual never says what happens when a readout is wider than the
    display (e.g. a two-digit problem with an operator and equals sign
    easily runs past 8 characters). JUDGMENT CALL: we keep the
    *right-most* 8 characters and drop the front, mimicking how a
    numeric display overflows by losing its leading (most significant)
    characters rather than its trailing ones -- the trailing end is
    where the answer/result of a problem or the last field of a score
    readout lives, so that's what we protect. This is a display-layer
    truncation only; we do NOT pad short strings, since blank-digit
    padding is a rendering concern for a real VFD's segments, not
    something a JSON API needs to encode.
    """
    if len(s) <= DISPLAY_WIDTH:
        return s
    return s[-DISPLAY_WIDTH:]


def problem_display(op, a, b):
    return format_display(f"{a} {OP_DISPLAY[op]} {b} =")


def reveal_display(op, a, b, result, remainder):
    s = f"{a} {OP_DISPLAY[op]} {b} = {result}"
    if remainder is not None:
        s += f" r{remainder}"
    return format_display(s)


def missing_number_display(op, a, b, result, box):
    """box is which slot is hidden: 'right' (the result), 'left' (the
    first operand), or 'middle' (the second operand)."""
    da = "?" if box == "left" else a
    db = "?" if box == "middle" else b
    dc = "?" if box == "right" else result
    return format_display(f"{da} {OP_DISPLAY[op]} {db} = {dc}")


FLASH_DISPLAY = format_display("-------⬡")  # "right answer" flash, Answer Checker (Operating Notes)
