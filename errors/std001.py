"""Linter issue STD001: Invalid namespace."""

from .base import LinterIssue


class STD001(LinterIssue):
    CODE = "STD001"
    TITLE = "invalid namespace"
    DESCRIPTION = "The specified namespace does not exist in the BASH standard library."

    def __init__(
        self, file: str, line: int, column: int, match: str, namespace: str
    ) -> None:
        self.namespace = namespace
        super().__init__(file, line, column, match)

    def format_message(self) -> str:
        return f"Invalid namespace '{self.namespace}'."
