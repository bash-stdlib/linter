import unittest
from unittest.mock import mock_open, patch

from issues import STD005, STD011
from linter import Linter
from tests.assets.linter.std011.metadata import STD011_METADATA


class TestSTD011(unittest.TestCase):
    def setUp(self) -> "None":
        self.metadata = STD011_METADATA

    def _lint_content(self, content: "str", filename: "str" = "test.sh"):
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)

            return linter.lint(filename)

    def test_check__array_in_brackets__reports_std011(self):
        content = 'stdlib.string.args.join "${@}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__array_slice_invalid_syntax__reports_std011(self):
        content = 'stdlib.string.args.join "${array[@]:a:b}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__quoted_at_sign__reports_std011(self):
        content = 'stdlib.string.args.join "$@"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__quoted_star__reports_std011(self):
        content = 'stdlib.string.args.join "$*"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__array_variable__reports_std011(self):
        content = 'stdlib.string.args.join "${args[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__raw_at_sign__reports_std011(self):
        content = "stdlib.string.args.join $@"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__raw_star__reports_std011(self):
        content = "stdlib.string.args.join $*"

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__static_array_slice_length__no_issues(self):
        content = 'stdlib.test.strict "${array[@]:0:1}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)

    def test_check__static_array_slice_excessive__reports_std005(self):
        content = 'stdlib.test.strict "${array[@]:0:2}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD005)

    def test_check__array_slice_no_length__reports_std011(self):
        content = 'stdlib.string.args.join "${array[@]:0}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_check__string_slice__no_issues(self):
        content = 'stdlib.test.strict "${text:6}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)

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

    def test_check__optional_args_omitted__no_issues(self):
        content = 'stdlib.test.optional "arg1"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 0)


if __name__ == "__main__":
    unittest.main()
