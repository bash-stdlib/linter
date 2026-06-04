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
                self._process_li_data(" ".join(self.li_data))

    def handle_data(self, data: "str") -> "None":
        if self.in_h3:
            name = data.strip()
            if name.startswith("stdlib."):
                name = name.split()[0]
                self.current_function = FunctionMetadata(name=name)
                self.functions[name] = self.current_function
                self.current_section = None
        elif self.in_h4:
            section_name = data.strip()
            if section_name in ["Arguments", "Variables set"]:
                self.current_section = section_name
        elif self.collecting_li:
            self.li_data.append(data)

    def _process_li_data(self, text: "str") -> "None":
        if not self.current_function:
            return

        text = text.strip()
        if not text:
            return

        if self.current_section == "Arguments":
            match = re.search(r"(\$\d+|\.\.\.|…)", text)
            if match:
                arg = match.group(1)
                if arg == "…":
                    arg = "..."

                if arg not in self.current_function.arguments:
                    self.current_function.arguments.append(arg)

                    if arg == "...":
                        self.current_function.max_args = -1
                    else:
                        if self.current_function.max_args != -1:
                            self.current_function.max_args += 1

                        if "(optional" not in text.lower():
                            if (
                                self.current_function.min_args
                                == self.current_function.max_args - 1
                            ):
                                self.current_function.min_args += 1

        elif self.current_section == "Variables set":
            match = re.search(r"\b(STDLIB_[A-Z0-9_]+)\b", text)
            if match:
                var = match.group(1)
                if var not in self.current_function.globals:
                    self.current_function.globals.append(var)
        else:
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
