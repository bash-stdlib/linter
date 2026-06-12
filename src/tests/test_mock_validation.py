"""Tests for mock validation in the linter."""

import unittest
from typing import Any, Dict
from unittest.mock import mock_open, patch
from linter import Linter

class TestMockValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata: Dict[str, Any] = {
            "functions": {
                "stdlib.io.print": {
                    "name": "stdlib.io.print",
                    "min_args": 1,
                    "max_args": -1,
                },
                "_mock.create": {
                    "name": "_mock.create",
                    "min_args": 1,
                    "max_args": 1,
                },
                "_mock.delete": {
                    "name": "_mock.delete",
                    "min_args": 1,
                    "max_args": 1,
                },
                "object.mock.assert_not_called": {
                    "name": "object.mock.assert_not_called",
                    "min_args": 0,
                    "max_args": 0,
                },
                "object.mock.clear": {
                    "name": "object.mock.clear",
                    "min_args": 0,
                    "max_args": 0,
                },
                "object.mock.assert_called_once_with": {
                    "name": "object.mock.assert_called_once_with",
                    "min_args": 1,
                    "max_args": 1,
                }
            },
            "namespaces": ["stdlib", "stdlib.io", "_mock", "object", "object.mock"],
        }
        self.linter = Linter(self.metadata)

    def test_lint__valid_global_mock__no_issues(self) -> None:
        content = """_mock.create ls
ls.mock.assert_not_called
ls -la"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        self.assertEqual(len(issues), 0, f"Expected no issues, found: {issues}")

    def test_lint__mock_in_production__reports_STD007(self) -> None:
        content = """_mock.create ls"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("production.sh")
        codes = [i.CODE for i in issues]
        self.assertIn("STD007", codes)

    def test_lint__inactive_mock__reports_STD010(self) -> None:
        content = """_mock.create ls
_mock.delete ls
ls.mock.assert_not_called"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        codes = [i.CODE for i in issues]
        self.assertIn("STD010", codes)

    def test_lint__sequential_mock_scope(self) -> None:
        content = """my_func() {
  _mock.create grep
  grep.mock.assert_not_called
}
grep.mock.assert_not_called"""
        # Mocks are sequential and stay active after creation
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        self.assertEqual(len(issues), 0, f"Expected no issues, found: {issues}")

    def test_lint__mock_stdlib_function(self) -> None:
        content = """_mock.create stdlib.io.print
stdlib.io.print "hello"
stdlib.io.print.mock.assert_not_called"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        self.assertEqual(len(issues), 0, f"Expected no issues, found: {issues}")

    def test_lint__invalid_mock_method__reports_STD002(self) -> None:
        content = """_mock.create ls
ls.mock.invalid_method"""
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        codes = [i.CODE for i in issues]
        self.assertIn("STD002", codes)

    def test_lint__mock_method_wrong_args__reports_STD005(self) -> None:
        content = """_mock.create ls
ls.mock.assert_called_once_with""" # Expects 1 arg
        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")
        codes = [i.CODE for i in issues]
        self.assertIn("STD005", codes)

if __name__ == "__main__":
    unittest.main()
