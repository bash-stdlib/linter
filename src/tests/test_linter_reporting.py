"""Unit tests for the linter reporting logic."""

import os
import unittest
from unittest.mock import MagicMock, mock_open, patch

from errors.std005 import STD005
from linter import Linter
from tests.assets.linter_reporting.metadata import METADATA


class TestLinterReporting(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def test_lint__filepath__is_absolute(self) -> None:
        content = "stdlib.array.assert"
        expected_path = os.path.abspath("test.sh")
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].file, expected_path)

    def test_get_line_number__content_offset__is_correct(self) -> None:
        content = "line1\nline2\nline3"
        offset = content.find("line2")

        result = self.linter._get_line_number(content, offset)

        self.assertEqual(result, 2)

    def test_get_column_number__content_offset__is_correct(self) -> None:
        content = "line1\nabcde"
        offset = content.find("c")

        result = self.linter._get_column_number(content, offset)

        self.assertEqual(result, 3)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="stdlib.array.assert.is_array\n"
        "stdlib.array.assert.is_array arg1 arg2",
    )
    def test_lint__issues__have_correct_coordinates(
        self,
        mock_file: MagicMock,
    ) -> None:
        linter = Linter(self.metadata)

        issues = linter.lint("dummy.sh")

        self.assertEqual(len(issues), 2)
        self.assertIsInstance(issues[0], STD005)
        self.assertEqual(issues[0].line, 1)
        self.assertIsInstance(issues[1], STD005)
        self.assertEqual(issues[1].line, 2)


if __name__ == "__main__":
    unittest.main()
