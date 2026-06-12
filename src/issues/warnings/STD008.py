"""Linter error STD008: Unused ignore."""

from .base import LinterWarningBase


class STD008(LinterWarningBase):
    CODE = "STD008"
    TITLE = "unused ignore"
    DESCRIPTION = (
        "A linter ignore directive was found but no matching error was suppressed."
    )

    def format_message(self) -> str:
        return "Unused ignore directive for '{}'.".format(self.match)
