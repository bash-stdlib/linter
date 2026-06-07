"""Unit tests for the NotNamespaceCallValidator."""

import unittest
from validators.not_namespace_call import NotNamespaceCallValidator
from tests.assets.linter_validation_namespace_call import FUNCTIONS, NAMESPACES

class TestNotNamespaceCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = FUNCTIONS
        self.namespaces = NAMESPACES
        self.validator = NotNamespaceCallValidator(self.functions, self.namespaces)

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
