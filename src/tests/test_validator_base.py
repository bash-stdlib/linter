import unittest
from typing import List, Optional

from errors.base import LinterErrorBase
from linter.state import LinterState
from validators.base import ValidatorBase


class ConcreteValidator(ValidatorBase):
    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: Optional[List[str]] = None,
    ) -> Optional[LinterErrorBase]:
        return None


class TestValidator(unittest.TestCase):
    def setUp(self) -> None:
        metadata = {
            "functions": {f: {} for f in ["stdlib.string.join", "stdlib.array.push"]},
            "namespaces": ["stdlib", "stdlib.string", "stdlib.array"],
        }
        self.state = LinterState(metadata)
        self.validator = ConcreteValidator(self.state)

    def test_find_longest_namespace_prefix__valid_prefix__returns_longest(self) -> None:
        call = "stdlib.string.join"

        result = self.validator._find_longest_namespace_prefix(call)

        self.assertEqual(result, "stdlib.string")

    def test_find_longest_namespace_prefix__no_valid_prefix__returns_none(self) -> None:
        call = "unknown.namespace.func"

        result = self.validator._find_longest_namespace_prefix(call)

        self.assertIsNone(result)

    def test_is_immediate_child_of_namespace__is_child__returns_true(self) -> None:
        call = "stdlib.string.join"
        namespace = "stdlib.string"

        result = self.validator._is_immediate_child_of_namespace(call, namespace)

        self.assertTrue(result)

    def test_is_immediate_child_of_namespace__is_not_child__returns_false(self) -> None:
        call = "stdlib.string.sub.join"
        namespace = "stdlib.string"

        result = self.validator._is_immediate_child_of_namespace(
            call,
            namespace,
        )

        self.assertFalse(result)

    def test_get_suggestion__has_close_match__returns_suggestion(self) -> None:
        call = "stdlib.string.jin"
        namespace = "stdlib.string"

        result = self.validator._get_suggestion(call, namespace)

        self.assertEqual(result, "stdlib.string.join")

    def test_get_suggestion__no_close_match__returns_none(self) -> None:
        call = "stdlib.string.a_very_long_string_that_is_definitely_not_join"
        namespace = "stdlib.string"

        result = self.validator._get_suggestion(call, namespace)

        self.assertIsNone(result)

    def test_extract_invalid_namespace__various_depths__returns_correct_namespace(
        self,
    ) -> None:
        call = "stdlib.string.unknown.func"
        prefix = "stdlib.string"

        result = self.validator._extract_invalid_namespace(call, prefix)

        self.assertEqual(result, "stdlib.string.unknown")


if __name__ == "__main__":
    unittest.main()
