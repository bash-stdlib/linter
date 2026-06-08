import os
import unittest
from unittest.mock import patch

from linter import Linter
from tests.assets.linter_mocking.metadata import METADATA

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets", "linter_mocking")


class TestLinterMocking(unittest.TestCase):
    def setUp(self) -> None:
        self.linter = Linter(METADATA)

    def _read_asset(self, filename: str) -> str:
        with open(os.path.join(ASSETS_DIR, filename), "r") as f:
            return f.read()

    def test_lint__local_mock__validates_correctly(self) -> None:
        content = self._read_asset("local_mock.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__out_of_scope_mock__reports_error(self) -> None:
        content = self._read_asset("out_of_scope.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        # Should be STD002 (unknown function) because my_mock is out of scope
        self.assertTrue(
            any(
                e.CODE == "STD002"
                and "my_mock.mock.assert_called_once_with" in e.format_message()
                for e in errors
            )
        )

    def test_lint__multiple_files__no_state_contamination(self) -> None:
        content1 = "_mock.create mock1\nmock1.mock.assert_called_once_with 'x'"
        content2 = "mock1.mock.assert_called_once_with 'x'"

        with patch("builtins.open", unittest.mock.mock_open(read_data=content1)):
            errors1 = self.linter.lint("test1.sh")
        with patch("builtins.open", unittest.mock.mock_open(read_data=content2)):
            errors2 = self.linter.lint("test2.sh")

        self.assertEqual(len(errors1), 0)
        # mock1 should NOT be visible in the second file
        self.assertTrue(any(e.CODE == "STD002" for e in errors2))

    def test_lint__indented_mock__reports_correct_column(self) -> None:
        content = "    _mock.create my_mock\n    my_mock.mock.assert_called_once_with"

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("test.sh")

        # should be STD005 for wrong args, but check the column
        error = next(e for e in errors if e.CODE == "STD005")
        # 'my_mock.mock.assert_called_once_with' starts at index 4 (0-based) in line 2
        # which is column 5 (1-based)
        self.assertEqual(error.column, 5)

    def test_lint__mock_in_setup__has_global_visibility(self) -> None:
        content = self._read_asset("setup_global.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__mock_at_top_level__has_global_visibility(self) -> None:
        content = self._read_asset("top_level_global.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__deleted_mock__reports_error(self) -> None:
        content = self._read_asset("deleted_mock.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        self.assertTrue(any(e.CODE == "STD002" for e in errors))

    def test_lint__reset_all_mocks__reports_error(self) -> None:
        content = self._read_asset("reset_all.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        self.assertTrue(any(e.CODE == "STD002" for e in errors))

    def test_lint__mock_method_wrong_args__reports_error(self) -> None:
        content = self._read_asset("wrong_args.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        # Should be STD005 (argument count)
        self.assertTrue(any(e.CODE == "STD005" for e in errors))

    def test_lint__nested_functions__innermost_scope_wins(self) -> None:
        content = self._read_asset("nested_functions.sh")

        with patch("builtins.open", unittest.mock.mock_open(read_data=content)):
            errors = self.linter.lint("/app/src/tests/test.sh")

        # The call inside 'inner' should be valid.
        # The call inside 'outer' (but outside 'inner') should be an error because
        # my_mock was local to 'inner'.
        self.assertTrue(
            any(
                e.CODE == "STD002"
                and "my_mock.mock.assert_called_once_with" in e.format_message()
                and e.line == 6
                for e in errors
            )
        )


if __name__ == "__main__":
    unittest.main()
