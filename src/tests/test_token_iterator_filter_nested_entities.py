"""Unit tests for the FilterNestedEntitiesTokenIterator."""

import unittest

from parsers.token_iterators.filter_nested_entities import (
    FilterNestedEntitiesTokenIterator,
)


class TestFilterNestedEntitiesTokenIterator(unittest.TestCase):
    def test_iterator__basic_tokens__returns_unchanged(self) -> None:
        tokens = ["arg1", "arg2"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__subshell__groups_tokens(self) -> None:
        # $(echo foo) -> ['$', '(', 'echo', 'foo', ')']
        tokens = ["$", "(", "echo", "foo", ")"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))

    def test_iterator__nested_subshell__groups_tokens(self) -> None:
        # $(echo $(bar)) -> ['$', '(', 'echo', '$', '(', 'bar', ')', ')']
        tokens = ["$", "(", "echo", "$", "(", "bar", ")", ")"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))

    def test_iterator__parameter_expansion__groups_tokens(self) -> None:
        # ${VAR:-val} -> ['$', '{', 'VAR', ':', '-', 'val', '}']
        tokens = ["$", "{", "VAR", ":", "-", "val", "}"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("${"))
        self.assertTrue(result[0].endswith("}"))

    def test_iterator__backticks__groups_tokens(self) -> None:
        # `echo foo` -> ['`', 'echo', 'foo', '`']
        tokens = ["`", "echo", "foo", "`"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))

    def test_iterator__escaped_backticks__groups_tokens(self) -> None:
        # `echo \`foo\`` -> ['`', 'echo', '\\', '`', 'foo', '\\', '`', '`']
        tokens = ["`", "echo", "\\", "`", "foo", "\\", "`", "`"]
        iterator = FilterNestedEntitiesTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))
