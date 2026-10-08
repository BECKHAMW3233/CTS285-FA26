"""Demonstrates acceptance criteria through the logic layer only (no interface involved).

Run:  python -m unittest test_criteria -v
"""

import unittest

from data_stub import InMemoryStore, Problem
from logic import AnswerChecker

LEARNER = "learner-1"


def make_checker(max_tries: int = 2) -> AnswerChecker:
    problems = [Problem(1, "7 x 8", 56), Problem(2, "9 x 6", 54), Problem(3, "12 - 5", 7)]
    return AnswerChecker(InMemoryStore(problems), max_tries=max_tries)


class PB02Criteria(unittest.TestCase):
    def test_pb02_criterion_3_three_answers_two_correct(self):
        """PB-02 #3: three submitted answers (two correct, one incorrect) give
        three history entries, exactly two marked correct."""
        checker = make_checker()
        checker.submit_answer(LEARNER, 1, "56")  # correct
        checker.submit_answer(LEARNER, 2, "50")  # incorrect
        checker.submit_answer(LEARNER, 3, "7")   # correct
        history = checker.history(LEARNER)
        self.assertEqual(len(history), 3)
        self.assertEqual(sum(1 for a in history if a.correct), 2)

    def test_pb01_criteria_1_2_result_for_correct_and_incorrect(self):
        """PB-01 #1 and #2: every submission gets a correct/incorrect result."""
        checker = make_checker()
        self.assertTrue(checker.submit_answer(LEARNER, 1, "56").correct)
        self.assertFalse(checker.submit_answer(LEARNER, 2, "1").correct)


class DesignQuestionChecks(unittest.TestCase):
    def test_first_and_second_miss_are_different_records(self):
        """The record must distinguish try 1 from try 2, and reveal only after the last miss."""
        checker = make_checker(max_tries=2)
        first = checker.submit_answer(LEARNER, 1, "10")
        self.assertEqual(first.try_number, 1)
        self.assertTrue(first.can_retry)
        self.assertIsNone(first.revealed_answer)
        second = checker.submit_answer(LEARNER, 1, "11")
        self.assertEqual(second.try_number, 2)
        self.assertFalse(second.can_retry)
        self.assertEqual(second.revealed_answer, 56)

    def test_try_state_lives_outside_the_interface(self):
        """Closed-after-Try-1: a brand-new checker over the same store still knows it is try 2."""
        checker = make_checker()
        store = checker._store
        checker.submit_answer(LEARNER, 1, "10")  # miss, then 'program closes'
        reopened = AnswerChecker(store, max_tries=2)
        self.assertEqual(reopened.current_try_number(LEARNER, 1), 2)

    def test_invalid_input_is_not_recorded(self):
        checker = make_checker()
        with self.assertRaises(ValueError):
            checker.submit_answer(LEARNER, 1, "abc")
        self.assertEqual(len(checker.history(LEARNER)), 0)

    def test_only_ascii_digits_are_accepted(self):
        """Non-ASCII numerals (for example Arabic-Indic digits) are rejected and not recorded."""
        checker = make_checker()
        for raw in ["٥٦", "５６", "5٦"]:
            with self.assertRaises(ValueError):
                checker.submit_answer(LEARNER, 1, raw)
        self.assertEqual(len(checker.history(LEARNER)), 0)
        self.assertTrue(checker.submit_answer(LEARNER, 1, "56").correct)

    def test_retry_reveal_rule_is_configurable(self):
        """Open question: the same logic works with three tries."""
        checker = make_checker(max_tries=3)
        checker.submit_answer(LEARNER, 1, "1")
        self.assertTrue(checker.submit_answer(LEARNER, 1, "2").can_retry)
        third = checker.submit_answer(LEARNER, 1, "3")
        self.assertEqual(third.revealed_answer, 56)


if __name__ == "__main__":
    unittest.main()
