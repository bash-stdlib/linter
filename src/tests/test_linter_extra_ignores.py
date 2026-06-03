"""Unit tests for the linter extra ignores logic."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.appendum.metadata import METADATA


class TestLinterExtraIgnores(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__extra_functions__returns_no_issues(self) -> None:
        linter = Linter(self.metadata, extra_functions=["stdlib.__message.get"])
        content = "stdlib.__message.get 'hello'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__extra_namespaces__returns_no_issues(self) -> None:
        linter = Linter(self.metadata, extra_namespaces=["my_ns"])
        content = "my_ns.foo 'bar'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 0)

    def test_lint__extra_namespaces_partial__only_flags_non_extra_calls(
        self,
    ) -> None:
        linter = Linter(self.metadata, extra_namespaces=["stdlib.private"])
        content = "stdlib.private.call 'arg'\nstdlib.public.call 'arg'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].CODE, "STD001")
        self.assertIn("stdlib.public", issues[0].message)

    def test_lint__extra_functions_exact__does_not_whitelist_subcalls(self) -> None:
        linter = Linter(self.metadata, extra_functions=["stdlib.private"])
        content = "stdlib.private 'arg'\nstdlib.private.subcall 'arg'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            issues = linter.lint("test.sh")

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].CODE, "STD001")
        self.assertIn("stdlib.private", issues[0].message)


if __name__ == "__main__":
    unittest.main()
