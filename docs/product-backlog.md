# DataMan Product Backlog

**Course:** CTS-285 | **Module:** 3 | **Source:** `docs/requirements.md` (Module 2 Requirements Register)

## Purpose

This backlog turns the validated Module 2 requirements into product work a team can understand, test, size, and prioritize. It introduces no new needs. Every item points back to a requirement ID and the evidence behind it. Items whose requirement still has an open question are marked **Not Ready** and are not committed work.

**Product-work chain:** Evidence → Need → Requirement → User Story → Acceptance Criteria → Priority

**Status key**
- **Draft**: story written and traceable; acceptance criteria, sizing, and priority still to come
- **Not Ready**: an open question in the requirements register must be resolved before this becomes committed work
- **Constraint**: a quality attribute that shapes the acceptance criteria of other stories rather than standing alone as a story

---

## Backlog Summary

| ID | Requirement | Story (short) | Status |
|----|-------------|---------------|--------|
| PB-01 | FR-01 | Know whether a submitted answer is correct | Draft |
| PB-02 | FR-02 | Practice problems and correct-response history are tracked | Draft |
| PB-03 | FR-03 | See current score | Draft |
| PB-04 | FR-04 | Resume practice where I left off | Not Ready |
| PB-05 | FR-05 | Parent/teacher visibility into practice and progress | Not Ready |
| n/a | NFR-01 to NFR-04 | Quality constraints on stories above | Constraint |

---

## Stories

### PB-01: Know whether my answer is correct

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-01 |
| **Evidence** | Evidence Note 1 (DataMan Manual, Answer Checker) |
| **Status** | Draft |

**Who receives the value?** The learner, a child practicing arithmetic.
**What outcome is needed?** To find out whether a submitted answer is correct.
**Why does it matter?** The learner can tell whether they understand the problem and decide what to do next.

**Story:**
> As a learner, I want to know whether the answer I submit to a math problem is correct so that I can tell if I understand it and decide what to do next.

**Why this story exists:** FR-01 requires answer submission with correctness feedback, grounded in the original Answer Checker behavior.

**Scope note:** The original Answer Checker also revealed the correct answer after repeated incorrect attempts (Evidence Note 1). Whether to preserve that retry/reveal flow is an unresolved Open Question, so it is deliberately excluded from PB-01 and is not yet in the backlog.

**Split check:** Submitting and receiving feedback are not independently valuable, so this stays one story.

**Constraints from NFRs:** NFR-01 (usable without a printed manual), NFR-04 (no adult assistance needed).

**Acceptance criteria:** *To be written.*

---

### PB-02: My practice history is tracked

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-02 |
| **Evidence** | Evidence Note 2 (DataMan Manual, Memory Bank) |
| **Status** | Draft |

**Who receives the value?** The learner.
**What outcome is needed?** The system keeps a record of the problems practiced and which answers were correct.
**Why does it matter?** Practice builds on itself, and the learner's results feed their score and, later, the progress visible to parents and teachers.

**Story:**
> As a learner, I want the problems I practice and my correct answers to be remembered so that my effort counts toward my progress instead of disappearing.

**Why this story exists:** FR-02 requires tracking practice problems and correct-response history, grounded in the original Memory Bank behavior.

**Dependencies:** PB-01 (correctness must exist before it can be tracked). PB-03 and PB-05 depend on this item.

**Open question touching this item:** The scope of "saved progress" (single problem, full history, or cumulative score) is unconfirmed. Tracking history within a session is supported by FR-02; persistence across sessions is governed by FR-04 (see PB-04).

**Acceptance criteria:** *To be written.*

---

### PB-03: See my current score

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-03 |
| **Evidence** | Evidence Note 2 (DataMan Manual, Memory Bank score display) |
| **Status** | Draft |

**Who receives the value?** The learner.
**What outcome is needed?** To see a current score based on tracked correct responses.
**Why does it matter?** The score shows the learner how they are doing and gives them a reason to keep practicing.

**Story:**
> As a learner, I want to see my current score so that I know how well I am doing and can see myself improve.

**Why this story exists:** FR-03 requires a current score based on tracked correct responses, grounded in the original Memory Bank score display.

**Dependencies:** PB-02 (score is calculated from tracked correct responses).

**Acceptance criteria:** *To be written.*

---

### PB-04: Resume my practice where I left off (NOT READY)

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-04 |
| **Evidence** | Evidence Note 3 (teacher-reported pause/return) and Evidence Note 6 (interrupted sessions, multiple devices) |
| **Status** | **Not Ready** |

**Who receives the value?** The learner (and the teacher, who expects practice state to remain available).
**What outcome is needed?** In-progress practice is preserved automatically, even after an unexpected session end or a switch to another device.
**Why does it matter?** The learner can continue without starting over.

**Story (provisional):**
> As a learner, I want my in-progress practice saved automatically so that I can pick up where I left off, even if my session ended unexpectedly or I switch devices.

**Why this story exists:** FR-04 was revised from "save on intentional exit" after Evidence Note 6 showed sessions may end abruptly and learners may change devices.

**Why it is not ready:** The scope of "saved progress" is an unresolved Open Question (a single in-progress problem, full practice history, or cumulative score). The story cannot be sized or given testable acceptance criteria until this is answered. The cross-device element also likely makes this a candidate for splitting once scope is confirmed: automatic preservation after an unexpected end, and continuity across devices are separable outcomes.

**To make ready:** Confirm the scope of saved progress with stakeholders, then decide whether to split by outcome.

**Dependencies:** PB-01, PB-02.

**Acceptance criteria:** *Blocked until scope is confirmed.*

---

### PB-05: Parents and teachers can see practice and progress (NOT READY)

| Field | Detail |
|-------|--------|
| **Requirement ID** | FR-05 |
| **Evidence** | Evidence Note 5 (parents and teachers want visibility; no format agreed) |
| **Status** | **Not Ready** |

**Who receives the value?** Parents and teachers (secondary users).
**What outcome is needed?** To understand what a learner practiced and whether progress is occurring.
**Why does it matter?** Adults can support the learner and tell whether practice is working.

**Story (provisional):**
> As a parent or teacher, I want to see what a learner has practiced and whether they are making progress so that I can support their learning.

**Why this story exists:** FR-05 confirms the underlying need for visibility; the delivery method is intentionally left unspecified.

**Why it is not ready:** No delivery format has been agreed (dashboard, printed report, or email summary), and stakeholders have not agreed on a reporting format. The story states the need without prescribing a solution, but it cannot be estimated or tested until the format question is resolved. Parents and teachers may also need separate stories if their needs differ.

**To make ready:** Agree a delivery format and confirm whether parent and teacher needs differ.

**Dependencies:** PB-02 (needs tracked history to report on).

**Acceptance criteria:** *Blocked until delivery format is agreed.*

---

## Non-Functional Requirements as Constraints

These are quality attributes. They are not written as standalone stories here because they apply across the backlog. They will be carried into the acceptance criteria of the stories they affect.

| Requirement | Constraint | Applies most directly to |
|-------------|------------|--------------------------|
| NFR-01 | Works reliably in a standard browser; usable without a printed manual | PB-01, PB-03 |
| NFR-02 | Minimal navigation to reach and complete a practice activity | PB-01, PB-03 |
| NFR-03 | Consistent behavior across Chromebooks, tablets, phones, and home computers | All stories; especially PB-04 |
| NFR-04 | A child can complete a core practice activity without adult help | PB-01, PB-03 |

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
                             ├──► PB-04 (resume practice)   [Not Ready]
                             └──► PB-05 (parent/teacher view) [Not Ready]
```

---

## Still To Do (later in Module 3)

- Write acceptance criteria for PB-01, PB-02, and PB-03
- Resolve or escalate the open questions blocking PB-04 and PB-05
- Estimate relative effort and note uncertainty
- Prioritize under the constraints given in the Product Owner Sprint Simulation and record the rationale
- Revise this backlog after the simulation using what you learn
