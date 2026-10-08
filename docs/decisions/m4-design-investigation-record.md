# M4 Design Investigation Record

## Product Slice
PB-01 (Know whether my answer is correct, FR-01) and PB-02 (My practice history is tracked, FR-02). PB-03 is a downstream dependency and is not part of this investigation.

## Initial Question
What must a recorded answer contain (learner, problem, submitted answer, correct or incorrect, and possibly an attempt number), and which layer is responsible for recording it? The goal is that session-only tracking works now without a redesign if retry/reveal or persistent history is confirmed later.

## Planned Evidence
A field/state table, and an acceptance-criteria trace of each field against PB-01 and PB-02.

## Evidence Actually Used
- Use-case boundary / actor-goal framing
- Behavior/state flow and two-attempt simulation
- Data-model/schema and Memory Bank constraint stress tests
- Interface/wireframe comparison and state audit
- Design complication and critique

## Findings
### Use-Case Boundary / Question Framing
Learner → check an answer and have that attempt count toward their practice history. Question: What must be recorded about each attempt (problem, submitted answer, correct or incorrect, and possibly an attempt number), and which layer owns recording it, so this works now with session-only tracking and survives a later retry/reveal or persistence decision without a redesign?

### Behavior / State
The behavior depends on knowing the try number, so the record can’t just be correct/incorrect. It answered that an attempt number is needed if the two-try flow is kept. It sharpened a new question: the same number also drives the reveal decision, so I have to decide whether recording the attempt and deciding what happens next are one responsibility or two. The Studio used two tries, but my register leaves retry/reveal as an open question, so I’m treating the field as supported for now, not the two-try rule.

### Data / Persistence
A screen showed me feedback for one attempt. The ERD showed that history needs one record per attempt, connected to both the learner and the problem, and that a single final answer on Problem can’t tell a first try from a second.

### Memory Bank Constraint
The limit has to be a rule with a defined outcome, not just a disabled button. If only the interface enforced it, a Flask version or another caller could add an eleventh. It also reinforced that rules like this belong in the logic layer.

**Constraint boundary selected:** both

### Interaction
Comparing the three paths showed that a live-only score panel can’t support any later review, and a stored session summary keeps the score but loses which problems were missed and how many tries they took. Only the learner history → session → problem attempts path keeps the try history, because it treats each attempt as its own record. That clarified my question: the record for one answer has to hold the try number and be separate from any summary, or later reporting can’t be built from it. It did not change my scope. Curator and parent/teacher review traces to PB-05, which is Not Ready because no delivery format is agreed, so I’m using this evidence to shape the record structure for PB-01 and PB-02, not to commit to building retrieval now.

## Layer Boundary Notes
**Business behavior that should remain outside the interface:**
The correctness decision, the try-number tracking, the rule for when a reveal is allowed, and recording the attempt. The text interface should only collect the answer and display the result (EEE, retry prompt, reveal). If those rules stayed in the interface, a Flask version would have to rewrite them.

**Data that can be stubbed now:**
Attempt and Problem records held in memory, behind a small recording interface, with a placeholder learner identity. Swapping in persistent storage later should not change the logic or interface. The identity approach is still unresolved in my backlog, so the stub should not assume one.

## New Complication
**Response:** Revise state boundary

I revised the state boundary because my own register already says sessions can end before intentional sign-out (Evidence Note 6, FR-04), and closing after Try 1 is that case. If try state lives only in the interface, the first miss disappears, and a later resume or report can’t tell a fresh problem from one that was already missed. The behavior round (try number drives reveal), the data round (Attempt as its own record), and the interface audit (the screen’s “Try 2 of 2” depends on state that vanishes on close) all point to the same fix: the logic layer owns the attempt record and try number, and the interface only displays them. This is not a decision to build persistence. Scope of saved progress and the identity/session approach are still unresolved, so cross-session resume stays in PB-04a/b. For now the record can sit in memory behind a clean boundary.

## Build-Readiness Decision
**Disposition:** Revise

**Design decision:**
Revise. PB-01 and PB-02 can go forward with one correction made first: each answer is recorded as its own attempt record (learner, problem, submitted answer, correct or incorrect, try number), and the logic layer owns recording and the try number. The interface only displays them. For the minimal prototype, records are held in memory behind a clear boundary so persistent storage can be added later without changing the logic or interface.

## Revision From Initial Thinking
I started with the question of what a recorded answer must contain and which layer owns it. The evidence changed the answer in two ways. First, I planned a field table and trace and expected an ERD to add little because there’s one main record. The Studio showed several relationships, and that Attempt must be separate from any summary. Second, the interface audit and the closed-after-Try-1 complication showed that the try number can’t live in the interface, because it disappears on close. The attempt number moved from “possibly needed” to required for the record.

## Tradeoff Accepted
Records live in memory for now, so nothing survives a closed session. I’m accepting that because persistence and cross-device continuity belong to PB-04a/b, which are Not Ready. In return I get a record structure and layer boundary that persistence can be added behind without rework.

## Unresolved Uncertainty
The scope of “saved progress” (single problem, full history, or score) is still unconfirmed, as is the identity/session approach. Whether retry and reveal are kept, and how many tries, is also undecided, so the two-try flow in the Studio is a test case, not a requirement. Who may see a learner’s history (the curator question) is a stakeholder decision tied to PB-05.

## Next Question
What does the stakeholder mean by “saved progress,” and which identity/session approach will be used? That answer decides whether the attempt record stays in memory or must be persisted, and whether an attempt record needs to be tied to a learner identity beyond a placeholder.

## Three-Layer Prototype Bridge
ext interface: Collects the learner’s answer and displays what the logic layer returns: correct/incorrect feedback (text plus symbol, not color alone), the current try, and any retry or reveal. It holds no try count of its own.

Business logic: Decides correct or incorrect, assigns and tracks the try number, creates the attempt record, and enforces the reveal gate and the 10-problem limit. The retry/reveal rule is configurable, because it is still an open question in my register.

Stubbed data layer: In-memory Problem, Attempt and Practice Set records (with the set-to-problem relationship) behind replaceable access functions. The learner identity is a placeholder, so persistent storage and the identity/session approach can be added later without changing the logic or interface.

## Trace Back to Product Work
PB-02 uncertainty note and criterion 7. Criterion 7 pushes persistence to PB-04a/b, and the scope of “saved progress” is unconfirmed.
PB-01 criterion 6. Retry and reveal are out of scope as an open question, even though Evidence Note 1 says the original Answer Checker revealed the answer after repeated misses.
Requirements: FR-01, FR-02, and the FR-04 open question.
