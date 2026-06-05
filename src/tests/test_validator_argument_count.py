"""Unit tests for the ArgumentCountValidator."""

import unittest

from validators.argument_count import ArgumentCountValidator


class TestArgumentCountValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"stdlib.foo.bar", "stdlib.baz.qux", "stdlib.variadic"}
        self.namespaces = {"stdlib.foo", "stdlib.baz"}
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
        args = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNotNone(result)
        self.assertEqual(result.CODE, "STD005")
        self.assertIn(
            "expects between 1 and 2 arguments, but 0",
            result.message,
        )

    def test_check__too_many_args__returns_std005(self) -> None:
        call = "stdlib.foo.bar"
        args = ["a1", "a2", "a3"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNotNone(result)
        self.assertEqual(result.CODE, "STD005")
        self.assertIn(
            "expects between 1 and 2 arguments, but 3",
            result.message,
        )

    def test_check__variadic_valid__returns_none(self) -> None:
        call = "stdlib.variadic"
        args = ["a"] * 10

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__variadic_invalid__returns_std005(self) -> None:
        call = "stdlib.variadic"
        args = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNotNone(result)
        self.assertEqual(result.CODE, "STD005")
        self.assertIn("expects at least 1 arguments, but 0", result.message)

    def test_check__unknown_function__returns_none(self) -> None:
        call = "stdlib.unknown"
        args = ["arg"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)
