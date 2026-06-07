"""Tests for linter error STD007: Testing function used in production script."""

import unittest

from errors import STD007


class TestSTD007(unittest.TestCase):
    def test_format_message__valid_metadata__returns_expected_string(self) -> None:
        error = STD007("/path/to/script.sh", 1, 1, "assert_array_equals")

        message = error.format_message()

        self.assertIn(
            "'assert_array_equals' is being used in a production script", message
        )
        self.assertIn("path containing 'test'", message)

    def test_to_dict__valid_metadata__returns_expected_dictionary(self) -> None:
        error = STD007("/path/to/script.sh", 10, 5, "assert_rc")

        result = error.to_dict()

        self.assertEqual(result["code"], "STD007")
        self.assertEqual(result["line"], 10)
        self.assertEqual(result["column"], 5)
        self.assertEqual(result["match"], "assert_rc")


if __name__ == "__main__":
    unittest.main()
