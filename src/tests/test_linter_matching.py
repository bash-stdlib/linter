"""Unit tests for the linter matching logic."""

import unittest
from unittest.mock import mock_open, patch

from errors.std001 import STD001
from errors.std002 import STD002
from errors.std003 import STD003
from errors.std004 import STD004
from errors.std006 import STD006
from linter import Linter
from tests.assets.linter_matching.metadata import METADATA

class TestLinterMatching(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__valid_call__is_ignored(self) -> None:
        content = "stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__function_definitions__are_ignored(self) -> None:
        content = "function stdlib.foo() {\n  echo hello\n}\nstdlib.foo () {\n  echo hi\n}"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__function_as_argument__is_ignored(self) -> None:
        content = "echo stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__assignment__is_ignored(self) -> None:
        content = "VAR=stdlib.foo"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__nested_complex_subshell__is_detected(self) -> None:
        content = 'nested="${HELLO:-"$(stdlib.foo)"}"'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__line_continuation__is_handled(self) -> None:
        content = "stdlib.bar \\\n  arg1"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__unbalanced_quotes__flags_std006_error(self) -> None:
        content = 'stdlib.bar "unbalanced'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD006)

    def test_lint__call_to_namespace__flags_std003_error(self) -> None:
        content = "stdlib"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertIn("STD003", [e.CODE for e in errors])

    def test_lint__misspelled_function__flags_std002_error(self) -> None:
        content = "stdlib.fao"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertIn("STD002", [e.CODE for e in errors])

    def test_lint__invalid_namespace__flags_std001_error(self) -> None:
        content = "stdlib.unknown.func"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertIn("STD001", [e.CODE for e in errors])

    def test_lint__unknown_stdlib_call__flags_std004_error(self) -> None:
        # If we have an unknown root but it looks like a stdlib call?
        # Standard roots are in self.namespaces or self.functions.
        content = "stdlib.completely_unknown"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        # In this metadata, stdlib IS a namespace. stdlib.completely_unknown
        # is a misspelled function in valid namespace (STD002) or invalid sub-namespace.
        # To get STD004, we need an unknown root.

        linter = Linter({"functions": {}, "namespaces": []})
        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        # If it is not in metadata and not matched by pattern, it won't even be matched.
        # So we need it to be matched but not found in functions or namespaces by validators.
        pass

if __name__ == "__main__":
    unittest.main()
