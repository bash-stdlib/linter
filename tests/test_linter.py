import unittest
import os
import json
from stdlib_html.parser import HTMLParser
from linter import validate_call, lint_file

class TestLinter(unittest.TestCase):
    def test_html_parser(self):
        html_content = """
        <html>
            <body>
                <h1>stdlib.array.assert.is_array</h1>
                <p>Some text stdlib.string.args.join.</p>
                <a href="#">stdlib.io.path.query.is_file</a>
                <span>Not a function stdlib.invalid</span>
            </body>
        </html>
        """
        parser = HTMLParser()
        parser.feed(html_content)

        self.assertTrue("stdlib.array.assert.is_array" in parser.functions)
        self.assertTrue("stdlib.string.args.join" in parser.functions)
        self.assertTrue("stdlib.io.path.query.is_file" in parser.functions)

    def test_validation_logic(self):
        functions = ["stdlib.array.assert.is_array", "stdlib.string.args.join"]
        namespaces = ["stdlib", "stdlib.array", "stdlib.array.assert", "stdlib.string", "stdlib.string.args"]

        # Valid function
        valid, msg = validate_call("stdlib.array.assert.is_array", functions, namespaces)
        self.assertTrue(valid)

        # Invalid function in valid namespace
        valid, msg = validate_call("stdlib.array.assert.is_ary", functions, namespaces)
        self.assertFalse(valid)
        self.assertIn("Invalid function", msg)
        self.assertIn("stdlib.array.assert", msg)
        self.assertIn("Did you mean 'stdlib.array.assert.is_array'?", msg)

        # Invalid namespace
        valid, msg = validate_call("stdlib.unknown.func", functions, namespaces)
        self.assertFalse(valid)
        self.assertIn("Invalid namespace", msg)

        # Calling a namespace
        valid, msg = validate_call("stdlib.array.assert", functions, namespaces)
        self.assertFalse(valid)
        self.assertIn("is a namespace", msg)

    def test_lint_file(self):
        metadata = {
            "functions": ["stdlib.array.assert.is_array"],
            "namespaces": ["stdlib", "stdlib.array", "stdlib.array.assert"]
        }
        test_file = "test_script.sh"
        content = """
#!/bin/bash
stdlib.array.assert.is_array my_array
stdlib.array.assert.is_ary wrong_func
"""
        with open(test_file, "w") as f:
            f.write(content)

        try:
            errors = lint_file(test_file, metadata)
            self.assertEqual(len(errors), 1)
            self.assertEqual(errors[0].line, 4)
            self.assertEqual(errors[0].match, "stdlib.array.assert.is_ary")
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

if __name__ == '__main__':
    unittest.main()
