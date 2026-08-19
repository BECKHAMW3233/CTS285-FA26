# Analyst's Case File

**System analyzed:** DataMan (Texas Instruments, 1977)
**Feature assigned:** Number Guesser
**Source document:** *The Story of DataMan* — manual transcript

**Your name:** William Beckham
**Date:** 2026-08-19

---

## How to fill this out

Every finding needs evidence. Evidence is an **exact quoted phrase** from the manual plus the **section heading** it came from. Cite sections by name — "Number Guesser (Story)" or "Electro Flash · Number Guesser · Wipe Out (Operating Notes)". Do not cite page numbers; the manual carries two numbering systems that do not agree.

Read **both registers** before you write anything. Part I describes the feature to a child. Part II describes it to an adult. Each contains information the other omits.

If you cannot find evidence for something, do not guess. Put it in Section 8. An unknown you can name is a finding. An assumption you record as fact is an error.

Rows are examples of format, not a quota. Add rows as your evidence requires.

---

## 1. Purpose

Why does this feature exist? What problem does it solve for the user?

| Finding | Evidence (exact quote) | Section |
|---|---|---|
| The Story frames the game as pure enjoyment of numbers, tied to the manual's fiction of resisting "AntiMath." | "One thing that annoys AntiMath and makes him green with envy is people having *fun* with numbers and mathematics!" | Number Guesser (Story) |
| The Story states, in general terms, that playing sharpens math ability, without naming a specific skill. | "As you play *Number Guesser* with your family or friends (or just by yourself), you'll be sharpening your math skills." | Number Guesser (Story) |
| The Operating Notes frame the feature's purpose as a strategy game for the whole family, not just a child's activity. | "*Number Guesser* is an educational game of number strategy the whole family will enjoy." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| The manual claims (this is the manual's assertion of educational value, not a description of what the system does) that the game teaches the concept of "number betweeness" and number logic. | "*Number Guesser* helps to teach the important basic concept of *number betweeness* (the unknown secret number is always *between* the two numbers shown in DataMan's display) and number logic." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| The manual further claims that the strategy of narrowing guesses builds estimation and averaging skills. | "The strategy involved in getting to the answer in the fewest tries will help build skills in estimation and averaging." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |

---

## 2. Users and Roles

Who interacts with this feature? Where a feature involves more than one person, name what each one *does* — the person who sets something up and the person who responds to it are different roles even when they are the same human being.

| Role | What this role does | Evidence (exact quote) | Section |
|---|---|---|---|
| Guesser | Enters guesses at the secret number. | "*You* enter your guess." | Number Guesser (Story) |
| Solo player | Can play the game with no other participant. | "As you play *Number Guesser* with your family or friends (or just by yourself), you'll be sharpening your math skills." | Number Guesser (Story) |
| Group of players taking sequential turns as guesser | Multiple people play in turn, each trying to find the secret number in fewer tries than the others. | "Take turns with your friends trying to guess the secret number in the fewest tries." | Number Guesser (Story) |
| Group of players taking sequential turns (adult register) | Confirms the turn-taking, competitive framing from the child register. | "Children can take turns seeing who can find a secret number in the least guesses!" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| Number selector | Chooses the secret number. In both registers, this role belongs to DataMan, not to any human player — neither section ever gives a person a way to set or supply the secret number. | "I'll pick a secret number for you to guess." | Number Guesser (Story) |
| Number selector (adult register) | Same role, confirmed in the operating notes. | "a secret number between 9 and 100 that DataMan has selected" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |

---

## 3. Inputs

What information or action enters the system? Include keystrokes, choices, and anything the system refuses to accept.

| Input | Supplied by | Evidence (exact quote) | Section |
|---|---|---|---|
| ON key, then the Number Guesser key, to start the activity | Player | "Just press **ON** and the *Number Guesser* key: **[???]**" | Number Guesser (Story) |
| ON key, then the [NUMBER GUESSER] key (adult-register phrasing of the same steps) | Player | "first turn DataMan on with the **ON** key, and then press the **[NUMBER GUESSER]** key" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| A guess (a number) | Player | "*You* enter your guess." | Number Guesser (Story) |
| A guess, entered repeatedly across the round | Player | "As you enter each guess, DataMan provides a hint by displaying two numbers that the secret number is between." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| Re-pressing the Number Guesser key to input a request for a new round | Player | "I'll pick a new secret number each time you press **[???]**" | Number Guesser (Story) |

Note: neither register states any input the system refuses for this feature (contrast Answer Checker's stated digit limits and rejection of negative-result subtraction). This absence is recorded as an unknown in Section 8 rather than assumed.

---

## 4. Processing

What does the system do with the input? Include any rule, limit, or constraint you can support.

| Rule or behavior | Evidence (exact quote) | Section |
|---|---|---|
| DataMan selects a secret number within a stated range (9 to 100) at the start of a round. | "I'll pick a secret number for you to guess. It will be somewhere between 9 and 100." | Number Guesser (Story) |
| Confirmed in the operating notes: the secret number falls in the same stated range and is DataMan's selection, not the player's. | "try to guess a secret number between 9 and 100 that DataMan has selected" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| After a guess is entered, the system displays two numbers such that the secret number is mechanically bounded between them. | "I'll flash and show you two numbers in my face mask. The secret number is always somewhere *between* the two numbers I show you." | Number Guesser (Story) |
| Confirmed in the operating notes as a per-guess hint mechanism. | "As you enter each guess, DataMan provides a hint by displaying two numbers that the secret number is between." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| A new secret number is generated each time the activity key is pressed, which is how a new round begins. | "I'll pick a new secret number each time you press **[???]**" | Number Guesser (Story) |
| The round ends when the player's guess matches the secret number, which the system detects and responds to. | "When you finally guess the secret number, I'll show you the number of tries it took, and then a great light show!" | Number Guesser (Story) |

(The two-number "betweenness" hint above is recorded here only as a mechanical fact — what the display shows. The manual's claim that this mechanism *teaches* the concept of betweenness is a value claim and is recorded in Section 1, Purpose, not here.)

---

## 5. Outputs

What information does the system return to the user?

| Output | When it appears | Evidence (exact quote) | Section |
|---|---|---|---|
| A pair of numbers (the "between" hint) | After each guess is entered | "I'll flash and show you two numbers in my face mask." | Number Guesser (Story) |
| Same hint, adult-register description | After each guess is entered | "DataMan provides a hint by displaying two numbers that the secret number is between." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| Count of tries/guesses taken | When the secret number is found | "I'll show you the number of tries it took" | Number Guesser (Story) |
| Same count, adult-register description ("total number of guesses") | When the secret number is found | "displays the total number of guesses that were taken" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| A light show | When the secret number is found | "a great light show!" | Number Guesser (Story) |
| Same light show, adult-register description | When the secret number is found | "DataMan rewards you with a spectacular "light show"" | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |

---

## 6. Feedback

How does the system respond to the user's actions? Feedback tells the user how they are doing. An output returns information; feedback comments on it. If you think a single behavior is both, record it once and say why.

| Feedback behavior | What it tells the user | Evidence (exact quote) | Section |
|---|---|---|---|
| The two-number hint | Bounds the guess: the player learns the secret number's location relative to their guess, not just a raw value. This is the same behavior listed under Outputs, recorded again here because it does more than return data — it comments on where the guess stands. | "The secret number is always somewhere *between* the two numbers I show you." | Number Guesser (Story) |
| The light show on success | Signals a completed, successful round — the manual's own word for this is "rewards," which frames it as feedback on performance rather than a neutral status readout. | "DataMan rewards you with a spectacular "light show" and displays the total number of guesses that were taken." | Electro Flash · Number Guesser · Wipe Out (Operating Notes) |
| The tries/guesses count | Functions as a comparison metric between players rather than a plain count, because the manual explicitly frames it as something to minimize and compare across turns. | "Take turns with your friends trying to guess the secret number in the fewest tries." | Number Guesser (Story) |

---

## 7. Observations and Assumptions

List three statements you were tempted to write as fact but could not fully support. For each, say what evidence you would need.

| Statement | Observation or assumption? | What evidence would settle it? |
|---|---|---|
| A human player can never choose or set the secret number themselves — only DataMan can. | Assumption. Both registers only ever describe DataMan picking ("I'll pick a secret number..." / "...that DataMan has selected"), and neither register describes an input sequence for a player to supply their own number. But absence of a described method is not the same as an explicit statement that it is impossible. | An explicit line either granting or denying player-set secret numbers — e.g., a statement that the number "cannot be entered by you" or, conversely, a described key sequence for setting one. |
| The two displayed hint numbers narrow progressively with each new guess, converging on the secret number (a binary-search-style hint). | Assumption, drawn from how such games conventionally work rather than from the text. The manual only ever states that the secret number lies "between" the two shown numbers at any given moment — it never describes how those two numbers are recalculated from one guess to the next. | A description of the update rule — e.g., a statement that one of the two numbers becomes the player's last guess, or a worked example showing the hint changing across a sequence of guesses. |
| Number Guesser is not a timed activity, unlike Electro Flash or Memory Bank. | Observation, based on contrast: the score outputs for Electro Flash and Memory Bank explicitly include a time/"ticks" figure, while Number Guesser's stated output is only the guess count ("displays the total number of guesses that were taken") with no time term anywhere in either Number Guesser section. But this is an argument from the absence of a mention, not a direct statement that the timer is off. | A direct statement that Number Guesser does or does not use DataMan's timer, or a score-display example for Number Guesser (comparable to the illustrated ones for other games) that shows whether a time field is present. |

---

## 8. Unknowns and Open Questions

What could not be determined from the manual? For each, state what you looked for and where you looked, so a reader knows the gap is real and not just unsearched.

| Open question | Where I looked | Why the manual does not answer it |
|---|---|---|
| Whether a human player can ever set the secret number themselves, rather than DataMan always selecting it. | Read Number Guesser (Story) and Electro Flash · Number Guesser · Wipe Out (Operating Notes) in full. | Both sections state only that DataMan picks the number ("I'll pick a secret number for you to guess" / "a secret number... that DataMan has selected"). Neither section describes any input sequence for a human to enter one, and neither states that this is impossible — the manual is simply silent on the possibility in both registers. |
| How the two displayed hint numbers are computed or updated relative to a given guess. | Read Number Guesser (Story) and the Operating Notes section; also checked for a worked example or illustration of a Number Guesser round (as exist for other games, e.g. Missing Number's worked examples) and found none. | Both registers state only that the secret number is "between" the two numbers shown, with no description of the update rule and no illustrated sample play-through for this feature. |
| Whether Number Guesser is a timed activity using DataMan's built-in clock, as Electro Flash, Memory Bank, and Missing Number are. | Read both Number Guesser sections; also read *DataMan's Timer* (Operating Notes), which describes the timer generally as covering "certain DataMan activities" without listing which. | Neither Number Guesser section's description of the end-of-round output mentions "ticks" or time, and the general Timer section does not enumerate which activities are or are not included, so neither register confirms or denies it for this feature. |
| Whether there is a limit on the number of guesses/tries, or how the system handles a guess outside the 9-100 range or a repeated guess. | Read both Number Guesser sections looking for a constraint or rejection statement comparable to Answer Checker's stated digit limits and negative-number rejection. | Neither section includes any equivalent constraint, limit, or rejection statement for Number Guesser; the topic is not addressed in either register, unlike Answer Checker where it is explicitly addressed. |
| Whether the stated range endpoints (9 and 100) are themselves possible secret numbers, or whether the secret number is always strictly between them. | Read both Number Guesser sections for the exact wording of the range. | Both sections use the same phrase, "between 9 and 100," without clarifying whether the endpoints are included or excluded, and neither register elaborates further. |

---

## 9. Cross-Register Note

This manual documents the same feature twice. Identify **one** thing your assigned feature's two sections handle differently — something one section states and the other omits, or something the two describe in ways that do not match.

**What differs:** The Story states the mechanism for starting a new round — re-pressing the Number Guesser key produces a new secret number. The Operating Notes, which describe turn-taking between players, never state how a new secret number is generated between turns or rounds.

**Part I says (quote):** "I'll pick a new secret number each time you press **[???]**" — Number Guesser (Story)

**Part II says (quote), or is silent:** Silent. Electro Flash · Number Guesser · Wipe Out (Operating Notes) describes players taking turns ("Children can take turns seeing who can find a secret number in the least guesses!") but never states what action produces a new secret number for the next player or the next round.

**Why this matters to an analyst:** The Operating Notes are the register aimed at the adult who will actually set up multi-player turns, yet they omit the one instruction needed to run more than a single round — how to get a new secret number. A reader relying only on Part II would have no documented way to do this and would have to infer it (or cross-reference Part I) to run the "take turns" activity Part II itself describes. This is exactly the failure mode the manual's own reading map warns about: a reader who consults only one part builds an incomplete model of the system.

---

## Before you submit

- [ ] Every finding has a quoted phrase, not a paraphrase.
- [ ] Every quote names the section it came from.
- [ ] I cited section headings, not page numbers.
- [ ] I read both Part I and Part II before writing.
- [ ] Section 8 is not empty.
- [ ] Nothing in Sections 1-6 is a conclusion I could not support.
