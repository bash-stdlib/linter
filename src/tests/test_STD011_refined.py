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

    def test_check__variadic_enough_args__no_issues(self):
        content = 'stdlib.test.variadic "arg1" "${array[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_check__variadic_insufficient_args__reports_std011(self):
        content = 'stdlib.test.variadic "${array[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__variadic_zero_min__no_issues(self):
        content = '_mock.create logger\nlogger.mock.assert_calls_are "${array[@]}"'

        issues = self._lint_content(content, filename="test_file.sh")

        self.assertEqual(len(issues), 0)

    def test_check__fixed_at_limit_with_dynamic__reports_std005(self):
        content = 'stdlib.test.strict "arg1" "${array[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_check__fixed_exceeding_limit__reports_std005(self):
        content = 'stdlib.test.strict "arg1" "arg2" "${array[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)


if __name__ == "__main__":
    unittest.main()
