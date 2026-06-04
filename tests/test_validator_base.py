import unittest
from typing import Optional
from errors.base import LinterError
from validators.base import Validator

class ConcreteValidator(Validator):
    def check(self, call: str, file: str, line: int, column: int) -> Optional[LinterError]:
        return None

class TestValidatorBase(unittest.TestCase):
    def setUp(self) -> None:
        self.functions = {"stdlib.string.join", "stdlib.array.push"}
        self.namespaces = {"stdlib", "stdlib.string", "stdlib.array"}
        self.validator = ConcreteValidator(self.functions, self.namespaces)

    def test_find_longest_namespace_prefix__valid_prefix__returns_longest(self) -> None:
        result = self.validator._find_longest_namespace_prefix("stdlib.string.join")
        self.assertEqual(result, "stdlib.string")

    def test_find_longest_namespace_prefix__no_valid_prefix__returns_none(self) -> None:
        result = self.validator._find_longest_namespace_prefix("unknown.namespace.func")
        self.assertIsNone(result)

    def test_is_immediate_child_of_namespace__is_child__returns_true(self) -> None:
        result = self.validator._is_immediate_child_of_namespace("stdlib.string.join", "stdlib.string")
        self.assertTrue(result)

    def test_is_immediate_child_of_namespace__is_not_child__returns_false(self) -> None:
        result = self.validator._is_immediate_child_of_namespace("stdlib.string.sub.join", "stdlib.string")
        self.assertFalse(result)

    def test_get_suggestion__has_close_match__returns_suggestion(self) -> None:
        result = self.validator._get_suggestion("stdlib.string.jin", "stdlib.string")
        self.assertEqual(result, "stdlib.string.join")

    def test_get_suggestion__no_close_match__returns_none(self) -> None:
        result = self.validator._get_suggestion("stdlib.string.a_very_long_string_that_is_definitely_not_join", "stdlib.string")
        self.assertIsNone(result)

    def test_extract_invalid_namespace__various_depths__returns_correct_namespace(self) -> None:
        result = self.validator._extract_invalid_namespace("stdlib.string.unknown.func", "stdlib.string")
        self.assertEqual(result, "stdlib.string.unknown")
