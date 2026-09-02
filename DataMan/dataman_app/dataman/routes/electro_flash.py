"""Electro Flash -- timed drill through one arithmetic table. See
dataman-manual.md, "Electro Flash (Operating Notes)"."""

import time

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..mathutil import compute
from ..display import problem_display, reveal_display, FLASH_DISPLAY
from ..config import OPS

electro_flash_bp = Blueprint("electro_flash", __name__, url_prefix="/api/electro-flash")


def _generate_electro_flash_table(digit, op, digit_first):
    """Build the full 0-9 sweep for the chosen digit/op, then filter.

    Electro Flash (Operating Notes): "Subtraction tables that result in
    negative answers will not give problems; division tables won't give
    a problem whose answer has a remainder." We build the whole
    candidate table first and filter it, rather than generating one
    problem at a time and rejecting bad user input after the fact.

    JUDGMENT CALL: the manual never states the numeric range of a
    "table" -- it just says "practice math tables" / "the five times
    table". We sweep the *other* operand over 0-9, matching the ten
    digit keys on the unit (so, e.g., the "5 times" table is 5x0..5x9
    before filtering), rather than inventing some other range like 1-12.
    """
    problems = []
    for n in range(0, 10):
        if digit_first:
            a, b = digit, n
        else:
            a, b = n, digit
        try:
            result, remainder = compute(op, a, b)
        except ValueError:
            continue
        if remainder is not None:
            continue
        problems.append({"op": op, "a": a, "b": b})
    return problems


def _ef_start_table(state):
    """(Re)build the table for the current ef_digit/ef_op and load the
    first problem. Used by both GO and the auto-advance-to-next-table
    step described in the Operating Notes."""
    table = _generate_electro_flash_table(state["ef_digit"], state["ef_op"], state["ef_digit_first"])
    state["ef_queue"] = table
    state["ef_right"] = 0
    state["ef_tried"] = 0
    state["ef_go_time"] = time.time()
    first = state["ef_queue"].pop(0)
    state["ef_pending"] = {**first, "attempt": 1}
    return first


@electro_flash_bp.route("/select", methods=["POST"])
def ef_select():
    """Select the table: {"first": "digit"|"op", "digit": 5, "op": "*"}.

    Electro Flash key order (documented conflict, Operating Notes win):
    the Story says the number key and the operator key can be pressed
    "in any order"; the Operating Notes add that "the order in which you
    press these keys will determine the order in which numbers are
    presented in the problem." We keep track of which was pressed first
    via "first", and use it in ef_go/answer to decide whether the fixed
    digit sits in the first or second position of each problem.
    """
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True)
    first = data.get("first")
    digit = data.get("digit")
    op = data.get("op")

    if first not in ("digit", "op"):
        return err('"first" must be "digit" or "op".')
    if op not in OPS:
        return err("Invalid operator.")
    if not isinstance(digit, int) or not (0 <= digit <= 9):
        return err("Digit must be a single key, 0-9.")

    state["mode"] = "electro_flash"
    state["ef_digit"] = digit
    state["ef_op"] = op
    state["ef_digit_first"] = (first == "digit")
    state["ef_queue"] = []
    state["ef_pending"] = None
    touch(state)
    save_state(state)
    return jsonify({"digit": digit, "op": op, "digit_first": state["ef_digit_first"]})


@electro_flash_bp.route("/go", methods=["POST"])
def ef_go():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()
    if state["ef_digit"] is None or state["ef_op"] is None:
        return err("Select a table first (digit + operator).")

    first = _ef_start_table(state)
    touch(state)
    save_state(state)
    return jsonify({
        "display": problem_display(first["op"], first["a"], first["b"]),
        "remaining": len(state["ef_queue"]) + 1,
    })


@electro_flash_bp.route("/answer", methods=["POST"])
def ef_submit_answer():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    pending = state.get("ef_pending")
    if not pending:
        touch(state)
        save_state(state)
        return err("Press GO to start Electro Flash.")

    data = request.get_json(force=True)
    user_answer = data.get("answer")

    op, a, b, attempt = pending["op"], pending["a"], pending["b"], pending["attempt"]
    result, remainder = compute(op, a, b)
    correct = (user_answer == result)

    response = {}

    def advance():
        if state["ef_queue"]:
            nxt = state["ef_queue"].pop(0)
            state["ef_pending"] = {**nxt, "attempt": 1}
            response["next_display"] = problem_display(nxt["op"], nxt["a"], nxt["b"])
            response["remaining"] = len(state["ef_queue"]) + 1
        else:
            ticks = int(time.time() - state["ef_go_time"]) if state["ef_go_time"] else 0
            response["table_complete"] = True
            response["score"] = {
                "right": state["ef_right"],
                "tried": state["ef_tried"],
                "ticks": ticks,
            }
            # "After each table is completed, DataMan will automatically
            # start over with the next appropriate table." JUDGMENT CALL:
            # "next appropriate table" isn't defined further, so we advance
            # to the next digit (wrapping 0-9) on the same operator/order.
            state["ef_digit"] = (state["ef_digit"] + 1) % 10
            nxt_first = _ef_start_table(state)
            response["next_table"] = {"digit": state["ef_digit"], "op": state["ef_op"]}
            response["next_display"] = problem_display(nxt_first["op"], nxt_first["a"], nxt_first["b"])

    if correct:
        state["ef_right"] += 1
        state["ef_tried"] += 1
        response["display"] = FLASH_DISPLAY
        response["correct"] = True
        if remainder is not None:
            response["remainder"] = remainder
        advance()
    else:
        if attempt == 1:
            pending["attempt"] = 2
            response["display"] = "EEE"
            response["correct"] = False
            response["try_again"] = True
        else:
            state["ef_tried"] += 1
            response["display"] = reveal_display(op, a, b, result, remainder)
            response["correct"] = False
            response["try_again"] = False
            advance()

    touch(state)
    save_state(state)
    return jsonify(response)
