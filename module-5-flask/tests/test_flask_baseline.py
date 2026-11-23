"""Change-impact baseline: behavior the Flask app already had before PB-03.

These reproduce the M5 acceptance scenarios (docs/evidence/m5-acceptance-test.md)
through Flask's test client, so they exercise route -> logic -> store -> template.
They were committed and passing BEFORE any PB-03 code. After PB-03 they must
still pass unchanged; a failure here means the extension altered old behavior.

Run from module-5-flask/:  python -m unittest discover -s tests -v
"""

import re
import unittest
from unittest import mock

import data_store
from app import app


class FlaskTestCase(unittest.TestCase):
    """Each test gets a new, empty in-memory store, the same as a fresh server process."""

    def setUp(self):
        patcher = mock.patch.object(data_store, "_STORE", data_store.InMemoryStore())
        patcher.start()
        self.addCleanup(patcher.stop)
        self.client = app.test_client()

    def get(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    def answer(self, value):
        response = self.client.post("/", data={"answer": value})
        self.assertEqual(response.status_code, 200)
        return response.get_data(as_text=True)

    @staticmethod
    def element(page, element_id):
        """Text inside the element with this id, with tags removed and whitespace collapsed."""
        match = re.search(rf'id="{element_id}"[^>]*>(.*?)</(p|ul|div|section)>', page, re.S)
        if not match:
            return None
        return " ".join(re.sub(r"<[^>]+>", " ", match.group(1)).split())

    @staticmethod
    def history(page):
        return [" ".join(re.sub(r"<[^>]+>", "", li).split())
                for li in re.findall(r"<li>(.*?)</li>", page, re.S)]


class ScenarioA_PB02Criterion3(FlaskTestCase):
    def test_three_answers_two_correct(self):
        """PB-02 #3 and PB-01 #1-2 over HTTP: 56, 50, 54 -> 3 entries, 2 correct."""
        self.assertIn("Problem: 7 x 8 = ?", self.get())
        self.assertIn("[Try 1 of 2] Correct!", self.answer("56"))
        page = self.answer("50")
        self.assertIn("[Try 1 of 2] EEE - Not quite. Try again.", page)
        self.assertIn("Problem: 9 x 6 = ?", page)
        page = self.answer("54")
        self.assertIn("[Try 2 of 2] Correct!", page)
        self.assertIn("Problem: 12 - 5 = ?", page)
        self.assertEqual(self.history(page), [
            "#1: 7 x 8 -> 56 (correct, try 1)",
            "#2: 9 x 6 -> 50 (incorrect, try 1)",
            "#3: 9 x 6 -> 54 (correct, try 2)",
        ])
        self.assertEqual(self.element(page, "totals"), "Entries: 3 Correct: 2")


class ScenarioA2_Reveal(FlaskTestCase):
    def test_reveal_after_last_miss_and_repost_not_recorded(self):
        for value in ("56", "54"):
            self.answer(value)
        self.assertIn("[Try 1 of 2] EEE - Not quite. Try again.", self.answer("1"))
        page = self.answer("2")
        self.assertIn("[Try 2 of 2] EEE - The answer is 7.", page)
        self.assertNotIn('<form', page)
        self.assertEqual(self.element(page, "totals"), "Entries: 4 Correct: 2")
        page = self.answer("99")  # every problem finished: nothing recorded
        self.assertEqual(self.element(page, "totals"), "Entries: 4 Correct: 2")


class ScenarioB_InvalidInput(FlaskTestCase):
    def test_invalid_input_rejected_and_not_recorded(self):
        for raw in ("abc", "5_6", "", "٥٦"):
            page = self.answer(raw)
            self.assertIn("Please enter a whole number.", page)
            self.assertEqual(self.element(page, "totals"), "Entries: 0 Correct: 0")
        self.assertIn("Problem: 7 x 8 = ?", page)


if __name__ == "__main__":
    unittest.main()
