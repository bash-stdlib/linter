"""Linter error STD006: Failed to parse arguments."""

from .base import LinterError


class STD006(LinterError):
    CODE = "STD006"
    TITLE = "failed to parse arguments"
    DESCRIPTION = (
        "The function's arguments could not be parsed, possibly due to "
        "unbalanced quotes or syntax errors."
    )

    def format_message(self) -> str:
        return "Failed to parse arguments for '{}'.".format(self.match)
