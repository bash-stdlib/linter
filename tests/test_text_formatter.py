import unittest

from errors.std003 import STD003
from formatters.text_formatter import TextFormatter


class TestTextFormatter(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = TextFormatter()

    def test_format__single_issue__returns_formatted_string(self) -> None:
        issue = STD003("test.sh", 5, 10, "stdlib.ns")

        result = self.formatter.format([issue])

        self.assertIn("test.sh:5:10", result)
        self.assertIn("[STD003]", result)
        self.assertIn("'stdlib.ns' is a namespace", result)

    def test_format__no_issues__returns_empty_message(self) -> None:
        result = self.formatter.format([])

        self.assertEqual(result, "No issues found.")


if __name__ == "__main__":
    unittest.main()
