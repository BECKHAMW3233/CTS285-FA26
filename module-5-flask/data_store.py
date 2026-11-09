"""Stubbed data layer (in-memory).

Holds Problem and Attempt records and exposes a small set of access functions.
Nothing outside this file knows the records live in a Python list. To move to a
real database later, replace InMemoryStore with a class that has the same methods;
logic.py and main.py should not need to change.

INTENTIONALLY STUBBED:
- Storage is in memory only, so nothing survives a closed program (PB-04a/b).
- Learner identity is a placeholder string. The identity/session approach is unresolved.
- No Practice Set and no 10-problem limit. Those came from the Design Studio scenario,
  not from PB-01/PB-02 or the requirements register.
"""

from dataclasses import dataclass
from typing import List, Optional

PLACEHOLDER_LEARNER_ID = "learner-1"


@dataclass(frozen=True)
class Problem:
    problem_id: int
    prompt: str
    correct_answer: int


@dataclass(frozen=True)
class Attempt:
    attempt_id: int
    learner_id: str
    problem_id: int
    submitted_answer: int
    correct: bool
    try_number: int


class InMemoryStore:
    """Replaceable data boundary. Only stores and returns records; makes no decisions."""

    def __init__(self, problems: Optional[List[Problem]] = None):
        self._problems = list(problems) if problems is not None else default_problems()
        self._attempts: List[Attempt] = []
        self._next_attempt_id = 1

    # ---- problems ----
    def list_problems(self) -> List[Problem]:
        return list(self._problems)

    def get_problem(self, problem_id: int) -> Problem:
        for problem in self._problems:
            if problem.problem_id == problem_id:
                return problem
        raise KeyError(f"No problem with id {problem_id}")

    # ---- attempts ----
    def next_attempt_id(self) -> int:
        attempt_id = self._next_attempt_id
        self._next_attempt_id += 1
        return attempt_id

    def save_attempt(self, attempt: Attempt) -> None:
        self._attempts.append(attempt)

    def attempts_for_learner(self, learner_id: str) -> List[Attempt]:
        return [a for a in self._attempts if a.learner_id == learner_id]

    def attempts_for_problem(self, learner_id: str, problem_id: int) -> List[Attempt]:
        return [
            a
            for a in self._attempts
            if a.learner_id == learner_id and a.problem_id == problem_id
        ]


def default_problems() -> List[Problem]:
    return [
        Problem(1, "7 x 8", 56),
        Problem(2, "9 x 6", 54),
        Problem(3, "12 - 5", 7),
    ]
