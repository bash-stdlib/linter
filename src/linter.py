"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional, Set

from errors import STD000, STD002, STD006, STD008
from linter_state import LinterState
from mock.manager import MockManager
from mock_scanner import MockScanner
from parsers import BashArgumentsParser
from parsers.comment_ignores import CommentIgnores
from parsers.token_iterators import ShlexTokenIterator
from parsers.transformers import LineContinuationTransformer
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
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
        self.mock_manager = MockManager(self.state.base_metadata)
        self.mock_scanner = MockScanner(self.mock_manager)
        self.stdlib_call_pattern: "Pattern[str]" = self._build_call_pattern()
        self.argument_parser = BashArgumentsParser()
        self.line_continuation_transformer = LineContinuationTransformer()
        self.validators: "List[ValidatorBase]" = [
            NotNamespaceCallValidator(self.state.functions, self.state.namespaces),
            IsFunctionCallValidator(self.state.functions, self.state.namespaces),
            ArgumentCountValidator(
                self.state.functions, self.state.namespaces, self.state.metadata
            ),
            IsTestingFunctionCallValidator(
                self.state.functions, self.state.namespaces, self.state.metadata
            ),
        ]

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        errors: "List[LinterErrorBase]" = []
        filepath = os.path.abspath(filepath)
        is_test_file = "test" in filepath

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

        comment_ignores = CommentIgnores()

        if is_test_file:
            # Pre-scan for mock creations
            scopes = self.mock_scanner.discover_scopes(file_content)
            self.mock_manager.set_function_scopes(scopes)
            self.mock_scanner.discover_mock_creations(file_content)
            # Rebuild pattern with all discovered mocks
            self.stdlib_call_pattern = self._build_call_pattern(
                self.mock_manager.get_all_possible_mock_names()
            )
        else:
            self.stdlib_call_pattern = self._build_call_pattern()

        offset = 0
        for i, line_content in enumerate(file_content.splitlines(True)):
            line_num = i + 1
            comment_ignores.process_line(line_content, line_num)

            if is_test_file:
                # Track deletions and resets sequentially
                self.mock_scanner.track_mock_lifetimes(line_content, offset)

            matches = sorted(
                list(self.stdlib_call_pattern.finditer(line_content)),
                key=lambda m: m.start(),
            )

            for match in matches:
                absolute_match_start = offset + match.start()
                if is_test_file:
                    self._sync_active_mocks(absolute_match_start)

                error = self._process_match(
                    match, file_content, filepath, comment_ignores, line_num, offset
                )
                if error:
                    errors.append(error)

            offset += len(line_content)

        for code, line in comment_ignores.get_unused_ignores():
            errors.append(STD008(filepath, line, 1, code))

        return errors

    def _build_call_pattern(
        self, extra_names: "Optional[Set[str]]" = None
    ) -> "Pattern[str]":
        dot_roots = set()
        underscore_roots = set()

        all_names = (
            self.state.base_functions | self.state.base_namespaces | self.appendum
        )
        if extra_names:
            all_names |= extra_names
            # Include all template methods for these mock names
            for mock_name in extra_names:
                for template_name in self.mock_manager.mock_templates.keys():
                    all_names.add(template_name.replace("object", mock_name))

        # Always include _mock.* calls in pattern
        all_names.add("_mock.create")
        all_names.add("_mock.delete")
        all_names.add("_mock.reset_all")

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
        # print("DEBUG: dot_pattern: {}".format(dot_pattern))
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

        # Ignore _mock calls from validation, they are handled by lifetime tracking
        if call_name in ["_mock.create", "_mock.delete", "_mock.reset_all"]:
            return None

        # Verify mock visibility if it's a mock method call
        error = self._check_mock_visibility(
            call_name, filepath, line_num, match.start() + 1, offset, comment_ignores
        )
        if error:
            return error

        if self._is_appendum(call_name):
            return None

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

    def _check_mock_visibility(
        self,
        call_name: str,
        filepath: str,
        line_num: int,
        column: int,
        offset: int,
        comment_ignores: CommentIgnores,
    ) -> "Optional[LinterErrorBase]":
        if self.mock_manager.is_mock_method_active(call_name, offset + column - 1):
            return None

        if any(
            call_name == t.replace("object", m)
            for m in self.mock_manager.get_all_possible_mock_names()
            for t in self.mock_manager.mock_templates.keys()
        ):
            # It matches a mock template but is NOT active
            if not self._is_ignored(STD002.CODE, line_num, comment_ignores):
                namespace = ".".join(call_name.split(".")[:-1])
                return STD002(filepath, line_num, column, call_name, namespace)
            return None
        return None

    def _sync_active_mocks(self, offset: int) -> None:
        active_names = self.mock_manager.get_active_mock_names(offset)

        self.state.reset()

        for name in active_names:
            mock_meta = self.mock_manager.get_mock_function_metadata(name)
            self.state.functions.add(name)
            self.state.functions.update(mock_meta.keys())
            self.state.metadata.update(mock_meta)
            # Update namespaces
            for mock_func in mock_meta.keys():
                parts = mock_func.split(".")
                for i in range(1, len(parts)):
                    self.state.namespaces.add(".".join(parts[:i]))

        # Update validators with current state
        for validator in self.validators:
            if hasattr(validator, "functions"):
                validator.functions = self.state.functions
            if hasattr(validator, "namespaces"):
                validator.namespaces = self.state.namespaces
            if hasattr(validator, "metadata"):
                validator.metadata = self.state.metadata
