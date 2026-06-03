"""Unit tests for the linter namespaces."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.namespaces.metadata import METADATA


class TestLinterNamespaces(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__testing_namespace_in_test_file__flags_std003(self) -> None:
        content = "_testing.example"
        filepath = "/path/to/test_script.sh"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint(filepath)

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD003", error_codes)

    def test_lint__parametrize_underscore__is_ignored(self) -> None:
        content = "@parametrize_with_error_messages"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__parametrize_dot__flags_error(self) -> None:
        content = "@parametrize.with_error_messages"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        matches = [e.match for e in errors]
        self.assertIn("@parametrize.with_error_messages", matches)

    def test_lint__unknown_assert_prefix__is_ignored(self) -> None:
        content = "assert_custom_func arg1"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__known_assert_prefix__is_linted_for_arguments(self) -> None:
        content = "assert_rc"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD005", error_codes)


if __name__ == "__main__":
    unittest.main()
