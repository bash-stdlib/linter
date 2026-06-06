import unittest
from transformers.line_continuation import LineContinuationTransformer

class TestLineContinuationTransformer(unittest.TestCase):
    def setUp(self):
        self.transformer = LineContinuationTransformer()

    def test_transform__line_continuation__replaces_with_space(self):
        content = "echo \\\nhello"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo  hello")

    def test_transform__no_line_continuation__returns_original_content(self):
        content = "echo hello"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo hello")

    def test_transform__multiple_line_continuations__replaces_all_with_spaces(self):
        content = "echo \\\nhello \\\nworld"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo  hello  world")

if __name__ == "__main__":
    unittest.main()
