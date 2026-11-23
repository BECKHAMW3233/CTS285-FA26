"""Change-impact retest of M5 Scenario E (stale page) after PB-03.

The M5 finding recorded that an answer from a stale page is charged to a
problem the learner never saw (PB-02 #1 fails) and asked for a test here.
With PB-03 the same records now feed a score the learner can see.

Fix (next commit after the failing test): the form sends the problem_id it
showed; check_answer() records nothing if that problem is already finished.

Real-browser check (Chromium, before any fix):
- double-click on Check: only 1 POST reached the server -> not a trigger
- back button + resubmit: Chromium re-GETs the page -> not a trigger
- two tabs on the same learner: TRIGGER (reproduced below)

Run from module-5-flask/:  python -m unittest discover -s tests -v
"""

import unittest

from test_flask_baseline import FlaskTestCase


class ScenarioE_TwoTabs(FlaskTestCase):
    def submit(self, answer, shown_problem_id):
        """What the browser form sends: the answer and the problem it showed."""
        response = self.client.post("/", data={"answer": answer, "problem_id": shown_problem_id})
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    def test_stale_tab_does_not_cost_the_learner_a_try_or_a_point(self):
        # tab1 and tab2 both showed 7 x 8 (problem 1)
        self.submit("56", 1)                 # tab1: right
        page = self.submit("56", 1)          # tab2: stale, still showing 7 x 8
        self.assertNotIn("Not quite", page)  # PB-01: a right answer is never called wrong
        self.assertIn("That problem is already finished. Here is your next problem.", page)
        self.assertIn("Problem: 9 x 6 = ?", page)
        page = self.submit("50", 2)          # tab1: the learner's first real miss on 9 x 6
        self.assertIn("[Try 1 of 2] EEE - Not quite. Try again.", page)
        self.assertEqual(self.history(page), [
            "#1: 7 x 8 -> 56 (correct, try 1)",
            "#2: 9 x 6 -> 50 (incorrect, try 1)",
        ])                                   # PB-02 #1: recorded with the problem it answered
        self.assertEqual(self.element(page, "score"), "Score: 1 right out of 1 tried")


    def test_stale_page_after_the_last_problem_records_nothing(self):
        for answer, shown in (("56", 1), ("54", 2), ("7", 3)):
            self.submit(answer, shown)
        page = self.submit("7", 3)  # stale tab still showing 12 - 5
        self.assertEqual(self.element(page, "totals"), "Entries: 3 Correct: 3")
        self.assertEqual(self.element(page, "score"), "Score: 3 right out of 3 tried")

    def test_page_sends_the_problem_it_shows(self):
        """The interface half of the fix: the hidden field matches the visible prompt."""
        self.assertIn('name="problem_id" value="1"', self.get())
        self.assertIn('name="problem_id" value="2"', self.submit("56", 1))

    def test_request_without_problem_id_keeps_old_behavior(self):
        """Deliberate compatibility: a client that omits problem_id (curl, the baseline
        tests) is not refused. It also is not protected. See the decision note."""
        self.answer("56")
        page = self.answer("56")
        self.assertIn("9 x 6 -> 56 (incorrect, try 1)", page)


if __name__ == "__main__":
    unittest.main()
