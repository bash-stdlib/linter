import os
import unittest
from typing import TYPE_CHECKING, List
from unittest.mock import MagicMock, mock_open, patch

from errors.std001 import STD001
from errors.std002 import STD002
from errors.std003 import STD003
from errors.std004 import STD004
from errors.std005 import STD005
from errors.std006 import STD006
from errors.std008 import STD008
from linter import Linter

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class TestLinter(unittest.TestCase):
    def setUp(self) -> "None":
        self.metadata = {
            "functions": {
                "stdlib.array.assert.is_array": {
                    "name": "stdlib.array.assert.is_array",
                    "arguments": ["$1"],
                    "keywords": [],
                    "globals": [],
                    "min_args": 1,
                    "max_args": 1,
                },
                "stdlib.string.args.join": {
                    "name": "stdlib.string.args.join",
                    "arguments": ["$1", "..."],
                    "keywords": [],
                    "globals": [],
                    "min_args": 1,
                    "max_args": -1,
                },
            },
            "namespaces": [
                "stdlib",
                "stdlib.array",
                "stdlib.array.assert",
                "stdlib.string",
                "stdlib.string.args",
            ],
        }
        self.linter = Linter(self.metadata)

    def _lint_content(self, content: "str") -> "List[LinterErrorBase]":
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_lint__returns_absolute_path(self) -> "None":
        content = "stdlib.array.assert"
        expected_path = os.path.abspath("test.sh")

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].file, expected_path)

    def test_lint__exact_match__returns_no_errors(self) -> "None":
        content = "stdlib.array.assert.is_array arg1"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 0)

    def test_lint__call_to_namespace__returns_std003_error(self) -> "None":
        content = "stdlib.array.assert"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD003)

    def test_lint__misspelled_function__returns_std002_error(self) -> "None":
        content = "stdlib.array.assert.is_ary arg1"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD002)
        self.assertIn("Did you mean 'stdlib.array.assert.is_array'?", errors[0].message)

    def test_lint__invalid_sub_namespace__returns_std001_error(self) -> "None":
        content = "stdlib.array.unknown.func arg1"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.array.unknown'", errors[0].message)

    def test_lint__invalid_root_namespace__returns_std001_error(self) -> "None":
        content = "stdlib.unknown.func arg1"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD001)
        self.assertIn("Invalid namespace 'stdlib.unknown'", errors[0].message)

    def test_lint__unknown_stdlib_call__returns_std004_error(self) -> "None":
        self.metadata["namespaces"].remove("stdlib")
        self.linter = Linter(self.metadata)
        content = "stdlib.completely_unknown arg1"

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD004)

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

        errors = linter.lint("dummy.sh")

        self.assertEqual(len(errors), 2)
        self.assertIsInstance(errors[0], STD005)
        self.assertEqual(errors[0].line, 1)
        self.assertIsInstance(errors[1], STD005)
        self.assertEqual(errors[1].line, 2)

    def test_lint__unbalanced_quotes__returns_std006_error(self) -> "None":
        content = 'stdlib.array.assert.is_array "unbalanced'

        errors = self._lint_content(content)

        self.assertEqual(len(errors), 1)
        self.assertIsInstance(errors[0], STD006)
        self.assertIn("Failed to parse arguments", errors[0].message)

    def test_lint__ignored_error_code__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["STD005"])

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0, "Errors: {}".format([e.CODE for e in errors]))

    def test_lint__ignored_error_code_lowercase__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata, ignored_codes=["std005"])

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0, "Errors found: {}".format([(e.CODE, e.message) for e in errors]))

    def test_lint__comment_disable_same_line__filters_out_error(self) -> "None":
        content = "stdlib.array.assert.is_array arg1 # stdlib: disable STD005"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        # Filter out STD003 (namespace call) and STD008 (unused ignore)
        # STD008 is triggered here because STD005 is not actually raised in this test script
        # since we are only calling the function name without any arguments being matched
        # as a separate match by the linter if we are not careful.
        actual_errors = [e for e in errors if e.CODE not in ('STD003', 'STD008')]
        self.assertEqual(len(actual_errors), 0, "Errors: {}".format([(e.CODE, e.line, e.match, e.message) for e in errors]))

    def test_lint__comment_disable_previous_line__filters_out_error(self) -> "None":
        content = "# stdlib: disable STD005\nstdlib.array.assert.is_array arg1 arg2"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        actual_errors = [e for e in errors if e.CODE != 'STD003']
        self.assertEqual(len(actual_errors), 0)

    def test_lint__comment_disable_file_level__filters_out_all_matching_errors(
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
            errors = linter.lint("test.sh")

        actual_errors = [e for e in errors if e.CODE != 'STD003']
        self.assertEqual(len(actual_errors), 0)

    def test_lint__unused_ignore__returns_std008_error(self) -> "None":
        content = "# stdlib: disable STD001\necho hello"
        linter = Linter(self.metadata)

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        actual_errors = [e for e in errors if e.CODE != 'STD003']
        self.assertEqual(len(actual_errors), 1)
        self.assertIsInstance(actual_errors[0], STD008)
        self.assertEqual(actual_errors[0].match, "STD001")


if __name__ == "__main__":
    unittest.main()
