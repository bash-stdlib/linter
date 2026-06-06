"""Unit tests for the IsTestingFunctionCallValidator."""

import unittest
from typing import Dict, Set

from validators.is_testing_function_call import IsTestingFunctionCallValidator


class TestIsTestingFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions: Set[str] = {"stdlib.test.func", "stdlib.prod.func"}
        self.namespaces: Set[str] = {"stdlib.test", "stdlib.prod"}
        self.metadata = {
            "stdlib.test.func": {"is_testing": True},
            "stdlib.prod.func": {"is_testing": False},
        }
        self.validator = IsTestingFunctionCallValidator(
            self.functions,
            self.namespaces,
            self.metadata,
        )

    def test_check__testing_func_in_test_file__returns_none(self) -> None:
        call = "stdlib.test.func"
        filepath = "/path/to/test_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        self.assertIsNone(result)

    def test_check__testing_func_in_prod_file__returns_std007(self) -> None:
        call = "stdlib.test.func"
        filepath = "/path/to/prod_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD007")

    def test_check__prod_func_in_prod_file__returns_none(self) -> None:
        call = "stdlib.prod.func"
        filepath = "/path/to/prod_script.sh"

        result = self.validator.check(call, filepath, 1, 1)

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
