"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional, Set

from errors import STD000, STD006, STD008
from parsers import BashArgumentsParser
from parsers.comment_ignores import CommentIgnores
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

        try:
            with open(filepath, "r") as f:
                file_content = f.read()
        except Exception as e:
            if not self._is_ignored("STD000", 1, None):
                errors.append(STD000(filepath, str(e)))
            return errors

        comment_ignores = CommentIgnores()
        offset = 0
        for i, line_content in enumerate(file_content.splitlines(True)):
            line_num = i + 1
            comment_ignores.process_line(line_content, line_num)

            for match in self.stdlib_call_pattern.finditer(line_content):
                error = self._process_match(
                    match, file_content, filepath, comment_ignores, line_num, offset
                )
                if error:
                    errors.append(error)

            offset += len(line_content)

        for code, line in comment_ignores.get_unused_ignores():
            errors.append(STD008(filepath, line, 1, code))

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

    def _is_ignored(
        self,
        code: str,
        line: int,
        comment_ignores: Optional[CommentIgnores],
    ) -> bool:
        code = code.upper()
        if code in self.ignored_codes:
            return True
        if comment_ignores and comment_ignores.is_ignored(code, line):
            return True
        return False

    def _process_match(
        self,
        match: "re.Match[str]",
        content: "str",
        filepath: "str",
        comment_ignores: CommentIgnores,
        line_num: int,
        offset: int = 0,
    ) -> "Optional[LinterErrorBase]":
        call_name = self._get_call_name(match)
        absolute_end = offset + match.end()
        column = match.start() + 1

        args = self.argument_parser.parse(content[absolute_end:])
        if args is None:
            if not self._is_ignored(STD006.CODE, line_num, comment_ignores):
                return STD006(filepath, line_num, column, call_name)
            return None

        for validator in self.validators:
            error = validator.check(call_name, filepath, line_num, column, args)
            if error:
                if not self._is_ignored(error.CODE, line_num, comment_ignores):
                    return error
                # Continue checking other validators if this error was ignored

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
