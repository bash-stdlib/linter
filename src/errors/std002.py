"""Linter error STD002: Invalid function name within a valid namespace."""

from typing import Optional

from .base import LinterError


class STD002(LinterError):
    CODE = "STD002"
    TITLE = "invalid function"
    DESCRIPTION = "The function name is incorrect, but the namespace is valid."

    def __init__(
        self,
        file: str,
        line: int,
        column: int,
        match: str,
        namespace: str,
        suggestion: Optional[str] = None,
    ) -> None:
        self.namespace = namespace
        self.suggestion = suggestion
        super().__init__(file, line, column, match)

    def format_message(self) -> str:
        msg = "Invalid function '{}' in valid namespace '{}'.".format(
            self.match, self.namespace
        )
        if self.suggestion:
            msg += " Did you mean '{}'?".format(self.suggestion)
        return msg
