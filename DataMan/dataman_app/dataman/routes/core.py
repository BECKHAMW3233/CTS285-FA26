"""Core/shared routes: the page itself, the keypad layout, power
on/off, and the developer-only client-log sink."""

from flask import Blueprint, jsonify, request, render_template

from ..state import fresh_state, save_state, touch
from ..display import format_display
from ..logging_utils import dataman_logger, sanitize_log_text

core_bp = Blueprint("core", __name__)


@core_bp.route("/")
def index():
    return render_template("index.html")


@core_bp.route("/api/keypad", methods=["GET"])
def keypad():
    """The real DataMan keypad: 24 keys, gray robot case, orange keys.
    Only the digit/operator/GO/=/ON/OFF keys carry text or familiar
    math symbols; the six activity keys (Electro Flash, Missing Number,
    Wipe Out, Number Guesser, Force Out, Memory Bank) carry only the
    abstract symbols shown on the unit -- no English words anywhere on
    the physical case. Layout and symbols per the keypad illustration
    description in dataman-manual.md, in the Force Out (Story) section.
    """
    rows = [
        [
            {"key": "electro_flash", "symbol": "⚡", "kind": "activity"},
            {"key": "missing_number", "symbol": "?", "kind": "activity"},
            {"key": "off", "symbol": "OFF", "kind": "power"},
            {"key": "on", "symbol": "ON", "kind": "power"},
        ],
        [
            {"key": "wipe_out", "symbol": "✳", "kind": "activity"},
            {"key": "number_guesser", "symbol": "???", "kind": "activity"},
            {"key": "force_out", "symbol": "↗", "kind": "activity"},
            {"key": "div", "symbol": "÷", "kind": "op", "value": "/"},
        ],
        [
            {"key": "7", "symbol": "7", "kind": "digit", "value": 7},
            {"key": "8", "symbol": "8", "kind": "digit", "value": 8},
            {"key": "9", "symbol": "9", "kind": "digit", "value": 9},
            {"key": "mul", "symbol": "×", "kind": "op", "value": "*"},
        ],
        [
            {"key": "4", "symbol": "4", "kind": "digit", "value": 4},
            {"key": "5", "symbol": "5", "kind": "digit", "value": 5},
            {"key": "6", "symbol": "6", "kind": "digit", "value": 6},
            {"key": "sub", "symbol": "−", "kind": "op", "value": "-"},
        ],
        [
            {"key": "1", "symbol": "1", "kind": "digit", "value": 1},
            {"key": "2", "symbol": "2", "kind": "digit", "value": 2},
            {"key": "3", "symbol": "3", "kind": "digit", "value": 3},
            {"key": "add", "symbol": "+", "kind": "op", "value": "+"},
        ],
        [
            {"key": "go", "symbol": "GO", "kind": "control"},
            {"key": "0", "symbol": "0", "kind": "digit", "value": 0},
            {"key": "memory_bank", "symbol": "⊜", "kind": "activity"},
            {"key": "equals", "symbol": "=", "kind": "control"},
        ],
    ]
    return jsonify({"rows": rows})


@core_bp.route("/api/on", methods=["POST"])
def turn_on():
    state = fresh_state()
    state["power"] = True
    state["mode"] = "answer_checker"
    touch(state)
    save_state(state)
    return jsonify({"display": format_display("="), "mode": "answer_checker", "power": True})


@core_bp.route("/api/off", methods=["POST"])
def turn_off():
    state = fresh_state()
    state["power"] = False
    save_state(state)
    return jsonify({"display": "", "power": False})


@core_bp.route("/api/client-log", methods=["POST"])
def client_log():
    """Sink for client-side-only events (see logging_utils.py's module
    docstring). Deliberately not power-gated and doesn't touch session
    state -- it should work even if the rest of the app is confused,
    since its whole point is capturing what happened for debugging."""
    data = request.get_json(silent=True) or {}
    is_error = data.get("level") == "error"
    message = sanitize_log_text(data.get("message", ""))
    log_fn = dataman_logger.warning if is_error else dataman_logger.info
    log_fn("CLIENT   %s", message)
    return jsonify({"logged": True})
