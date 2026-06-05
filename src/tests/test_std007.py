"""Tests for linter error STD007: Testing function used in production script."""

import unittest
from unittest.mock import MagicMock

from errors import STD007
from validators import IsTestingFunctionCallValidator


class TestSTD007(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"assert_array_equals", "stdlib.string.echo"}
        self.namespaces = {"stdlib.string"}
        self.metadata = {
            "assert_array_equals": {"name": "assert_array_equals", "is_testing": True},
            "stdlib.string.echo": {"name": "stdlib.string.echo", "is_testing": False},
        }
        self.validator = IsTestingFunctionCallValidator(
            self.functions, self.namespaces, self.metadata
        )

    def test_check__testing_function_in_production_script__returns_std007(self) -> None:
        call = "assert_array_equals"
        file = "/path/to/script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, file, line, column)

        self.assertIsInstance(error, STD007)
        if error:
            self.assertEqual(error.CODE, "STD007")
            self.assertEqual(error.match, call)

    def test_check__testing_function_in_test_script__returns_none(self) -> None:
        call = "assert_array_equals"
        file = "/path/to/test_script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, file, line, column)

        self.assertIsNone(error)

    def test_check__non_testing_function_in_production_script__returns_none(self) -> None:
        call = "stdlib.string.echo"
        file = "/path/to/script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, file, line, column)

        self.assertIsNone(error)

    def test_format_message__returns_expected_string(self) -> None:
        error = STD007("/path/to/script.sh", 1, 1, "assert_array_equals")

        message = error.format_message()

        self.assertIn("'assert_array_equals' is being used in a production script", message)
        self.assertIn("path containing 'test'", message)


if __name__ == "__main__":
    unittest.main()
