import unittest
from unittest.mock import mock_open, patch

from issues import STD005, STD011
from linter import Linter
from tests.assets.linter.core.metadata import METADATA

TEST_METADATA = METADATA.copy()
TEST_METADATA["functions"] = METADATA["functions"].copy()
TEST_METADATA["functions"]["stdlib.test.strict"] = {
    "name": "stdlib.test.strict",
    "min_args": 1,
    "max_args": 1,
}


class TestSTD011(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = TEST_METADATA

    def _lint_content(self, content: str):
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_STD011__array_in_brackets__reported(self):
        content = 'stdlib.string.args.join "${@}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__array_slice_with_invalid_syntax__reported(self):
        content = 'stdlib.string.args.join "${array[@]:a:b}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__quoted_at_sign__reported(self):
        content = 'stdlib.string.args.join "$@"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__quoted_star__reported(self):
        content = 'stdlib.string.args.join "$*"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__array_variable__reported(self):
        content = 'stdlib.string.args.join "${args[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__raw_at_sign__reported(self):
        content = "stdlib.string.args.join $@"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__raw_star__reported(self):
        content = "stdlib.string.args.join $*"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__too_many_args_with_array__reports_STD005(self):
        content = 'stdlib.test.strict arg1 "${@}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_STD011__array_slice_with_static_length__parsed_correctly(self):
        content = 'stdlib.test.strict "${array[@]:0:1}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_STD011__array_slice_with_too_many_length__reports_STD005(self):
        content = 'stdlib.test.strict "${array[@]:0:2}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_STD011__array_slice_without_length__reported(self):
        content = 'stdlib.string.args.join "${array[@]:0}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__string_slice__not_reported(self):
        content = 'stdlib.test.strict "${text:6}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
