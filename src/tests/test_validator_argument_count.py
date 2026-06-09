"""Unit tests for the ArgumentCountValidator."""

import unittest
from typing import List

from errors.std005 import STD005
from linter.state import LinterState
from tests.assets.validator_argument_count.metadata import METADATA
from validators.argument_count import ArgumentCountValidator


class TestArgumentCountValidator(unittest.TestCase):
    def setUp(self) -> None:
        metadata = {
            "functions": METADATA,
            "namespaces": ["stdlib", "stdlib.string", "stdlib.array"],
        }
        self.state = LinterState(metadata)
        self.validator = ArgumentCountValidator(self.state)

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

    def test_check__too_few_args__returns_std005_with_counts(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert isinstance(result, STD005)
        self.assertEqual(result.CODE, "STD005")
        self.assertEqual(result.actual_args, 1)
        self.assertEqual(result.min_args, 2)
        self.assertEqual(result.max_args, 2)

    def test_check__too_many_args__returns_std005_with_counts(self) -> None:
        call = "stdlib.array.push"
        args = ["arg1", "arg2", "arg3"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert isinstance(result, STD005)
        self.assertEqual(result.CODE, "STD005")
        self.assertEqual(result.actual_args, 3)
        self.assertEqual(result.min_args, 2)
        self.assertEqual(result.max_args, 2)

    def test_check__variadic_args__returns_none(self) -> None:
        call = "stdlib.string.join"
        args = ["arg1", "arg2", "arg3", "arg4"]

        result = self.validator.check(call, "test.sh", 1, 1, args)

        self.assertIsNone(result)

    def test_check__variadic_no_args__returns_std005_with_counts(self) -> None:
        call = "stdlib.string.join"
        args: List[str] = []

        result = self.validator.check(call, "test.sh", 1, 1, args)

        assert isinstance(result, STD005)
        self.assertEqual(result.CODE, "STD005")
        self.assertEqual(result.actual_args, 0)
        self.assertEqual(result.min_args, 1)
        self.assertEqual(result.max_args, -1)


if __name__ == "__main__":
    unittest.main()
