# M4 Investigation Brief

## Product Slice
PB-01: Know whether my answer is correct (FR-01), and PB-02: My practice history is tracked (FR-02). PB-03 is a downstream dependency and not part of this investigation.

## Trace to Product Work
PB-02's stated uncertainty and criterion 7. PB-02 assumes tracking within a session, but the scope of "saved progress" is unconfirmed, and criterion 7 pushes persistence to PB-04a/b. PB-01 criterion 6 also leaves retry and reveal out of scope as an open question, even though Evidence Note 1 shows the original Answer Checker revealed the answer after repeated misses. If either decision changes, the design for these two stories could need rework.

## Initial Design Question
**Question type:** Data / State

What must a recorded answer contain (learner, problem, submitted answer, correct or incorrect, and possibly an attempt number), and which layer is responsible for recording it, so that session-only tracking works now without a redesign if retry/reveal or persistent history is later confirmed?

## Why This Question Matters
PB-02 assumes tracking within a session, but the scope of "saved progress" is unconfirmed, and FR-04 (PB-04a/b) will need persistence later. If I code history as in-session state with no clear record structure, then adding persistence or a retry/reveal flow (an open question in PB-01) could force changes to the logic, the interface, and the stored structure together. A record that can't hold an attempt number would have to be reshaped later. A recording rule living in the interface would have to be rewritten for each new interface. Settling the record contents and the layer boundary first keeps those changes contained.

## Planned Evidence
- Field or state table
- Acceptance-criteria trace

## Why This Evidence Is a Reasonable Starting Point
My question is what a recorded answer must contain and which layer owns recording it. A field or state table is the lightest way to list what the record needs, including whether an attempt number is required. Tracing each field to the PB-01 and PB-02 acceptance criteria shows whether PB-01's feedback result gives PB-02 everything it needs, and which fields exist only for the open retry/reveal and persistence questions. An ERD would add little because there is one main record. Once the field list is in place, I expect to test the layer boundary with a small prototype in the studio.

## Studio Check
During the DataMan Design Studio, record whether the evidence actually answered the question, whether you needed different evidence, and what new question emerged.
