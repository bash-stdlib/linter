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

    def test_STD011__variadic_with_enough_args__not_reported(self):
        # min_args: 1, max_args: -1. 1 guaranteed arg provided ("arg1").
        content = 'stdlib.test.variadic "arg1" "${array[@]}"'
        issues = self._lint_content(content)
        # Desired: 0 issues (currently it should fail and report 1 issue)
        self.assertEqual(len(issues), 0)

    def test_STD011__variadic_with_not_enough_args__reported(self):
        # min_args: 1, max_args: -1. 0 guaranteed args provided.
        # Array could be empty, violating min_args.
        content = 'stdlib.test.variadic "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__variadic_min_zero__not_reported(self):
        # min_args: 0, max_args: -1.
        content = '_mock.create logger\nlogger.mock.assert_calls_are "${array[@]}"'
        issues = self._lint_content(content, filename="test_file.sh")
        self.assertEqual(len(issues), 0)

    def test_STD011__strict_with_array__reports_STD005(self):
        # min_args: 1, max_args: 1.
        # Even if we provide 1 arg, the array might add more, violating max_args.
        # Since 1 is already max_args, any array (even empty) will likely be
        # problematic, but technically bash allows empty arrays.
        # Our refined logic prefers STD005 if we are already at or above max_args.
        content = 'stdlib.test.strict "arg1" "${array[@]}"'
        issues = self._lint_content(content)
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_STD011__strict_already_too_many__reports_STD005(self):
        # min_args: 1, max_args: 1.
        # 2 guaranteed args already violate max_args.
        content = 'stdlib.test.strict "arg1" "arg2" "${array[@]}"'
        issues = self._lint_content(content)
        # It could report STD005 because we are SURE it's too many.
        # Or it could report STD011.
        # Given current implementation, it checks too many first.
        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)


if __name__ == "__main__":
    unittest.main()
