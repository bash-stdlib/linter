"""Linter error STD007: Testing function used in production script."""

from .base import LinterError


class STD007(LinterError):
    CODE = "STD007"
    TITLE = "testing function in production script"
    DESCRIPTION = (
        "Testing functions should only be used in scripts with 'test' in their path."
    )

    def format_message(self) -> str:
        return (
            "The testing function '{}' is being used in a production script. "
            "Testing functions are only valid in test scripts or helpers "
            "(path containing 'test')."
        ).format(self.match)
