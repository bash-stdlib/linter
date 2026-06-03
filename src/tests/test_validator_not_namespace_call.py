"""Unit tests for the NotNamespaceCallValidator."""

import unittest

from linter.state.file_state import FileLinterState
from linter.state.global_state import GlobalLinterState
from tests.assets.validator.not_namespace_call.metadata import METADATA
from validators.not_namespace_call import NotNamespaceCallValidator


class TestNotNamespaceCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.global_state = GlobalLinterState(METADATA)
        self.file_state = FileLinterState()
        self.validator = NotNamespaceCallValidator(self.global_state, self.file_state)

    def test_check__valid_function_call__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__namespace_call__returns_std003(self) -> None:
        call = "stdlib.string"

        result = self.validator.check(call, "test.sh", 1, 1)

        assert result is not None
        self.assertEqual(result.CODE, "STD003")
        self.assertEqual(result.match, "stdlib.string")

    def test_check__unknown_call__returns_none(self) -> None:
        call = "unknown.command"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
