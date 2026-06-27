import unittest

from stdlib_html.parser import HTMLParser


class TestHTMLParser(unittest.TestCase):
    def setUp(self) -> "None":
        self.parser = HTMLParser()

    def test_parse__single_function__extracts_name_correctly(self) -> "None":
        html = """
        <section id="stdlib-array-assert-is-array">
        <h3>stdlib.array.assert.is_array</h3>
        </section>
        """

        result = self.parser.parse(html)

        self.assertIn("stdlib.array.assert.is_array", result)

    def test_parse__multiple_functions__extracts_all_names_correctly(self) -> "None":
        html = """
        <section id="stdlib-func1"><h3>stdlib.func1</h3></section>
        <section id="stdlib-func2"><h3>stdlib.func2</h3></section>
        """

        result = self.parser.parse(html)

        self.assertEqual(len(result), 2)
        self.assertIn("stdlib.func1", result)
        self.assertIn("stdlib.func2", result)

    def test_parse__arguments__extracts_arguments_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-args">
        <h3>stdlib.test.args</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (string): Arg 1</p></li>
        <li><p><strong>$2</strong> (integer): Arg 2</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.args"]
        self.assertEqual(metadata.arguments[0].name, "$1")
        self.assertEqual(metadata.arguments[0].type, "string")
        self.assertFalse(metadata.arguments[0].is_optional)
        self.assertEqual(metadata.arguments[1].name, "$2")
        self.assertEqual(metadata.arguments[1].type, "integer")
        self.assertFalse(metadata.arguments[1].is_optional)

    def test_parse__keywords__extracts_keywords_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-keywords">
        <h3>stdlib.test.keywords</h3>
        <ul class="simple">
        <li><p>STDLIB_KW_1 string keyword: Some keyword</p></li>
        <li><p>STDLIB_KW_2 boolean keyword: Another keyword</p></li>
        </ul>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.keywords"]
        self.assertEqual(metadata.keywords[0].name, "STDLIB_KW_1")
        self.assertEqual(metadata.keywords[0].type, "string")
        self.assertEqual(metadata.keywords[0].modifier, "keyword")
        self.assertEqual(metadata.keywords[1].name, "STDLIB_KW_2")
        self.assertEqual(metadata.keywords[1].type, "boolean")
        self.assertEqual(metadata.keywords[1].modifier, "keyword")

    def test_parse__globals__extracts_globals_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-globals">
        <h3>stdlib.test.globals</h3>
        <section id="variables-set">
        <h4>Variables set</h4>
        <ul class="simple">
        <li><p><strong>STDLIB_VAR_1</strong> (string): Some global</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.globals"]
        self.assertEqual(metadata.globals[0].name, "STDLIB_VAR_1")
        self.assertEqual(metadata.globals[0].type, "string")
        self.assertEqual(metadata.globals[0].modifier, "global")

    def test_parse__mixed_metadata__extracts_everything_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-mixed">
        <h3>stdlib.test.mixed</h3>
        <ul class="simple">
        <li><p>STDLIB_KW string keyword: A keyword</p></li>
        </ul>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (string): An argument</p></li>
        </ul>
        </section>
        <section id="variables-set">
        <h4>Variables set</h4>
        <ul class="simple">
        <li><p><strong>STDLIB_GLOBAL</strong> (string): A global variable</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.mixed"]
        self.assertEqual(metadata.name, "stdlib.test.mixed")
        self.assertEqual(metadata.arguments[0].name, "$1")
        self.assertEqual(metadata.arguments[0].type, "string")
        self.assertEqual(metadata.keywords[0].name, "STDLIB_KW")
        self.assertEqual(metadata.keywords[0].type, "string")
        self.assertEqual(metadata.keywords[0].modifier, "keyword")
        self.assertEqual(metadata.globals[0].name, "STDLIB_GLOBAL")
        self.assertEqual(metadata.globals[0].type, "string")
        self.assertEqual(metadata.globals[0].modifier, "global")

    def test_parse__optional_arguments__calculates_min_max_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-optional">
        <h3>stdlib.test.optional</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (string): Required arg</p></li>
        <li><p><strong>$2</strong> (integer, optional): Optional arg</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.optional"]
        self.assertEqual(metadata.min_args, 1)
        self.assertEqual(metadata.max_args, 2)
        self.assertEqual(metadata.arguments[1].type, "integer")
        self.assertTrue(metadata.arguments[1].is_optional)

    def test_parse__variadic_arguments__calculates_min_max_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-variadic">
        <h3>stdlib.test.variadic</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (string): Required arg</p></li>
        <li><p><strong>...</strong>: Variadic</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.variadic"]
        self.assertEqual(metadata.min_args, 1)
        self.assertEqual(metadata.max_args, -1)
        self.assertEqual(metadata.arguments[1].name, "...")
        self.assertEqual(metadata.arguments[1].type, "string")

    def test_parse__required_after_optional__calculates_min_args_as_count(
        self,
    ) -> "None":
        html = """
        <section id="stdlib-test-mixed-order">
        <h3>stdlib.test.mixed_order</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (string): Opt 1 (optional)</p></li>
        <li><p><strong>$2</strong> (string): Req 2</p></li>
        </ul>
        </section>
        </section>
        """

        result = self.parser.parse(html)

        metadata = result["stdlib.test.mixed_order"]

        self.assertEqual(metadata.min_args, 1)
        self.assertEqual(metadata.max_args, 2)
        self.assertTrue(metadata.arguments[0].is_optional)
        self.assertFalse(metadata.arguments[1].is_optional)

    def test_parse__multiple_args_in_one_li__extracts_all_counts_correctly(
        self,
    ) -> "None":
        html = """
        <section id="stdlib-test-multiple">
        <h3>stdlib.test.multiple</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1, $2</strong> (string): Two required args</p></li>
        </ul>
        </section>
        </section>
        """
        result = self.parser.parse(html)
        metadata = result["stdlib.test.multiple"]
        self.assertEqual(metadata.min_args, 2)
        self.assertEqual(metadata.max_args, 2)
        self.assertEqual(len(metadata.arguments), 2)
        self.assertEqual(metadata.arguments[0].name, "$1")
        self.assertEqual(metadata.arguments[0].type, "string")
        self.assertEqual(metadata.arguments[1].name, "$2")
        self.assertEqual(metadata.arguments[1].type, "string")

    def test_parse__array_type__is_extracted_as_array_str(self) -> "None":
        html = """
        <section id="stdlib-test-array">
        <h3>stdlib.test.array</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (array): An array</p></li>
        </ul>
        </section>
        </section>
        """
        result = self.parser.parse(html)
        metadata = result["stdlib.test.array"]
        self.assertEqual(metadata.arguments[0].type, "array[str]")

    def test_parse__reserved_modifier__is_extracted_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-reserved">
        <h3>stdlib.test.reserved</h3>
        <section id="arguments">
        <h4>Arguments</h4>
        <ul class="simple">
        <li><p><strong>$1</strong> (reserved): A reserved arg</p></li>
        </ul>
        </section>
        </section>
        """
        result = self.parser.parse(html)
        metadata = result["stdlib.test.reserved"]
        self.assertEqual(metadata.arguments[0].modifier, "reserved")

    def test_parse__paren_type_and_modifier__extracts_both_correctly(self) -> "None":
        html = """
        <section id="stdlib-test-mixed-paren">
        <h3>stdlib.test.mixed_paren</h3>
        <ul class="simple">
        <li><p>STDLIB_VAR (integer global): A global var</p></li>
        </ul>
        </section>
        """
        result = self.parser.parse(html)
        metadata = result["stdlib.test.mixed_paren"]
        self.assertEqual(metadata.globals[0].type, "integer")
        self.assertEqual(metadata.globals[0].modifier, "global")


if __name__ == "__main__":
    unittest.main()
