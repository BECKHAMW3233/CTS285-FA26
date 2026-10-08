# DataMan Text-Only Prototype (Module 4)

Tests the design decision from `docs/decisions/m4-design-investigation-record.md`:
each answer is its own attempt record with a try number, the logic layer owns recording
and the try number, and the interface only displays results.

**Slice:** PB-01 (know whether my answer is correct, FR-01) and PB-02 (my practice history is tracked, FR-02).

## Run it

Requires Python 3. From this folder:

```
python main.py              # two tries before reveal (the Design Studio test case)
python main.py --tries 3    # original three-attempt flow (still an open question)
python -m unittest test_criteria -v
```

## Where things are

| Layer | File | Responsibility |
|---|---|---|
| Text interface (entry point) | `main.py` | Reads input, prints output. Keeps no try counter and makes no correctness decisions. |
| Business logic | `logic.py` | Parses answers, decides correct/incorrect, assigns the try number, creates the attempt record, decides retry vs reveal. No printing, no input, no storage details. |
| Stubbed data | `data_stub.py` | In-memory Problem and Attempt records behind access methods. Replaceable. |
| Evidence | `test_criteria.py` | Demonstrates acceptance criteria against the logic layer without the interface. |

Design record: [docs/decisions/m4-design-investigation-record.md](https://github.com/BECKHAMW3233/CTS285-FA26/blob/main/docs/decisions/m4-design-investigation-record.md)

## Acceptance criteria demonstrated

- **PB-02 criterion 3:** three submitted answers (two correct, one incorrect) give three history entries, exactly two marked correct. (`test_pb02_criterion_3_three_answers_two_correct`, and visible in the history printed by `main.py`.)
- **PB-01 criteria 1 and 2:** every submitted answer gets a correct or incorrect result.
- **Design question:** the first and second miss are different records, and the answer is only revealed after the last allowed miss. A new checker built over the same store still knows it is try 2, so try state does not live in the interface.

## Intentionally stubbed

- Storage is in memory only. Closing `main.py` loses everything. The test above shows the boundary holds when a new checker reuses a store, but this program cannot resume across runs. That belongs to PB-04a/b.
- Learner identity is the placeholder `learner-1`. The identity/session approach is unresolved.
- No score display (PB-03), no parent/teacher view (PB-05).
- No Practice Set and no 10-problem limit. Those came from the Design Studio scenario, not from PB-01/PB-02 or the requirements register, so they were left out of the slice.

## Unresolved uncertainty

- Scope of "saved progress" (single problem, full history, or score) is unconfirmed.
- Whether retry/reveal is kept, and after how many tries. `max_tries` is a setting for this reason; two is only the Studio's test case.
- Who may see a learner's history (curator access) is a stakeholder question tied to PB-05.

## What running the prototype showed

These come from running the code and tests, not from the earlier design work alone.

- **Confirmed:** keeping the try number out of the interface works. `main.py` prints "Try N of M" from the result the logic returns, and the logic derives the try number from stored attempts.
- **Exposed: the Attempt record has no round marker.** The try number only makes sense within one "round" on a problem, and I had to infer where a round ends (after a correct answer or after the reveal) by scanning earlier attempts. That works here, but if the same problem is asked again later, or history is persisted across sessions, the record may need an explicit round or session id. I did not add one, because the scope of saved progress is still open.
- **Decision made while building:** invalid input (for example "abc") is rejected and not recorded, so it never counts as an attempt or advances the try number. The register doesn't say how to treat it, so this is my assumption.

## Next implementation question

What does "saved progress" cover, and which identity/session approach will be used? That decides whether the attempt record needs a round or session id and whether `InMemoryStore` is replaced by persistent storage for Module 5.
