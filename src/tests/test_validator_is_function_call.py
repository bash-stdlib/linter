"""Unit tests for the IsFunctionCallValidator."""

import unittest
from typing import Set

from validators.is_function_call import IsFunctionCallValidator


class TestIsFunctionCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions: Set[str] = {"stdlib.string.join", "stdlib.array.push"}
        self.namespaces: Set[str] = {"stdlib", "stdlib.string", "stdlib.array"}
        self.validator = IsFunctionCallValidator(self.functions, self.namespaces)

    def test_check__valid_function__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__misspelled_function__returns_std002(self) -> None:
        call = "stdlib.string.jin"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD002")
        self.assertEqual(result.match, "stdlib.string.jin")

    def test_check__invalid_sub_namespace__returns_std001(self) -> None:
        call = "stdlib.unknown.func"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD001")
        self.assertEqual(getattr(result, "namespace", None), "stdlib.unknown")

    def test_check__completely_unknown__returns_std004(self) -> None:
        call = "unknown.command"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD004")


if __name__ == "__main__":
    unittest.main()
