"""Linter error STD004: Unknown stdlib call."""

from .base import LinterError


class STD004(LinterError):
    CODE = "STD004"
    TITLE = "unknown namespace or function"
    DESCRIPTION = "The call does not match any known stdlib pattern."

    def format_message(self) -> str:
        return f"Invalid namespace or function '{self.match}'."
