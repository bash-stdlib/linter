"""Unit tests for the NotNamespaceCallValidator."""

import unittest
from typing import Set

from validators.not_namespace_call import NotNamespaceCallValidator


class TestNotNamespaceCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions: Set[str] = {"stdlib.string.join"}
        self.namespaces: Set[str] = {"stdlib", "stdlib.string"}
        self.validator = NotNamespaceCallValidator(self.functions, self.namespaces)

    def test_check__valid_function_call__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

    def test_check__namespace_call__returns_std003(self) -> None:
        call = "stdlib.string"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result.CODE, "STD003")
            self.assertEqual(result.match, "stdlib.string")

    def test_check__unknown_call__returns_none(self) -> None:
        call = "unknown.command"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)

if __name__ == "__main__":
    unittest.main()
