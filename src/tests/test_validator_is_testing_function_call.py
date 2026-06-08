"""Unit tests for the IsTestingFunctionCallValidator."""

import unittest

from tests.assets.linter_validation_testing_call import FUNCTIONS, METADATA, NAMESPACES
from validators.is_testing_function_call import IsTestingFunctionCallValidator


class TestIsTestingFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        from linter.state import LinterState

        self.functions = FUNCTIONS
        self.namespaces = NAMESPACES
        self.metadata = METADATA
        metadata = {
            "functions": self.metadata,
            "namespaces": list(self.namespaces),
        }
        self.state = LinterState(metadata)
        self.validator = IsTestingFunctionCallValidator(self.state)

    def test_check__testing_func__in_test_file__returns_none(self) -> None:
        call = "stdlib.test.func"
        filepath = "/path/to/test_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        self.assertIsNone(result)

    def test_check__testing_func__in_prod_file__returns_std007(self) -> None:
        call = "stdlib.test.func"
        filepath = "/path/to/prod_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD007")

    def test_check__prod_func__in_prod_file__returns_none(self) -> None:
        call = "stdlib.prod.func"
        filepath = "/path/to/prod_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
