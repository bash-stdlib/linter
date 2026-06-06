"""Unit tests for the ArgumentCountValidator."""

import unittest
from typing import List, Set

from validators.argument_count import ArgumentCountValidator


class TestArgumentCountValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions: Set[str] = {"stdlib.foo.bar", "stdlib.baz.qux", "stdlib.variadic"}
        self.namespaces: Set[str] = {"stdlib.foo", "stdlib.baz"}
        self.metadata = {
            "stdlib.foo.bar": {"min_args": 1, "max_args": 2},
            "stdlib.baz.qux": {"min_args": 0, "max_args": 1},
            "stdlib.variadic": {"min_args": 1, "max_args": -1},
        }
        self.validator = ArgumentCountValidator(
            self.functions,
            self.namespaces,
            self.metadata,
        )

    def test_check__valid_args__returns_none(self) -> None:
        call = "stdlib.foo.bar"
        args = ["arg1"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__valid_args_max__returns_none(self) -> None:
        call = "stdlib.foo.bar"
        args = ["arg1", "arg2"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__too_few_args__returns_std005(self) -> None:
        call = "stdlib.foo.bar"
        args: List[str] = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")
        self.assertIn("expects between 1 and 2 arguments, but 0", result.message)

    def test_check__too_many_args__returns_std005(self) -> None:
        call = "stdlib.foo.bar"
        args = ["arg1", "arg2", "arg3"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")
        self.assertIn("expects between 1 and 2 arguments, but 3", result.message)

    def test_check__variadic_args__returns_none(self) -> None:
        call = "stdlib.variadic"
        args = ["arg1", "arg2", "arg3", "arg4"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__variadic_no_args__returns_std005(self) -> None:
        call = "stdlib.variadic"
        args: List[str] = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert result is not None
        self.assertEqual(result.CODE, "STD005")
        self.assertIn("expects at least 1 arguments, but 0", result.message)

if __name__ == "__main__":
    unittest.main()
