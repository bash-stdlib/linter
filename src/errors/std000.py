"""Linter error STD000: Failed to read file."""

from .base import LinterError


class STD000(LinterError):
    CODE = "STD000"
    TITLE = "system error"
    DESCRIPTION = "An error occurred while accessing the filesystem or network."

    def __init__(self, file: str, exception_msg: str) -> None:
        self.exception_msg = exception_msg
        super().__init__(file, 0, 0, "")

    def format_message(self) -> str:
        return "Failed to read file: {}".format(self.exception_msg)
