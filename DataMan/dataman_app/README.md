# DataMan (Flask reimplementation)

A Flask reimplementation of Texas Instruments' 1977 educational toy
calculator, **DataMan**: Answer Checker, Memory Bank, Electro Flash,
Number Guesser, Wipe Out, Force Out, and Missing Number ("Box")
Problems. Behavior is modeled on the "For Parents and Teachers"
(Operating Notes) section of the original manual, *The Story of
DataMan*, wherever it conflicts with the child-facing Story section.

This folder (`dataman_app/`) holds the runnable program. The source
material it was built from -- the manual transcript, the independent
hardware/product research, and the original Claude Code prompt -- lives
one level up, in the project root (`../dataman-manual (1).md`,
`../RESEARCH.md`, `../CLAUDE_CODE_PROMPT.md`).

---

## The real product

**What it was.** DataMan was an electronic learning toy released by Texas
Instruments on June 5, 1977, aimed at kids age 7 and up. It shipped with a
booklet, *The Story of DataMan*, that taught a child how to use it through
a space-adventure narrative (DataMan the robot vs. the evil wizard
AntiMath), plus a separate reference section for parents and teachers.

**Hardware** (see `../RESEARCH.md` for full sourcing):
- Gray plastic case styled as a robot, with 24 orange keys of differing
  shapes: 10 digit keys, 4 arithmetic operator keys, an equals key, a
  Memory Bank key, ON/OFF keys, and 5 unlabeled game-activity keys
  (symbols only -- no text on the keys themselves).
- 8-digit vacuum fluorescent display (VFD), Itron FG105H1.
- Single 9-volt battery; the TMC1982 chip (TMS1000-family) has an
  integrated charge-pump driver, contra an earlier, lower-confidence
  claim about a bare unregulated feed -- see `../RESEARCH.md` §2 for the
  correction and the sourcing conflict behind it.
- Auto-off after about 5 minutes of no key presses (the manual calls this
  the "Power Saver Feature").

**Activities documented in the manual:**
| Activity | What it does |
|---|---|
| Answer Checker | Default mode on power-up. You type a problem and your answer; DataMan confirms right/wrong. |
| Memory Bank | Store up to 10 problems (by anyone -- parent, teacher, friend); play them back later with `GO`. |
| Electro Flash | Timed drill through a full times/plus/minus/divide table. |
| Number Guesser | Guess-the-secret-number with between-two-bounds hints. |
| Wipe Out | Hot-potato multiplayer game against a hidden random timer. |
| Force Out | Two-or-more-player subtract-to-zero strategy game (a NIM variant). |
| Missing Number ("Box") Problems | Fill-in-the-blank problems, blank position selectable, two difficulty levels. |
| Starmath Race, Orbit Math, First Out, Space Ball, Astro Race, Antimath Maze | Story-book-only games/boards built on top of the above activities; **no corresponding operating instructions exist** for these anywhere in the manual, so they are out of scope for this app. |

**Sources used for this project:**
- *The Story of DataMan* (TI, 1977, LCB #3051) -- full transcript,
  `../dataman-manual (1).md`, scan courtesy of the Datamath Calculator
  Museum (Joerg Woerner).
- `../RESEARCH.md` -- independently-sourced hardware/product history
  (Smithsonian NMAH object record, Datamath Museum, Wikipedia, etc.).
  Used only for physical-fidelity details (display width, keypad
  layout); it is not treated as a source for game *rules*.

---

## A manual with two voices -- and where they disagree

The manual documents DataMan twice: **Part I ("The Story")** narrates each
feature to a child in DataMan's own voice, and **Part II ("For Parents and
Teachers")** describes the same features to an adult in operational,
reference language. They don't fully agree with each other. This project
treats **Part II (Operating Notes) as authoritative** wherever they
conflict, since it is the adult/reference register. Where the Operating
Notes are simply *silent* (not contradictory) about something the Story
documents, the Story's version is kept instead of being dropped.

Known conflicts, per the transcript's analyst note, and how each is
resolved here:

- **Missing Number box travel.** The Story's prose says the box moves
  "left to right"; the Operating Notes -- and the Story's own worked
  examples -- show right → left → middle. **Implemented as right → left →
  middle**, since the Story's own examples override its own prose (a
  narrower case than the general rule).
- **Force Out starting number.** Story shows a fixed `37`; Operating
  Notes show `63` and say it's "a different one each time".
  **Implemented as random**, per Operating-Notes-wins.
- **Electro Flash key order.** Story says number/operator can be pressed
  in any order; Operating Notes add that order changes which operand
  comes first in the displayed problem. **Implemented**: press order is
  tracked and determines problem layout.
- **Wipe Out miss handling.** Story says DataMan answers the problem for
  you after 2 misses; Operating Notes don't mention this (silence, not
  contradiction). **Implemented per the Story**: after a 2nd miss,
  DataMan reveals the answer and serves a fresh problem the same player
  must clear before passing.
- **Missing Number difficulty levels.** *Your Score · More DataMan Fun!*
  (Story) explains both level 2 and the return to level 1; Operating
  Notes mention only level 2 (silence). **Both are implemented.**

None of the above affect Answer Checker or Memory Bank, which is why
those two were built first -- they're the two places where the two
registers substantially agree.

---

## What this app implements

**Answer Checker** (`/api/answer-checker/*`)
- Operands: one or two digits (0-99). Answers: one to three digits (0-999).
- Wrong answer → `EEE`, one retry allowed; still wrong → reveals the
  correct problem and result.
- Division answers are whole-number; a remainder is flagged with `r` and
  shown, per the manual.
- Subtraction that would produce a negative result is rejected outright.
- Score (right, tried) is reported every 10 problems -- two fields, no
  timer, matching the Operating Notes (Answer Checker has no clock).

**Memory Bank** (`/api/memory-bank/*`)
- Store up to 10 problems (unanswered) via `store`.
- `go` starts playback: one problem at a time, two tries each.
- Final score is three fields -- right, tried, and **ticks**.

**Electro Flash** (`/api/electro-flash/*`)
- `select` picks a table: a single digit key (0-9) plus an operator key,
  with the press order recorded (`"first": "digit"` or `"op"`) since that
  order determines which operand is displayed first.
- `go` builds the table by sweeping the *other* operand 0-9, filtering out
  subtraction problems that would go negative and division problems with
  a remainder -- filtered when the table is built, not rejected after a
  user submits an answer.
- Two tries per problem. On table completion, score is three fields
  (right, tried, ticks), and DataMan automatically advances to the next
  table (same operator, digit + 1, wrapping 0-9), per "DataMan will
  automatically start over with the next appropriate table."

**Number Guesser** (`/api/number-guesser/*`)
- `new` picks a secret in **10-99**: read as the range strictly *between*
  the manual's stated fenceposts of 9 and 100 (see the code comment on
  `ng_new` for the full reasoning -- this is an inference, not a
  manual-stated fact).
- Each `guess` returns the two nearest bounding numbers the secret is
  between, narrowing as you guess. Guess count is tracked and reported
  on success.

**Wipe Out** (`/api/wipe-out/*`)
- Modeled as one shared session passed between players in turn (per this
  project's fixed single-unit design premise -- no networked multiplayer).
- A hidden random countdown, picked when `go` is pressed, ends the round;
  the manual gives no numeric range for it, so a reasonable one was
  chosen (see the code comment on `_wo_start_round`).
- Only addition problems, per the Operating Notes.
- Two misses on a problem → DataMan reveals the answer and serves a fresh
  problem the same player must clear before passing (Story's rule; the
  Operating Notes are silent, not contradictory, on this point).
- When the hidden timer fires, whoever is holding it is eliminated; play
  continues among the rest until one player remains.

**Force Out** (`/api/force-out/*`)
- Random starting number each game (Operating-Notes-wins over the
  Story's fixed example). Players subtract 1-9 per turn; a `0` entry is
  rejected the same way Answer Checker rejects invalid entries, and so is
  any entry that would drive the total negative.
- Whoever's subtraction makes the display hit exactly 0 is "Forced Out"
  and loses the round.

**Missing Number ("Box") Problems** (`/api/missing-number/*`)
- `cycle-box` advances the blank's position right → left → middle → right
  → ... on every press (matching the physical key's repeated-press
  behavior).
- `select-level` supports both level 1 (basic) and level 2 (harder).
- `go` generates 10 problems for the chosen operator/box/level, filtering
  out negative-subtraction and remainder-division results the same way
  Electro Flash does. Two tries each; final score is three fields
  (right, tried, ticks), per *Your Score · More DataMan Fun!*.

**Power**
- `ON` resets to Answer Checker mode and clears state.
- Power Saver: any API call first checks elapsed time since last
  activity; past 5 minutes idle, the session is auto-powered-off. See the
  code comment on `power_ok` for why this app doesn't also sweep idle
  sessions proactively in the background.

**Physical fidelity**
- `format_display()` enforces the real unit's 8-character VFD width on
  every display string in the app (see the code comment for the
  overflow judgment call: right-most 8 characters are kept).
- `/api/keypad` returns the real 24-key symbol-only layout (6 rows x 4
  keys), pulled from the keypad illustration described in the manual
  near the Force Out (Story) section. `templates/index.html` renders its
  keypad from this endpoint instead of hardcoded English option labels;
  clicking digit/operator keys types into whichever input field last had
  focus, and the 5 unlabeled activity keys plus the Memory Bank key
  switch panels / trigger the matching action.

## What this app does *not* implement

The six story-only games/boards -- **Starmath Race, Orbit Math, First
Out, Space Ball, Astro Race, Antimath Maze**. These appear only in the
child-facing narrative half of the manual; the "For Parents and
Teachers" reference half never explains how to actually drive them via
a key sequence (no `[key: ...]` annotation, no Operating Notes section),
so there's no reference-register rule set to implement them against.
They're all built as *variations on top of* the activities above (Memory
Bank scoring for Starmath Race and Orbit Math, Force Out for First Out,
Electro Flash for Space Ball, Missing Number for Astro Race, Answer
Checker for Antimath Maze), so once an activity above is implemented,
playing those story games is a matter of house rules on top of it, not
additional server-side logic.

---

## Project structure

```
dataman_app/
├── app.py                    entry point -- create_app() + app.run()
├── requirements.txt
├── templates/index.html      keypad UI, one panel per activity, Output box
└── dataman/                  application package
    ├── __init__.py            create_app(): builds the Flask app, registers blueprints
    ├── config.py               shared constants (OPS, digit widths, timeouts, ...)
    ├── mathutil.py              compute()/validate_digits() -- DataMan's shared arithmetic rules
    ├── display.py               the 8-char VFD display-string helpers
    ├── state.py                  the single per-session state dict + power gate
    ├── logging_utils.py          developer-only file logging (see Debugging, below)
    └── routes/                  one blueprint per activity
        ├── core.py               /, /api/keypad, /api/on, /api/off, /api/client-log
        ├── answer_checker.py
        ├── memory_bank.py
        ├── electro_flash.py
        ├── number_guesser.py
        ├── wipe_out.py
        ├── force_out.py
        └── missing_number.py
```

Each activity's rules, JUDGMENT CALL comments, and manual citations live
in its own route module rather than one large file -- see the module
docstring at the top of each for which section of the manual it's
modeling.

## Running it

```bash
cd dataman_app
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/`. The frontend
(`templates/index.html`) is intentionally bare -- plain form inputs and
a symbol keypad rendered from `/api/keypad` -- since the interesting
content here is the API's behavior, not its styling. All 7 activities
have their own labeled tab across the top; the current activity's
controls, the keypad, and the live JSON "Output" box all sit in one row
so nothing needs scrolling to reach.

## Debugging

Every request the API receives and every response it sends -- including
validation errors that return a normal 400 and never crash anything --
is written to `dataman_app/dataman.log` (rotated at 1MB, a few backups
kept). This is a plain file on disk, not shown anywhere in the page;
open it directly (`tail -f dataman.log` while the app is running works
well). Client-side-only events that never reach the server on their own
-- a raw keypad press building up an unsubmitted field, switching
activity tabs, an uncaught JS error -- are also reported to that same
file via `POST /api/client-log`. See `dataman/logging_utils.py`.

## API summary

| Endpoint | Method | Purpose |
|---|---|---|
| `/api/on` | POST | Power on, reset to Answer Checker |
| `/api/off` | POST | Power off |
| `/api/keypad` | GET | The 24-key symbol layout |
| `/api/client-log` | POST | Developer log sink `{level, message}` -- see Debugging |
| `/api/answer-checker/problem` | POST | Enter a problem `{op, a, b}` |
| `/api/answer-checker/answer` | POST | Submit an answer `{answer}` |
| `/api/answer-checker/score` | GET | Current right/tried |
| `/api/memory-bank/store` | POST | Store a problem `{op, a, b}` (max 10) |
| `/api/memory-bank/clear` | POST | Empty the Memory Bank |
| `/api/memory-bank/go` | POST | Start playback of stored problems |
| `/api/memory-bank/answer` | POST | Submit an answer during playback |
| `/api/electro-flash/select` | POST | Pick a table `{first, digit, op}` |
| `/api/electro-flash/go` | POST | Start the table |
| `/api/electro-flash/answer` | POST | Submit an answer `{answer}` |
| `/api/number-guesser/new` | POST | Pick a new secret number |
| `/api/number-guesser/guess` | POST | Submit a guess `{guess}` |
| `/api/wipe-out/select` | POST | Set up players `{players: [...]}` |
| `/api/wipe-out/go` | POST | Start a round (hidden timer) |
| `/api/wipe-out/answer` | POST | Submit an answer `{answer}` |
| `/api/wipe-out/pass` | POST | Pass to the next player |
| `/api/force-out/select` | POST | Set up players, pick random start |
| `/api/force-out/subtract` | POST | Subtract `{amount}` (1-9) |
| `/api/missing-number/cycle-box` | POST | Advance the blank position |
| `/api/missing-number/select-op` | POST | Pick the operator `{op}` |
| `/api/missing-number/select-level` | POST | Pick difficulty `{level: 1\|2}` |
| `/api/missing-number/go` | POST | Start a 10-problem round |
| `/api/missing-number/answer` | POST | Submit an answer `{answer}` |

`op` is one of `"+" "-" "*" "/"`.
