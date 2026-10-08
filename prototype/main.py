"""Text interface layer (entry point).

Run:  python main.py            (two tries, the Design Studio test case)
      python main.py --tries 3  (original three-attempt flow, still an open question)

This file only reads input and prints output. It holds no try counter and makes
no correctness decisions. Everything it shows comes from logic.py.
"""

import argparse

from data_stub import PLACEHOLDER_LEARNER_ID, InMemoryStore
from logic import AnswerChecker


def ask_problem(checker: AnswerChecker, store: InMemoryStore, problem) -> bool:
    """Run one problem until it is answered correctly or revealed. Returns False if the learner quits."""
    print(f"\nProblem: {problem.prompt} = ?")
    while True:
        raw = input("Your answer (or q to quit): ")
        if raw.strip().lower() == "q":
            return False
        try:
            result = checker.submit_answer(PLACEHOLDER_LEARNER_ID, problem.problem_id, raw)
        except ValueError as error:
            print(f"  {error}")  # nothing was recorded
            continue

        label = f"Try {result.try_number} of {result.max_tries}"
        if result.correct:
            print(f"  [{label}] Correct!")
            return True
        if result.can_retry:
            print(f"  [{label}] EEE - Not quite. Try again.")
        else:
            print(f"  [{label}] EEE - The answer is {result.revealed_answer}.")
            return True


def print_history(checker: AnswerChecker, store: InMemoryStore) -> None:
    attempts = checker.history(PLACEHOLDER_LEARNER_ID)
    print("\n--- Practice history (this session only) ---")
    if not attempts:
        print("No answers recorded.")
        return
    for a in attempts:
        prompt = store.get_problem(a.problem_id).prompt
        mark = "correct" if a.correct else "incorrect"
        print(f"  #{a.attempt_id}: {prompt} -> {a.submitted_answer} ({mark}, try {a.try_number})")
    print(f"Entries: {len(attempts)}   Correct: {checker.correct_count(PLACEHOLDER_LEARNER_ID)}")


def main() -> None:
    parser = argparse.ArgumentParser(description="DataMan text-only prototype")
    parser.add_argument("--tries", type=int, default=2, help="tries before reveal (default 2)")
    args = parser.parse_args()
    if args.tries < 1:
        parser.error("--tries must be at least 1")

    store = InMemoryStore()
    checker = AnswerChecker(store, max_tries=args.tries)

    print("DataMan text-only prototype. Records are kept in memory only.")
    try:
        for problem in store.list_problems():
            if not ask_problem(checker, store, problem):
                break
    except (EOFError, KeyboardInterrupt):
        print("\nInput ended. Exiting.")  # attempts already submitted stay recorded
    print_history(checker, store)


if __name__ == "__main__":
    main()
