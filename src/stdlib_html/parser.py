"""HTML parser to extract bash-stdlib function metadata from documentation."""

import enum
import html.parser
import re
from typing import Dict, List, Optional, Tuple

from .metadata import FunctionMetadata


class HTMLParser(html.parser.HTMLParser):
    """Parses bash-stdlib documentation to extract function metadata."""

    EXCLUDED_HEADINGS: "List[str]" = ["Index", "Mock Object Reference"]
    PERMALINK_SYMBOLS: "List[str]" = ["\uf0c1", "\u00b6"]
    SECTIONS_TITLES: "Dict[str, str]" = {"args": "Arguments", "set": "Variables set"}
    INDICATORS = enum.Enum("type", ["optional"])
    MODIFIER_TYPES = enum.Enum("type", ["keyword", "global"])
    VARIADIC_SYMBOLS: "List[str]" = ["...", "…"]
    RE_ARGUMENT: "str" = r"(\$\d+|\.\.\.|…)"
    RE_STDLIB_VAR: "str" = r"\b(STDLIB_[A-Z0-9_]+)\b"
    RE_NUMERIC_SUFFIX: "str" = r"\[\d+\]"

    def __init__(self, is_testing: "bool" = False) -> "None":
        super().__init__()
        self.is_testing = is_testing
        self.functions: "Dict[str, FunctionMetadata]" = {}
        self.current_function: "Optional[FunctionMetadata]" = None
        self.current_section: "Optional[str]" = None
        self.in_h3: "bool" = False
        self.in_h4: "bool" = False
        self.collecting_li: "bool" = False
        self.h3_data: "List[str]" = []
        self.h4_data: "List[str]" = []
        self.li_data: "List[str]" = []

    def parse(self, html_content: "str") -> "Dict[str, FunctionMetadata]":
        """Parse HTML content and return a map of function names to metadata."""
        self.feed(html_content)
        return self.functions

    def handle_starttag(
        self,
        tag: "str",
        attrs: "List[Tuple[str, Optional[str]]]",
    ) -> "None":
        if tag == "h3":
            self.in_h3 = True
            self.h3_data = []
        elif tag == "h4":
            self.in_h4 = True
            self.h4_data = []
        elif tag == "li":
            self.collecting_li = True
            self.li_data = []

    def handle_endtag(self, tag: "str") -> "None":
        if tag == "h3":
            self.in_h3 = False
            self._process_h3_data("".join(self.h3_data))
        elif tag == "h4":
            self.in_h4 = False
            self._process_h4_data("".join(self.h4_data))
        elif tag == "li":
            self.collecting_li = False
            if self.li_data:
                self._process_li_data("".join(self.li_data))

    def handle_data(self, data: "str") -> "None":
        if self.in_h3:
            self.h3_data.append(data)
        elif self.in_h4:
            self.h4_data.append(data)
        elif self.collecting_li:
            self.li_data.append(data)

    def _process_h3_data(self, data: "str") -> "None":
        name = self._clean_heading(data)
        if name and name not in self.EXCLUDED_HEADINGS:
            name = name.split()[0]
            self.current_function = FunctionMetadata(name=name, is_testing=self.is_testing)
            self.functions[name] = self.current_function
            self.current_section = None
        else:
            self.current_function = None

    def _process_h4_data(self, data: "str") -> "None":
        self.current_section = self._clean_heading(data)

    def _clean_heading(self, text: "str") -> "str":
        # Remove common RTD/Sphinx permalink symbols
        for symbol in self.PERMALINK_SYMBOLS:
            text = text.replace(symbol, "")

        # Remove numeric suffixes like [123]
        text = re.sub(self.RE_NUMERIC_SUFFIX, "", text)

        return text.strip()

    def _process_li_data(self, text: "str") -> "None":
        if not self.current_function:
            return

        text = text.strip()
        if not text:
            return

        if self.current_section == self.SECTIONS_TITLES["args"]:
            self._process_argument(text)
        elif self.current_section == self.SECTIONS_TITLES["set"]:
            self._process_variable_set(text)
        else:
            self._process_other_li(text)

    def _process_argument(self, text: "str") -> "None":
        args = re.findall(self.RE_ARGUMENT, text)
        if not args:
            return

        is_required = self._is_required(text)

        for arg in args:
            if arg in self.current_function.arguments:
                continue

            self.current_function.arguments.append(arg)

            if self._is_variadic(arg):
                self.current_function.max_args = -1
            else:
                self._increment_max_args()
                if is_required:
                    self.current_function.min_args += 1

    def _is_variadic(self, arg: "str") -> "bool":
        return arg in self.VARIADIC_SYMBOLS

    def _is_required(self, text: "str") -> "bool":
        return self.INDICATORS.optional.name not in text.lower()

    def _increment_max_args(self) -> "None":
        if self.current_function.max_args != -1:
            self.current_function.max_args += 1

    def _process_variable_set(self, text: "str") -> "None":
        match = re.search(self.RE_STDLIB_VAR, text)
        if match:
            var = match.group(1)
            if var not in self.current_function.globals:
                self.current_function.globals.append(var)

    def _process_other_li(self, text: "str") -> "None":
        for modifier, function_set in dict(
            {
                self.MODIFIER_TYPES["global"].name: self.current_function.globals,
                self.MODIFIER_TYPES["keyword"].name: self.current_function.keywords,
            }
        ).items():
            if modifier in text.lower():
                match = re.search(self.RE_STDLIB_VAR, text)
                if match:
                    entity = match.group(1)
                    if entity not in function_set:
                        function_set.append(entity)
