from __future__ import annotations

import unittest
from typing import TYPE_CHECKING
from unittest.mock import mock_open, patch

from errors.std001 import STD001
from errors.std002 import STD002
from errors.std003 import STD003
from errors.std004 import STD004
from linter import Linter

if TYPE_CHECKING:
    from errors.base import LinterError
    from unittest.mock import MagicMock


class TestLinter(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": ["stdlib.array.assert.is_array", "stdlib.string.args.join"],
            "namespaces": [
                "stdlib",
                "stdlib.array",
                "stdlib.array.assert",
                "stdlib.string",
                "stdlib.string.args",
            ],
        }
        self.linter = Linter(self.metadata)

    def _lint_content(self, content: str) -> list[LinterError]:
        with patch("builtins.open", mock_open(read_data=content)):
            return self.linter.lint("test.sh")

    def test_lint__exact_match__returns_no_errors(self) -> None:
        errors = self._lint_content("stdlib.array.assert.is_array")

        self.assertEqual(len(errors), 0)

    def test_lint__call_to_namespace__returns_std003_error(self) -> None:
        errors = self._lint_content("stdlib.array.assert")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD003)

    def test_lint__misspelled_function__returns_std002_error(self) -> None:
        errors = self._lint_content("stdlib.array.assert.is_ary")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD002)
        self.assertIn(
            "Did you mean 'stdlib.array.assert.is_array'?", errors[0].message
        )

    def test_lint__invalid_sub_namespace__returns_std001_error(self) -> None:
        errors = self._lint_content("stdlib.array.unknown.func")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.array.unknown'", errors[0].message)

    def test_lint__invalid_root_namespace__returns_std001_error(self) -> None:
        errors = self._lint_content("stdlib.unknown.func")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.unknown'", errors[0].message)

    def test_lint__unknown_stdlib_call__returns_std004_error(self) -> None:
        # To get STD004, we need something that DOES NOT have any valid namespace prefix.
        # But all matches start with 'stdlib.' due to STDLIB_PATTERN.
        # 'stdlib' itself IS a namespace in our default metadata.
        # So we remove it to test STD004.
        self.metadata["namespaces"].remove("stdlib")
        self.linter = Linter(self.metadata)

        errors = self._lint_content("stdlib.completely_unknown")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD004)

    def test_get_line_number__content_offset__returns_correct_line(self) -> None:
        content = "line1\nline2\nline3"
        offset = content.find("line2")

        result = self.linter._get_line_number(content, offset)

        self.assertEqual(result, 2)

    def test_get_column_number__content_offset__returns_correct_column(self) -> None:
        content = "line1\nabcde"
        offset = content.find("c")

        result = self.linter._get_column_number(content, offset)

        self.assertEqual(result, 3)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="stdlib.array.assert.is_array\nstdlib.invalid",
    )
    def test_lint__script_with_error__returns_error_list_with_codes(
        self, mock_file: MagicMock
    ) -> None:
        errors = self.linter.lint("dummy.sh")

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD002)
        self.assertEqual(errors[0].match, "stdlib.invalid")
        self.assertEqual(errors[0].line, 2)


if __name__ == "__main__":
    unittest.main()
