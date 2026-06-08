import unittest
from typing import Any
from unittest.mock import mock_open, patch

from linter import Linter


class TestLinterMocking(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = {
            "functions": {
                "stdlib.echo": {"name": "stdlib.echo", "min_args": 1, "max_args": 1},
                "object.mock.assert_called_once_with": {
                    "name": "object.mock.assert_called_once_with",
                    "min_args": 1,
                    "max_args": 1,
                    "is_mock_template": True,
                },
            },
            "namespaces": ["stdlib", "object", "object.mock"],
        }
        self.linter = Linter(self.metadata)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
function test_func {
    _mock.create my_mock
    my_mock.mock.assert_called_once_with "hello"
}
""",
    )
    def test_lint__local_mock__validates_correctly(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        self.assertEqual(len(errors), 0)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
function test_func {
    _mock.create my_mock
}
my_mock.mock.assert_called_once_with "hello"
""",
    )
    def test_lint__out_of_scope_mock__reports_error(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        # Should be STD002 (unknown function) because my_mock is out of scope
        self.assertTrue(
            any(
                e.CODE == "STD002"
                and "my_mock.mock.assert_called_once_with" in e.format_message()
                for e in errors
            )
        )

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
function setup {
    _mock.create global_mock
}
function test_func {
    global_mock.mock.assert_called_once_with "hello"
}
""",
    )
    def test_lint__mock_in_setup__has_global_visibility(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        self.assertEqual(len(errors), 0)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
_mock.create global_mock
function test_func {
    global_mock.mock.assert_called_once_with "hello"
}
""",
    )
    def test_lint__mock_at_top_level__has_global_visibility(
        self, mock_file: Any
    ) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        self.assertEqual(len(errors), 0)

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
_mock.create my_mock
_mock.delete my_mock
my_mock.mock.assert_called_once_with "hello"
""",
    )
    def test_lint__deleted_mock__reports_error(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        self.assertTrue(any(e.CODE == "STD002" for e in errors))

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
_mock.create my_mock
_mock.reset_all
my_mock.mock.assert_called_once_with "hello"
""",
    )
    def test_lint__reset_all_mocks__reports_error(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        self.assertTrue(any(e.CODE == "STD002" for e in errors))

    @patch(
        "builtins.open",
        new_callable=mock_open,
        read_data="""
_mock.create my_mock
my_mock.mock.assert_called_once_with
""",
    )
    def test_lint__mock_method_wrong_args__reports_error(self, mock_file: Any) -> None:
        errors = self.linter.lint("/app/src/tests/test.sh")
        # Should be STD005 (argument count)
        self.assertTrue(any(e.CODE == "STD005" for e in errors))


if __name__ == "__main__":
    unittest.main()
