"""Linter error STD010: Inactive or unknown mock object."""

from typing import Optional

from .base import LinterErrorBase


class STD010(LinterErrorBase):
    CODE = "STD010"
    TITLE = "inactive or unknown mock"
    DESCRIPTION = "The mock object is not active at this position or is unknown."

    def __init__(
        self,
        file: str,
        line: int,
        column: int,
        match: str,
        message: Optional[str] = None,
    ) -> None:
        self.message = message
        super().__init__(file, line, column, match)

    def format_message(self) -> str:
        if self.message:
            return "Mock error for '{}': {}".format(self.match, self.message)
        return "The mock object '{}' is not active or is unknown.".format(self.match)
