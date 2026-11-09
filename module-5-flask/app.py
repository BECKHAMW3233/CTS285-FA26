"""Flask interface layer: routes and request/response coordination only.

Run from this folder:
    python -m flask --app app run --debug --host=0.0.0.0

Each route loads the store, calls the business logic, and renders what the
logic returns. No correctness, try-number, or next-problem decision is made
here.
"""
from flask import Flask, render_template, request

from business_logic import AnswerChecker, check_answer, practice_view
from data_store import PLACEHOLDER_LEARNER_ID, get_store

app = Flask(__name__)
app.config["MAX_TRIES"] = 2  # same default as prototype/main.py (--tries 2)


def make_checker() -> AnswerChecker:
    return AnswerChecker(get_store(), max_tries=app.config["MAX_TRIES"])


@app.get("/")
def practice_page():
    view = practice_view(make_checker(), PLACEHOLDER_LEARNER_ID)
    return render_template("index.html", view=view)


@app.post("/")
def submit_answer():
    view = check_answer(make_checker(), PLACEHOLDER_LEARNER_ID,
                        request.form.get("answer", ""))
    return render_template("index.html", view=view)
