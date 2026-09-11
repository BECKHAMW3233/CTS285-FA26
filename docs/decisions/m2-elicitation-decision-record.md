# M2 Elicitation Decision Record

## Investigation Path

1. What exactly do stakeholders mean by "students shouldn't lose their work"?
   Evidence revealed: Teachers report that students may pause practice and return later. They want a learner's saved practice state to remain available after leaving and returning to the application.

2. What does "modern" need to mean from a user perspective?
   Evidence revealed: Stakeholders say modern means the experience should work reliably in a browser, be understandable without a printed manual, and avoid making the learner navigate unnecessary screens. They do not specify a visual style or framework.

3. What do parents or teachers need to understand about learner activity?
   Evidence revealed: Adults want to understand what the learner practiced and whether progress is occurring, but stakeholders have not yet agreed on a detailed reporting dashboard.

## Initial Position

**Supported evidence:** Kids need their progress saved so it's still there when they come back later — teachers said students pause and come back (Evidence 1). Stakeholders said "modern" just means it works reliably in a browser, you don't need a manual to figure it out, and there's no extra clicking around — not a specific look or tech (Evidence 2). Parents/teachers want to see what the kid practiced and if they're improving (Evidence 3).

**Remaining uncertainty:** We don't know exactly what "saved progress" covers — just the current problem, the whole history, or the score. We also don't know what form the parent/teacher view should take — Evidence 3 says that's not agreed on yet. And "keep it simple" was never actually asked about, so it's still unclear.

**Likely functional requirement:** The system must save a student's progress so it's still there when they leave and come back later.

**Likely non-functional requirement / quality constraint:** The app must work reliably in a normal web browser and be usable without needing instructions.

**Assumption or proposed solution I am not treating as confirmed:** A detailed parent/teacher dashboard — the evidence says that's not agreed on yet, just that parents want to see progress somehow.

**Why my initial position is defensible:** Because everything above comes straight from the evidence gathered, not guesses — saving progress comes from Evidence 1, the reliability/no-manual requirement comes from Evidence 2, and the dashboard is left out on purpose since Evidence 3 says that part isn't settled.

## Complication

Students may use DataMan on school Chromebooks, phones, tablets, and home computers. Some sessions may be interrupted before intentional sign-out.

**What this affects:** It affects the "students shouldn't lose their work" requirement. We assumed students would just close the app and come back later on the same device. Now we know sessions can get cut off suddenly — Chromebook dies, tablet loses power, wifi drops — and the student might come back on a totally different device (phone instead of Chromebook, home computer instead of a school one).

**What I revised, if anything:** I'd revise the functional requirement so it's not just "save progress when they leave" but "save progress automatically, even if the session cuts off without warning, and make it available again no matter which device they log back in on."

**Final decision and reasoning:** Revise. The first version only covered a clean, on-purpose exit and return. It doesn't hold up once we know sessions get interrupted unexpectedly and kids switch devices — that's a real gap the original requirement didn't cover, so it needs to change, not just stay as-is.

## Next Project Action

Use this evidence to update the DataMan Requirements Register and preserve any unresolved questions as open assumptions or follow-up items.
