import unittest

from src.example.shlex import EnhancedShlex


class TestEnhancedShlex(unittest.TestCase):
    def setUp(self):
        self.target_chars = ["|", "#"]

    def test_unquoted_token(self):
        """Standard tokens without quotes should be marked as False."""
        stream = "hello world"
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "hello")
        self.assertFalse(tokens[0].is_fully_quoted)
        self.assertEqual(tokens[1].value, "world")
        self.assertFalse(tokens[1].is_fully_quoted)

    def test_fully_quoted_token(self):
        """Tokens completely wrapped in quotes should be marked as True."""
        stream = "\"hello world\" 'single quotes'"
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "hello world")
        self.assertTrue(tokens[0].is_fully_quoted)
        self.assertEqual(tokens[1].value, "single quotes")
        self.assertTrue(tokens[1].is_fully_quoted)

    def test_partially_quoted_token(self):
        """Partially quoted tokens should not be marked as fully quoted."""
        stream = 'prefix"middle"suffix'
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "prefixmiddlesuffix")
        self.assertFalse(tokens[0].is_fully_quoted)

    def test_unquoted_special_characters(self):
        """Target characters outside of quotes must be identified."""
        stream = "cat file.txt | grep pattern"
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        pipe_token = tokens[2]
        self.assertEqual(pipe_token.value, "|")
        self.assertIn("|", pipe_token.unquoted_specials)

    def test_quoted_special_characters(self):
        """Target characters inside quotes must NOT be flagged as unquoted specials."""
        stream = "\"pipe | inside\" 'hash # inside'"
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0].value, "pipe | inside")
        self.assertTrue(tokens[0].is_fully_quoted)
        self.assertEqual(tokens[0].unquoted_specials, set())

        self.assertEqual(tokens[1].value, "hash # inside")
        self.assertTrue(tokens[1].is_fully_quoted)
        self.assertEqual(tokens[1].unquoted_specials, set())

    def test_hash_comment_disabled(self):
        """The '#' character should be processed as text, not a comment starter."""
        stream = "command #unquoted_hash_tag"
        lexer = EnhancedShlex(stream, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[1].value, "#unquoted_hash_tag")
        self.assertIn("#", tokens[1].unquoted_specials)

    def test_escaped_special_character(self):
        """An escaped target character in POSIX mode should not be flagged as unquoted."""
        stream = r"escaped\|pipe"
        lexer = EnhancedShlex(stream, posix=True, target_chars=self.target_chars)
        lexer.whitespace_split = True
        tokens = list(lexer)

        self.assertEqual(len(tokens), 1)
        self.assertEqual(tokens[0].value, "escaped|pipe")
        self.assertEqual(tokens[0].unquoted_specials, set())


if __name__ == "__main__":
    unittest.main()
