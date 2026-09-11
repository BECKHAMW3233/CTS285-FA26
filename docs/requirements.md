# DataMan Requirements Register

## Project Context

This project modernizes the 1977 Texas Instruments DataMan educational toy into a 2026 web-based application. The primary users are children practicing arithmetic (learners), with parents and teachers as secondary users who need visibility into learner activity and progress. The goal is to preserve DataMan's original self-paced, low-friction practice experience while meeting modern expectations for browser-based access, reliability, and use across multiple personal and school-owned devices.

## Evidence Notes

1. **[DataMan Manual]** The original Answer Checker accepts a math problem and answer, indicates whether the answer is correct, and reveals the correct answer after repeated incorrect attempts.
2. **[DataMan Manual]** The original Memory Bank stores practice problems, tracks correct responses, and displays a score.
3. **[Elicitation Simulation — Evidence 1]** Teachers report that students may pause practice and return later. They expect a learner's saved practice state to remain available after leaving and returning to the application.
4. **[Elicitation Simulation — Evidence 2]** Stakeholders define "modern" as working reliably in a browser, being understandable without a printed manual, and avoiding unnecessary navigation. They do not specify a visual style or technology.
5. **[Elicitation Simulation — Evidence 3]** Parents and teachers want to understand what a learner practiced and whether progress is occurring, but stakeholders have not agreed on a detailed reporting format.
6. **[Elicitation Simulation — Complication]** Students may use DataMan on school Chromebooks, phones, tablets, and home computers, and some sessions may be interrupted before the learner intentionally signs out.

## Functional Requirements

**FR-01:** The system must allow a learner to submit an answer to a math problem and receive correctness feedback.
*Source/Rationale:* Original DataMan Answer Checker behavior (Evidence Note 1).

**FR-02:** The system must track a learner's practice problems and correct-response history.
*Source/Rationale:* Original DataMan Memory Bank behavior (Evidence Note 2).

**FR-03:** The system must display a learner's current score based on tracked correct responses.
*Source/Rationale:* Original DataMan Memory Bank score-display behavior (Evidence Note 2).

**FR-04:** The system must automatically preserve a learner's in-progress practice state so it is available when the learner returns, even if the session ends unexpectedly or the learner switches to a different device.
*Source/Rationale:* Initially drafted from Evidence Note 3 (teacher-reported pause/return behavior); revised after the simulation complication (Evidence Note 6) revealed that sessions may end abruptly and learners may switch devices, so the original "save on intentional exit" wording was not sufficient.

**FR-05:** The system must provide parents and teachers a way to view what a learner has practiced and whether progress is occurring.
*Source/Rationale:* Evidence Note 5 confirms the underlying need for visibility into learner activity. The delivery method (e.g., dashboard, report, email) is intentionally left unspecified — see Open Questions.

## Non-Functional Requirements

**NFR-01:** The application must operate reliably in a standard web browser and be usable by a learner without a printed manual or external instructions.
*Source/Rationale:* Evidence Note 4 (stakeholder definition of "modern").

**NFR-02:** The application must minimize unnecessary navigation, requiring no more steps than needed for a learner to reach and complete a practice activity.
*Source/Rationale:* Evidence Note 4.

**NFR-03:** The application must function consistently across the range of devices learners are expected to use, including school-managed Chromebooks, tablets, phones, and home computers.
*Source/Rationale:* Evidence Note 6 (simulation complication).

**NFR-04:** The application must be usable by a child learner without requiring adult assistance to complete a core practice activity.
*Source/Rationale:* Original DataMan's intent to provide enjoyable, self-paced math practice for children (DataMan Manual context) combined with Evidence Note 4.

## Open Questions / Assumptions

- The exact scope of "saved progress" (a single in-progress problem, full practice history, or cumulative score) has not been confirmed.
- No delivery format for parent/teacher visibility into learner progress has been agreed on (e.g., dashboard, printed report, email summary) — Evidence Note 5 explicitly leaves this open.
- The stakeholder statement "keep it simple" was not directly investigated during the elicitation simulation and remains unclarified.
- Whether original DataMan behaviors such as the auto shut-off after inactivity or the three-attempt-before-reveal answer flow should be preserved as-is or redesigned for a web context has not been decided.
- Which original DataMan behaviors are considered essential to preserve has not been directly investigated.
- The nature, location, and cause of the staff data-entry errors raised in the "Too Many Errors" stakeholder concern have not yet been confirmed through interview, observation, or record review; no requirement has been drafted from this concern yet.
