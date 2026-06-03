import unittest
from unittest.mock import patch, mock_open
from linter import Linter
from models import ErrorCode

class TestLinter(unittest.TestCase):
    def setUp(self):
        self.metadata = {
            "functions": ["stdlib.array.assert.is_array", "stdlib.string.args.join"],
            "namespaces": ["stdlib", "stdlib.array", "stdlib.array.assert", "stdlib.string", "stdlib.string.args"]
        }
        self.linter = Linter(self.metadata)

    def test_validate_call__exact_match__returns_true(self):
        result, error_info = self.linter._validate_call("stdlib.array.assert.is_array")

        self.assertTrue(result)
        self.assertIsNone(error_info)

    def test_validate_call__call_to_namespace__returns_false_with_std003(self):
        result, error_info = self.linter._validate_call("stdlib.array.assert")

        self.assertFalse(result)
        self.assertEqual(error_info['code'], ErrorCode.STD003)
        self.assertIn("is a namespace, not a function", error_info['message'])

    def test_validate_call__misspelled_function__returns_false_with_std002(self):
        result, error_info = self.linter._validate_call("stdlib.array.assert.is_ary")

        self.assertFalse(result)
        self.assertEqual(error_info['code'], ErrorCode.STD002)
        self.assertIn("Invalid function 'stdlib.array.assert.is_ary' in valid namespace 'stdlib.array.assert'", error_info['message'])
        self.assertIn("Did you mean 'stdlib.array.assert.is_array'?", error_info['message'])

    def test_validate_call__invalid_sub_namespace__returns_false_with_std001(self):
        result, error_info = self.linter._validate_call("stdlib.array.unknown.func")

        self.assertFalse(result)
        self.assertEqual(error_info['code'], ErrorCode.STD001)
        self.assertIn("Invalid namespace 'stdlib.array.unknown'", error_info['message'])

    def test_validate_call__invalid_root_namespace__returns_false_with_std001(self):
        result, error_info = self.linter._validate_call("stdlib.unknown.func")

        self.assertFalse(result)
        self.assertEqual(error_info['code'], ErrorCode.STD001)
        self.assertIn("Invalid namespace 'stdlib.unknown'", error_info['message'])

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

    @patch('builtins.open', new_callable=mock_open, read_data="stdlib.array.assert.is_array\nstdlib.invalid")
    def test_lint__script_with_error__returns_error_list_with_codes(self, mock_file):
        errors = self.linter.lint("dummy.sh")

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].code, "STD002")
        self.assertEqual(errors[0].match, "stdlib.invalid")
        self.assertEqual(errors[0].line, 2)

if __name__ == "__main__":
    unittest.main()
