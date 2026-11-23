# Module 5: Flask App (PB-01 / PB-02, extended with PB-03)

The Module 4 text-only prototype ([`../prototype/`](../prototype/)) moved into Flask, then extended with one connected story: **PB-03 "See my current score"** (FR-03). This folder is the project root, and all commands run from here.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v          # 29 tests
python -m flask --app app run --debug --host=0.0.0.0
```

Open port 5000. Records are in memory only, so restarting the server clears the history and the score.

| File | Responsibility | Comes from |
|---|---|---|
| `app.py` | Flask routes `GET /` and `POST /`: build the checker, pass form fields (`answer`, `problem_id`) to the logic, render | Replaces `prototype/main.py` |
| `business_logic.py` | Parse answer, correct/incorrect, try number, attempt record, retry/reveal, next problem, feedback text, **score (PB-03)**, **stale-page refusal**. No Flask imports. | `prototype/logic.py` |
| `data_store.py` | State boundary: `Problem`/`Attempt` records in one `InMemoryStore` per server process, via `get_store()`. Unchanged by PB-03: the score is derived, not stored. | `prototype/data_stub.py` |
| `templates/index.html` | Prints the score, `view.message`, the current problem (with a hidden `problem_id`), and the history the logic returns | — |
| `tests/` | `test_m4_criteria.py` and `test_flask_baseline.py` are the change-impact baseline (committed before PB-03). `test_pb03_score.py` and `test_flask_pb03.py` are feature tests. `test_scenario_e_stale_page.py` retests the known stale-page defect. | — |

## Module 5 extension: PB-03

- **Brief, written before coding:** [`../docs/design/m5-pb03-feature-brief.md`](../docs/design/m5-pb03-feature-brief.md)
- **Feature and change-impact evidence:** [`../docs/evidence/m5-pb03-score-test.md`](../docs/evidence/m5-pb03-score-test.md)
- **Implementation decision:** [`../docs/decisions/m5-pb03-implementation-decision.md`](../docs/decisions/m5-pb03-implementation-decision.md)

## Module 5 minimal app: PB-01 / PB-02

- **Acceptance evidence (PB-02 criterion 3):** [`../docs/evidence/m5-acceptance-test.md`](../docs/evidence/m5-acceptance-test.md)
- **Finding:** [`../docs/decisions/m5-implementation-finding.md`](../docs/decisions/m5-implementation-finding.md)
