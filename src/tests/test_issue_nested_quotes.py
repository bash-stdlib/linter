import unittest

from linter.token_iterators.shlex import ShlexTokenIterator


class TestIssueNestedQuotes(unittest.TestCase):
    def test_read_token__complex_nested_quotes__identifies_single_token(self):
        content = """test_two() {
  echo "complex nested"$'\n'"and escaped quotes\'\";"
}"""
        iterator = ShlexTokenIterator(content)

        found_complex = False
        token_start = -1
        token_end = -1
        for token in iterator:
            if token == "echo":
                continue

            if token in ("\n", " ", "{", "}", "()", "test_two"):
                continue

            token_start = token.start_offset
            token_end = token.end_offset
            found_complex = True
            break

        self.assertTrue(found_complex)
        self.assertEqual(token_start, 20)
        self.assertEqual(token_end, 61)

    def test_read_token__escaped_double_quote__identifies_single_token(self):
        content = 'echo "a\\"b"'
        iterator = ShlexTokenIterator(content)

        tokens = [t for t in iterator if t != "\n"]

        self.assertEqual(len(tokens), 2)
        self.assertEqual(tokens[0], "echo")
        self.assertEqual(str(tokens[1]), 'a"b')
        self.assertEqual(tokens[1].start_offset, 5)
        self.assertEqual(tokens[1].end_offset, 11)


if __name__ == "__main__":
    unittest.main()
