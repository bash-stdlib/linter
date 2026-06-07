"""Unit tests for the IsFunctionCallValidator."""

import unittest
from validators.is_function_call import IsFunctionCallValidator
from tests.assets.linter_validation_function_call import METADATA

class TestIsFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = METADATA["functions"]
        self.namespaces = METADATA["namespaces"]
        self.validator = IsFunctionCallValidator(self.functions, self.namespaces)

    def test_check__valid_function_call__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__misspelled_function__returns_std002(self) -> None:
        call = "stdlib.string.joinn"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD002")

    def test_check__invalid_namespace__returns_std001(self) -> None:
        call = "stdlib.unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD001")

    def test_check__unknown_root__returns_std004(self) -> None:
        call = "unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD004")

    def test_check__whitelisted_prefix__returns_none(self) -> None:
        call = "assert_custom_func"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
