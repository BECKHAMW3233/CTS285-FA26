"""PB-03 "See my current score" (FR-03), tested through the logic layer only.

Criteria: docs/product-backlog.md, PB-03. Score rule and uncertainty:
docs/design/m5-pb03-feature-brief.md.

Run from module-5-flask/:  python -m unittest discover -s tests -v
"""

import unittest

from business_logic import AnswerChecker
from data_store import InMemoryStore, Problem

LEARNER = "learner-1"


def make_checker(max_tries: int = 2) -> AnswerChecker:
    problems = [Problem(1, "7 x 8", 56), Problem(2, "9 x 6", 54), Problem(3, "12 - 5", 7)]
    return AnswerChecker(InMemoryStore(problems), max_tries=max_tries)


class PB03Criteria(unittest.TestCase):
    def test_criterion_2_incorrect_answer_does_not_increase_score(self):
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        before = checker.score(LEARNER).right
        checker.submit_answer(LEARNER, 2, "50")  # incorrect
        self.assertEqual(checker.score(LEARNER).right, before)

    def test_criterion_3_two_correct_one_incorrect(self):
        """Same answers as PB-02 #3 in the app: 56 (right), 50 (miss), 54 (right on try 2)."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        checker.submit_answer(LEARNER, 2, "50")
        checker.submit_answer(LEARNER, 2, "54")
        score = checker.score(LEARNER)
        self.assertEqual((score.right, score.tried), (2, 2))
        self.assertEqual(score.text, "2 right out of 2 tried")

    def test_criterion_3_with_three_different_problems(self):
        """Wording variant: the incorrect answer is a revealed problem, not a retried one."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        checker.submit_answer(LEARNER, 2, "1")
        checker.submit_answer(LEARNER, 2, "2")  # revealed
        checker.submit_answer(LEARNER, 3, "7")
        score = checker.score(LEARNER)
        self.assertEqual((score.right, score.tried), (2, 3))

    def test_criterion_4_score_updates_after_a_new_correct_answer(self):
        checker = make_checker()
        self.assertEqual(checker.score(LEARNER).right, 0)
        checker.submit_answer(LEARNER, 1, "56")
        self.assertEqual(checker.score(LEARNER).right, 1)


class ScoreRuleChecks(unittest.TestCase):
    def test_correct_on_try_2_counts_as_right(self):
        """Memory Bank: 'two tries to get it right'."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "10")
        checker.submit_answer(LEARNER, 1, "56")
        self.assertEqual(checker.score(LEARNER).right, 1)

    def test_revealed_problem_counts_as_tried_not_right(self):
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "10")
        checker.submit_answer(LEARNER, 1, "11")  # revealed
        score = checker.score(LEARNER)
        self.assertEqual((score.right, score.tried), (0, 1))

    def test_uncertainty_pending_retry_is_not_counted_as_tried(self):
        """The brief's open question: after a try-1 miss the score does not drop to 1 of 2."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        checker.submit_answer(LEARNER, 2, "50")  # miss, retry pending
        score = checker.score(LEARNER)
        self.assertEqual((score.right, score.tried), (1, 1))

    def test_score_counts_problems_not_correct_attempts(self):
        """Second question in the brief. submit_answer() lets a caller answer a
        finished problem again. That gives 2 correct attempts but only 1 problem right."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        checker.submit_answer(LEARNER, 1, "56")  # problem already finished
        self.assertEqual(checker.correct_count(LEARNER), 2)
        self.assertEqual(checker.score(LEARNER).right, 1)

    def test_score_is_derived_from_stored_attempts_not_kept_in_the_checker(self):
        """Same shape as the M4 try-state test: a new checker over the same store agrees."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")
        checker.submit_answer(LEARNER, 2, "50")
        reopened = AnswerChecker(checker._store, max_tries=2)
        self.assertEqual(reopened.score(LEARNER), checker.score(LEARNER))

    def test_score_follows_the_configurable_retry_rule(self):
        checker = make_checker(max_tries=3)
        checker.submit_answer(LEARNER, 1, "1")
        checker.submit_answer(LEARNER, 1, "2")
        self.assertEqual(checker.score(LEARNER).tried, 0)  # third try still allowed
        checker.submit_answer(LEARNER, 1, "3")
        self.assertEqual(checker.score(LEARNER).tried, 1)

    def test_other_learners_do_not_change_the_score(self):
        checker = make_checker()
        checker.submit_answer("learner-2", 1, "56")
        self.assertEqual((checker.score(LEARNER).right, checker.score(LEARNER).tried), (0, 0))


if __name__ == "__main__":
    unittest.main()
