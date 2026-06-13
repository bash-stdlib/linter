import unittest
from unittest.mock import mock_open, patch

from issues import STD011
from linter import Linter
from tests.assets.linter.core.metadata import METADATA


class TestSTD011(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def _lint_content(self, content: str):
        with patch("builtins.open", mock_open(read_data=content)):
            linter = Linter(self.metadata)
            return linter.lint("test.sh")

    def test_STD011__array_in_brackets__reported(self):
        content = 'stdlib.string.args.join "${@}"'

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
        self.assertEqual(issues[0].line, 1)

    def test_STD011__array_variable__reported(self):
        content = 'stdlib.string.args.join "${args[@]}"'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__raw_at_sign__reported(self):
        content = 'stdlib.string.args.join $@'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)

    def test_STD011__raw_star__reported(self):
        content = 'stdlib.string.args.join $*'

        issues = self._lint_content(content)

        self.assertEqual(len(issues), 1)
        self.assertIsInstance(issues[0], STD011)


if __name__ == "__main__":
    unittest.main()
