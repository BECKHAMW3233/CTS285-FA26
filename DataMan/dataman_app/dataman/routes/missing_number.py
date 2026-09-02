"""Missing Number ("Box") Problems -- fill-in-the-blank problems, blank
position selectable, two difficulty levels. See dataman-manual.md,
"Missing Number (Box) Problems (Operating Notes)"."""

import random
import time

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..mathutil import compute
from ..display import missing_number_display, reveal_display, FLASH_DISPLAY
from ..config import OPS, PROBLEMS_PER_ROUND

missing_number_bp = Blueprint("missing_number", __name__, url_prefix="/api/missing-number")


def _gen_missing_number_triple(op, level):
    """Generate a valid (a, b, result) honoring the same "no negative
    subtraction, no remainder division" rule used everywhere else on
    DataMan, so every box position always has a solvable, in-range
    answer.

    JUDGMENT CALL: the manual says level 2 is "more challenging" but
    never states by how much. We use single-digit operands (0-9) for
    level 1 and two-digit operands (0-99) for level 2 -- the same
    single-vs-double-digit split the rest of the product already uses
    to distinguish problem difficulty.
    """
    digit_max = 9 if level == 1 else 99
    while True:
        a = random.randint(0, digit_max)
        b = random.randint(0, digit_max)
        try:
            result, remainder = compute(op, a, b)
        except ValueError:
            continue
        if remainder is not None:
            continue
        return a, b, result


def _mn_next_box(current):
    """Missing Number box travel (the manual's clearest internal
    contradiction, per the analyst's note): the Story's prose says the
    box moves "left to right"; the Operating Notes describe -- and the
    Story's OWN worked examples (4 x 3 = [?], [?] x 3 = 12, 4 x [?] = 12)
    independently confirm -- a right -> left -> middle cycle. This is a
    narrower, more specific override than the general
    Operating-Notes-wins rule: here the Story's own examples override the
    Story's own prose, so it's worth calling out on its own rather than
    folding it into the general rule.

    JUDGMENT CALL: the manual only describes three presses (right, left,
    middle) starting from "not yet pressed". What a fourth press does
    isn't stated; we cycle back to "right", the only mechanically sound
    way to keep a physical key doing something on every press.
    """
    if current is None:
        return "right"
    return {"right": "left", "left": "middle", "middle": "right"}[current]


def _mn_missing_value(problem):
    return {"right": problem["result"], "left": problem["a"], "middle": problem["b"]}[problem["box"]]


@missing_number_bp.route("/cycle-box", methods=["POST"])
def mn_cycle_box():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    state["mode"] = "missing_number"
    state["mn_box"] = _mn_next_box(state["mn_box"])
    touch(state)
    save_state(state)
    return jsonify({"box": state["mn_box"]})


@missing_number_bp.route("/select-op", methods=["POST"])
def mn_select_op():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True)
    op = data.get("op")
    if op not in OPS:
        return err("Invalid operator.")

    state["mode"] = "missing_number"
    state["mn_op"] = op
    touch(state)
    save_state(state)
    return jsonify({"op": op})


@missing_number_bp.route("/select-level", methods=["POST"])
def mn_select_level():
    """Level 2 = harder (press 2 before GO); pressing 1 returns to level
    1. This return-to-1 detail is Story-only -- *Your Score* / *More
    DataMan Fun!* states it and the Operating Notes are simply silent
    (not contradictory) about it, so per the silence rule we keep it."""
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True)
    level = data.get("level")
    if level not in (1, 2):
        return err("Level must be 1 or 2.")

    state["mn_level"] = level
    touch(state)
    save_state(state)
    return jsonify({"level": level})


@missing_number_bp.route("/go", methods=["POST"])
def mn_go():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()
    if state["mn_box"] is None or state["mn_op"] is None:
        return err("Press the Missing Number key and choose an operator first.")

    queue = []
    for _ in range(PROBLEMS_PER_ROUND):
        a, b, result = _gen_missing_number_triple(state["mn_op"], state["mn_level"])
        queue.append({"op": state["mn_op"], "a": a, "b": b, "result": result, "box": state["mn_box"]})

    state["mn_queue"] = queue
    state["mn_right"] = 0
    state["mn_tried"] = 0
    state["mn_go_time"] = time.time()

    first = state["mn_queue"].pop(0)
    state["mn_pending"] = {**first, "attempt": 1}
    touch(state)
    save_state(state)

    return jsonify({
        "display": missing_number_display(first["op"], first["a"], first["b"], first["result"], first["box"]),
        "remaining": len(state["mn_queue"]) + 1,
    })


@missing_number_bp.route("/answer", methods=["POST"])
def mn_submit_answer():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    pending = state.get("mn_pending")
    if not pending:
        touch(state)
        save_state(state)
        return err("Press GO to start Missing Number.")

    data = request.get_json(force=True)
    user_answer = data.get("answer")

    target = _mn_missing_value(pending)
    correct = (user_answer == target)

    response = {}

    def advance():
        if state["mn_queue"]:
            nxt = state["mn_queue"].pop(0)
            state["mn_pending"] = {**nxt, "attempt": 1}
            response["next_display"] = missing_number_display(nxt["op"], nxt["a"], nxt["b"], nxt["result"], nxt["box"])
            response["remaining"] = len(state["mn_queue"]) + 1
        else:
            state["mn_pending"] = None
            ticks = int(time.time() - state["mn_go_time"]) if state["mn_go_time"] else 0
            response["run_complete"] = True
            response["score"] = {
                "right": state["mn_right"],
                "tried": state["mn_tried"],
                "ticks": ticks,
            }

    if correct:
        state["mn_right"] += 1
        state["mn_tried"] += 1
        response["display"] = FLASH_DISPLAY
        response["correct"] = True
        advance()
    else:
        if pending["attempt"] == 1:
            pending["attempt"] = 2
            response["display"] = "EEE"
            response["correct"] = False
            response["try_again"] = True
        else:
            state["mn_tried"] += 1
            response["display"] = reveal_display(pending["op"], pending["a"], pending["b"], pending["result"], None)
            response["correct"] = False
            response["try_again"] = False
            advance()

    touch(state)
    save_state(state)
    return jsonify(response)
