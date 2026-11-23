# M5 Implementation Decision: PB-03 "See my current score"

**Story:** PB-03 (FR-03), the next Ready item after PB-01 and PB-02. Its source is the DataMan Manual, *Memory Bank (Story)*: "your score … number of right answers · number of problems you tried".
**Criterion tested:** PB-03 #3: "after two correct answers and one incorrect answer, the displayed score reflects the two correct responses and not the incorrect one." #1, #2 and #4 were also tested.
**Brief (written before coding):** [`m5-pb03-feature-brief.md`](../design/m5-pb03-feature-brief.md). **Evidence:** [`m5-pb03-score-test.md`](../evidence/m5-pb03-score-test.md). **Code:** [`module-5-flask/`](../../module-5-flask/).

## Question → evidence → decision

**Question.** Can a second product behavior sit on the PB-02 slice without new state, and without the score drifting away from the history?

**Evidence and decision.** It can. The score is derived from the existing Attempt records each time it is shown, and it is never stored. In the app, `56`, `50`, `54` gave `Score: 2 right out of 2 tried` beside the same three-entry history. **PB-03 #3 passes** through the test client and in Chromium at desktop and phone widths.

## What changed in each responsibility

| Layer | Change |
|---|---|
| **Flask** (`app.py`) | No new route. A `/score` page would break PB-03 #4 and NFR-02, which say there is no navigating away. `POST /` now passes the form's `problem_id` to the logic (the revision below). It still decides nothing. |
| **Business logic** (`business_logic.py`) | New `Score` and `AnswerChecker.score()`: distinct problems right / distinct problems finished. `practice_view()` carries `score_text` and the Memory Bank final score. `check_answer()` refuses an answer from a stale page. |
| **State / data** (`data_store.py`) | **Unchanged.** The score is read from Attempt records, as M4 recommended: a stored summary "loses which problems were missed". The score has the same lifetime as the history (in memory). |
| **Template** | Shows the score above the problem and sends a hidden `problem_id`. |

## Test result that mattered: the score made an old defect visible

The score rule passed on the first run. The more useful result came from retesting the open M5 defect, Scenario E. With two tabs open, a correct `56` for `7 x 8` sent from the stale tab was recorded as a `9 x 6` miss, and the learner was told "Not quite". The learner's first real miss on `9 x 6` then counted as try 2, so the answer was revealed and the score fell to `1 right out of 2 tried`.

Before PB-03 this was a wrong history line. After PB-03 it is a lost retry and a lower number shown to the learner. The extension did not create the defect, but it raised its cost.

- **Classification: state/data problem, plus a design decision that needed revision.** Score arithmetic was correct for the records it was given. The records were wrong because the request did not say which problem the learner saw.
- The M5 finding expected the fix to wait for the identity/session approach. **The evidence revised that.** In Chromium, double-click (1 POST) and the back button (page re-requested) did *not* trigger it. Only a second view of the same learner did, and refusing a stale answer requires no identity at all.

## Keep / revise / defer / next question

- **Kept:** the score rule. It counts per problem, a try-2 correct counts (Memory Bank: "two tries to get it right"), and a pending retry is not counted as tried, so a try-1 miss never shows a point as lost. A logic test showed correct *attempts* can exceed problems right, so counting problems was the right unit.
- **Revised:** the form sends the `problem_id` it showed, and `check_answer()` records nothing if that problem is finished (commit `12f714a`; it was a failing test first in `d1a59d1`). It refuses rather than records against the old problem, so a finished problem is never reopened and the M4 round-marker question is avoided. M5 Scenario E now passes, and so do PB-02 #1 and PB-01 for that case.
- **Deferred:**
  - A request without `problem_id` keeps the old behavior so the existing contract and baseline tests hold. Only the browser form is protected.
  - Learner identity is still the placeholder: two different children on two devices still share one history and one score (PB-04a/b).
  - The score resets on a server restart. Whether "saved progress" includes a cumulative score is the register's open question.
- **Next question:** PB-03 #5 (understood without help) is untested. The page shows `Score: 2 right out of 3 tried` and `Entries: 4 Correct: 2`, two counts in different units. Does a first-time learner read them as a contradiction? Test the page with a learner before relabelling the PB-02 totals, because the PB-02 criterion 3 evidence relies on them.
