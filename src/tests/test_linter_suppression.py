"""Unit tests for the linter suppression logic."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter_suppression.metadata import METADATA


class TestLinterSuppression(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__ignored_code__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["STD005"])

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__ignored_code_lowercase__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["std005"])

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__inline_disable_same_line__is_filtered(self) -> None:
        content = "stdlib.array.assert.is_array arg1 # stdlib: disable STD005"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in errors])

    def test_lint__inline_disable_previous_line__is_filtered(self) -> None:
        content = "# stdlib: disable STD005\nstdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in errors])

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
            errors = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in errors])

    def test_lint__unused_ignore__flags_error(self) -> None:
        content = "# stdlib: disable STD001\necho hello"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        error_codes = [e.CODE for e in errors]
        self.assertIn("STD008", error_codes)
        unused_error = [e for e in errors if e.CODE == "STD008"][0]
        self.assertEqual(unused_error.match, "STD001")


if __name__ == "__main__":
    unittest.main()
