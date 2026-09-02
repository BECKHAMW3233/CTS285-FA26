"""Arithmetic rules shared by every activity: what counts as a valid
DataMan problem (no negative subtraction result, no unhandled
divide-by-zero) and the digit-count limits from Answer Checker
(Operating Notes), which the other activities reuse rather than
re-deriving."""

from .config import OPS


def compute(op, a, b):
    """Returns (result, remainder_or_None). Raises ValueError if invalid."""
    if op not in OPS:
        raise ValueError("bad operator")
    if op == "+":
        return a + b, None
    if op == "-":
        if b > a:
            # DataMan will not accept an operand that drives the result negative
            raise ValueError("negative_result")
        return a - b, None
    if op == "*":
        return a * b, None
    if op == "/":
        if b == 0:
            raise ValueError("divide_by_zero")
        return a // b, (a % b if a % b != 0 else None)


def validate_digits(a, b, answer=None):
    """Operands: 1-2 digits (0-99). Answer: 1-3 digits (0-999)."""
    if not (0 <= a <= 99) or not (0 <= b <= 99):
        raise ValueError("operand_out_of_range")
    if answer is not None and not (0 <= answer <= 999):
        raise ValueError("answer_out_of_range")


def invalid_problem_message(exc):
    return {
        "negative_result": "DataMan will not accept an operand that "
                            "would make the answer negative.",
        "divide_by_zero": "Cannot divide by zero.",
        "operand_out_of_range": "Operands must be one or two digits (0-99).",
    }.get(str(exc), "Invalid problem.")
