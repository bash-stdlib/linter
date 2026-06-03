import unittest

from stdlib_html.parser import HTMLParser


class TestHTMLParser(unittest.TestCase):

    def setUp(self) -> None:
        self.parser = HTMLParser()

    def test_parse__single_function__extracts_correctly(self) -> None:
        html = "<div>stdlib.array.assert.is_array</div>"

        result = self.parser.parse(html)

        self.assertIn("stdlib.array.assert.is_array", result)

    def test_parse__multiple_functions__extracts_all_correctly(self) -> None:
        html = "<h1>stdlib.func1</h1><p>stdlib.func2</p>"

        result = self.parser.parse(html)

        self.assertEqual(len(result), 2)
        self.assertIn("stdlib.func1", result)
        self.assertIn("stdlib.func2", result)

    def test_parse__trailing_dot__strips_invalid_char(self) -> None:
        html = "<span>stdlib.func1.</span>"

        result = self.parser.parse(html)

        self.assertIn("stdlib.func1", result)
        self.assertNotIn("stdlib.func1.", result)

    def test_parse__trailing_underscore__strips_invalid_char(self) -> None:
        html = "<span>stdlib.func1_</span>"

        result = self.parser.parse(html)

        self.assertIn("stdlib.func1", result)

    def test_parse__non_stdlib_text__ignores_content(self) -> None:
        html = "<span>other.library.func</span>"

        result = self.parser.parse(html)

        self.assertEqual(len(result), 0)

    def test_parse__nested_tags__extracts_correctly(self) -> None:
        html = "<div><a href='#'>stdlib.nested.func</a></div>"

        result = self.parser.parse(html)

        self.assertIn("stdlib.nested.func", result)

    def test_parse__missing_sub_namespaces__ignores_incomplete_name(
            self) -> None:
        html = "<span>stdlib</span>"

        result = self.parser.parse(html)

        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
