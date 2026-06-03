"""Linter issue STD002: Invalid function name within a valid namespace."""

from typing import Optional

from .base import LinterIssue


class STD002(LinterIssue):
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
        msg = f"Invalid function '{self.match}' in valid namespace '{self.namespace}'."
        if self.suggestion:
            msg += f" Did you mean '{self.suggestion}'?"
        return msg
