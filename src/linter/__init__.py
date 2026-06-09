"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional, Set

from constants import MOCK_LIFETIME_FUNCTIONS
from errors import STD000, STD006, STD008
from functions.scope import FunctionScope as FunctionScope
from linter.state import LinterState
from parsers import BashArgumentsParser
from parsers.comment_ignores import CommentIgnores
from parsers.token_iterators import ShlexTokenIterator
from parsers.token_iterators.discovery import DiscoveryTokenIterator
from parsers.token_iterators.discovery_events.base import DiscoveryEvent
from parsers.transformers import LineContinuationTransformer
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    IsMockCallValidator,
    IsTestingFunctionCallValidator,
    NotNamespaceCallValidator,
)

if TYPE_CHECKING:
    from typing import Match, Pattern

    from errors.base import LinterErrorBase
    from validators.base import ValidatorBase


class Linter:
    def __init__(
        self,
        metadata: "Any",
        ignored_codes: "Optional[List[str]]" = None,
        appendum: "Optional[List[str]]" = None,
    ) -> "None":
        self.state = LinterState(metadata)

        self.ignored_codes: "Set[str]" = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.appendum: "Set[str]" = set(appendum) if appendum else set()
        self.stdlib_call_pattern: "Pattern[str]" = self._build_call_pattern("dummy.sh")
        self.argument_parser = BashArgumentsParser()
        self.line_continuation_transformer = LineContinuationTransformer()
        self.validators: "List[ValidatorBase]" = [
            IsMockCallValidator(self.state),
            NotNamespaceCallValidator(self.state),
            IsFunctionCallValidator(self.state),
            ArgumentCountValidator(self.state),
            IsTestingFunctionCallValidator(self.state),
        ]

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        errors: "List[LinterErrorBase]" = []
        filepath = os.path.abspath(filepath)

        try:
            with open(filepath, "r") as f:
                raw_content = f.read()
                file_content = self.line_continuation_transformer.transform(
                    raw_content, preserve_lines=True
                )
        except Exception as e:
            if not self._is_ignored("STD000", 1, None):
                errors.append(STD000(filepath, str(e)))
            return errors

        self.state.clear()

        # Pass 1: Discovery
        discovery = DiscoveryTokenIterator(file_content, posix=True)
        for item in discovery:
            if isinstance(item, DiscoveryEvent):
                self.state.event_log.append(item)
                item.handle_pre_scan(self.state.mock_manager)

        all_possible_mock_names = self.state.mock_manager.get_all_possible_mock_names()
        self.stdlib_call_pattern = self._build_call_pattern(
            filepath, all_possible_mock_names
        )

        comment_ignores = CommentIgnores()
        lines = file_content.splitlines(True)

        # Process comments first to support # stdlib: disable
        for i, line in enumerate(lines):
            comment_ignores.process_line(line, i + 1)

        # Pass 2: Validation (Global regex search)
        self.state.mock_manager.clear_instances()
        last_event_idx = 0

        for match in self.stdlib_call_pattern.finditer(file_content):
            absolute_match_start = match.start()

            # Replay events up to this offset
            while last_event_idx < len(self.state.event_log):
                event = self.state.event_log[last_event_idx]
                if event.offset <= absolute_match_start:
                    event.handle(self)
                    last_event_idx += 1
                else:
                    break

            line_num = self._get_line_number(file_content, absolute_match_start)
            self.state.current_absolute_offset = absolute_match_start

            # Sync active mocks for this match
            self._sync_active_mocks(absolute_match_start)

            error = self._process_match(
                match,
                file_content,
                filepath,
                comment_ignores,
                line_num,
                0,
            )
            if error:
                errors.append(error)

        for code, line_num_unused in comment_ignores.get_unused_ignores():
            errors.append(STD008(filepath, line_num_unused, 1, code))

        return errors

    def _build_call_pattern(
        self, filepath: str, all_possible_mock_names: Optional[Set[str]] = None
    ) -> "Pattern[str]":
        dot_roots = set()
        underscore_roots = set()

        all_names = (
            self.state.base_functions | self.state.base_namespaces | self.appendum
        )

        if all_possible_mock_names:
            all_names |= all_possible_mock_names
            for mock_name in all_possible_mock_names:
                for template_name in self.state.mock_manager.mock_templates.keys():
                    all_names.add(template_name.replace("object", mock_name))

        # Only include _mock.* calls in pattern if it's a test file
        if "test" in os.path.basename(filepath).lower():
            all_names |= MOCK_LIFETIME_FUNCTIONS

        for name in all_names:
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

        # Always include mock templates so they are matched even if not created
        # (allowing us to report STD002 for out-of-scope mock methods)
        for template_name in self.state.mock_manager.mock_templates.keys():
            # Add to dot_roots if it contains a dot, or just add directly
            parts = template_name.split(".")
            for i in range(1, len(parts) + 1):
                dot_roots.add(".".join(parts[:i]))

        sorted_dot_roots = sorted(list(dot_roots), key=len, reverse=True)
        sorted_underscore_roots = sorted(list(underscore_roots), key=len, reverse=True)

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

        pattern = r"(?<!\w)({}|{}|[a-z0-9._]+\.mock\.[a-z0-9._]+)(?![a-z0-9._])".format(
            dot_pattern, underscore_pattern
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

    def _is_appendum(self, call_name: str) -> bool:
        """Check if the call name or any of its parent namespaces are in appendum."""
        if call_name in self.appendum:
            return True

        parts = call_name.split(".")
        for i in range(1, len(parts)):
            prefix = ".".join(parts[:i])
            if prefix in self.appendum:
                return True
        return False

    def _process_match(
        self,
        match: "Match[str]",
        content: "str",
        filepath: "str",
        comment_ignores: CommentIgnores,
        line_num: int,
        offset: int = 0,
    ) -> "Optional[LinterErrorBase]":
        if self._is_function_definition(match, content, offset):
            return None

        if not self._is_at_command_position(match, content, offset):
            return None

        call_name = self._get_call_name(match)

        # Column within the line
        column = self._get_column_number(content, offset + match.start())

        if self._is_appendum(call_name):
            return None

        absolute_end = offset + match.end()

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

    def _sync_active_mocks(self, offset: int) -> None:
        active_names = self.state.mock_manager.get_active_mock_names(offset)

        self.state.reset()

        for name in active_names:
            mock_meta = self.state.mock_manager.get_mock_function_metadata(name)
            self.state.functions.add(name)
            self.state.functions.update(mock_meta.keys())
            self.state.metadata.update(mock_meta)
            # Update namespaces
            for mock_func in mock_meta.keys():
                parts = mock_func.split(".")
                for i in range(1, len(parts)):
                    self.state.namespaces.add(".".join(parts[:i]))
