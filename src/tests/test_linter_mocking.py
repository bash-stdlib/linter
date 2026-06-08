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


if __name__ == "__main__":
    unittest.main()
