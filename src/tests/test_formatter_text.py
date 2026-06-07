import unittest

from errors.std003 import STD003
from formatters.text_formatter import TextFormatterBase


class TestTextFormatterBase(unittest.TestCase):
    def setUp(self) -> None:
        self.formatter = TextFormatterBase()

    def test_format__single_error__returns_formatted_string(self) -> None:
        error = STD003("test.sh", 5, 10, "stdlib.ns")

        result = self.formatter.format([error])

        self.assertIn("test.sh:5:10", result)
        self.assertIn("[error:STD003]", result)
        self.assertIn("'stdlib.ns' is a namespace", result)

    def test_format__no_errors__returns_empty_message(self) -> None:
        result = self.formatter.format([])

        self.assertEqual(result, "No errors found.")


if __name__ == "__main__":
    unittest.main()
