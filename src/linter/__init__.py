"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional

from errors import STD000, STD006, STD008, STD009
from linter.line_iterators.comment_ignores import CommentIgnores
from linter.line_iterators.events_iterator import EventsIterator
from linter.state.file_state import FileLinterState
from linter.state.global_state import GlobalLinterState
from parsers import BashArgumentsParser
from parsers.token_iterators import ShlexTokenIterator
from parsers.transformers import LineContinuationTransformer
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    IsTestingFunctionCallValidator,
    NotNamespaceCallValidator,
)

if TYPE_CHECKING:
    from typing import List, Match, Pattern

    from errors.base import LinterErrorBase
    from linter.line_iterators.base import LineIteratorBase
    from validators.base import ValidatorBase


class Linter:
    def __init__(
        self,
        metadata: "Any",
        ignored_codes: "Optional[List[str]]" = None,
        appendum: "Optional[List[str]]" = None,
    ) -> "None":
        self.global_state = GlobalLinterState(metadata, ignored_codes, appendum)
        self.stdlib_call_pattern: "Pattern[str]" = self._build_call_pattern()
        self.argument_parser = BashArgumentsParser()
        self.line_continuation_transformer = LineContinuationTransformer()

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        self.file_state = FileLinterState()
        validators: "List[ValidatorBase]" = [
            NotNamespaceCallValidator(self.global_state, self.file_state),
            IsFunctionCallValidator(self.global_state, self.file_state),
            ArgumentCountValidator(self.global_state, self.file_state),
            IsTestingFunctionCallValidator(self.global_state, self.file_state),
        ]
        line_iterators: "List[LineIteratorBase]" = [
            CommentIgnores(self.global_state, self.file_state),
            EventsIterator(self.global_state, self.file_state),
        ]

        errors: "List[LinterErrorBase]" = []
        filepath = os.path.abspath(filepath)

        try:
            with open(filepath, "r") as f:
                raw_content = f.read()
                file_content = self.line_continuation_transformer.transform(
                    raw_content, preserve_lines=True
                )
        except Exception as e:
            if not self._is_ignored("STD000", 1):
                errors.append(STD000(filepath, str(e)))
            return errors

        offset = 0
        for i, line_content in enumerate(file_content.splitlines(True)):
            line_num = i + 1
            for iterator in line_iterators:
                iterator.process_line(line_content, line_num, offset)

            for match in self.stdlib_call_pattern.finditer(line_content):
                error = self._process_match(
                    match, file_content, filepath, validators, line_num, offset
                )
                if error:
                    errors.append(error)

            offset += len(line_content)

        for scope in self.file_state.function_scopes:
            if scope.end_line == -1:
                if not self._is_ignored(STD009.CODE, scope.start_line):
                    # For STD009, we don't have a column, but let's use 1
                    errors.append(STD009(filepath, scope.start_line, 1, scope.name))

        for code, line in self.file_state.get_unused_ignores():
            errors.append(STD008(filepath, line, 1, code))

        return errors

    def _build_call_pattern(self) -> "Pattern[str]":
        dot_roots = set()
        underscore_roots = set()

        for name in (
            self.global_state.functions
            | self.global_state.namespaces
            | self.global_state.appendum
        ):
            if name.startswith("_"):
                # Handle cases like _testing.func or _testing.example
                dot_roots.add(name.split(".")[0])
            elif "." in name:
                dot_roots.add(name.split(".")[0])
            elif "_" in name:
                underscore_roots.add(name.split("_")[0] + "_")
            elif name.startswith("@"):
                # Always treat names starting with @ as dot-based roots
                dot_roots.add(name.split(".")[0])
            else:
                dot_roots.add(name)

        sorted_dot_roots = sorted(list(dot_roots), key=len, reverse=True)
        sorted_underscore_roots = sorted(list(underscore_roots), key=len, reverse=True)

        # Combine all roots into a single pattern.
        # dot_roots are names that should only match if they are either exactly the name
        # or followed by a dot (to avoid matching things like @parametrize_with_errors).
        # underscore_roots (like assert_) can be followed by anything.

        dot_pattern = (
            r"(?:{})(?:\.[a-z0-9._]*)?".format(
                "|".join(re.escape(r) for r in sorted_dot_roots)
            )
            if sorted_dot_roots
            else r"(?!)"
        )
        underscore_pattern = (
            r"(?:{})[a-z0-9._]*".format(
                "|".join(re.escape(r) for r in sorted_underscore_roots)
            )
            if sorted_underscore_roots
            else r"(?!)"
        )

        pattern = r"(?<!\w)({}|{})(?![a-z0-9._])".format(
            dot_pattern, underscore_pattern
        )

        return re.compile(pattern)

    def _is_ignored(
        self,
        code: str,
        line: int,
    ) -> bool:
        code = code.upper()
        if code in self.global_state.ignored_codes:
            return True
        if self.file_state.is_ignored(code, line):
            return True
        return False

    def _is_appendum(self, call_name: str) -> bool:
        """Check if the call name or any of its parent namespaces are in appendum."""
        if call_name in self.global_state.appendum:
            return True

        parts = call_name.split(".")
        for i in range(1, len(parts)):
            prefix = ".".join(parts[:i])
            if prefix in self.global_state.appendum:
                return True
        return False

    def _process_match(
        self,
        match: "Match[str]",
        content: "str",
        filepath: "str",
        validators: "List[ValidatorBase]",
        line_num: int,
        offset: int = 0,
    ) -> "Optional[LinterErrorBase]":
        if self._is_function_definition(match, content, offset):
            return None

        if not self._is_at_command_position(match, content, offset):
            return None

        call_name = self._get_call_name(match)

        if self._is_appendum(call_name):
            return None

        absolute_end = offset + match.end()
        column = match.start() + 1

        args = self.argument_parser.parse(content[absolute_end:])
        if args is None:
            if not self._is_ignored(STD006.CODE, line_num):
                return STD006(filepath, line_num, column, call_name)
            return None

        for validator in validators:
            error = validator.check(call_name, filepath, line_num, column, args)
            if error:
                if not self._is_ignored(error.CODE, line_num):
                    return error
                # Continue checking other validators if this error was ignored

        return None

    def _is_at_command_position(
        self, match: "Match[str]", content: "str", offset: "int"
    ) -> bool:
        """Check if the match is at the start of a command."""
        before = content[: offset + match.start()]

        if before.endswith("$") or before.endswith("${"):
            return False

        last_newline = before.rfind("\n")
        line_before = before[last_newline + 1 :]

        shlex_iterator = ShlexTokenIterator(line_before)
        return shlex_iterator.is_at_command_position()

    def _is_function_definition(
        self, match: "Match[str]", content: "str", offset: "int"
    ) -> bool:
        """Check if the match is part of a function definition."""
        before = content[: offset + match.start()]
        if ShlexTokenIterator.is_preceded_by_function_keyword(before):
            return True

        after_content = content[offset + match.end() :]
        shlex_iterator = ShlexTokenIterator(after_content)
        return shlex_iterator.is_function_definition()

    def _get_call_name(self, match: "Match[str]") -> "str":
        call = str(match.group(1))
        if call.endswith("."):
            return call[:-1]
        return call

    def _get_line_number(self, content: "str", offset: "int") -> "int":
        return content.count("\n", 0, offset) + 1

    def _get_column_number(self, content: "str", offset: "int") -> "int":
        last_newline = content.rfind("\n", 0, offset)
        return offset - last_newline if last_newline != -1 else offset + 1
