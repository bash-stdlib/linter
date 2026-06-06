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

    def test_lint__mock_create__registers_dynamic_mock(self) -> None:
        content = """
function setup() {
  _mock.create stdlib.string.new_mock
}

function test_one() {
  stdlib.string.new_mock "hello"
}
"""
        with patch("builtins.open", mock_open(read_data=content)):
            errors = self.linter.lint("test_file.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__fake__registers_dynamic_mock(self) -> None:
        content = """
function setup() {
  fake my_custom_fake
}

function test_one() {
  my_custom_fake "hello"
}
"""
        # fake is not in metadata, but added to appendum in __init__
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
