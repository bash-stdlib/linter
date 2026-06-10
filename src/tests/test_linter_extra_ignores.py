"""Unit tests for the linter extra ignores logic."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.appendum.metadata import METADATA


class TestLinterExtraIgnores(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__extra_functions__returns_no_errors(self) -> None:
        linter = Linter(self.metadata, extra_functions=["stdlib.__message.get"])
        content = "stdlib.__message.get 'hello'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__extra_namespaces__returns_no_errors(self) -> None:
        linter = Linter(self.metadata, extra_namespaces=["my_ns"])
        content = "my_ns.foo 'bar'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__extra_namespaces_partial__only_flags_non_extra_calls(
        self,
    ) -> None:
        linter = Linter(self.metadata, extra_namespaces=["stdlib.private"])
        content = "stdlib.private.call 'arg'\nstdlib.public.call 'arg'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD001")
        self.assertIn("stdlib.public", errors[0].message)

    def test_lint__extra_functions_exact__does_not_whitelist_subcalls(self) -> None:
        linter = Linter(self.metadata, extra_functions=["stdlib.private"])
        content = "stdlib.private 'arg'\nstdlib.private.subcall 'arg'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD001")
        self.assertIn("stdlib.private", errors[0].message)


if __name__ == "__main__":
    unittest.main()
