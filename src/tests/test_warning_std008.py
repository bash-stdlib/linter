import unittest

from errors.enum import Severity
from errors.std008 import STD008


class TestWarningSTD008(unittest.TestCase):
    def test_format_message__always__returns_correct_message(self) -> None:
        issue = STD008("test.sh", 1, 1, "STD001")
        self.assertEqual(issue.message, "Unused ignore directive for 'STD001'.")
        self.assertEqual(issue.SEVERITY, Severity.WARNING)

    def test_to_dict__always__contains_expected_metadata(self) -> None:
        issue = STD008("test.sh", 1, 1, "STD001")
        result = issue.to_dict()
        self.assertEqual(result["code"], "STD008")
        self.assertEqual(result["severity"], Severity.WARNING.level)


if __name__ == "__main__":
    unittest.main()
