"""Unit tests for the individual rule classes."""

import unittest

from errors import STD001, STD002, STD003, STD004
from rules import (
    InvalidFunctionRule,
    InvalidNamespaceRule,
    NamespaceAsFunctionRule,
    UnknownCallRule,
)


class TestRules(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"stdlib.string.join", "stdlib.array.push"}
        self.namespaces = {"stdlib", "stdlib.string", "stdlib.array"}

    def test_namespace_as_function_rule__call_is_namespace__returns_std003(self) -> None:
        rule = NamespaceAsFunctionRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string", "test.sh", 1, 1)

        self.assertIsInstance(issue, STD003)

    def test_namespace_as_function_rule__call_is_not_namespace__returns_none(self) -> None:
        rule = NamespaceAsFunctionRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.join", "test.sh", 1, 1)

        self.assertIsNone(issue)

    def test_invalid_function_rule__misspelled_function__returns_std002(self) -> None:
        rule = InvalidFunctionRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.jon", "test.sh", 1, 1)

        self.assertIsInstance(issue, STD002)

    def test_invalid_function_rule__valid_function__returns_none(self) -> None:
        rule = InvalidFunctionRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.join", "test.sh", 1, 1)

        self.assertIsNone(issue)

    def test_invalid_namespace_rule__invalid_sub_namespace__returns_std001(self) -> None:
        rule = InvalidNamespaceRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.invalid.func", "test.sh", 1, 1)

        self.assertIsInstance(issue, STD001)

    def test_invalid_namespace_rule__valid_namespace__returns_none(self) -> None:
        rule = InvalidNamespaceRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.join", "test.sh", 1, 1)

        self.assertIsNone(issue)

    def test_unknown_call_rule__unknown_root_namespace__returns_std004(self) -> None:
        rule = UnknownCallRule(self.functions, self.namespaces)

        issue = rule.check("unknown.func", "test.sh", 1, 1)

        self.assertIsInstance(issue, STD004)

    def test_unknown_call_rule__known_namespace__returns_none(self) -> None:
        rule = UnknownCallRule(self.functions, self.namespaces)

        issue = rule.check("stdlib.string.join", "test.sh", 1, 1)

        self.assertIsNone(issue)


if __name__ == "__main__":
    unittest.main()
