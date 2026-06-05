"""Unit tests for the TokenIteratorFilterNestedEntities."""

import unittest
from parsers.token_iterators.token_iterator_filter_nested_entities import TokenIteratorFilterNestedEntities


class TestTokenIteratorFilterNestedEntities(unittest.TestCase):
    def test_iterator__basic_tokens__returns_unchanged(self) -> None:
        tokens = ["arg1", "arg2"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__subshell__groups_tokens(self) -> None:
        # $(echo foo) -> ['$', '(', 'echo', 'foo', ')']
        tokens = ["$", "(", "echo", "foo", ")"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))

    def test_iterator__nested_subshell__groups_tokens(self) -> None:
        # $(echo $(bar)) -> ['$', '(', 'echo', '$', '(', 'bar', ')', ')']
        tokens = ["$", "(", "echo", "$", "(", "bar", ")", ")"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))

    def test_iterator__parameter_expansion__groups_tokens(self) -> None:
        # ${VAR:-val} -> ['$', '{', 'VAR', ':', '-', 'val', '}']
        tokens = ["$", "{", "VAR", ":", "-", "val", "}"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("${"))
        self.assertTrue(result[0].endswith("}"))

    def test_iterator__backticks__groups_tokens(self) -> None:
        # `echo foo` -> ['`', 'echo', 'foo', '`']
        tokens = ["`", "echo", "foo", "`"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))

    def test_iterator__escaped_backticks__groups_tokens(self) -> None:
        # `echo \`foo\`` -> ['`', 'echo', '\\', '`', 'foo', '\\', '`', '`']
        tokens = ["`", "echo", "\\", "`", "foo", "\\", "`", "`"]
        iterator = TokenIteratorFilterNestedEntities(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))
