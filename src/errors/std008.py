"""Linter error STD008: Unused ignore."""

from .base import LinterWarning


class STD008(LinterWarning):
    CODE = "STD008"
    TITLE = "unused ignore"
    DESCRIPTION = (
        "A linter ignore directive was found but no matching error was suppressed."
    )

    def format_message(self) -> str:
        return "Unused ignore directive for '{}'.".format(self.match)
