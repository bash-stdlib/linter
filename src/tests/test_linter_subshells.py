"""Unit tests for the linter subshell logic."""

import unittest
from unittest.mock import mock_open, patch

from errors.std001 import STD001
from linter import Linter
from tests.assets.linter_subshells.metadata import METADATA

class TestLinterSubshells(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__command_in_nested_parameter_subshell__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.invalid.call hello)"}"'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertTrue(any(isinstance(e, STD001) and getattr(e, "namespace", None) == "stdlib.invalid" for e in errors))

    def test_lint__command_in_unassigned_parameter_backticks__is_detected(self) -> None:
        content = '${HELLO:-`stdlib.invalid.call hello`}'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertTrue(any(isinstance(e, STD001) and getattr(e, "namespace", None) == "stdlib.invalid" for e in errors))

    def test_lint__command_in_complex_nested_expansion__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.some.command arg1 arg2)"}"'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
