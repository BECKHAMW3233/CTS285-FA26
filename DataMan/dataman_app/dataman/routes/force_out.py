"""Force Out -- subtraction-to-zero strategy game (a NIM variant). See
dataman-manual.md, "Force Out (Operating Notes)"."""

import random

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..display import format_display
from ..config import OP_DISPLAY

force_out_bp = Blueprint("force_out", __name__, url_prefix="/api/force-out")


@force_out_bp.route("/select", methods=["POST"])
def fo_select():
    """Force Out starting number (documented conflict, Operating Notes
    win): the Story shows a fixed example, 37; the Operating Notes show
    63 and say it's "a different one each time". We randomize.

    JUDGMENT CALL: no numeric range is given for the random starting
    number (63 is only an example). We pick a two-digit range so the
    game takes a handful of turns and stays within the display's easy
    comfort zone.
    """
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True) or {}
    players = data.get("players")
    if players is None:
        players = ["Player 1", "Player 2"]
    if not isinstance(players, list) or len(players) < 2:
        return err("Force Out needs at least 2 players.")

    state["mode"] = "force_out"
    state["fo_players"] = list(players)
    state["fo_active_idx"] = 0
    state["fo_value"] = random.randint(20, 99)
    state["fo_game_over"] = False
    state["fo_loser"] = None
    touch(state)
    save_state(state)
    return jsonify({
        "display": format_display(f"{state['fo_value']} {OP_DISPLAY['-']} ="),
        "value": state["fo_value"],
        "active_player": state["fo_players"][state["fo_active_idx"]],
    })


@force_out_bp.route("/subtract", methods=["POST"])
def fo_subtract():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    if state["fo_value"] is None:
        return err("Select Force Out first.")
    if state["fo_game_over"]:
        return err("This round is over. Select Force Out to start a new one.")

    data = request.get_json(force=True)
    amount = data.get("amount")

    if not isinstance(amount, int) or not (1 <= amount <= 9):
        # "put in a number from 1 to 9. (I won't let you put in a zero!)"
        return err("Enter a number from 1 to 9 (0 is not accepted).")
    if amount > state["fo_value"]:
        # Not explicit in the manual for this activity, but Force Out is
        # a subtraction game on the same machine whose Answer Checker
        # (Operating Notes) explicitly "will not accept" a subtraction
        # that would go negative -- JUDGMENT CALL: we extend that same
        # rule here, since a negative Force Out total isn't a sensible
        # game state to begin with.
        return err("DataMan will not accept an operand that would make the answer negative.")

    active_player = state["fo_players"][state["fo_active_idx"]]
    state["fo_value"] -= amount

    response = {
        "value": state["fo_value"],
        "display": format_display(f"{state['fo_value']} {OP_DISPLAY['-']} ="),
    }

    if state["fo_value"] == 0:
        state["fo_game_over"] = True
        state["fo_loser"] = active_player
        response["game_over"] = True
        response["loser"] = active_player
    else:
        state["fo_active_idx"] = (state["fo_active_idx"] + 1) % len(state["fo_players"])
        response["active_player"] = state["fo_players"][state["fo_active_idx"]]

    touch(state)
    save_state(state)
    return jsonify(response)
