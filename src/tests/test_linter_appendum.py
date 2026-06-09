"""Unit tests for the linter appendum logic."""

import unittest
from unittest.mock import mock_open, patch

from linter import Linter
from tests.assets.linter.appendum.metadata import METADATA


class TestLinterAppendum(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = METADATA

    def test_lint__appendum_function__returns_no_errors(self) -> None:
        linter = Linter(self.metadata, appendum=["stdlib.__message.get"])
        content = "stdlib.__message.get 'hello'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__appendum_namespace__returns_no_errors(self) -> None:
        linter = Linter(self.metadata, appendum=["my_ns"])
        content = "my_ns.foo 'bar'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 0)

    def test_lint__appendum_partial_namespace__only_flags_non_appendum_calls(
        self,
    ) -> None:
        linter = Linter(self.metadata, appendum=["stdlib.private"])
        content = "stdlib.private.call 'arg'\nstdlib.public.call 'arg'\n"

        with patch("builtins.open", mock_open(read_data=content)):
            errors = linter.lint("test.sh")

        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].CODE, "STD001")
        self.assertIn("stdlib.public", errors[0].message)


if __name__ == "__main__":
    unittest.main()
