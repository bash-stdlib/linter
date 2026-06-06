import unittest
from unittest.mock import mock_open, patch

from errors.std001 import STD001
from linter import Linter


class TestLinterSubshell(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
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

        self.assertTrue(any(isinstance(e, STD001) and e.namespace == "stdlib.invalid" for e in errors))

    def test_lint__command_in_unassigned_parameter_backticks__is_detected(self) -> None:
        content = '${HELLO:-`stdlib.invalid.call hello`}'

        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        self.assertTrue(any(isinstance(e, STD001) and e.namespace == "stdlib.invalid" for e in errors))

if __name__ == "__main__":
    unittest.main()
