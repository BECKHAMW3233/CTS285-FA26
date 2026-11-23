"""Change-impact retest of M5 Scenario E (stale page) after PB-03.

The M5 finding recorded that an answer from a stale page is charged to a
problem the learner never saw (PB-02 #1 fails) and asked for a test here.
With PB-03 the same records now feed a score the learner can see.

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

    @unittest.expectedFailure  # KNOWN DEFECT: the form does not send the problem it showed
    def test_stale_tab_does_not_cost_the_learner_a_try_or_a_point(self):
        # tab1 and tab2 both showed 7 x 8 (problem 1)
        self.submit("56", 1)                 # tab1: right
        page = self.submit("56", 1)          # tab2: stale, still showing 7 x 8
        self.assertNotIn("Not quite", page)  # PB-01: a right answer is never called wrong
        page = self.submit("50", 2)          # tab1: the learner's first real miss on 9 x 6
        self.assertIn("[Try 1 of 2] EEE - Not quite. Try again.", page)
        self.assertEqual(self.history(page), [
            "#1: 7 x 8 -> 56 (correct, try 1)",
            "#2: 9 x 6 -> 50 (incorrect, try 1)",
        ])                                   # PB-02 #1: recorded with the problem it answered
        self.assertEqual(self.element(page, "score"), "Score: 1 right out of 1 tried")


if __name__ == "__main__":
    unittest.main()
