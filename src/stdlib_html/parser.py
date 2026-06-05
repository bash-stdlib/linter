"""HTML parser to extract bash-stdlib function metadata from documentation."""

import html.parser
import re
from typing import Dict, List, Optional, Tuple

from .metadata import FunctionMetadata


class HTMLParser(html.parser.HTMLParser):
    """Parses bash-stdlib documentation to extract function metadata."""

    def __init__(self) -> "None":
        super().__init__()
        self.functions: "Dict[str, FunctionMetadata]" = {}
        self.current_function: "Optional[FunctionMetadata]" = None
        self.current_section: "Optional[str]" = None
        self.in_h3: "bool" = False
        self.in_h4: "bool" = False
        self.collecting_li: "bool" = False
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
        elif tag == "h4":
            self.in_h4 = True
        elif tag == "li":
            self.collecting_li = True
            self.li_data = []

    def handle_endtag(self, tag: "str") -> "None":
        if tag == "h3":
            self.in_h3 = False
        elif tag == "h4":
            self.in_h4 = False
        elif tag == "li":
            self.collecting_li = False
            if self.li_data:
                self._process_li_data("".join(self.li_data))

    def handle_data(self, data: "str") -> "None":
        if self.in_h3:
            name = data.strip()
            if name.startswith("stdlib."):
                name = name.split()[0]
                self.current_function = FunctionMetadata(name=name)
                self.functions[name] = self.current_function
                self.current_section = None
        elif self.in_h4:
            self.current_section = data.strip()
        elif self.collecting_li:
            self.li_data.append(data)

    def _process_li_data(self, text: "str") -> "None":
        if not self.current_function:
            return

        text = text.strip()
        if not text:
            return

        if self.current_section == "Arguments":
            self._process_argument(text)
        elif self.current_section == "Variables set":
            self._process_variable_set(text)
        else:
            self._process_other_li(text)

    def _process_argument(self, text: "str") -> "None":
        match = re.search(r"(\$\d+|\.\.\.|…)", text)
        if not match:
            return

        arg = match.group(1)
        if arg in self.current_function.arguments:
            return

        self.current_function.arguments.append(arg)

        if self._is_variadic(arg):
            self.current_function.max_args = -1
        else:
            self._increment_max_args()
            if self._is_required(text):
                self.current_function.min_args += 1

    def _is_variadic(self, arg: "str") -> "bool":
        return arg in ["...", "…"]

    def _is_required(self, text: "str") -> "bool":
        return "optional" not in text.lower()

    def _increment_max_args(self) -> "None":
        if self.current_function.max_args != -1:
            self.current_function.max_args += 1

    def _process_variable_set(self, text: "str") -> "None":
        match = re.search(r"\b(STDLIB_[A-Z0-9_]+)\b", text)
        if match:
            var = match.group(1)
            if var not in self.current_function.globals:
                self.current_function.globals.append(var)

    def _process_other_li(self, text: "str") -> "None":
        if "keyword" in text.lower():
            match = re.search(r"\b(STDLIB_[A-Z0-9_]+)\b", text)
            if match:
                kw = match.group(1)
                if kw not in self.current_function.keywords:
                    self.current_function.keywords.append(kw)
        elif "global" in text.lower():
            match = re.search(r"\b(STDLIB_[A-Z0-9_]+)\b", text)
            if match:
                var = match.group(1)
                if var not in self.current_function.globals:
                    self.current_function.globals.append(var)
