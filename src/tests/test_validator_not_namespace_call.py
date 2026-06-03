import unittest

from errors.std003 import STD003
from validators.not_namespace_call import NotNamespaceCallValidator


class TestNotNamespaceCallValidator(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"stdlib.string.join"}
        self.namespaces = {"stdlib.string"}
        self.validator = NotNamespaceCallValidator(
            self.functions,
            self.namespaces,
        )

    def test_check__call_is_namespace__returns_std003(self) -> None:
        call = "stdlib.string"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsInstance(result, STD003)

    def test_check__call_is_not_namespace__returns_none(self) -> None:
        call = "stdlib.string.join"

        result = self.validator.check(call, "test.sh", 1, 1)

        self.assertIsNone(result)
