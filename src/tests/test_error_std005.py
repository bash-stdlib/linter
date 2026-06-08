import unittest

from errors.enum import Severity
from errors.std005 import STD005


class TestSTD005(unittest.TestCase):
    def test_format_message__exact_args__returns_correct_message(self) -> None:
        error = STD005("test.sh", 1, 1, "func", 2, 1, 1)
        self.assertEqual(error.message, "'func' expects 1 arguments, but 2 were provided.")
        self.assertEqual(error.SEVERITY, Severity.ERROR)

    def test_format_message__range_args__returns_correct_message(self) -> None:
        error = STD005("test.sh", 1, 1, "func", 4, 1, 3)
        self.assertEqual(error.message, "'func' expects between 1 and 3 arguments, but 4 were provided.")

    def test_format_message__at_least_args__returns_correct_message(self) -> None:
        error = STD005("test.sh", 1, 1, "func", 0, 1, -1)
        self.assertEqual(error.message, "'func' expects at least 1 arguments, but 0 were provided.")

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD005("test.sh", 1, 1, "match", 1, 1, 1)
        result = error.to_dict()
        self.assertEqual(result["code"], "STD005")
        self.assertEqual(result["severity"], Severity.ERROR.level)


if __name__ == "__main__":
    unittest.main()
