# AI Prompt Log — M3A

Each entry covers one exchange with Claude in this conversation.

## Exchange 1
Prompt: Uploaded the M3A assignment PDF/text and asked what it was asking for.
What the AI gave me: A summary of the four parts (plan from evidence, ask before you build, build, check/decide), the planning gate, hooks, and submission requirements.
What I kept, changed, or threw away: Used it to understand the assignment scope. No content generated.

## Exchange 2
Prompt: Uploaded adventure_start.py, adventure_start.cpp, brief-template.md, coda-prompts.md, story_check.py, twee-basics.md, slides_cyoa.html, example.twee and asked which route to use.
What the AI gave me: Recommendation to use Python (closest to upcoming Flask module), plus notes on the planning gate, AI-use logging requirement, and the H2 hook.
What I kept, changed, or threw away: Decided on Python as my route.

## Exchange 3
Prompt: Pasted terminal output showing three runs of adventure_start.py (testing both endings).
What the AI gave me: Confirmation that both endings work and that this satisfies "run the starter, play it" (step 1 of Part 3).
What I kept, changed, or threw away: Informational only — no content generated.

## Exchange 4
Prompt: Asked Claude to run the checker.
What the AI gave me: Explanation that Claude didn't have my local files in its own workspace, with two options (run it myself, or upload the files).
What I kept, changed, or threw away: Uploaded the files instead.

## Exchange 5
Prompt: Uploaded all project files (attachment.txt, adventure_start.cpp/.py, brief-template.md, coda-prompts.md, m3a-fall-break-adventure.md, story_check.py, twee-basics.md, slides_cyoa.html x2, example.twee).
What the AI gave me: Acknowledged the files and corrected its earlier claim that it couldn't access them.
What I kept, changed, or threw away: N/A — correction, no content generated.

## Exchange 6
Prompt: Told Claude to run the checker.
What the AI gave me: Ran `python story_check.py adventure_start.py --map` and reported the ORPHAN finding on passage_vent, plus the Mermaid map output.
What I kept, changed, or threw away: Used the finding to understand TODO 1 (the vent passage isn't linked yet). No story content generated — this is the unmodified starter file.

## Exchange 7
Prompt: Noted that the vent code exists but isn't actually wired up/used.
What the AI gave me: Confirmed that "Crawl into the vent" is only a comment, not implemented in passage_closet()'s ask() call.
What I kept, changed, or threw away: Confirmed my own observation. No content generated.

## Exchange 8
Prompt: Asked whether the other files reference this same orphan/gap.
What the AI gave me: A grep across all uploaded files showing the same unlinked passage_vent gap exists identically in adventure_start.py, adventure_start.cpp, and example.twee, and that slides_cyoa.html uses this exact finding as its worked example.
What I kept, changed, or threw away: Confirmed this is an intentional exercise built into all three starter routes, not a bug. No content generated.

## Exchange 9
Prompt: Asked Claude to summarize m3a-fall-break-adventure.md and "let's begin this adventure."
What the AI gave me: Confirmed the file duplicates content already summarized; explained it could not fabricate Part 1 player answers and offered two paths: real player interview, or the no-player self-interview (Prompt 2N) fallback.
What I kept, changed, or threw away: Chose option 1 (real player interview).

## Exchange 10
Prompt: Replied "1" to select the real-player-interview path.
What the AI gave me: The six brief-template.md interview questions (E-01 to E-06) to ask my player, with notes on the planning-gate analyst rule (write answers as given, don't argue or fix).
What I kept, changed, or threw away: Used these as my question list.

## Exchange 11
Prompt: Said I'd interview my 11-year-old nephew, have a few days, and will use Claude Code to help.
What the AI gave me: Suggested a concrete E-06 question suited to an 11-year-old, and guidance on keeping his answers verbatim and on how to use Claude Code appropriately during Part 3 (one passage at a time, log prompts, must be able to explain every line).
What I kept, changed, or threw away: Kept the suggested E-06 question and the verbatim-answer guidance.

## Exchange 12
Prompt: Asked for "the list of questions and such" to bring to the interview.
What the AI gave me: The six questions in table form plus interview tips (ask one at a time, one follow-up allowed, E-03 is especially useful, don't argue).
What I kept, changed, or threw away: Used as my working interview sheet.

## Exchange 13
Prompt: Asked for this as an artifact in md format.
What the AI gave me: An HTML-formatted interview-sheet artifact (not markdown as requested).
What I kept, changed, or threw away: Rejected — wrong format, asked for correction.

## Exchange 14
Prompt: Pointed out the format was wrong (asked for md, got HTML).
What the AI gave me: Acknowledgment of the error and offer to fix it.
What I kept, changed, or threw away: N/A — asked for the corrected version.

## Exchange 15
Prompt: Demanded the markdown-format artifact be created.
What the AI gave me: A markdown artifact with the same six questions and tips.
What I kept, changed, or threw away: Kept as my markdown interview sheet.

## Exchange 16
Prompt: Asked why the raw markdown syntax wasn't visible in the artifact viewer.
What the AI gave me: Explanation that the artifact viewer renders markdown rather than showing raw syntax, with options to download the file or have it pasted as a code block.
What I kept, changed, or threw away: Asked for raw text pasted directly.

## Exchange 17
Prompt: Asked for the raw md format directly.
What the AI gave me: The interview sheet's literal markdown source pasted as a code block.
What I kept, changed, or threw away: Kept as my raw-text working copy.

## Exchange 18
Prompt: Asked what else is needed for the repo.
What the AI gave me: Full submission checklist (brief.md, story file, prompts.md, hook extras) and which starter-kit files are not submission items.
What I kept, changed, or threw away: Used as my repo checklist.

## Exchange 19
Prompt: Asked for brief.md in raw markdown to copy-paste.
What the AI gave me: Full brief-template.md structure, pre-filled with my name and Python as the route, all content fields left blank.
What I kept, changed, or threw away: Kept as my working brief.md, to fill in once I have my player's answers.

## Exchange 20
Prompt: Asked what other files are needed before the interview.
What the AI gave me: Confirmed nothing else needs creating yet; suggested setting up the m3a repo folder now and starting prompts.md early to log AI use as I go.
What I kept, changed, or threw away: Used as my pre-interview checklist.

## Exchange 21
Prompt: Asked Claude to read this chat and create prompts.md in raw format.
What the AI gave me: An initial prompts.md draft logging only the planning-stage prompts it judged substantive, leaving idea/build stages as empty placeholders.
What I kept, changed, or threw away: Rejected as incomplete — asked for every exchange to be included.

## Exchange 22
Prompt: Told Claude every prompt and exchange in the chat needed to be logged, not a filtered subset.
What the AI gave me: This full-chat-history version of prompts.md.
What I kept, changed, or threw away: This is the version being kept.
