"""Tests for IsTestingFunctionCallValidator."""

import unittest

from errors import STD007
from validators import IsTestingFunctionCallValidator


class TestIsTestingFunctionCallValidator(unittest.TestCase):
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
        filepath = "/path/to/script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, filepath, line, column)

        self.assertIsInstance(error, STD007)
        if error:
            self.assertEqual(error.CODE, "STD007")
            self.assertEqual(error.match, call)

    def test_check__testing_function_in_test_script__returns_none(self) -> None:
        call = "assert_array_equals"
        filepath = "/path/to/test_script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, filepath, line, column)

        self.assertIsNone(error)

    def test_check__non_testing_function_in_production_script__returns_none(self) -> None:
        call = "stdlib.string.echo"
        filepath = "/path/to/script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, filepath, line, column)

        self.assertIsNone(error)

    def test_check__unknown_function__returns_none(self) -> None:
        call = "unknown_func"
        filepath = "/path/to/script.sh"
        line = 1
        column = 1

        error = self.validator.check(call, filepath, line, column)

        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
