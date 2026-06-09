"""Main validation pipeline for the linter."""

from typing import TYPE_CHECKING, List, Optional

from errors import STD006, STD008, STD009
from linter.line_iterators.comment_ignores import CommentIgnores
from parsers.token_iterators import ShlexTokenIterator
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    IsTestingFunctionCallValidator,
    NotNamespaceCallValidator,
)

if TYPE_CHECKING:
    from typing import Match, Pattern

    from errors.base import LinterErrorBase
    from linter.line_iterators.base import LineIteratorBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState
    from parsers import BashArgumentsParser
    from validators.base import ValidatorBase


class ValidationPipeline:
    """Manages the validation pass of the linter."""

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
        stdlib_call_pattern: "Pattern[str]",
        argument_parser: "BashArgumentsParser",
    ) -> None:
        self.global_state = global_state
        self.file_state = file_state
        self.stdlib_call_pattern = stdlib_call_pattern
        self.argument_parser = argument_parser
        self.validators: List["ValidatorBase"] = [
            NotNamespaceCallValidator(global_state, file_state),
            IsFunctionCallValidator(global_state, file_state),
            ArgumentCountValidator(global_state, file_state),
            IsTestingFunctionCallValidator(global_state, file_state),
        ]
        self.line_iterators: List["LineIteratorBase"] = [
            CommentIgnores(global_state, file_state),
        ]

    def run(self, file_content: str, filepath: str) -> List["LinterErrorBase"]:
        """Run the validation pass."""
        errors: List["LinterErrorBase"] = []
        offset = 0
        for i, line_content in enumerate(file_content.splitlines(True)):
            line_num = i + 1
            for iterator in self.line_iterators:
                iterator.process_line(line_content, line_num, offset)

            for match in self.stdlib_call_pattern.finditer(line_content):
                error = self._process_match(
                    match, file_content, filepath, line_num, offset
                )
                if error:
                    errors.append(error)

            offset += len(line_content)

        self._check_unclosed_scopes(errors, filepath)
        self._check_unused_ignores(errors, filepath)

        return errors

    def _process_match(
        self,
        match: "Match[str]",
        content: "str",
        filepath: "str",
        line_num: int,
        offset: int = 0,
    ) -> Optional["LinterErrorBase"]:
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

        for validator in self.validators:
            error = validator.check(call_name, filepath, line_num, column, args)
            if error:
                if not self._is_ignored(error.CODE, line_num):
                    return error
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
        """Get the call name from the match."""
        call = str(match.group(1))
        if call.endswith("."):
            return call[:-1]
        return call

    def _is_appendum(self, call_name: str) -> bool:
        """Check if the call name is in the appendum list."""
        if call_name in self.global_state.appendum:
            return True
        parts = call_name.split(".")
        for i in range(1, len(parts)):
            prefix = ".".join(parts[:i])
            if prefix in self.global_state.appendum:
                return True
        return False

    def _is_ignored(self, code: str, line: int) -> bool:
        """Check if the error code is ignored for the given line."""
        code = code.upper()
        if code in self.global_state.ignored_codes:
            return True
        return self.file_state.is_ignored(code, line)

    def _check_unclosed_scopes(
        self, errors: List["LinterErrorBase"], filepath: str
    ) -> None:
        """Check for unclosed function scopes and report them."""
        for scope in self.file_state.function_scopes:
            if scope.end_line == -1:
                if not self._is_ignored(STD009.CODE, scope.start_line):
                    errors.append(STD009(filepath, scope.start_line, 1, scope.name))

    def _check_unused_ignores(
        self, errors: List["LinterErrorBase"], filepath: str
    ) -> None:
        """Check for unused ignore directives and report them."""
        for code, line in self.file_state.get_unused_ignores():
            errors.append(STD008(filepath, line, 1, code))
