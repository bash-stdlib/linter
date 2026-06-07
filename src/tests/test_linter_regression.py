"""Reproduction tests for reported namespace bugs."""

import unittest
from typing import Set, Dict, Any
from linter import Linter
from unittest.mock import patch, mock_open

class TestNamespaceRegression(unittest.TestCase):
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
                },
                "assert_rc": {
                    "name": "assert_rc",
                    "arguments": ["$1"],
                    "min_args": 1,
                    "max_args": 1,
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

    def test_lint__unknown_assert_prefix__is_ignored(self) -> None:
        # Known assert functions like assert_rc should still be linted for arguments.
        # But unknown ones like assert_custom should NOT be flagged as unknown standard library functions.
        content = "assert_rc\nassert_custom_func arg1"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        # Line 1: assert_rc is a function, needs 1 arg. Should have STD005.
        self.assertIn("STD005", error_codes)
        # Line 2: assert_custom_func is unknown but starts with assert_. Should have NO error (was STD004/STD002/STD001).
        # We need to make sure no error matches line 2.
        line2_errors = [e for e in errors if e.line == 2]
        self.assertEqual(len(line2_errors), 0, "Errors for unknown assert_: {}".format([e.CODE for e in line2_errors]))

if __name__ == "__main__":
    unittest.main()
