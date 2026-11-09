# M5 Implementation Finding: PB-01 / PB-02 in Flask

**Slice:** PB-01 (FR-01) and PB-02 (FR-02). **Criterion carried forward:** PB-02 criterion 3.
**Evidence:** [`docs/evidence/m5-acceptance-test.md`](../evidence/m5-acceptance-test.md). **Code:** [`module-5-flask/`](../../module-5-flask/).

## Confirmed

The M4 decision holds in Flask: one attempt record per answer, the try number derived by the logic from stored attempts, and an interface that only displays.

- The unchanged M4 criteria tests pass against `business_logic.py` and `data_store.py` (7/7).
- In the running app, `56`, `50`, `54` gave history `#1 7 x 8 -> 56 (correct, try 1)`, `#2 9 x 6 -> 50 (incorrect, try 1)`, `#3 9 x 6 -> 54 (correct, try 2)` and `Entries: 3   Correct: 2`. **PB-02 criterion 3 passes**, through both curl and a real browser.
- `Try 2 of 2` and `The answer is 7.` came from `CheckResult`, not from the route.

## Forced to reconsider: the next-problem rule lived in the interface

**Classification: weak implementation choice (revised, commit `f3f85f0`).**

In `prototype/main.py`, the `for problem in store.list_problems()` loop decided which problem comes next. That is state held by the interface, which is what the M4 record said the interface must not keep. A Flask request has no loop to resume. So `AnswerChecker.current_problem()` and `problem_finished()` now derive the current problem from stored attempts, the same way `current_try_number()` does. The routes only call `practice_view()` and `check_answer()` and render the result.

## Exposed: the server cannot tell which problem the learner was looking at

**Classification: state/data problem caused by an unresolved source question (not fixed).**

In Scenario E, browser A showed `7 x 8 = ?` while browser B answered it. When A then submitted `56`, it was recorded as **`#2: 9 x 6 -> 56 (incorrect, try 1)`**. That is an answer charged to a problem the learner never saw, which **fails PB-02 criterion 1** ("recorded together with the problem it answered").

Two M4 choices combine to cause it:
1. `data_store.get_store()` holds one `InMemoryStore` for the whole process, under the placeholder `learner-1`, so every browser is the same learner.
2. The request carries only the answer, so the logic applies it to whatever problem is current on the server.

In the CLI, one terminal and one loop made the displayed problem and the current problem always the same. Over HTTP that assumption no longer holds. Because the server sets no cookie, the requests from A and B are identical. A second tab or the back button in one browser would therefore send the same request; I tested only the two-client case.

I did not fix it. The real fix depends on the identity/session approach, which the backlog lists as the unresolved dependency of PB-04a/b. Scenarios C and D (history emptied on restart and on a `--debug` reload) are the expected cost of keeping the store in memory until those items are Ready.

Also found and fixed: `parse_answer()` accepted `5_6` as 56, because `int()` allows underscores. That is a coding defect against the M4 "only plain 0-9" rule (commit `4ccbe5c`).

## Next action

Decide the identity/session approach for PB-04a/b. Until then, test this question in Module 6: should the form send the `problem_id` that was displayed, so `submit_answer()` (which already accepts a `problem_id`) records the answer against the problem the learner actually saw?

That raises the M4 open question about a round/session marker, because a stale submit would reopen a finished problem. Add a test for Scenario E in `module-5-flask/tests/`. It should fail until that decision is made.
