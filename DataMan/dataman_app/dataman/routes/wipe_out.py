"""Wipe Out -- hot-potato multiplayer game against a hidden random
timer. Modeled as one shared session passed between players in turn
(see the fixed single-unit design premise in state.py). See
dataman-manual.md, "Wipe Out (Operating Notes)"."""

import random
import time

from flask import Blueprint, jsonify, request

from ..state import get_state, save_state, touch, power_ok, powered_off_response, err
from ..mathutil import compute
from ..display import problem_display, reveal_display, FLASH_DISPLAY

wipe_out_bp = Blueprint("wipe_out", __name__, url_prefix="/api/wipe-out")


def _wo_new_problem():
    """Wipe Out (Operating Notes): "DataMan pops up randomly selected
    ADDITION problems" -- unlike the other timed activities, Wipe Out is
    addition-only."""
    a = random.randint(0, 99)
    b = random.randint(0, 99)
    return {"op": "+", "a": a, "b": b}


def _wo_start_round(state):
    """Pick the hidden countdown and serve the first problem of a round.

    "The time it takes to wipe out is selected at random by DataMan when
    the GO key is pressed, and is known only to him." JUDGMENT CALL: no
    numeric range is given anywhere in the manual, so we pick a
    real-seconds window that's long enough for a few problems to get
    answered but short enough to keep a demo round moving.
    """
    hidden_seconds = random.randint(10, 45)
    state["wo_wipeout_time"] = time.time() + hidden_seconds
    state["wo_go_time"] = time.time()
    state["wo_can_pass"] = False
    problem = _wo_new_problem()
    state["wo_pending"] = {**problem, "attempt": 1}
    return problem


@wipe_out_bp.route("/select", methods=["POST"])
def wo_select():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    data = request.get_json(force=True) or {}
    players = data.get("players")
    if players is None:
        players = ["Player 1", "Player 2"]
    if not isinstance(players, list) or len(players) < 2:
        return err("Wipe Out needs at least 2 players.")

    state["mode"] = "wipe_out"
    state["wo_players"] = list(players)
    state["wo_remaining"] = list(players)
    state["wo_active_idx"] = 0
    state["wo_pending"] = None
    state["wo_can_pass"] = False
    touch(state)
    save_state(state)
    return jsonify({"players": state["wo_remaining"]})


@wipe_out_bp.route("/go", methods=["POST"])
def wo_go():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()
    if not state["wo_remaining"]:
        return err("Select Wipe Out players first.")

    problem = _wo_start_round(state)
    touch(state)
    save_state(state)
    return jsonify({
        "display": problem_display(problem["op"], problem["a"], problem["b"]),
        "active_player": state["wo_remaining"][state["wo_active_idx"]],
    })


@wipe_out_bp.route("/answer", methods=["POST"])
def wo_submit_answer():
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    pending = state.get("wo_pending")
    if not pending:
        touch(state)
        save_state(state)
        return err("Press GO to start Wipe Out.")

    active_player = state["wo_remaining"][state["wo_active_idx"]]

    # Only DataMan knows when the hidden timer runs out; check it before
    # even looking at the answer, since the player holding the unit when
    # it fires is out regardless of what they were about to type.
    if time.time() >= state["wo_wipeout_time"]:
        state["wo_remaining"].pop(state["wo_active_idx"])
        state["wo_pending"] = None
        state["wo_can_pass"] = False
        response = {"wipe_out": True, "eliminated": active_player,
                    "remaining": list(state["wo_remaining"])}
        if len(state["wo_remaining"]) <= 1:
            response["game_over"] = True
            response["winner"] = state["wo_remaining"][0] if state["wo_remaining"] else None
        else:
            # "Play continues until only one final winner is left" --
            # the survivors keep going, so we roll straight into a new
            # hidden countdown for them.
            state["wo_active_idx"] = state["wo_active_idx"] % len(state["wo_remaining"])
            next_problem = _wo_start_round(state)
            response["next_display"] = problem_display(next_problem["op"], next_problem["a"], next_problem["b"])
            response["active_player"] = state["wo_remaining"][state["wo_active_idx"]]
        touch(state)
        save_state(state)
        return jsonify(response)

    data = request.get_json(force=True)
    user_answer = data.get("answer")
    op, a, b, attempt = pending["op"], pending["a"], pending["b"], pending["attempt"]
    result, _rem = compute(op, a, b)
    correct = (user_answer == result)

    response = {"active_player": active_player}

    if correct:
        response["display"] = FLASH_DISPLAY
        response["correct"] = True
        state["wo_can_pass"] = True
        response["can_pass"] = True
    else:
        if attempt == 1:
            pending["attempt"] = 2
            response["display"] = "EEE"
            response["correct"] = False
            response["try_again"] = True
        else:
            # Story: "If you miss the problem twice, I'll answer the
            # problem for you. You need to work the next problem before
            # you pass me on." -- reveal, then immediately serve a fresh
            # makeup problem to the SAME player; they can't pass until
            # they clear it.
            response["display"] = reveal_display(op, a, b, result, None)
            response["correct"] = False
            response["try_again"] = False
            makeup = _wo_new_problem()
            state["wo_pending"] = {**makeup, "attempt": 1}
            state["wo_can_pass"] = False
            response["makeup_display"] = problem_display(makeup["op"], makeup["a"], makeup["b"])
            response["can_pass"] = False

    touch(state)
    save_state(state)
    return jsonify(response)


@wipe_out_bp.route("/pass", methods=["POST"])
def wo_pass():
    """The current player hands the unit to the next player."""
    state = get_state()
    if not power_ok(state):
        save_state(state)
        return powered_off_response()

    if not state["wo_can_pass"]:
        return err("Current player must answer correctly before passing.")

    state["wo_active_idx"] = (state["wo_active_idx"] + 1) % len(state["wo_remaining"])
    problem = _wo_new_problem()
    state["wo_pending"] = {**problem, "attempt": 1}
    state["wo_can_pass"] = False
    touch(state)
    save_state(state)
    return jsonify({
        "display": problem_display(problem["op"], problem["a"], problem["b"]),
        "active_player": state["wo_remaining"][state["wo_active_idx"]],
    })
