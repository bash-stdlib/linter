import unittest
from unittest.mock import mock_open, patch

from errors.std001 import STD001
from errors.std002 import STD002
from errors.std003 import STD003
from linter import Linter


class TestLinter(unittest.TestCase):
    def setUp(self):
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

    def test_validate_call__exact_match__returns_none(self):
        issue = self.linter._validate_call(
            "stdlib.array.assert.is_array", "test.sh", 1, 1
        )

        self.assertIsNone(issue)

    def test_validate_call__call_to_namespace__returns_std003_issue(self):
        issue = self.linter._validate_call("stdlib.array.assert", "test.sh", 1, 1)

        self.assertIsNotNone(issue)
        self.assertIsInstance(issue, STD003)

    def test_validate_call__misspelled_function__returns_std002_issue(self):
        issue = self.linter._validate_call(
            "stdlib.array.assert.is_ary", "test.sh", 1, 1
        )

        self.assertIsNotNone(issue)
        self.assertIsInstance(issue, STD002)
        self.assertIn("Did you mean 'stdlib.array.assert.is_array'?", issue.message)

    def test_validate_call__invalid_sub_namespace__returns_std001_issue(self):
        issue = self.linter._validate_call("stdlib.array.unknown.func", "test.sh", 1, 1)

        self.assertIsNotNone(issue)
        self.assertIsInstance(issue, STD001)
        self.assertIn("Invalid namespace 'stdlib.array.unknown'", issue.message)

    def test_validate_call__invalid_root_namespace__returns_std001_issue(self):
        issue = self.linter._validate_call("stdlib.unknown.func", "test.sh", 1, 1)

        self.assertIsNotNone(issue)
        self.assertIsInstance(issue, STD001)
        self.assertIn("Invalid namespace 'stdlib.unknown'", issue.message)

    def test_get_line_number__content_offset__returns_correct_line(self):
        content = "line1\nline2\nline3"
        offset = content.find("line2")

        result = self.linter._get_line_number(content, offset)

        self.assertEqual(result, 2)

    def test_get_column_number__content_offset__returns_correct_column(self):
        content = "line1\nabcde"
        offset = content.find("c")

        result = self.linter._get_column_number(content, offset)

        self.assertEqual(result, 3)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="stdlib.array.assert.is_array\nstdlib.invalid",
    )
    def test_lint__script_with_error__returns_issue_list_with_codes(self, mock_file):
        issues = self.linter.lint("dummy.sh")

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD002)
        self.assertEqual(issues[0].match, "stdlib.invalid")
        self.assertEqual(issues[0].line, 2)


if __name__ == "__main__":
    unittest.main()
