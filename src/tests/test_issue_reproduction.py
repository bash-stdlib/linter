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
                }
            },
            "namespaces": [
                "stdlib",
                "stdlib.array",
                "stdlib.array.assert",
                "_testing",
                "_testing.example"
            ],
        }

    def test_lint__match_in_comment__is_ignored(self) -> None:
        content = "# stdlib.array.assert.is_array\necho 'hello'"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        self.assertNotIn("STD003", error_codes)
        self.assertNotIn("STD005", error_codes)

    def test_lint__testing_namespace_in_test_file__is_flagged(self) -> None:
        content = "_testing.example"
        filepath = "/path/to/test_script.sh"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint(filepath)

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD003", error_codes, "Should flag _testing.example as a namespace violation in test files")

if __name__ == "__main__":
    unittest.main()
