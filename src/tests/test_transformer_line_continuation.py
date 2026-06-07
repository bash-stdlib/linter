import unittest

from parsers.transformers.line_continuation import LineContinuationTransformer


class TestLineContinuationTransformer(unittest.TestCase):
    def setUp(self) -> None:
        self.transformer = LineContinuationTransformer()

    def test_transform__line_continuation__replaces_with_spaces_by_default(
        self,
    ) -> None:
        content = "echo \\\nhello"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo   hello")

    def test_transform__line_continuation__replaces_with_vtab_when_preserving(
        self,
    ) -> None:
        content = "echo \\\nhello"

        result = self.transformer.transform(content, preserve_lines=True)

        self.assertEqual(result, "echo  \vhello")

    def test_transform__no_line_continuation__returns_original_content(self) -> None:
        content = "echo hello"

        result = self.transformer.transform(content)

        self.assertEqual(result, "echo hello")

    def test_transform__multiple_line_continuations__replaces_all_correctly(
        self,
    ) -> None:
        content = "echo \\\nhello \\\nworld"

        result = self.transformer.transform(content)
        self.assertEqual(result, "echo   hello   world")

        result_preserved = self.transformer.transform(content, preserve_lines=True)
        self.assertEqual(result_preserved, "echo  \vhello  \vworld")


if __name__ == "__main__":
    unittest.main()
