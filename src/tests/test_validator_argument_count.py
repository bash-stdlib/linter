"""Unit tests for the ArgumentCountValidator."""

import unittest
from validators.argument_count import ArgumentCountValidator
from tests.assets.linter_validation_argument_count import METADATA

class TestArgumentCountValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = set(METADATA.keys())
        self.namespaces = {"stdlib", "stdlib.string", "stdlib.array"}
        self.validator = ArgumentCountValidator(
            self.functions,
            self.namespaces,
            METADATA,
        )

    def test_check__valid_args__returns_none(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1", "arg2"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__valid_args_max__returns_none(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1", "arg2"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__too_few_args__returns_std005(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")

    def test_check__too_many_args__returns_std005(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1", "arg2", "arg3"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")

    def test_check__variadic_args__returns_none(self) -> None:
        call = "stdlib.string.join"
        args = ["arg1", "arg2", "arg3", "arg4"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__variadic_no_args__returns_std005(self) -> None:
        call = "stdlib.string.join"
        args = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")

if __name__ == "__main__":
    unittest.main()
