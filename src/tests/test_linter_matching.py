"""Unit tests for the linter matching logic."""

import unittest
from unittest.mock import mock_open, patch

from issues.errors.STD006 import STD006
from linter import Linter
from tests.assets.linter.matching.metadata import METADATA


class TestLinterMatching(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__valid_call__is_ignored(self) -> None:
        content = "stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__function_definitions__are_ignored(self) -> None:
        content = (
            "function stdlib.foo() {\n  echo hello\n}\nstdlib.foo () {\n  echo hi\n}"
        )
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__function_as_argument__is_ignored(self) -> None:
        content = "echo stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__assignment__is_ignored(self) -> None:
        content = "VAR=stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__nested_complex_subshell__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.foo)"}"'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__line_continuation__is_handled(self) -> None:
        content = "stdlib.bar \\\n  arg1"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__unbalanced_quotes__flags_std006_error(self) -> None:
        content = 'stdlib.bar "unbalanced'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD006)

    def test_lint__call_to_namespace__flags_std003_error(self) -> None:
        content = "stdlib"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertIn("STD003", [e.CODE for e in issues])

    def test_lint__misspelled_function__flags_std002_error(self) -> None:
        content = "stdlib.fao"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertIn("STD002", [e.CODE for e in issues])

    def test_lint__invalid_namespace__flags_std001_error(self) -> None:
        content = "stdlib.unknown.func"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertIn("STD001", [e.CODE for e in issues])

    def test_lint__unknown_stdlib_call__flags_std004_error(self) -> None:
        # To get STD004, the name must match the root pattern but NOT have a valid
        # namespace prefix.
        # This happens if a root is matched but it is not in the namespaces list and
        # is a function.
        metadata = {"functions": {"stdlib": {}}, "namespaces": []}
        linter = Linter(metadata)
        content = "stdlib.unknown"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertIn("STD004", [e.CODE for e in issues])


if __name__ == "__main__":
    unittest.main()
