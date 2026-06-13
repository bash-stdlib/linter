"""Tests for mock validation in the linter."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.mock.metadata import METADATA, SCRIPTS


class TestMockValidation(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def test_lint__valid_global_mock__no_issues(self) -> None:
        content = SCRIPTS["valid_global_mock"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__mock_in_production__reports_std007(self) -> None:
        content = SCRIPTS["mock_in_production"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("production.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD007", codes)

    def test_lint__inactive_mock__reports_std010(self) -> None:
        content = SCRIPTS["inactive_mock"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD010", codes)

    def test_lint__sequential_mock_scope__no_issues(self) -> None:
        content = SCRIPTS["sequential_mock_scope"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__mock_stdlib_function__no_issues(self) -> None:
        content = SCRIPTS["mock_stdlib_function"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__invalid_mock_method__reports_std002(self) -> None:
        content = SCRIPTS["invalid_mock_method"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD002", codes)

    def test_lint__mock_method_wrong_args__reports_std005(self) -> None:
        content = SCRIPTS["mock_method_wrong_args"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        codes = [i.CODE for i in issues]
        self.assertIn("STD005", codes)

    def test_lint__mock_custom_function__no_issues(self) -> None:
        content = SCRIPTS["mock_custom_function"]

        with patch("builtins.open", mock_open(read_data=content)):
            issues = self.linter.lint("test_file.sh")

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
