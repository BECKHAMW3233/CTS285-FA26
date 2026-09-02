"""
DataMan (1977, Texas Instruments) -- Flask reimplementation.

Behavior is modeled on "Part II -- For Parents and Teachers" (the
Operating Notes), the reference/adult register of the manual, per the
analyst's note distinguishing it from the child-facing Story register.
Wherever the two registers actually contradict each other, the Operating
Notes win. Wherever the Operating Notes are merely silent (not
contradictory) about something the Story documents, the Story's version
is kept. See ../dataman-manual.md's own analyst's note for the checklist
of known conflicts this package resolves.

Physical-fidelity notes (see ../RESEARCH.md):
- The real unit's display was an 8-character VFD (Itron FG105H1). Every
  display string in this app is run through display.format_display() to
  enforce that width.
- The real keypad had no text on its activity keys -- symbols only.
  routes/core.py's /api/keypad exposes the symbol layout so the frontend
  can render real keys instead of English option labels.

Design premise that is NOT up for revisiting: this models one physical
DataMan unit, held by one user, exactly as it worked as a physical
product -- single global session state, no accounts, no websocket
multiplayer. See state.py.

Package layout:
    config.py          shared constants
    mathutil.py         DataMan's arithmetic rules (compute, validation)
    display.py           the 8-char VFD display-string helpers
    state.py              the shared per-session state dict and power gate
    logging_utils.py       developer-only file logging (never shown in the UI)
    routes/               one blueprint per activity
"""

import os

from flask import Flask

from .logging_utils import register_logging
from .routes.core import core_bp
from .routes.answer_checker import answer_checker_bp
from .routes.memory_bank import memory_bank_bp
from .routes.electro_flash import electro_flash_bp
from .routes.number_guesser import number_guesser_bp
from .routes.wipe_out import wipe_out_bp
from .routes.force_out import force_out_bp
from .routes.missing_number import missing_number_bp

_PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_PACKAGE_DIR)
_TEMPLATE_DIR = os.path.join(_PROJECT_ROOT, "templates")


def create_app():
    app = Flask(__name__, template_folder=_TEMPLATE_DIR)
    app.secret_key = "dataman-1977-lcb-3051"  # dev only

    register_logging(app)

    app.register_blueprint(core_bp)
    app.register_blueprint(answer_checker_bp)
    app.register_blueprint(memory_bank_bp)
    app.register_blueprint(electro_flash_bp)
    app.register_blueprint(number_guesser_bp)
    app.register_blueprint(wipe_out_bp)
    app.register_blueprint(force_out_bp)
    app.register_blueprint(missing_number_bp)

    return app
