"""Core linter logic for validating bash-stdlib function calls."""

import re
import shlex
from typing import TYPE_CHECKING, Any, Optional

from constants import STDLIB_PATTERN
from errors import STD000
from validators import (
    ArgumentCountValidator,
    IsFunctionCallValidator,
    NotNamespaceCallValidator,
)

if TYPE_CHECKING:
    from typing import List, Set

    from errors.base import LinterErrorBase
    from validators.base import ValidatorBase


class Linter:
    def __init__(self, metadata: "Any") -> "None":
        self.functions: "Set[str]" = set(metadata["functions"].keys())
        self.namespaces: "Set[str]" = set(metadata["namespaces"])
        self.metadata = metadata["functions"]
        self.stdlib_call_pattern: "re.Pattern[str]" = re.compile(STDLIB_PATTERN)
        self.validators: "List[ValidatorBase]" = [
            NotNamespaceCallValidator(self.functions, self.namespaces),
            IsFunctionCallValidator(self.functions, self.namespaces),
            ArgumentCountValidator(self.functions, self.namespaces, self.metadata),
        ]

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        errors: "List[LinterErrorBase]" = []
        file_content = self._read_file(filepath, errors)
        if file_content is None:
            return errors

        for match in self.stdlib_call_pattern.finditer(file_content):
            error = self._process_match(match, file_content, filepath)
            if error:
                errors.append(error)

        return errors

    def _read_file(
        self,
        filepath: "str",
        errors: "List[LinterErrorBase]",
    ) -> "Optional[str]":
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception as e:
            errors.append(STD000(filepath, str(e)))
            return None

    def _process_match(
        self, match: "re.Match[str]", content: "str", filepath: "str"
    ) -> "Optional[LinterErrorBase]":
        call_name = self._get_call_name(match)
        line = self._get_line_number(content, match.start())
        column = self._get_column_number(content, match.start())

        # Extract arguments following the function call
        args = self._extract_arguments(content, match.end())

        for validator in self.validators:
            error = validator.check(call_name, filepath, line, column, args)
            if error:
                return error

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

    def _extract_arguments(self, content: "str", start_offset: "int") -> "List[str]":
        """Extract arguments following a function call using shlex."""
        remaining_content = content[start_offset:]

        # Handle backslash-newline continuation by removing it.
        # This simplifies lexing without significantly affecting argument count logic.
        remaining_content = remaining_content.replace("\\\n", "")

        try:
            # We use shlex.split to accurately group tokens into words/arguments,
            # respecting quotes and escape characters.
            all_tokens = shlex.split(remaining_content, posix=True)

            args = []
            skip_next = False
            for token in all_tokens:
                if skip_next:
                    skip_next = False
                    continue

                # Stop at command separators
                if token in [";", "|", "&", "&&", "||"]:
                    break

                # Handle redirections
                # Basic redirects: '>', '>>', '<', '>&', '<&'
                if token in [">", ">>", "<", ">&", "<&"]:
                    skip_next = True
                    continue

                # File descriptor redirects: '2>', '2>>', '2>&1', etc.
                if re.match(r"^\d+>>?$", token) or re.match(r"^\d+>&?$", token):
                    # If it's something like '2>', we skip the next token (the target)
                    # If it's something like '2>&1', it's self-contained and we just skip it
                    if not re.search(r"&\d+$", token) and not re.search(
                        r"[^>]\d+$", token
                    ):
                        skip_next = True
                    continue

                # Self-contained redirects like '2>&1' or '1>/dev/null' (if shlex kept them together)
                if re.match(r"^\d+>&?\d+$", token) or re.match(
                    r"^\d+>/\S+$", token
                ):
                    continue

                args.append(token)

            return args
        except Exception:
            # If shlex fails (e.g., unbalanced quotes), we return an empty list.
            # This avoids crashing the linter on malformed scripts.
            return []
