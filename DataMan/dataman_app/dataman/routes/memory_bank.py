"""Memory Bank -- store up to 10 problems, then GO replays them with
DataMan's built-in timer running. See dataman-manual.md, "Memory Bank
(Operating Notes)"."""

import time

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..mathutil import compute, validate_digits, invalid_problem_message
from ..display import problem_display, reveal_display, FLASH_DISPLAY
from ..config import MAX_MEMORY_PROBLEMS

memory_bank_bp = Blueprint("memory_bank", __name__, url_prefix="/api/memory-bank")


@memory_bank_bp.route("/store", methods=["POST"])
def mb_store():
    """Store a problem (unanswered) into memory. Up to 10 total."""
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    if len(state["mb_problems"]) >= MAX_MEMORY_PROBLEMS:
        touch(state)
        save_state(state)
        return err("Memory Bank is full (10 problems max).")

    data = request.get_json(force=True)
    op = data.get("op")
    a = data.get("a")
    b = data.get("b")

    try:
        validate_digits(a, b)
        compute(op, a, b)
    except ValueError as e:
        touch(state)
        save_state(state)
        return err(invalid_problem_message(e))

    state["mode"] = "memory_bank"
    state["mb_problems"].append({"op": op, "a": a, "b": b})
    touch(state)
    save_state(state)

    return jsonify({
        "stored": len(state["mb_problems"]),
        "max": MAX_MEMORY_PROBLEMS,
    })


@memory_bank_bp.route("/clear", methods=["POST"])
def mb_clear():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()
    state["mb_problems"] = []
    state["mb_queue"] = []
    state["mb_right"] = 0
    state["mb_tried"] = 0
    state["mb_pending"] = None
    state["mb_go_time"] = None
    touch(state)
    save_state(state)
    return jsonify({"stored": 0})


@memory_bank_bp.route("/go", methods=["POST"])
def mb_go():
    """Start playing back stored problems, one at a time, timer running."""
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    if not state["mb_problems"]:
        touch(state)
        save_state(state)
        return err("Memory Bank is empty. Store problems first.")

    state["mode"] = "memory_bank"
    state["mb_queue"] = list(state["mb_problems"])
    state["mb_right"] = 0
    state["mb_tried"] = 0
    state["mb_go_time"] = time.time()

    first = state["mb_queue"].pop(0)
    state["mb_pending"] = {**first, "attempt": 1}
    touch(state)
    save_state(state)

    return jsonify({
        "display": problem_display(first["op"], first["a"], first["b"]),
        "remaining": len(state["mb_queue"]) + 1,
    })


@memory_bank_bp.route("/answer", methods=["POST"])
def mb_submit_answer():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    pending = state.get("mb_pending")
    if not pending:
        touch(state)
        save_state(state)
        return err("Press GO to start Memory Bank playback.")

    data = request.get_json(force=True)
    user_answer = data.get("answer")

    op, a, b, attempt = pending["op"], pending["a"], pending["b"], pending["attempt"]
    result, remainder = compute(op, a, b)
    correct = (user_answer == result)

    response = {}

    def advance():
        """Move to next queued problem, or finish the run."""
        if state["mb_queue"]:
            nxt = state["mb_queue"].pop(0)
            state["mb_pending"] = {**nxt, "attempt": 1}
            response["next_display"] = problem_display(nxt["op"], nxt["a"], nxt["b"])
            response["remaining"] = len(state["mb_queue"]) + 1
        else:
            state["mb_pending"] = None
            ticks = int(time.time() - state["mb_go_time"]) if state["mb_go_time"] else 0
            response["run_complete"] = True
            response["score"] = {
                "right": state["mb_right"],
                "tried": state["mb_tried"],
                "ticks": ticks,
            }

    if correct:
        state["mb_right"] += 1
        state["mb_tried"] += 1
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
            state["mb_tried"] += 1
            response["display"] = reveal_display(op, a, b, result, remainder)
            response["correct"] = False
            response["try_again"] = False
            advance()

    touch(state)
    save_state(state)
    return jsonify(response)
