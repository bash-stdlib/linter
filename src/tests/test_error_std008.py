import unittest

from errors.base import Severity
from errors.std008 import STD008


class TestSTD008(unittest.TestCase):
    def test_format_message__valid_exception__returns_correct_message(self) -> None:
        error = STD008("test.sh", 1, 1, "STD001")

        self.assertEqual(error.SEVERITY, Severity.WARNING)
        self.assertEqual(error.CODE, "STD008")
        self.assertEqual(error.message, "Unused ignore directive for 'STD001'.")

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        error = STD008("test.sh", 1, 1, "STD001")

        result = error.to_dict()

        self.assertEqual(result["severity"], "warning")
        self.assertEqual(result["code"], "STD008")


if __name__ == "__main__":
    unittest.main()
