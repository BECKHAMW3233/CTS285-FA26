"""Business logic layer.

Contains the rules and decisions. It does not print, read input, or know how
records are stored. Any interface (this text program now, Flask later) can call it.

Rules owned here:
- Parse/validate a submitted answer.
- Decide correct vs incorrect (PB-01).
- Assign and track the try number (the state the interface must NOT keep).
- Create one Attempt record per submission, correct or not (PB-02).
- Decide when a retry is allowed and when the answer is revealed.

The retry/reveal rule is a setting (max_tries), not a hard-coded requirement,
because it is an open question in the requirements register. Two tries is the
Design Studio's test case. Use max_tries=3 to model the original three-attempt flow.
"""

from dataclasses import dataclass
from typing import Optional

from data_stub import Attempt, InMemoryStore


@dataclass(frozen=True)
class CheckResult:
    correct: bool
    try_number: int
    max_tries: int
    can_retry: bool
    revealed_answer: Optional[int]  # set only after the last allowed miss
    attempt: Attempt


class AnswerChecker:
    def __init__(self, store: InMemoryStore, max_tries: int = 2):
        if max_tries < 1:
            raise ValueError("max_tries must be at least 1")
        self._store = store
        self._max_tries = max_tries

    @property
    def max_tries(self) -> int:
        return self._max_tries

    @staticmethod
    def parse_answer(raw: str) -> int:
        """Turn raw text into an integer answer. Raises ValueError if not a whole number."""
        try:
            text = raw.strip()
            if not text.isascii():  # only plain 0-9, no other numeral systems
                raise ValueError
            return int(text)
        except (ValueError, AttributeError):
            raise ValueError("Please enter a whole number.")

    def current_try_number(self, learner_id: str, problem_id: int) -> int:
        """Which try the next submission for this problem will be.

        A new round starts after a correct answer or after the answer was revealed.
        State comes from stored attempts, so it does not live in the interface.
        """
        tries_this_round = 0
        for attempt in self._store.attempts_for_problem(learner_id, problem_id):
            if attempt.correct or attempt.try_number >= self._max_tries:
                tries_this_round = 0  # round finished
            else:
                tries_this_round = attempt.try_number
        return tries_this_round + 1

    def submit_answer(self, learner_id: str, problem_id: int, raw_answer: str) -> CheckResult:
        submitted = self.parse_answer(raw_answer)  # invalid input is never recorded
        problem = self._store.get_problem(problem_id)
        try_number = self.current_try_number(learner_id, problem_id)
        correct = submitted == problem.correct_answer

        attempt = Attempt(
            attempt_id=self._store.next_attempt_id(),
            learner_id=learner_id,
            problem_id=problem_id,
            submitted_answer=submitted,
            correct=correct,
            try_number=try_number,
        )
        self._store.save_attempt(attempt)

        out_of_tries = (not correct) and try_number >= self._max_tries
        return CheckResult(
            correct=correct,
            try_number=try_number,
            max_tries=self._max_tries,
            can_retry=(not correct) and not out_of_tries,
            revealed_answer=problem.correct_answer if out_of_tries else None,
            attempt=attempt,
        )

    def history(self, learner_id: str):
        """Every recorded attempt for the learner, in order submitted."""
        return self._store.attempts_for_learner(learner_id)

    def correct_count(self, learner_id: str) -> int:
        return sum(1 for a in self.history(learner_id) if a.correct)
