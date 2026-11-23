# M5 Extension Brief: PB-03 "See my current score"

Written before any PB-03 code. It records the evidence that defines the feature, so the test results can be judged against it.

## Why this story

PB-03 is the next **Ready** item in backlog priority order. It depends only on PB-02, which the M5 Flask app already implements and tests. The other candidates are blocked: PB-04a/b by the identity/session approach and PB-05 by the delivery format (see [`product-backlog.md`](../product-backlog.md)). PB-03 is also Small, so it can be tested end to end.

## Evidence that defines the feature

| Item | Evidence |
|---|---|
| **Requirement** | **FR-03:** "The system must display a learner's current score based on tracked correct responses." ([`requirements.md`](../requirements.md)) |
| **Story** | **PB-03:** "As a learner, I want to see my current score so that I know how well I am doing and can see myself improve." |
| **Source behavior** | DataMan Manual, *Memory Bank (Story)*: "I'll take a problem from my memory and give you two tries to get it right. When you've tried all of the problems, I'll show you your score like this: [number of right answers] · [number of problems you tried]." *Answer Checker* shows the same two-number score (for example `9 10`). |
| **Acceptance criteria under test** | **PB-03 #1** score visible during practice. **#2** calculated from tracked correct responses only; an incorrect answer does not increase it. **#3** *test case:* after two correct answers and one incorrect answer, the score reflects the two correct responses and not the incorrect one. **#4** updates after a new correct answer, with no navigation away from practice (NFR-02). |
| **Criteria checked by inspection only** | **#5** (first-time learner understands it without a manual or an adult: NFR-01, NFR-04) needs a real child. **#6** (all NFR-03 devices) needs the devices. I can run one desktop browser and a phone-sized viewport. That is partial evidence, not a pass. |

## Existing logic to reuse

- `AnswerChecker.history()` / `data_store.attempts_for_learner()`: the tracked attempts PB-02 already records. FR-03 says the score is *based on* these.
- `AnswerChecker.problem_finished()`: already decides when a problem is done (correct, or revealed after the last allowed try).
- `practice_view()`: already assembles everything the page shows. The score can travel in the same view dict.

## Planned change by layer

| Layer | Planned change |
|---|---|
| **Flask (`app.py`)** | **No new route.** NFR-02 and criterion 4 say that the score must update without leaving practice. A separate `/score` page would break that. `GET /` and `POST /` already render whatever `practice_view()` returns. |
| **Template** | Show the score in its own labelled element on the practice page, as text and not color alone. |
| **Business logic** | Add a score rule, `AnswerChecker.score()`, that returns *problems right* and *problems tried*, derived from stored attempts. Add it to `practice_view()`. When every problem is finished, say so and show the final score. That is the Memory Bank behavior. It also closes the A2 gap from the M5 test (a re-POST after the end showed no message). |
| **State / data** | **No new stored field.** The score is computed from Attempt records and is never saved as its own number. That follows the M4 interaction finding: a stored summary "keeps the score but loses which problems were missed". It also means the score cannot drift away from the history. |

## Score rule (my reading of the evidence, to be tested)

- **Problems right:** distinct problems that have a correct attempt. A correct answer on try 2 counts. The Memory Bank gives "two tries to get it right".
- **Problems tried:** distinct problems that are *finished*, meaning answered correctly or revealed.
- An incorrect attempt never adds to *right* (criterion 2).

## Uncertainty I expect to test

**Does a problem count as "tried" while a retry is still pending?** The Memory Bank shows the score only at the end, so it never has to answer this. PB-03 #1 asks for a score *during* practice, so I do. If a pending problem counts, a try-1 miss shows `1 of 2` and then becomes `2 of 2` after a correct retry. The learner would see a point "lost" that they can still earn. I plan to count only finished problems and to test both sequences to see what the learner actually sees.

**Second question:** the existing `Correct:` total counts correct *attempts*, and the score counts correct *problems*. Can they ever differ? If they can, the page shows two different "correct" numbers.

## Known risk carried in

The M5 finding (Scenario E) showed that a stale page records an answer against a problem the learner never saw. A learner-visible score built on those records could inherit the defect. I will retest Scenario E after the change.

## Persistence dependency

The score lives as long as the in-memory attempts and resets on a server restart. Keeping a score across sessions belongs to PB-04a/b, and "saved progress might mean cumulative score" is an open question in the register. I am not adding storage for it.
