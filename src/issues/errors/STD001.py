"""Linter error STD001: Invalid namespace."""

from .base import LinterErrorBase


class STD001(LinterErrorBase):
    CODE = "STD001"
    TITLE = "invalid namespace"
    DESCRIPTION = "The specified namespace does not exist in the BASH standard library."

    def __init__(
        self, file: str, line: int, column: int, match: str, namespace: str
    ) -> None:
        self.namespace = namespace
        super().__init__(file, line, column, match)

    def format_message(self) -> str:
        return "Invalid namespace '{}'.".format(self.namespace)
