# M3 Product Owner Decision Record

## Scenario
StudyTrack release planning under constrained capacity.

## Round 1 — Capacity 13
- ST-01: Create a study task (3 pts)
- ST-02: Mark a study task complete (2 pts)
- ST-03: Recover a missed task (3 pts)
- ST-04: Keyboard-accessible task entry (2 pts)

**Why this release slice was defensible:**
I selected ST-01, ST-02, ST-03, and ST-04 for 10 of 13 points. All four are high value and ready, and they directly serve the release goal: planning study work (ST-01, ST-02), recovering from missed work (ST-03), and making task entry accessible (ST-04). Every dependency is satisfied within the slice, since ST-01 comes first. I kept 3 points unallocated as a buffer rather than filling them with the low-value ST-06, because more features aren't the goal and the buffer reduces release risk if capacity changes.

**One intentional deferral and why:**
I deferred ST-08, the Parent progress dashboard. It's Medium value, 5 points, marked "Needs refinement" because scope and privacy expectations are unsettled, and it depends on ST-05, which is also not in this release. It would carry the most rework risk, and it doesn't serve the goal of helping students plan and recover. It should wait until ST-05 exists and the privacy and scope questions are resolved.

## Complication
Capacity dropped from 13 to 10 points. Keyboard accessibility testing revealed that task entry cannot reliably be completed with keyboard navigation, so ST-04 became release-critical.

## Revised Release Slice — Capacity 10
- ST-01: Create a study task (3 pts)
- ST-02: Mark a study task complete (2 pts)
- ST-03: Recover a missed task (3 pts)
- ST-04: Keyboard-accessible task entry (2 pts)

### Removed after complication
- None

### Added after complication
- None

**What changed and why:**
The plan itself did not change. I keep ST-01, ST-02, ST-03, and ST-04 for exactly 10 of 10 points. The 3 points I left unallocated in Round 1 absorb the capacity drop from 13 to 10, so I did not need to remove any work. What changed is the status of ST-04: accessibility testing found that keyboard users cannot reliably complete task entry, so ST-04 is now a release blocker and must be completed and verified before release. I also sequenced ST-01 and ST-04 first, since the fix depends on the task-entry flow. Everything else stays deferred for the same reasons as before: ST-05 is medium value and no longer fits, ST-06 is cosmetic, and ST-07 and ST-08 still need refinement.

**Tradeoff accepted:**
I accepted zero remaining buffer. The release is at full capacity with no room for overruns, so any slip in ST-01, ST-03, or ST-04 puts the release date at risk. I also accepted that students get no progress visibility (ST-05) in this release, and that the Parent progress dashboard (ST-08) and AI recommendations (ST-07) wait for a later release. I chose this over cutting ST-04 or ST-03, because releasing task entry that keyboard users cannot complete would fail the accessibility requirement, and dropping recovery would remove half of the release goal. If the team falls behind, ST-02 is the first item to reconsider, since students can still plan and recover work without marking tasks complete, though I would treat that as a last resort.

## Transfer to DataMan
Before finalizing your DataMan backlog, review whether any item is high value but not ready, depends on unresolved work, consumes disproportionate effort, or should move because it reduces risk or unlocks other work.
