"""Reproduction tests for reported bugs."""

import unittest
from typing import Set, Dict, Any
from linter import Linter
from unittest.mock import patch, mock_open

class TestIssueReproduction(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": {
                "stdlib.array.assert.is_array": {
                    "name": "stdlib.array.assert.is_array",
                    "arguments": ["$1"],
                    "min_args": 1,
                    "max_args": 1,
                },
                "_testing.func": {
                    "name": "_testing.func",
                    "arguments": [],
                    "min_args": 0,
                    "max_args": 0,
                    "is_testing": True
                },
                "@parametrize.compose": {
                    "name": "@parametrize.compose",
                    "arguments": ["$1", "..."],
                    "min_args": 1,
                    "max_args": -1,
                    "is_testing": True
                }
            },
            "namespaces": [
                "stdlib",
                "stdlib.array",
                "stdlib.array.assert",
                "_testing",
                "_testing.example",
                "@parametrize"
            ],
        }

    def test_lint__match_in_comment__is_ignored(self) -> None:
        content = "# stdlib.array.assert.is_array\n_testing.func"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        self.assertNotIn("STD005", error_codes)

    def test_lint__code_after_comment__is_still_linted(self) -> None:
        content = "# some comment\nstdlib.array.assert.is_array" # Missing argument
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("script.sh")

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD005", error_codes, "Should still lint code after a comment")

    def test_lint__testing_namespace_in_test_file__is_flagged(self) -> None:
        content = "_testing.example"
        filepath = "/path/to/test_script.sh"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint(filepath)

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD003", error_codes, "Should flag _testing.example as a namespace violation in test files")

    def test_lint__parametrize_underscore_vs_dot__only_flags_dot(self) -> None:
        content = "@parametrize_with_error_messages\n@parametrize.with_error_messages"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        matches = [e.match for e in errors]
        self.assertNotIn("@parametrize_with_error_messages", matches)
        self.assertIn("@parametrize.with_error_messages", matches)

    def test_lint__multiple_violations_on_different_lines__all_caught(self) -> None:
        content = "stdlib.array.assert.is_array\nstdlib.array.assert.is_array a b"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("script.sh")

        self.assertEqual(len(errors), 2)
        self.assertEqual(errors[0].line, 1)
        self.assertEqual(errors[1].line, 2)

    def test_lint__quoted_hash__is_not_treated_as_comment(self) -> None:
        content = 'echo "# stdlib.array.assert.is_array"\nstdlib.array.assert.is_array'
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        # Line 2 should have STD005 (missing arg)
        self.assertIn("STD005", error_codes)

if __name__ == "__main__":
    unittest.main()
