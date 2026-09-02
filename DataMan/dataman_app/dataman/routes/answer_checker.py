"""Answer Checker -- DataMan's default mode on power-up. See
dataman-manual.md, "Answer Checker (Operating Notes)"."""

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..mathutil import compute, validate_digits, invalid_problem_message
from ..display import problem_display, reveal_display, FLASH_DISPLAY
from ..config import PROBLEMS_PER_ROUND

answer_checker_bp = Blueprint("answer_checker", __name__, url_prefix="/api/answer-checker")


@answer_checker_bp.route("/problem", methods=["POST"])
def ac_new_problem():
    """User enters a problem, e.g. {"op": "+", "a": 9, "b": 4}."""
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True)
    op = data.get("op")
    a = data.get("a")
    b = data.get("b")

    try:
        validate_digits(a, b)
        # Try the computation now purely to validate negative-subtraction
        # rejection at entry time, matching "the display would show 7 -.
        # It would not accept the 8."
        compute(op, a, b)
    except ValueError as e:
        touch(state)
        save_state(state)
        return err(invalid_problem_message(e))

    state["mode"] = "answer_checker"
    state["ac_pending"] = {"op": op, "a": a, "b": b, "attempt": 1}
    touch(state)
    save_state(state)

    return jsonify({"display": problem_display(op, a, b), "attempt": 1})


@answer_checker_bp.route("/answer", methods=["POST"])
def ac_submit_answer():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    pending = state.get("ac_pending")
    if not pending:
        touch(state)
        save_state(state)
        return err("No problem entered yet.")

    data = request.get_json(force=True)
    user_answer = data.get("answer")

    op, a, b, attempt = pending["op"], pending["a"], pending["b"], pending["attempt"]
    result, remainder = compute(op, a, b)

    correct = (user_answer == result)

    response = {}

    if correct:
        state["ac_right"] += 1
        state["ac_tried"] += 1
        state["ac_pending"] = None
        response["display"] = FLASH_DISPLAY
        response["correct"] = True
        if remainder is not None:
            response["remainder"] = remainder
        response["round_complete"] = (state["ac_tried"] % PROBLEMS_PER_ROUND == 0)
        if response["round_complete"]:
            response["score"] = {"right": state["ac_right"], "tried": state["ac_tried"]}
    else:
        if attempt == 1:
            pending["attempt"] = 2
            response["display"] = "EEE"
            response["correct"] = False
            response["attempt"] = 2
            response["try_again"] = True
        else:
            state["ac_tried"] += 1
            state["ac_pending"] = None
            response["display"] = reveal_display(op, a, b, result, remainder)
            response["correct"] = False
            response["try_again"] = False
            response["round_complete"] = (state["ac_tried"] % PROBLEMS_PER_ROUND == 0)
            if response["round_complete"]:
                response["score"] = {"right": state["ac_right"], "tried": state["ac_tried"]}

    touch(state)
    save_state(state)
    return jsonify(response)


@answer_checker_bp.route("/score", methods=["GET"])
def ac_score():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()
    return jsonify({"right": state["ac_right"], "tried": state["ac_tried"]})
