"""Linter issue STD000: Failed to read file."""

from .base import LinterIssue


class STD000(LinterIssue):
    CODE = "STD000"
    TITLE = "system error"
    DESCRIPTION = "An error occurred while accessing the filesystem or network."

    def __init__(self, file: str, exception_msg: str) -> None:
        self.exception_msg = exception_msg
        super().__init__(file, 0, 0, "")

    def format_message(self) -> str:
        return f"Failed to read file: {self.exception_msg}"
