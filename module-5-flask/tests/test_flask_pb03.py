"""PB-03 "See my current score" through the whole Flask slice.

User action (form POST) -> Flask route -> AnswerChecker.score() -> attempts in
the store -> template. Criteria: docs/product-backlog.md, PB-03.

Run from module-5-flask/:  python -m unittest discover -s tests -v
"""

import unittest

from test_flask_baseline import FlaskTestCase


class PB03InTheApp(FlaskTestCase):
    def test_criterion_1_score_visible_on_the_practice_page(self):
        page = self.get()
        self.assertEqual(self.element(page, "score"), "Score: 0 right out of 0 tried")
        self.assertIn("Problem: 7 x 8 = ?", page)  # same page as practice

    def test_criteria_2_to_4_two_correct_one_incorrect(self):
        """56 (right), 50 (miss), 54 (right on try 2): the PB-02 #3 sequence."""
        page = self.answer("56")
        self.assertEqual(self.element(page, "score"), "Score: 1 right out of 1 tried")
        page = self.answer("50")  # criterion 2: an incorrect answer does not increase it
        self.assertEqual(self.element(page, "score"), "Score: 1 right out of 1 tried")
        self.assertIn("Problem: 9 x 6 = ?", page)  # criterion 4: still on the practice page
        page = self.answer("54")  # criterion 3
        self.assertEqual(self.element(page, "score"), "Score: 2 right out of 2 tried")
        self.assertIn("Problem: 12 - 5 = ?", page)

    def test_invalid_input_does_not_change_score(self):
        self.answer("56")
        page = self.answer("abc")
        self.assertIn("Please enter a whole number.", page)
        self.assertEqual(self.element(page, "score"), "Score: 1 right out of 1 tried")

    def test_final_score_when_every_problem_is_finished(self):
        """Memory Bank: 'When you've tried all of the problems, I'll show you your score'."""
        for value in ("56", "1", "2"):  # 7x8 right, 9x6 revealed
            page = self.answer(value)
        self.assertIsNone(self.element(page, "complete"))
        page = self.answer("7")
        self.assertEqual(self.element(page, "score"), "Score: 2 right out of 3 tried")
        self.assertEqual(self.element(page, "complete"),
                         "All problems finished! Final score: 2 right out of 3 tried.")
        # A2 gap from the M5 test: a re-POST after the end used to show nothing.
        page = self.answer("99")
        self.assertEqual(self.element(page, "complete"),
                         "All problems finished! Final score: 2 right out of 3 tried.")
        self.assertEqual(self.element(page, "totals"), "Entries: 4 Correct: 2")


if __name__ == "__main__":
    unittest.main()
