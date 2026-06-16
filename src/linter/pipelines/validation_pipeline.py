"""Main validation pipeline for the linter."""

import re
from typing import TYPE_CHECKING, List, Optional

from issues import STD006, STD008, STD009
from linter.line_iterators import CommentIgnores, LineIteratorBase
from linter.pipelines.base import BasePipeline
from linter.token_iterators import ShlexTokenIterator
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    IsMockCallValidator,
    IsTestingFunctionCallValidator,
    NotNamespaceCallValidator,
)

if TYPE_CHECKING:
    from typing import Match, Pattern

    from issues.base import LinterIssueBase
    from linter.state.file_state import FileLinterState
    from linter.state.global_state import GlobalLinterState
    from validators.base import ValidatorBase

if TYPE_CHECKING:
    from linter.pipelines import ArgumentPipeline


class ValidationPipeline(BasePipeline):
    """Manages the validation pass of the linter."""

    MOCK_WILDCARD_PATTERN = re.compile(
        r"(?<!\w)([a-z0-9._]+(?:\.mock\.[a-z0-9._]+)?)(?![a-z0-9._])"
    )

    def __init__(
        self,
        global_state: "GlobalLinterState",
        file_state: "FileLinterState",
        stdlib_call_pattern: "Pattern[str]",
        argument_pipeline: "ArgumentPipeline",
    ) -> None:
        super().__init__(global_state, file_state)
        self.stdlib_call_pattern = stdlib_call_pattern
        self.argument_pipeline = argument_pipeline
        self.validators: List["ValidatorBase"] = [
            NotNamespaceCallValidator(global_state, file_state),
            IsMockCallValidator(global_state, file_state),
            IsFunctionCallValidator(global_state, file_state),
            ArgumentCountValidator(global_state, file_state),
            IsTestingFunctionCallValidator(global_state, file_state),
        ]
        self.line_iterators: List["LineIteratorBase"] = [
            CommentIgnores(global_state, file_state),
        ]

    def execute(self) -> None:
        """Execute the pipeline (abstract method from BasePipeline)."""
        pass

    def run(self, file_content: str, filepath: str) -> List["LinterIssueBase"]:
        """Run the validation pass."""
        issues: List["LinterIssueBase"] = []
        offset = 0
        for i, line_content in enumerate(file_content.splitlines(True)):
            line_num = i + 1
            for iterator in self.line_iterators:
                iterator.process_line(line_content, line_num, offset)

            matches = self._find_all_matches(line_content, offset)

            for match in matches:
                issue = self._process_match(
                    match, file_content, filepath, line_num, offset
                )
                if issue:
                    issues.append(issue)

            offset += len(line_content)

        self._check_unclosed_scopes(issues, filepath)
        self._check_unused_ignores(issues, filepath)

        return issues

    def _find_all_matches(
        self, line_content: str, line_offset: int
    ) -> List["Match[str]"]:
        """Find and deduplicate all stdlib and mock-related matches on a line."""
        stdlib_matches = list(self.stdlib_call_pattern.finditer(line_content))

        all_potential_matches = stdlib_matches
        stdlib_match_offsets = {m.start() for m in stdlib_matches}

        for match in self.MOCK_WILDCARD_PATTERN.finditer(line_content):
            if match.start() in stdlib_match_offsets:
                continue

            call_name = match.group(1)
            is_mock_related = ".mock." in call_name or self.file_state.is_mock_active(
                call_name, line_offset + match.start()
            )

            if is_mock_related:
                all_potential_matches.append(match)

        if not all_potential_matches:
            return []

        return self._deduplicate_overlapping_matches(all_potential_matches)

    def _deduplicate_overlapping_matches(
        self, matches: List["Match[str]"]
    ) -> List["Match[str]"]:
        """Filter matches so that only the longest, non-overlapping ones remain."""
        # Sort by start position (ascending), then by length (descending)
        matches.sort(key=lambda x: (x.start(), -len(x.group(0))))

        final_matches = []
        last_match_end_position = -1

        for match in matches:
            is_outside_previous_match = match.start() >= last_match_end_position
            if is_outside_previous_match:
                final_matches.append(match)
                last_match_end_position = match.end()

        return final_matches

    def _process_match(
        self,
        match: "Match[str]",
        content: "str",
        filepath: "str",
        line_num: int,
        offset: int = 0,
    ) -> Optional["LinterIssueBase"]:
        absolute_offset = offset + match.start()

        if self._is_function_definition(match, content, offset):
            return None

        matched_token = self._get_command_token(match, content, offset)
        if matched_token is None:
            return None

        call_name = self._get_call_name(match)

        if self._is_extra_ignore(call_name):
            return None

        # Use the end of the actual token (which might be quoted) as the start for args
        line_start = content.rfind("\n", 0, absolute_offset) + 1
        absolute_token_end = line_start + matched_token.end_offset
        column = match.start() + 1

        args = self.argument_pipeline.run(content[absolute_token_end:])
        if args is None:
            if not self._is_ignored(STD006.CODE, line_num):
                return STD006(filepath, line_num, column, call_name)
            return None

        for validator in self.validators:
            issue = validator.check(
                call_name, filepath, line_num, column, args, absolute_offset
            )
            if issue:
                if not self._is_ignored(issue.CODE, line_num):
                    return issue
        return None

    def _get_command_token(
        self, match: "Match[str]", content: "str", offset: "int"
    ) -> Optional["AdvancedToken"]:
        """Check if the match is at the start of a command and return its token."""
        from linter.enhanced_shlex import AdvancedToken

        absolute_start = offset + match.start()
        absolute_end = offset + match.end()

        # Find the boundaries of the line containing the match
        line_start = content.rfind("\n", 0, absolute_start) + 1
        line_end = content.find("\n", absolute_end)
        if line_end == -1:
            line_end = len(content)

        line_content = content[line_start:line_end]
        match_start_in_line = absolute_start - line_start
        match_end_in_line = absolute_end - line_start

        shlex_iterator = ShlexTokenIterator(line_content)

        # Basic command position check logic
        # at_start is True at the beginning of a line or after a command separator.
        at_start = True
        for token in shlex_iterator:
            # Check if this token matches our regex match
            # token.start_offset and token.end_offset are relative to line_content
            if (
                token.start_offset <= match_start_in_line
                and token.end_offset >= match_end_in_line
            ):
                # We found the token that contains our match.
                # It must be exactly the match (possibly quoted)
                # and it must be at a valid command position.

                is_exact_match = (
                    token.start_offset == match_start_in_line
                    and token.end_offset == match_end_in_line
                )
                is_exact_quoted_match = (
                    token.is_fully_quoted
                    and token.start_offset + 1 == match_start_in_line
                    and token.end_offset - 1 == match_end_in_line
                )

                if is_exact_match or is_exact_quoted_match:
                    if at_start and "=" not in token:
                        return token
                    return None

                # If we are here, the match is a substring of a larger token.
                return None

            # Update at_start for the next token
            if not token.is_fully_quoted and (
                token in {";", "|", "&", "&&", "||", "(", ")", "{", "}", "`", "!"}
                or token
                in {
                    "if",
                    "then",
                    "elif",
                    "else",
                    "while",
                    "until",
                    "do",
                    "for",
                    "in",
                }
            ):
                at_start = True
                continue

            if token == "$":
                # Likely part of an expansion, not a command position reset
                at_start = False
                continue

            if "=" in token and at_start:
                # Still at command position for the NEXT token if this was an assignment
                continue

            at_start = False

        return None

    def _is_function_definition(
        self, match: "Match[str]", content: "str", offset: "int"
    ) -> bool:
        """Check if the match is part of a function definition."""
        absolute_start = offset + match.start()
        before = content[:absolute_start]
        if ShlexTokenIterator.is_preceded_by_function_keyword(before):
            return True

        absolute_end = offset + match.end()
        after_content = content[absolute_end:]
        last_newline = after_content.find("\n")
        line_after = (
            after_content[:last_newline] if last_newline != -1 else after_content
        )
        shlex_iterator = ShlexTokenIterator(line_after)
        return shlex_iterator.is_function_definition()

    def _get_call_name(self, match: "Match[str]") -> "str":
        """Get the call name from the match."""
        call = str(match.group(1))
        if call.endswith("."):
            return call[:-1]
        return call

    def _is_extra_ignore(self, call_name: str) -> bool:
        """Check if the call name is in the extra namespaces or functions list."""
        if call_name in self.global_state.extra_functions:
            return True

        if call_name in self.global_state.extra_namespaces:
            return True

        parts = call_name.split(".")
        for i in range(1, len(parts)):
            prefix = ".".join(parts[:i])
            if prefix in self.global_state.extra_namespaces:
                return True
        return False

    def _is_ignored(self, code: str, line: int) -> bool:
        """Check if the issue code is ignored for the given line."""
        code = code.upper()
        if code in self.global_state.ignored_codes:
            return True
        return self.file_state.is_ignored(code, line)

    def _check_unclosed_scopes(
        self, issues: List["LinterIssueBase"], filepath: str
    ) -> None:
        """Check for unclosed function scopes and report them."""
        for scope in self.file_state.function_scopes:
            if scope.end_line == -1:
                if not self._is_ignored(STD009.CODE, scope.start_line):
                    issues.append(STD009(filepath, scope.start_line, 1, scope.name))

    def _check_unused_ignores(
        self, issues: List["LinterIssueBase"], filepath: str
    ) -> None:
        """Check for unused ignore directives and report them."""
        for code, line in self.file_state.get_unused_ignores():
            issues.append(STD008(filepath, line, 1, code))
