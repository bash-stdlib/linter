"""HTML parser to extract stdlib function names from documentation."""

import html.parser
import re
from constants import STDLIB_PATTERN

class HTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.functions = set()

    def parse(self, html_content):
        self.feed(html_content)
        return self.functions

    def handle_data(self, data):
        self._extract_stdlib_functions(data)

    def _extract_stdlib_functions(self, text):
        potential_functions = re.findall(STDLIB_PATTERN, text)
        for candidate in potential_functions:
            clean_function = self._clean_function_name(candidate)
            if self._is_valid_function_name(clean_function):
                self.functions.add(clean_function)

    def _clean_function_name(self, name):
        cleaned_name = name
        while clean_function_ends_with_invalid_char(cleaned_name):
            cleaned_name = cleaned_name[:-1]
        return cleaned_name

    def _is_valid_function_name(self, name):
        return '.' in name

def clean_function_ends_with_invalid_char(name):
    return name and (name.endswith('.') or name.endswith('_'))
