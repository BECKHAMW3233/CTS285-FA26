# DataMan (1977, Texas Instruments) — Background Research

This is a standalone research writeup. It does not assume any app, code,
or prior deliverable exists. Every claim below is attributed to a specific
source so you can verify it yourself. Where sources disagree or a fact is
uncertain, that's stated explicitly rather than resolved silently.

---

## 1. What DataMan was

DataMan was an electronic educational toy manufactured by Texas
Instruments, designed to teach basic arithmetic (addition, subtraction,
multiplication, division) to children through a set of built-in
calculator-based games. It was styled to look like a robot rather than a
plain calculator, and shipped with an illustrated storybook/manual, *The
Story of DataMan*, that taught a child how to use it through a
space-adventure narrative.

**Introduction date:** June 5, 1977.
Source: Datamath Calculator Museum product page (datamath.org/Edu/DataMan.htm,
maintained by Joerg Woerner — the same museum that scanned the manual PDF
you have), and independently corroborated by Wikipedia's "Dataman" article
and the Centre for Computing History's catalog entry.

**Target audience:** children age 7 and up (positioned as the follow-on
product to TI's earlier *Little Professor*, which targeted age 5+).
Source: Smithsonian National Museum of American History object record
(nmah_334470); Datamath Museum page.

**Original retail price:** listed as $24.95 by the Datamath Museum
(datamath.org). Separately, the Smithsonian's object record cites period
newspaper advertisements showing the price varying over time and by
market: $19.99 (Hartford Courant, Nov 6 1977), $16.95 (LA Times, June 5
1979), $19.95 (LA Times, Nov 17 1979), $25 (LA Times, Dec 11 1979 feature
article), $16.99 regular $24.99 (Hartford Courant, Dec 21 1980), and
$16–18 on sale, regular $25 (LA Times, Apr 14 1981). These are two
different kinds of figures — one is a museum's stated "new price," the
others are dated newspaper sale prices — and I have not reconciled them
into one number; the toy was clearly sold across a wide price band over
its multi-year run.

---

## 2. Physical hardware

| Attribute | Value | Source |
|---|---|---|
| Case | Gray plastic, styled as a robot | Smithsonian NMAH object record |
| Keys | 24 total, "of differing shape": 10 digit keys, 4 arithmetic operator keys, an equals key, a Memory Bank key, ON key, OFF key, plus additional unlabeled game-activity keys | Smithsonian NMAH object record |
| Key color | Orange | Smithsonian NMAH object record |
| Display | Vacuum fluorescent display (VFD), 8 digits | Datamath Museum spec table; Wikipedia "Dataman"; Smithsonian |
| Display part number | Itron FG105H1 | Datamath Museum teardown (datamath.org/Edu/DataMan.htm) |
| Dimensions | 5.8 × 3.5 × 1.2 in (148 × 88 × 30 mm) | Datamath Museum spec table |
| Weight | 4.8 oz (136 g) | Datamath Museum spec table |
| Battery | Single 9-volt | Datamath Museum spec table; confirmed by Smithsonian ("compartment for a nine-volt battery") |
| Auto power-off | After approximately 5 minutes of no key activity ("Power Saver Feature") | Stated directly in the manual (uploaded transcript, "Turning DataMan Off" / Appendix sections); corroborated by independent collector site 99er.net |
| Main IC | TMC1982, a member of the TMC1980 chip family (related to the TMC0980 used in the 1976 TI-30), itself based on the TMS1000 microcomputer architecture. ROM: 18,432 bits (2K × 9). RAM: 576 bits (9 registers × 16 digits). Includes an integrated charge-pump driver (~ -22V) to power the VFD's anodes/grids, plus integrated filament (heater) drivers | Datamath Museum teardown page, describing a specific dismantled unit |
| PCB | Single-sided printed circuit board | Datamath Museum teardown page |
| Country of manufacture (the specific unit the museum tore down) | Rieti, Italy, dated week 30 of 1980 | Datamath Museum teardown page |
| Country of manufacture (per your uploaded manual's back-cover text) | "Printed in El Salvador," code 1019557-11 | Your uploaded manual transcript, "Back Cover" section |

**Note on the manufacturing-location discrepancy:** the manual you have
says the *booklet* was printed in El Salvador; the Datamath Museum's
teardown is of a specific physical *unit* built in Italy in 1980. These
aren't necessarily in conflict — a US-market product line commonly had
booklets and hardware built in different plants, and TI is independently
documented (via the ROMchip journal abstract, see §4) as having
manufactured related products in Central America across multiple years.
I have not found a source stating all units were built in one location.

**Earlier (incorrect) claim I made in this conversation, corrected here:**
I initially wrote "no voltage stepping to the main IC," sourced from the
Wikipedia article, implying a bare 9V feed to the chip and that the
chip's internal clock was audible through the battery contacts. The more
detailed and technically specific Datamath Museum teardown says the
opposite in effect: the TMC1982 chip has an *integrated* charge-pump
driver that steps the 9V up to roughly -22V to drive the VFD, plus
integrated filament drivers. Wikipedia's own footnote for that claim
points to a Wired.com "GeekDad" retro-gaming blog post, which is a much
lower-reliability source than either the museum teardown or the chip
family page. **I'm not resolving this conflict for you — I'm flagging
that I passed along a claim I should have checked harder, and the more
technically detailed source disagrees with it.**

---

## 3. Built-in activities

The Datamath Museum's product page lists six activities:

- Answer checker
- Missing number
- Electro Flash
- Wipe Out
- Number Guesser
- Force Out

This matches the Smithsonian's list (Electro Flash, Wipe Out, Number
Guesser, Force Out, plus "[?]" for missing-number/unknowns) and matches
what's documented with full rules in your uploaded manual transcript,
which also documents a **Memory Bank** feature (store-and-replay custom
problems) and six **story-only games/boards** (Starmath Race, Orbit Math,
First Out, Space Ball, Astro Race, Antimath Maze) that appear in the
child-facing narrative half of the manual but have **no corresponding
operating instructions** anywhere in the reference half — meaning they're
presented to a child as things DataMan can do, but the adult reference
section never explains how to actually drive them via key sequence. This
gap is called out explicitly in your manual's own analyst's note section
at the end of the transcript.

I have not independently verified the exact rule text for each activity
(e.g., Number Guesser's number range, Missing Number's blank-position
cycling order) against any source other than your uploaded manual
transcript. That transcript is itself a secondhand vision-transcription of
scanned pages, not the original document — accurate as far as I can tell,
but I have not cross-checked it page-for-page against a second copy of
the manual or against a physical unit.

---

## 4. Further reading I did not have full access to

**Jon-Paul C. Dyson, "The Many Histories of DataMan," ROMchip, Vol. 3
No. 2 (Dec 18, 2021), ISSN 2573-9794.** Author is VP for exhibits and
director of the International Center for the History of Electronic Games
at the Strong National Museum of Play. The journal's own keyword list for
the article includes: DataMan, Texas Instruments, El Salvador,
calculators, mathematical play, electronic handhelds, gender, Central
America, plastics, computer chips, educational games, vacuum fluorescent
display, Latin America. This strongly suggests the article covers the
Central American manufacturing history and possibly gender-marketing
angles, but **I could not retrieve the article's actual body text** — the
page I fetched returned only the abstract/landing shell. If that history
matters to you, I'd need you to supply the PDF or I'd need another way to
access it.

**Wired.com, "Super Bonus GeekDad Retro Gaming: DataMan," James Floyd
Kelly, July 5, 2011.** Cited by Wikipedia as the source for the
audible-clock/no-voltage-stepping claim discussed in §2. I have not
fetched this article directly; treat that specific claim as unverified
by me beyond what Wikipedia quotes from it.

---

## 5. Source list (for your own verification)

1. Datamath Calculator Museum — DataMan product page: http://www.datamath.org/Edu/DataMan.htm
2. Smithsonian National Museum of American History — object record nmah_334470: https://americanhistory.si.edu/collections/object/nmah_334470
3. Wikipedia — "Dataman": https://en.wikipedia.org/wiki/Dataman
4. 99er.net — DataMan collector page (manual download, power/battery note): https://www.99er.net/dataman.html
5. ROMchip journal — "The Many Histories of DataMan" (abstract/landing page only): https://romchip.org/index.php/romchip-journal/article/view/154
6. Your uploaded manual transcript — `dataman-manual.md` / `dataman-manual_md.pdf` (vision-transcription of the scanned 1977 TI manual, scan courtesy of the Datamath Calculator Museum)
7. Period vintage-toy resale listings (eBay/Worthpoint/Poshmark) — used only to corroborate the game list and general physical description; not treated as authoritative for specifications.

---

## 6. What I still don't know / haven't checked

- Whether the manual transcript you have is complete and error-free
  relative to the original scan (I have not compared it page-by-page
  against a second source).
- The El Salvador vs. Italy manufacturing discrepancy (§2) is unresolved.
- The Wired.com claim about audible chip noise / no voltage stepping is
  unverified and appears to be contradicted by the more technical
  Datamath Museum teardown.
- The ROMchip article's actual content (§4) — I only have its metadata.
- Exact unit sales figures, total production run, or the manual's
  original page count as printed (your transcript says 28 PDF pages
  covering "printed p. 24," but I have not verified against an
  independent listing that also states the physical booklet's page count.
  One eBay listing I found separately states the booklet is "24 pages" —
  which is a different framing of the same document, since PDF page count
  can include covers that the "printed" numbering doesn't).
