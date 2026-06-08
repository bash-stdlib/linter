import unittest

from errors.enum import Severity
from errors.std004 import STD004


class TestSTD004(unittest.TestCase):
    def test_format_message__always__returns_correct_message(self) -> None:
        error = STD004("test.sh", 1, 1, "stdlib.unknown")

        self.assertEqual(
            error.message,
            "Invalid namespace or function 'stdlib.unknown'.",
        )
        self.assertEqual(error.CODE, "STD004")
        self.assertEqual(error.SEVERITY, Severity.ERROR)

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD004("test.sh", 1, 1, "match")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD004")
        self.assertEqual(result["title"], "unknown namespace or function")
        self.assertEqual(result["severity"], Severity.ERROR.level)


if __name__ == "__main__":
    unittest.main()
