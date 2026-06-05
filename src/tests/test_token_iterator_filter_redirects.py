"""Unit tests for the TokenIteratorFilterRedirects."""

import unittest
from parsers.token_iterators.token_iterator_filter_redirects import TokenIteratorFilterRedirects


class TestTokenIteratorFilterRedirects(unittest.TestCase):
    def test_iterator__no_redirects__returns_all_tokens(self) -> None:
        tokens = ["arg1", "arg2", "arg3"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2", "arg3"])

    def test_iterator__standard_redirect__filters_out_redirect_and_target(self) -> None:
        tokens = ["arg1", ">", "file", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__append_redirect__filters_out_redirect_and_target(self) -> None:
        tokens = ["arg1", ">>", "file", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__input_redirect__filters_out_redirect_and_target(self) -> None:
        tokens = ["arg1", "<", "file", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__here_string__filters_out_redirect_and_target(self) -> None:
        tokens = ["arg1", "<<<", "here-string", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__fd_redirect__filters_out_fd_operator_and_target(self) -> None:
        # e.g. 2 > file
        tokens = ["arg1", "2", ">", "file", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__self_contained_fd_redirect__filters_out_token(self) -> None:
        # shlex sometimes keeps them together depending on spaces
        tokens = ["arg1", "2>&1", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_iterator__prefixed_redirect_no_target_needed__filters_correctly(self) -> None:
        # e.g. 2 >& 1
        tokens = ["arg1", "2", ">&", "1", "arg2"]
        iterator = TokenIteratorFilterRedirects(tokens)

        result = list(iterator)

        self.assertEqual(result, ["arg1", "arg2"])
