# Prompt for Claude Code

Paste everything below the line into Claude Code, run from inside this
project's directory (the one containing `app.py`, `README.md`,
`RESEARCH.md`, `dataman-manual.md`, `requirements.txt`, and
`templates/index.html`).

---

## Read these first, in this order

1. `RESEARCH.md` — independently-sourced background on the real 1977
   Texas Instruments DataMan hardware and product history. Every claim in
   it is cited; some claims from different sources conflict with each
   other and are left unresolved on purpose. Don't treat anything in here
   as a spec for the app's *rules* — it's hardware/product history, not
   game logic.
2. `dataman-manual.md` — the actual source material for game logic. This
   is a transcript of the original TI manual. It has two internal
   registers: Part I ("The Story") narrates each feature to a child;
   Part II ("For Parents and Teachers" / "Operating Notes") describes the
   same features to an adult in reference language. **They disagree with
   each other in several places.** The manual's own analyst's note at the
   very end of the file lists the known disagreements explicitly — read
   that section before touching any game logic. Where I've already made a
   call about which register wins, I've said so below; otherwise, treat
   an unresolved conflict as something to ask me about, not something to
   silently pick a side on.
3. `README.md` — describes what `app.py` currently implements (Answer
   Checker and Memory Bank only) and explicitly lists what it does not
   implement yet.
4. `app.py` and `templates/index.html` — the current state of the app.

## The one design premise that is fixed — do not change this

This app models **one physical DataMan unit, held by one user, exactly as
it worked as a physical product**: single global session state, no user
accounts, no concurrent multiplayer synchronization, one problem visible
at a time, same as a kid holding one calculator. This was confirmed
explicitly and is not up for revisiting. If a task below seems to invite
a multi-user or networked redesign (e.g. Wipe Out and Force Out are
described in the manual as being played by passing one physical unit
between people), implement it the way the manual describes it being used
physically — one shared display/state that players take turns
interacting with via the same session — not as separate accounts or
websocket-synced multiplayer.

## Rule for resolving Story-vs-Operating-Notes conflicts

Wherever the two registers actually contradict each other, **the
Operating Notes win**, since that's the adult/reference register — this
is the rule already applied in the existing Answer Checker and Memory
Bank code, and you should keep applying it.

This is different from a case where the Operating Notes are simply
*silent* about something the Story describes. Silence is not a conflict.
Where the Story documents a rule and the Operating Notes just don't
mention it one way or the other, include the Story's version — don't
drop a documented rule just because only one register states it.

The manual's analyst's note lists the specific known conflicts. Use it as
your checklist rather than re-deriving conflicts from scratch.

## Task: implement the remaining keypad activities

Add these, each as its own group of Flask routes, following the same
pattern as the existing Answer Checker/Memory Bank code in `app.py`:
JSON in/out, state stored in the single global session dict, a
power-saver idle check at the top of every route.

Work from `dataman-manual.md`'s actual text for each activity — its exact
numbers, ranges, and sequences — rather than inferring rules from the
activity's name or from general knowledge of similar toys.

- **Electro Flash** — a timed drill through one arithmetic table (e.g.
  "the 5 times table"). Look up the manual's stated key-press sequence
  and exactly what the Story vs. Operating Notes say about whether
  press-order of the number key and operator key matters — this is one of
  the documented conflicts, so apply the Operating-Notes-wins rule here.
  Also implement the stated problem-generation exclusions (no
  negative-result subtraction problems, no division problems with a
  remainder) by filtering the generated problem set, not by rejecting
  after the fact.

- **Number Guesser** — secret number chosen in the manual's stated range;
  check the manual's exact wording for whether the bounds are inclusive.
  Each guess returns two bounding numbers the secret is between. Track
  and report guess count on success.

- **Wipe Out** — modeled as one shared session being passed between
  players in sequence (see the fixed design premise above — don't build
  multi-user sync for this). A hidden random countdown ends the round;
  the manual doesn't give a numeric range for it, so pick something
  reasonable and say in a comment that it's a judgment call, not a
  manual-sourced number. Implement the Story's stated miss-handling
  (DataMan answers the problem after two misses) since the Operating
  Notes are silent, not contradictory, on this point.

- **Force Out** — subtraction-to-zero game. This is one of the documented
  conflicts (Story shows a fixed example starting number; Operating Notes
  say DataMan picks a different random number each time and describe it
  as a general subtraction strategy game). Apply Operating-Notes-wins:
  random starting number each time. Reject a 0 entry the same way the
  existing Answer Checker code rejects invalid entries.

- **Missing Number ("Box") Problems** — this is the manual's clearest
  internal contradiction: the Story's prose says the blank travels
  "left to right," but the Operating Notes describe (and the Story's own
  worked examples independently confirm) a right → left → middle cycle.
  Implement the right→left→middle cycle — note in a comment that this is
  a case where the Story's own examples override its own prose, which is
  a narrower and more specific situation than the general
  Operating-Notes-wins rule, so it's worth documenting separately.
  Implement both difficulty levels described in the manual (this is a
  Story-only detail the Operating Notes are silent about, not
  contradicted by — include it per the silence rule above).

For each activity, use the same right-answer / `EEE`-then-reveal pattern
already in the codebase, and check each activity's own section of the
manual for its specific score-field shape (some report two fields, some
three including elapsed ticks) rather than assuming they all match
Answer Checker.

## Task: physical fidelity pass

Use `RESEARCH.md` for the hardware facts driving these:

- **8-digit display truncation.** The real unit's display was 8
  characters (VFD, part number Itron FG105H1, per `RESEARCH.md` §2). Add
  a shared `format_display()` helper enforcing an 8-character width and
  run every existing and new display string through it. The manual
  doesn't specify what happens to a score readout that doesn't fit —
  decide something reasonable and say so in a comment.

- **Unlabeled game keys.** The real keypad had no text on the
  activity keys — symbols only. Add a `/api/keypad` endpoint returning the
  symbol-only layout (pull the exact symbols from the manual's keypad
  illustration description — search `dataman-manual.md` for the keypad
  layout description near the Force Out section), and update
  `templates/index.html` to render buttons from that layout instead of
  the current hardcoded English option labels.

- **Power Saver edge case.** The idle-timeout check currently only runs
  when the next API call comes in, so an abandoned session can sit
  "on" in stored state indefinitely between calls. Decide whether this
  matters for a single-process demo app and either leave it with a
  comment explaining why it's fine, or fix it — make the reasoning
  explicit either way.

## Constraints

- Don't change the existing Answer Checker or Memory Bank behavior unless
  you find an actual bug in it.
- Keep the bare-functional style: JSON API plus minimal HTML, no CSS
  framework, no build step, no database.
- Anywhere the manual is silent and you have to make a judgment call, say
  so in a code comment — don't present a guess as if it came from the
  manual.
- Update `README.md`'s "what this app does not implement yet" section to
  reflect what you've added, and leave `RESEARCH.md` alone — it's a
  separate research document, not app documentation.
