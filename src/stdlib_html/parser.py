"""HTML parser to extract bash-stdlib function metadata from documentation."""

import html.parser
import re
from typing import Dict, List, Optional, Tuple

from .enum import (
    DocumentationIndicator,
    DocumentationSection,
    FunctionArgumentType,
    FunctionModifierType,
)
from .metadata import FunctionInput, FunctionMetadata


class HTMLParser(html.parser.HTMLParser):
    """Parses bash-stdlib documentation to extract function metadata."""

    EXCLUDED_HEADINGS: "List[str]" = ["Index", "Mock Object Reference"]
    PERMALINK_SYMBOLS: "List[str]" = ["\uf0c1", "\u00b6"]
    RE_ARGUMENT: "str" = r"(\$\d+|\.\.\.|…)"
    RE_MODIFIER_ONLY: "str" = r"\b({})\b".format(
        "|".join(m.value for m in FunctionModifierType)
    )
    RE_NUMERIC_SUFFIX: "str" = r"\[\d+\]"
    RE_STDLIB_VAR: "str" = r"\b(STDLIB_[A-Z0-9_]+)\b"
    RE_TYPE_MODIFIER: "str" = r"\b({})\s+({})\b".format(
        "|".join(t.value for t in FunctionArgumentType),
        "|".join(m.value for m in FunctionModifierType),
    )
    RE_TYPE_PAREN: "str" = (
        r"\((?:(?P<type>{}|{})|(?P<only_optional>{}))(?:,\s*(?P<optional>{}))?\)"
    ).format(
        "|".join(t.value for t in FunctionArgumentType),
        "|".join(m.value for m in FunctionModifierType),
        DocumentationIndicator.OPTIONAL.value,
        DocumentationIndicator.OPTIONAL.value,
    )
    VARIADIC_SYMBOLS: "List[str]" = ["...", "…"]

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
            if self.collecting_li and self.li_data:
                self._process_li_data("".join(self.li_data))
            self.collecting_li = False

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
            self.current_function = FunctionMetadata(
                name=name, is_testing=self.is_testing
            )
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

        if self.current_section == DocumentationSection.ARGUMENTS.value:
            self._process_argument(text)
        elif self.current_section == DocumentationSection.VARIABLES_SET.value:
            self._process_variable_set(text)
        else:
            self._process_other_li(text)

    def _process_argument(self, text: "str") -> "None":
        args = re.findall(self.RE_ARGUMENT, text)
        if not args or not self.current_function:
            return

        entity_type, is_optional, modifier = self._parse_argument_type(text)

        for arg in args:
            if any(a.name == arg for a in self.current_function.arguments):
                continue

            self.current_function.arguments.append(
                FunctionInput(arg, entity_type, is_optional, modifier)
            )

            if self._is_variadic(arg):
                self.current_function.max_args = -1
            else:
                self._increment_max_args()
                if not is_optional:
                    self.current_function.min_args += 1

    def _parse_argument_type(
        self, text: "str"
    ) -> "Tuple[FunctionArgumentType, bool, Optional[FunctionModifierType]]":
        """Extract type and optionality from an argument definition using parentheses."""
        entity_type = FunctionArgumentType.STRING
        is_optional = False
        modifier = None

        paren_match = re.search(self.RE_TYPE_PAREN, text)
        if paren_match:
            groups = paren_match.groupdict()
            type_val = groups.get("type")
            if type_val:
                found_type = FunctionArgumentType.from_str(type_val)
                if found_type:
                    entity_type = found_type

                found_modifier = FunctionModifierType.from_str(type_val)
                if found_modifier:
                    modifier = found_modifier
            if groups.get("optional") or groups.get("only_optional"):
                is_optional = True

        return entity_type, is_optional, modifier

    def _parse_modifier_type(
        self, text: "str"
    ) -> "Tuple[FunctionArgumentType, bool, Optional[FunctionModifierType]]":
        """Extract type and modifier from a keyword or global."""
        entity_type = FunctionArgumentType.STRING
        is_optional = False
        modifier = None

        # 1. Try suffix style: "string keyword"
        modifier_match = re.search(self.RE_TYPE_MODIFIER, text)
        if modifier_match:
            found_type = FunctionArgumentType.from_str(modifier_match.group(1))
            if found_type:
                entity_type = found_type

            found_modifier = FunctionModifierType.from_str(modifier_match.group(2))
            if found_modifier:
                modifier = found_modifier

        # 2. Try parentheses style: "(string)"
        if entity_type == FunctionArgumentType.STRING and not modifier:
            p_type, p_optional, p_modifier = self._parse_argument_type(text)
            if p_type != FunctionArgumentType.STRING or p_optional or p_modifier:
                entity_type = p_type
                is_optional = p_optional
                modifier = p_modifier

        # 3. Try standalone modifier
        if not modifier:
            only_modifier_match = re.search(self.RE_MODIFIER_ONLY, text)
            if only_modifier_match:
                modifier = FunctionModifierType.from_str(only_modifier_match.group(1))

        return entity_type, is_optional, modifier

    def _is_variadic(self, arg: "str") -> "bool":
        return arg in self.VARIADIC_SYMBOLS

    def _increment_max_args(self) -> "None":
        if self.current_function and self.current_function.max_args != -1:
            self.current_function.max_args += 1

    def _process_variable_set(self, text: "str") -> "None":
        match = re.search(self.RE_STDLIB_VAR, text)
        if match and self.current_function:
            var = match.group(1)
            if not any(g.name == var for g in self.current_function.globals):
                entity_type, is_optional, modifier = self._parse_modifier_type(text)
                if not modifier:
                    modifier = FunctionModifierType.GLOBAL
                self.current_function.globals.append(
                    FunctionInput(var, entity_type, is_optional, modifier)
                )

    def _process_other_li(self, text: "str") -> "None":
        if not self.current_function:
            return

        entity_type, is_optional, modifier = self._parse_modifier_type(text)
        if not modifier:
            return

        match = re.search(self.RE_STDLIB_VAR, text)
        if not match:
            return

        var = match.group(1)

        if modifier == FunctionModifierType.GLOBAL:
            target = self.current_function.globals
        elif modifier == FunctionModifierType.KEYWORD:
            target = self.current_function.keywords
        else:
            return

        if not any(e.name == var for e in target):
            target.append(FunctionInput(var, entity_type, is_optional, modifier))
