"""Developer-only activity log written to a file on disk, never
rendered anywhere in the page. Captures every request DataMan's API
receives (every key press that reached the server: problems, answers,
ON/OFF, activity selection) and every response, including validation
errors that return normal 400s and never crash anything. Purely
client-side events that never hit the server on their own (a raw digit
typed into an unsubmitted field, a UI panel switch, an uncaught JS
error) are reported by the frontend to /api/client-log (see
routes/core.py) and land in the same file. Rotated at 1MB so it doesn't
grow unbounded across a long dev session.
"""

import os
import json
import logging
from logging.handlers import RotatingFileHandler
from flask import request

# dataman_app/dataman.log -- this file lives at dataman_app/dataman/logging_utils.py,
# so two directories up is the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(PROJECT_ROOT, "dataman.log")

dataman_logger = logging.getLogger("dataman")
dataman_logger.setLevel(logging.DEBUG)
if not dataman_logger.handlers:
    # Guarded so re-calling create_app() in the same process (tests, an
    # interactive shell) doesn't attach a second handler and duplicate
    # every log line -- logging.getLogger("dataman") is a process-wide
    # singleton keyed by name.
    _log_handler = RotatingFileHandler(LOG_PATH, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    _log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    dataman_logger.addHandler(_log_handler)
    dataman_logger.propagate = False  # don't also spam Flask's own console output


def sanitize_log_text(s, max_len=2000):
    """Strip newlines so a malicious/weird value can't forge extra log
    lines, and cap length so one bad request can't balloon the file."""
    return str(s).replace("\n", " ").replace("\r", " ")[:max_len]


def register_logging(app):
    """Attach before/after_request hooks that log every request/response
    that hits any route in the app. Call once from create_app()."""

    @app.before_request
    def _log_request():
        if request.path == "/api/client-log":
            return  # that route logs itself, with its own CLIENT framing
        body = ""
        if request.method == "POST":
            parsed = request.get_json(silent=True)
            if parsed is not None:
                body = json.dumps(parsed)
        dataman_logger.info("REQUEST  %s %s %s", request.method, request.path, sanitize_log_text(body))

    @app.after_request
    def _log_response(response):
        if request.path == "/api/client-log":
            return response
        payload = response.get_data(as_text=True) if response.is_json else "<non-json>"
        level = logging.INFO
        if response.status_code >= 400:
            level = logging.WARNING
        else:
            try:
                if json.loads(payload).get("error"):
                    level = logging.WARNING
            except (ValueError, AttributeError):
                pass
        dataman_logger.log(level, "RESPONSE %s %s -> %s %s",
                            request.method, request.path, response.status_code, sanitize_log_text(payload))
        return response
