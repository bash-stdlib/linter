import os
import sys
import unittest

# Ensure src is in PYTHONPATH
sys.path.append(os.path.join(os.getcwd(), "src"))

from linter.token_iterators.shlex import ShlexTokenIterator


class TestIssueNestedQuotes(unittest.TestCase):
    def test_complex_nested_quotes(self):
        # The reproduction case provided by the user
        content = """test_two() {
  echo "complex nested"$'\n'"and escaped quotes\'\";"
}"""
        iterator = ShlexTokenIterator(content)

        # Collect tokens until we find ';'
        found_complex = False
        for token in iterator:
            if token == "echo":
                continue
            if (
                token == "\n"
                or token == " "
                or token == "{"
                or token == "}"
                or token == "()"
                or token == "test_two"
            ):
                continue

            # This should be our complex token
            self.assertEqual(token.start_offset, 20)
            # It should end where the ';' starts
            # "test_two() {\n  echo " (20 chars)
            # "complex nested"$'\n'"and escaped quotes\'\";" (41 chars)
            # Wait, 20 + 41 = 61.
            self.assertEqual(token.end_offset, 61)
            found_complex = True
            break

        self.assertTrue(found_complex)

    def test_escaped_double_quote_in_double_quotes(self):
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
