"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, Optional

from errors import STD000, STD006
from parsers import BashArgumentsParser
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    NotNamespaceCallValidator,
    IsTestingFunctionCallValidator,
)

if TYPE_CHECKING:
    from typing import List, Set

    from errors.base import LinterErrorBase
    from validators.base import ValidatorBase


class Linter:
    def __init__(
        self,
        metadata: "Any",
        ignored_codes: "Optional[List[str]]" = None,
    ) -> "None":
        self.functions: "Set[str]" = set(metadata["functions"].keys())
        self.namespaces: "Set[str]" = set(metadata["namespaces"])
        self.metadata = metadata["functions"]
        self.ignored_codes: "Set[str]" = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.stdlib_call_pattern: "re.Pattern[str]" = self._build_call_pattern()
        self.argument_parser = BashArgumentsParser()
        self.validators: "List[ValidatorBase]" = [
            NotNamespaceCallValidator(self.functions, self.namespaces),
            IsFunctionCallValidator(self.functions, self.namespaces),
            ArgumentCountValidator(self.functions, self.namespaces, self.metadata),
            IsTestingFunctionCallValidator(
                self.functions, self.namespaces, self.metadata
            ),
        ]

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        errors: "List[LinterErrorBase]" = []
        filepath = os.path.abspath(filepath)
        file_content = self._read_file(filepath, errors)
        if file_content is None:
            return errors

        for match in self.stdlib_call_pattern.finditer(file_content):
            error = self._process_match(match, file_content, filepath)
            if error:
                errors.append(error)

        return errors

    def _build_call_pattern(self) -> "re.Pattern[str]":
        roots = set()
        for name in self.functions | self.namespaces:
            if "." in name:
                roots.add(name.split(".")[0])
            elif "_" in name:
                roots.add(name.split("_")[0] + "_")
            elif name.startswith("@"):
                roots.add("@")
            else:
                roots.add(name)

        sorted_roots = sorted(list(roots), key=len, reverse=True)
        pattern = r"(?<!\w)({}[a-z0-9._]*)\b".format(
            "|".join(re.escape(r) for r in sorted_roots)
        )

        return re.compile(pattern)

    def _read_file(
        self,
        filepath: "str",
        errors: "List[LinterErrorBase]",
    ) -> "Optional[str]":
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception as e:
            if STD000.CODE not in self.ignored_codes:
                errors.append(STD000(filepath, str(e)))
            return None

    def _process_match(
        self, match: "re.Match[str]", content: "str", filepath: "str"
    ) -> "Optional[LinterErrorBase]":
        call_name = self._get_call_name(match)
        line = self._get_line_number(content, match.start())
        column = self._get_column_number(content, match.start())

        args = self.argument_parser.parse(content[match.end() :])
        if args is None:
            if STD006.CODE not in self.ignored_codes:
                return STD006(filepath, line, column, call_name)
            return None

        for validator in self.validators:
            error = validator.check(call_name, filepath, line, column, args)
            if error:
                if error.CODE not in self.ignored_codes:
                    return error
                return None

        return None

    def _get_call_name(self, match: "re.Match[str]") -> "str":
        call = str(match.group(1))
        if call.endswith("."):
            return call[:-1]
        return call

    def _get_line_number(self, content: "str", offset: "int") -> "int":
        return content.count("\n", 0, offset) + 1

    def _get_column_number(self, content: "str", offset: "int") -> "int":
        last_newline = content.rfind("\n", 0, offset)
        return offset - last_newline if last_newline != -1 else offset + 1
