"""Core linter logic for validating bash-stdlib function calls."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any, Optional

from constants import STDLIB_PATTERN
from errors import STD000
from validators import IsFunctionCallValidator, NotNamespaceCallValidator

if TYPE_CHECKING:
    from errors.base import LinterError
    from validators.base import Validator


class Linter:
    def __init__(self, metadata: dict[str, Any]) -> None:
        self.functions = set(metadata["functions"])
        self.namespaces = set(metadata["namespaces"])
        self.stdlib_call_pattern = re.compile(STDLIB_PATTERN)
        self.validators: list[Validator] = [
            NotNamespaceCallValidator(self.functions, self.namespaces),
            IsFunctionCallValidator(self.functions, self.namespaces),
        ]

    def lint(self, filepath: str) -> list[LinterError]:
        errors: list[LinterError] = []
        file_content = self._read_file(filepath, errors)
        if file_content is None:
            return errors

        for match in self.stdlib_call_pattern.finditer(file_content):
            error = self._process_match(match, file_content, filepath)
            if error:
                errors.append(error)

        return errors

    def _read_file(self, filepath: str, errors: list[LinterError]) -> Optional[str]:
        try:
            with open(filepath, "r") as f:
                return f.read()
        except Exception as e:
            errors.append(STD000(filepath, str(e)))
            return None

    def _process_match(
        self, match: re.Match[str], content: str, filepath: str
    ) -> Optional[LinterError]:
        call_name = self._get_call_name(match)
        line = self._get_line_number(content, match.start())
        column = self._get_column_number(content, match.start())

        for validator in self.validators:
            error = validator.check(call_name, filepath, line, column)
            if error:
                return error

        return None

    def _get_call_name(self, match: re.Match[str]) -> str:
        call = str(match.group(1))
        if call.endswith("."):
            return call[:-1]
        return call

    def _get_line_number(self, content: str, offset: int) -> int:
        return content.count("\n", 0, offset) + 1

    def _get_column_number(self, content: str, offset: int) -> int:
        last_newline = content.rfind("\n", 0, offset)
        return offset - last_newline if last_newline != -1 else offset + 1
