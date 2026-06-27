import unittest
from unittest.mock import mock_open, patch

from issues import STD005, STD011
from linter import Linter
from tests.assets.linter.core.metadata import METADATA

TEST_METADATA = METADATA.copy()
TEST_METADATA["functions"] = METADATA["functions"].copy()
TEST_METADATA["functions"]["stdlib.test.variadic"] = {
    "name": "stdlib.test.variadic",
    "min_args": 1,
    "max_args": -1,
}
TEST_METADATA["functions"]["stdlib.test.strict"] = {
    "name": "stdlib.test.strict",
    "min_args": 1,
    "max_args": 1,
}
TEST_METADATA["functions"]["object.mock.assert_calls_are"] = {
    "name": "object.mock.assert_calls_are",
    "min_args": 0,
    "max_args": -1,
}
TEST_METADATA["namespaces"] = TEST_METADATA["namespaces"] + ["object", "object.mock"]


class TestSTD011Refined(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = TEST_METADATA

    def _lint_content(self, content: str, filename: str = "test.sh"):
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint(filename)

    def test_variadic_function_with_enough_guaranteed_args_suppresses_STD011(self):
        # min_args: 1, max_args: -1. 1 guaranteed arg provided ("arg1").
        # The dynamic array "${array[@]}" is allowed and doesn't trigger a warning.
        content = 'stdlib.test.variadic "arg1" "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 0)

    def test_variadic_function_with_insufficient_guaranteed_args_reports_STD011(self):
        # min_args: 1, max_args: -1. 0 guaranteed args provided.
        # Since the dynamic array could be empty, we still warn.
        content = 'stdlib.test.variadic "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_variadic_function_with_zero_min_args_suppresses_STD011(self):
        # object.mock.assert_calls_are has min_args: 0.
        # Any dynamic argument is safe.
        content = '_mock.create logger\nlogger.mock.assert_calls_are "${array[@]}"'
        issues = self._lint_content(content, filename="test_file.sh")
        self.assertEqual(len(issues), 0)

    def test_fixed_args_function_at_limit_with_dynamic_arg_reports_STD005(self):
        # stdlib.test.strict has max_args: 1.
        # Providing 1 arg ("arg1") plus a dynamic array will definitely exceed max_args
        # (assuming the array expands to at least one element, or even if it's empty,
        # our heuristic treats it as an extra potential argument).
        content = 'stdlib.test.strict "arg1" "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_fixed_args_function_exceeding_limit_reports_STD005(self):
        # stdlib.test.strict has max_args: 1.
        # Providing 2 guaranteed args already violates the contract.
        content = 'stdlib.test.strict "arg1" "arg2" "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)


if __name__ == "__main__":
    unittest.main()
