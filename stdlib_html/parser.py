"""HTML parser to extract stdlib function names from documentation."""

import html.parser
import re

from constants import STDLIB_PATTERN


class HTMLParser(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.functions: set[str] = set()

    def parse(self, html_content: str) -> set[str]:
        self.feed(html_content)
        return self.functions

    def handle_data(self, data: str) -> None:
        self._extract_stdlib_functions(data)

    def _extract_stdlib_functions(self, text: str) -> None:
        potential_functions = re.findall(STDLIB_PATTERN, text)
        for candidate in potential_functions:
            clean_function = self._clean_function_name(candidate)
            if self._is_valid_function_name(clean_function):
                self.functions.add(clean_function)

    def _clean_function_name(self, name: str) -> str:
        cleaned_name = name
        while clean_function_ends_with_invalid_char(cleaned_name):
            cleaned_name = cleaned_name[:-1]
        return cleaned_name

    def _is_valid_function_name(self, name: str) -> bool:
        return "." in name


def clean_function_ends_with_invalid_char(name: str) -> bool:
    return bool(name and (name.endswith(".") or name.endswith("_")))
