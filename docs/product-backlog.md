# DataMan Product Backlog

**Course:** CTS-285 | **Module:** 3 | **Source:** `docs/requirements.md` (Module 2 Requirements Register)

## Purpose

This backlog turns the validated Module 2 requirements into product work a team can understand, test, size, and prioritize. It introduces no new needs. Every item points back to a requirement ID and the evidence behind it. Items whose requirement still has an open question are marked **Not Ready** and are not committed work.

**Product-work chain:** Evidence → Need → Requirement → User Story → Acceptance Criteria → Priority

**Status key**
- **Ready**: traceable, acceptance criteria written, no unresolved requirement question blocking it
- **Not Ready**: an open question in the requirements register or an unresolved dependency must be settled before this becomes committed work
- **Constraint**: a quality attribute that shapes the acceptance criteria of other stories rather than standing alone as a story

**Relative effort key:** Small / Medium / Large. These are relative sizes, not hours. Estimates for Not Ready items are provisional and low confidence.

---

## Backlog Summary (in priority order)

| Priority | ID | Requirement | Story (short) | Value | Effort | Status |
|----------|----|-------------|---------------|-------|--------|--------|
| 1 | PB-01 | FR-01 | Know whether a submitted answer is correct | High | Small | Ready |
| 2 | PB-02 | FR-02 | Practice problems and correct-response history are tracked | High | Medium | Ready |
| 3 | PB-03 | FR-03 | See current score | Medium | Small | Ready |
| 4 | PB-04a | FR-04 | Practice state preserved after an unexpected session end | High | Medium | Not Ready |
| 5 | PB-04b | FR-04 | Practice continues on a different device | High | Large | Not Ready |
| 6 | PB-05 | FR-05 | Parent/teacher visibility into practice and progress | Medium | Medium | Not Ready |
| n/a | n/a | NFR-01 to NFR-04 | Quality constraints on stories above | n/a | n/a | Constraint |

**Priority rationale.** PB-01 to PB-03 are ready, trace to original DataMan behavior (Answer Checker, Memory Bank), and form one dependency chain, so they are the committable core. PB-04a and PB-04b are high value but blocked by an unconfirmed scope and an unresolved identity/session approach, so they rank below ready work. High value does not mean ready. PB-05 is medium value and blocked by an unagreed delivery format. If capacity were reduced, PB-03 is the first ready item to wait: tracking (PB-02) still works without a displayed score, and PB-03 is the lowest-value ready item.

---

## Stories

### PB-01: Know whether my answer is correct

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-01 |
| **Evidence** | Evidence Note 1 (DataMan Manual, Answer Checker) |
| **Status** | Ready |
| **Value / Effort** | High / Small |

**Who receives the value?** The learner, a child practicing arithmetic.
**What outcome is needed?** To find out whether a submitted answer is correct.
**Why does it matter?** The learner can tell whether they understand the problem and decide what to do next.

**Story:**
> As a learner, I want to know whether the answer I submit to a math problem is correct so that I can tell if I understand it and decide what to do next.

**Why this story exists:** FR-01 requires answer submission with correctness feedback, grounded in the original Answer Checker behavior.

**Scope note:** The original Answer Checker also revealed the correct answer after repeated incorrect attempts (Evidence Note 1). Whether to preserve that retry/reveal flow is an unresolved Open Question, so it is deliberately excluded from PB-01 and is not yet in the backlog.

**Split check:** Submitting and receiving feedback are not independently valuable, so this stays one story.

**Dependencies:** None. PB-02, PB-03, PB-04a/b depend on this item.

**Constraints from NFRs:** NFR-01, NFR-02, NFR-03, NFR-04 (each appears in the criteria below).

**Acceptance criteria:**
1. When a learner submits an answer to a displayed math problem, the system shows whether the answer is correct or incorrect.
2. The result is shown for every submitted answer, both correct and incorrect.
3. The learner sees the result without leaving the practice activity (NFR-02).
4. A first-time learner can open the application, submit an answer, and understand the result without a printed manual or external instructions (NFR-01) and without adult assistance (NFR-04). Verified by observing a tester acting as a first-time user.
5. Criteria 1 to 3 pass in a standard browser on a school Chromebook, a tablet, a phone, and a home computer (NFR-03).
6. Out of scope: revealing the correct answer and limiting or allowing retries (open question).

---

### PB-02: My practice history is tracked

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-02 |
| **Evidence** | Evidence Note 2 (DataMan Manual, Memory Bank) |
| **Status** | Ready |
| **Value / Effort** | High / Medium |

**Who receives the value?** The learner.
**What outcome is needed?** The system keeps a record of the problems practiced and which answers were correct.
**Why does it matter?** Practice builds on itself, and the learner's results feed their score and, later, the progress visible to parents and teachers.

**Story:**
> As a learner, I want the problems I practice and my correct answers to be remembered so that my effort counts toward my progress instead of disappearing.

**Why this story exists:** FR-02 requires tracking practice problems and correct-response history, grounded in the original Memory Bank behavior.

**Dependencies:** PB-01 (correctness must exist before it can be tracked). PB-03, PB-04a/b, and PB-05 depend on this item.

**Uncertainty:** The scope of "saved progress" (single problem, full history, or cumulative score) is unconfirmed. This story assumes tracking within a session, which FR-02 supports; persistence across sessions is governed by FR-04 (PB-04a/b). If stakeholders decide saved progress means full history, the storage approach for this story may need rework. That risk is the reason effort is Medium.

**Acceptance criteria:**
1. Each submitted answer is recorded together with the problem it answered and whether it was correct.
2. Both correct and incorrect answers are recorded, and only correct answers are counted as correct responses.
3. Test case: a learner submits three answers (two correct, one incorrect). The tracked history contains three entries, and exactly two are marked correct.
4. The history available in the current session matches the answers the learner submitted in that session.
5. Recording happens automatically, with no action required from the learner (NFR-04).
6. Behavior is consistent across the browsers and devices in NFR-03.
7. Out of scope: keeping the history after the session ends or on another device (PB-04a/b).

---

### PB-03: See my current score

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-03 |
| **Evidence** | Evidence Note 2 (DataMan Manual, Memory Bank score display) |
| **Status** | Ready |
| **Value / Effort** | Medium / Small |

**Who receives the value?** The learner.
**What outcome is needed?** To see a current score based on tracked correct responses.
**Why does it matter?** The score shows the learner how they are doing and gives them a reason to keep practicing.

**Story:**
> As a learner, I want to see my current score so that I know how well I am doing and can see myself improve.

**Why this story exists:** FR-03 requires a current score based on tracked correct responses, grounded in the original Memory Bank score display.

**Dependencies:** PB-02 (score is calculated from tracked correct responses).

**Uncertainty:** The requirements do not define a score formula. These criteria test only that the score derives from tracked correct responses, and no formula is assumed.

**Acceptance criteria:**
1. The learner can see a current score during practice.
2. The score is calculated from tracked correct responses only; an incorrect answer does not increase it.
3. Test case: after two correct answers and one incorrect answer, the displayed score reflects the two correct responses and not the incorrect one.
4. The score updates after a new correct answer is submitted, and the learner does not need to navigate away from practice to see it (NFR-02).
5. A first-time learner can find and understand the score without a printed manual (NFR-01) and without adult assistance (NFR-04).
6. Criteria 1 to 4 pass across the browsers and devices in NFR-03.

---

### PB-04a: My practice is saved if my session ends unexpectedly (NOT READY)

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-04 |
| **Evidence** | Evidence Note 3 (teacher-reported pause/return) and Evidence Note 6 (sessions may end before intentional sign-out) |
| **Status** | **Not Ready** |
| **Value / Effort** | High / Medium (provisional) |

**Who receives the value?** The learner (and the teacher, who expects practice state to remain available).
**What outcome is needed?** In-progress practice is preserved automatically, even when the session ends unexpectedly.
**Why does it matter?** The learner can continue without starting over.

**Story (provisional):**
> As a learner, I want my in-progress practice saved automatically so that I can pick up where I left off, even if my session ended unexpectedly.

**Why this story exists:** FR-04 was revised from "save on intentional exit" after Evidence Note 6 showed sessions may end abruptly. This story covers that outcome. Continuity across devices is split out as PB-04b because it is a separable outcome with a heavier dependency, and the triage record rated the combined preserve-progress work Large.

**Why it is not ready:**
- The scope of "saved progress" (single in-progress problem, full practice history, or cumulative score) is an unresolved Open Question, so the story cannot be given testable criteria.
- The identity/session approach for recognizing a returning learner is unresolved. The triage record identified this as the dependency that increased uncertainty for persistence work.

**To make ready:** Confirm the scope of saved progress with stakeholders, and resolve the identity/session approach.

**Dependencies:** PB-01, PB-02; unresolved identity/session approach.

**Acceptance criteria:** *Blocked until scope of saved progress is confirmed.*

---

### PB-04b: I can continue my practice on a different device (NOT READY)

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-04 |
| **Evidence** | Evidence Note 6 (learners may switch between Chromebooks, phones, tablets, and home computers) |
| **Status** | **Not Ready** |
| **Value / Effort** | High / Large (provisional) |

**Who receives the value?** The learner.
**What outcome is needed?** In-progress practice is available when the learner returns on a different device.
**Why does it matter?** Learners use school and home devices, and starting over on each one would waste their effort.

**Story (provisional):**
> As a learner, I want my in-progress practice available on whichever device I use next so that I can continue without starting over.

**Why this story exists:** FR-04 explicitly includes the case where the learner switches to a different device (Evidence Note 6).

**Why it is not ready:** It has the same scope question as PB-04a. In addition, continuing on a different device requires recognizing the same learner across devices, so it depends directly on the unresolved identity/session approach.

**To make ready:** Confirm the scope of saved progress, resolve the identity/session approach, then re-check size.

**Dependencies:** PB-04a, PB-02; unresolved identity/session approach.

**Acceptance criteria:** *Blocked until scope and identity/session approach are resolved.*

---

### PB-05: Parents and teachers can see practice and progress (NOT READY)

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-05 |
| **Evidence** | Evidence Note 5 (parents and teachers want visibility; no format agreed) |
| **Status** | **Not Ready** |
| **Value / Effort** | Medium / Medium (provisional) |

**Who receives the value?** Parents and teachers (secondary users).
**What outcome is needed?** To understand what a learner practiced and whether progress is occurring.
**Why does it matter?** Adults can support the learner and tell whether practice is working.

**Story (provisional):**
> As a parent or teacher, I want to see what a learner has practiced and whether they are making progress so that I can support their learning.

**Why this story exists:** FR-05 confirms the underlying need for visibility; the delivery method is intentionally left unspecified.

**Why it is not ready:** No delivery format has been agreed (dashboard, printed report, or email summary), and stakeholders have not agreed on a reporting format. The story cannot be estimated or tested until the format question is resolved. Parents and teachers may need separate stories if their needs differ; there is not yet evidence to split.

**To make ready:** Agree a delivery format and confirm whether parent and teacher needs differ.

**Dependencies:** PB-02 (needs tracked history to report on).

**Acceptance criteria:** *Blocked until delivery format is agreed.*

---

## Non-Functional Requirements as Constraints

These are quality attributes. They are not written as standalone stories because they apply across the backlog. They are carried into the acceptance criteria of the stories they affect (see PB-01 to PB-03), so a story that violates one fails its criteria.

| Requirement | Constraint | Applies most directly to |
|-------------|------------|--------------------------|
| NFR-01 | Works reliably in a standard browser; usable without a printed manual | PB-01, PB-03 |
| NFR-02 | Minimal navigation to reach and complete a practice activity | PB-01, PB-03 |
| NFR-03 | Consistent behavior across Chromebooks, tablets, phones, and home computers | All stories; especially PB-04b |
| NFR-04 | A child can complete a core practice activity without adult help | PB-01, PB-02, PB-03 |

---

## Items Not Yet in the Backlog

These are unresolved in the requirements register. No story has been drafted, because none should become committed work without supporting evidence.

| Item | Why it is not a story |
|------|------------------------|
| Retry and reveal-after-repeated-incorrect-attempts (original three-attempt flow) | Whether to preserve or redesign it has not been decided |
| Auto shut-off after inactivity | Preserve vs. redesign for the web has not been decided |
| "Too Many Errors" staff data-entry concern | Not confirmed through interview, observation, or record review; no requirement drafted |
| Which original DataMan behaviors are essential to preserve | Not directly investigated |
| "Keep it simple" | Not investigated during elicitation; remains unclarified |

---

## Dependencies at a Glance

```
PB-01 (feedback) ──► PB-02 (history tracked) ──► PB-03 (score)
                             │
                             ├──► PB-04a (save after unexpected end) ──► PB-04b (continue on another device)
                             │         [Not Ready]                         [Not Ready]
                             │              ▲                                   ▲
                             │              └─── identity/session approach (unresolved) ───┘
                             │
                             └──► PB-05 (parent/teacher view) [Not Ready]
```

---

## Review Log (Module 3 backlog review)

**Confirmed, no change:** Requirement ID traceability for all items; user/value statements; PB-05 not split (no evidence yet that parent and teacher needs differ); "Items Not Yet in the Backlog."

**Revised:**
- Wrote acceptance criteria for PB-01 to PB-03 and carried NFR-01 to NFR-04 into them.
- Split PB-04 into PB-04a and PB-04b, both tracing to FR-04, because the outcomes are separable and the cross-device outcome carries the heavier dependency (triage record rated the preserve-progress work Large).
- Recorded the identity/session approach as an unresolved dependency on PB-04a and PB-04b (from the M3 triage record).
- Added value, relative effort, uncertainty, and priority order with rationale.
- Recorded the stated assumption and rework risk on PB-02, and the undefined score formula on PB-03.

**Next actions to unblock committed work:**
- Confirm the scope of saved progress with stakeholders (unblocks PB-04a, PB-04b, and settles the PB-02 assumption).
- Resolve the identity/session approach (unblocks PB-04a, PB-04b).
- Agree a delivery format for parent/teacher visibility and whether their needs differ (unblocks PB-05).
