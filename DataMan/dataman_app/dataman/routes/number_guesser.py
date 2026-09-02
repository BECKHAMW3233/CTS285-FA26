"""Number Guesser -- guess-the-secret-number with between-two-bounds
hints. See dataman-manual.md, "Number Guesser (Operating Notes)"."""

import random

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err

number_guesser_bp = Blueprint("number_guesser", __name__, url_prefix="/api/number-guesser")


@number_guesser_bp.route("/new", methods=["POST"])
def ng_new():
    """Pick a new secret number and reset the bounding hints.

    Range: the manual (Story and Operating Notes) both say only "a
    secret number between 9 and 100" -- it never states whether 9 and
    100 themselves are eligible. JUDGMENT CALL: we read "between 9 and
    100" as *exclusive* fenceposts, i.e. the secret is drawn from
    10-99. Reasons: (1) 9 and 100 are also literally the two numbers
    DataMan shows as the very first hint bounds, which only makes sense
    if they're outer fenceposts the secret can never equal; (2) 10-99 is
    exactly "all two-digit numbers", consistent with the rest of
    DataMan's number system (operands elsewhere are always 1-2 digits);
    (3) it gives a clean round total of 90 possible secrets. The
    alternative inclusive reading (9-100) is not unreasonable -- flagging
    it here rather than presenting this as manual-stated fact.
    """
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    state["mode"] = "number_guesser"
    state["ng_secret"] = random.randint(10, 99)
    state["ng_lower"] = 9
    state["ng_upper"] = 100
    state["ng_guesses"] = 0
    touch(state)
    save_state(state)
    return jsonify({"lower": state["ng_lower"], "upper": state["ng_upper"], "guesses": 0})


@number_guesser_bp.route("/guess", methods=["POST"])
def ng_guess():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    if state["ng_secret"] is None:
        touch(state)
        save_state(state)
        return err("Press Number Guesser to pick a secret number first.")

    data = request.get_json(force=True)
    guess = data.get("guess")
    if not isinstance(guess, int):
        return err("Guess must be a whole number.")

    state["ng_guesses"] += 1

    response = {"guesses": state["ng_guesses"]}

    if guess == state["ng_secret"]:
        response["correct"] = True
        state["ng_secret"] = None
    else:
        response["correct"] = False
        if guess < state["ng_secret"]:
            state["ng_lower"] = max(state["ng_lower"], guess)
        else:
            state["ng_upper"] = min(state["ng_upper"], guess)
        response["lower"] = state["ng_lower"]
        response["upper"] = state["ng_upper"]

    touch(state)
    save_state(state)
    return jsonify(response)
