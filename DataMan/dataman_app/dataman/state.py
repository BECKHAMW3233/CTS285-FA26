"""The single global per-session DataMan state dict, the Power Saver
idle check, and the shared power-gate/error-response helpers every
route uses.

Design premise that is NOT up for revisiting: this models one physical
DataMan unit, held by one user, exactly as it worked as a physical
product -- single global session state, no accounts, no websocket
multiplayer. Wipe Out and Force Out are "multiplayer" only in the sense
that a physical unit is handed between people using the same session,
same as the manual describes.
"""

import time
from flask import session, jsonify

from .config import IDLE_TIMEOUT_SECONDS


def fresh_state():
    return {
        "power": False,
        "mode": None,
        "last_active": time.time(),
        # Answer Checker round state
        "ac_right": 0,
        "ac_tried": 0,
        "ac_pending": None,  # {"op": .., "a": .., "b": .., "attempt": 1}
        # Memory Bank state
        "mb_problems": [],
        "mb_queue": [],
        "mb_right": 0,
        "mb_tried": 0,
        "mb_pending": None,
        "mb_go_time": None,
        # Electro Flash state
        "ef_digit": None,       # the single 0-9 digit key pressed
        "ef_op": None,
        "ef_digit_first": None,  # True if digit key was pressed before the op key
        "ef_queue": [],
        "ef_pending": None,
        "ef_right": 0,
        "ef_tried": 0,
        "ef_go_time": None,
        # Number Guesser state
        "ng_secret": None,
        "ng_lower": None,
        "ng_upper": None,
        "ng_guesses": 0,
        # Wipe Out state
        "wo_players": [],
        "wo_remaining": [],
        "wo_active_idx": 0,
        "wo_pending": None,
        "wo_wipeout_time": None,
        "wo_go_time": None,
        "wo_can_pass": False,
        # Force Out state
        "fo_players": [],
        "fo_active_idx": 0,
        "fo_value": None,
        "fo_game_over": False,
        "fo_loser": None,
        # Missing Number state
        "mn_box": None,     # None until [?] pressed once; then "right"/"left"/"middle"
        "mn_op": None,
        "mn_level": 1,
        "mn_queue": [],
        "mn_pending": None,  # includes the full (op,a,b,result,box) plus attempt
        "mn_right": 0,
        "mn_tried": 0,
        "mn_go_time": None,
    }


def get_state():
    if "dm" not in session:
        session["dm"] = fresh_state()
    return session["dm"]


def save_state(state):
    session["dm"] = state
    session.modified = True


def check_power_saver(state):
    """Auto-off if idle too long. Returns True if it just powered off."""
    if state["power"] and (time.time() - state["last_active"]) > IDLE_TIMEOUT_SECONDS:
        state.update(fresh_state())
        state["power"] = False
        return True
    return False


def touch(state):
    state["last_active"] = time.time()


def require_power(state):
    return state["power"]


def power_ok(state):
    """True if the unit is on and wasn't just idle-timed-out. If this
    returns False the caller must still save_state(state) (the idle
    check may have reset it) and respond with powered_off_response()."""
    if check_power_saver(state):
        return False
    return require_power(state)


def powered_off_response():
    return jsonify({"error": "DataMan is off. Press ON first."}), 400


def err(msg, code=400):
    return jsonify({"error": msg}), code


# Power Saver edge case (physical fidelity task): the real unit's 5-minute
# auto-off runs on its own clock regardless of whether anyone is looking at
# it. Here, the idle check only runs when the next API call arrives, so an
# abandoned session can sit "on" in server-side session storage indefinitely
# between calls. JUDGMENT CALL: left as-is, on purpose. This is a
# single-process demo app with no background scheduler, no persistent store,
# and per-browser-session state that costs nothing to leave sitting idle
# (a few dict fields in a signed cookie-backed session, not a held
# resource like a socket or a battery). A real device drains a real 9V
# battery while "on" and idle, which is *why* it needs to actively cut its
# own power; a Flask session has no equivalent resource being consumed by
# sitting idle, so there's nothing to protect against. Adding an
# APScheduler-style sweep job to proactively flip stale sessions to "off"
# in storage would add real complexity (a background thread/process, plus
# all the state-store implications that come with it) to fix a distinction
# users can't observe anyway, since the next request through this session
# is guaranteed to see the idle check and behave exactly as if it had been
# powered off promptly.
