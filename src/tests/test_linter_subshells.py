import unittest
from unittest.mock import mock_open, patch
from typing import Any, Dict

from errors.std001 import STD001
from linter import Linter


class TestLinterSubshell(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata: Dict[str, Any] = {
            "functions": {
                "stdlib.echo": {
                    "name": "stdlib.echo",
                    "min_args": 1,
                    "max_args": -1,
                }
            },
            "namespaces": ["stdlib"],
        }
        self.linter = Linter(self.metadata)

    def test_lint__command_in_nested_parameter_subshell__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.invalid.call hello)"}"'

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertTrue(any(isinstance(e, STD001) and getattr(e, "namespace", None) == "stdlib.invalid" for e in errors))

    def test_lint__command_in_unassigned_parameter_backticks__is_detected(self) -> None:
        content = '${HELLO:-`stdlib.invalid.call hello`}'

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertTrue(any(isinstance(e, STD001) and getattr(e, "namespace", None) == "stdlib.invalid" for e in errors))

    def test_lint__command_in_complex_nested_expansion__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.some.command arg1 arg2)"}"'
        self.metadata["functions"]["stdlib.some.command"] = {
            "name": "stdlib.some.command",
            "min_args": 2,
            "max_args": 2,
        }
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

if __name__ == "__main__":
    unittest.main()
