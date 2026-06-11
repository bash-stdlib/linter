import os
import unittest
from typing import TYPE_CHECKING, List
from unittest.mock import MagicMock, mock_open, patch

from issues.errors.STD001 import STD001
from issues.errors.STD002 import STD002
from issues.errors.STD003 import STD003
from issues.errors.STD004 import STD004
from issues.errors.STD005 import STD005
from issues.errors.STD006 import STD006
from linter import Linter
from tests.assets.linter.core.metadata import METADATA

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class TestLinter(unittest.TestCase):
    def setUp(self) -> "None":
        self.metadata = METADATA
        self.linter = Linter(self.metadata)

    def _lint_content(self, content: "str") -> "List[LinterIssueBase]":
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_lint__script_path__returns_absolute_path(self) -> "None":
        content = "stdlib.array.assert"
        expected_path = os.path.abspath("test.sh")

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].file, expected_path)

    def test_lint__exact_match__returns_no_issues(self) -> "None":
        content = "stdlib.array.assert.is_array arg1"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_lint__call_to_namespace__returns_std003_error(self) -> "None":
        content = "stdlib.array.assert"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD003)

    def test_lint__misspelled_function__returns_std002_error(self) -> "None":
        content = "stdlib.array.assert.is_ary arg1"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD002)
        self.assertIn("Did you mean 'stdlib.array.assert.is_array'?", issues[0].message)

    def test_lint__invalid_sub_namespace__returns_std001_error(self) -> "None":
        content = "stdlib.array.unknown.func arg1"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.array.unknown'", issues[0].message)

    def test_lint__invalid_root_namespace__returns_std001_error(self) -> "None":
        content = "stdlib.unknown.func arg1"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.unknown'", issues[0].message)

    def test_lint__unknown_stdlib_call__returns_std004_error(self) -> "None":
        self.metadata["namespaces"] = [
            ns for ns in self.metadata["namespaces"] if ns != "stdlib"
        ]
        self.linter = Linter(self.metadata)
        content = "stdlib.completely_unknown arg1"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD004)

    def test_get_line_number__content_offset__returns_correct_line(self) -> "None":
        content = "line1\nline2\nline3"
        offset = content.find("line2")

        result = self.linter._get_line_number(content, offset)

        self.assertEqual(result, 2)

    def test_get_column_number__content_offset__returns_correct_column(self) -> "None":
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
    def test_lint__script_with_error__returns_error_list_with_codes(
        self,
        mock_file: "MagicMock",
    ) -> "None":
        linter = Linter(self.metadata)

        issues = linter.lint("dummy.sh")

        self.assertEqual(len(issues), 2)
        self.assertIsInstance(issues[0], STD005)
        self.assertEqual(issues[0].line, 1)
        self.assertIsInstance(issues[1], STD005)
        self.assertEqual(issues[1].line, 2)

    def test_lint__unbalanced_quotes__returns_std006_error(self) -> "None":
        content = 'stdlib.array.assert.is_array "unbalanced'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD006)
        self.assertIn("Failed to parse arguments", issues[0].message)

    def test_lint__ignored_error_code__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["STD005"])

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0, "Errors: {}".format([e.CODE for e in issues]))

    def test_lint__ignored_error_code_lowercase__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["std005"])

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(
            len(issues),
            0,
            "Errors found: {}".format([(e.CODE, e.message) for e in issues]),
        )

    def test_lint__comment_disable_same_line__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 # stdlib: disable STD005"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in issues])

    def test_lint__comment_disable_previous_line__filters_out_error(self) -> "None":
        content = "# stdlib: disable STD005\nstdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertNotIn("STD005", [e.CODE for e in issues])

    def test_lint__comment_disable_file_level__filters_out_all_matching_issues(
        self,
    ) -> "None":
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

    def test_lint__unused_ignore__returns_std008_error(self) -> "None":
        content = "# stdlib: disable STD001\necho hello"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        error_codes = [e.CODE for e in issues]
        self.assertIn("STD008", error_codes)
        unused_error = [e for e in issues if e.CODE == "STD008"][0]
        self.assertEqual(unused_error.match, "STD001")


if __name__ == "__main__":
    unittest.main()
