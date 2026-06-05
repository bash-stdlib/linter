"""Unit tests for the BashTokenIterator."""

import unittest
from parsers.bash_token_iterator import BashTokenIterator


class TestBashTokenIterator(unittest.TestCase):
    def test_iterator__basic_tokens__returns_unchanged(self) -> None:
        tokens = ["arg1", "arg2"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__subshell__groups_tokens(self) -> None:
        # $(echo foo) -> ['$', '(', 'echo', 'foo', ')']
        tokens = ["$", "(", "echo", "foo", ")"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        # We don't preserve whitespace information from tokens,
        # but it should be ONE argument.
        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))
        self.assertIn("echo", result[0])
        self.assertIn("foo", result[0])

    def test_iterator__nested_subshell__groups_tokens(self) -> None:
        # $(echo $(bar)) -> ['$', '(', 'echo', '$', '(', 'bar', ')', ')']
        tokens = ["$", "(", "echo", "$", "(", "bar", ")", ")"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("$("))
        self.assertTrue(result[0].endswith(")"))
        self.assertIn("bar", result[0])

    def test_iterator__parameter_expansion__groups_tokens(self) -> None:
        # ${VAR:-val} -> ['$', '{', 'VAR', ':', '-', 'val', '}']
        tokens = ["$", "{", "VAR", ":", "-", "val", "}"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("${"))
        self.assertTrue(result[0].endswith("}"))

    def test_iterator__backticks__groups_tokens(self) -> None:
        # `echo foo` -> ['`', 'echo', 'foo', '`']
        tokens = ["`", "echo", "foo", "`"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))

    def test_iterator__escaped_backticks__groups_tokens(self) -> None:
        # `echo \`foo\`` -> ['`', 'echo', '\\', '`', 'foo', '\\', '`', '`']
        tokens = ["`", "echo", "\\", "`", "foo", "\\", "`", "`"]
        iterator = BashTokenIterator(tokens)

        result = list(iterator)

        self.assertEqual(len(result), 1)
        self.assertTrue(result[0].startswith("`"))
        self.assertTrue(result[0].endswith("`"))
