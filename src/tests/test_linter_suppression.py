"""Unit tests for the linter suppression logic."""

import unittest
from unittest.mock import mock_open, patch

from errors.enum import Severity
from linter import Linter
from tests.assets.linter_suppression.metadata import METADATA


class TestLinterSuppression(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__ignored_code__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["STD005"])

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__ignored_code_lowercase__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["std005"])

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__inline_disable_same_line__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 # stdlib: disable STD005"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in issues])

    def test_lint__inline_disable_previous_line__is_filtered(self) -> None:
        content = "# stdlib: disable STD005\nstdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in issues])

    def test_lint__file_level_disable__is_filtered(
        self,
    ) -> None:
        content = (
            "#!/bin/bash\n"
            "# stdlib: disable STD005\n"
            "stdlib.array.assert.is_array arg1 arg2\n"
            "stdlib.array.assert.is_array a b c"
        )
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in issues])

    def test_lint__unused_ignore__flags_error(self) -> None:
        content = "# stdlib: disable STD001\necho hello"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        issue_codes = [e.CODE for e in issues]
        self.assertIn("STD008", issue_codes)
        unused_issue = [e for e in issues if e.CODE == "STD008"][0]
        self.assertEqual(unused_issue.match, "STD001")
        self.assertEqual(unused_issue.SEVERITY, Severity.WARNING)


if __name__ == "__main__":
    unittest.main()
