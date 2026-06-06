import unittest
from unittest.mock import mock_open, patch
from linter import Linter

class TestLinterDynamicMocks(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": {
                "stdlib.string.echo": {"name": "stdlib.string.echo", "is_testing": False},
                "_mock.create": {"name": "_mock.create", "is_testing": True, "min_args": 1, "max_args": 1},
            },
            "namespaces": ["stdlib.string"]
        }
        self.linter = Linter(self.metadata)

    def test_lint__mock_create_in_setup__registers_dynamic_mock(self) -> None:
        content = """
setup() {
  _mock.create stdlib.string.new_mock
}

function test_one() {
  stdlib.string.new_mock "hello"
}
"""
        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test_file.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__mock_create_outside_setup__does_not_register_globally(self) -> None:
        content = """
function other_func() {
  _mock.create stdlib.string.local_mock
}

function test_one() {
  stdlib.string.local_mock "hello"
}
"""
        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test_file.sh")

        self.assertGreater(len(errors), 0)
        self.assertEqual(errors[0].CODE, "STD002")

    def test_lint__mock_create_in_setup_suite__registers_dynamic_mock(self) -> None:
        content = """
function setup_suite {
  _mock.create stdlib.string.suite_mock
}

function test_one() {
  stdlib.string.suite_mock "hello"
}
"""
        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test_file.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__dynamic_mock__is_removed_after_lint(self) -> None:
        content = "_mock.create dyn_mock"
        with patch("builtins.open", mock_open(read_data=content)):
            self.linter.lint("file1.sh")

        self.assertNotIn("dyn_mock", self.linter.functions)

if __name__ == "__main__":
    unittest.main()
