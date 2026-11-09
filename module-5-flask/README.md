# Module 5: Minimal Flask App (PB-01 / PB-02)

The Module 4 text-only prototype ([`../prototype/`](../prototype/)) moved into Flask. This folder is the project root, and all commands run from here.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m flask --app app run --debug --host=0.0.0.0
```

Open port 5000. Records are in memory only, so restarting the server clears them.

| File | Responsibility | Comes from |
|---|---|---|
| `app.py` | Flask routes `GET /` and `POST /`: build the checker, call the logic, render | Replaces `prototype/main.py` |
| `business_logic.py` | Parse answer, correct/incorrect, try number, attempt record, retry/reveal, next problem, feedback text. No Flask imports. | `prototype/logic.py` |
| `data_store.py` | State boundary: `Problem`/`Attempt` records in one `InMemoryStore` per server process, via `get_store()` | `prototype/data_stub.py` |
| `templates/index.html` | Prints `view.message`, the current problem, and the history the logic returns | — |

- **Acceptance evidence (PB-02 criterion 3):** [`../docs/evidence/m5-acceptance-test.md`](../docs/evidence/m5-acceptance-test.md)
- **Finding:** [`../docs/decisions/m5-implementation-finding.md`](../docs/decisions/m5-implementation-finding.md)
