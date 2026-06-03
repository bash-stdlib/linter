"""Linter error STD003: Namespace called as a function."""

from .base import LinterErrorBase


class STD003(LinterErrorBase):
    CODE = "STD003"
    TITLE = "namespace called as function"
    DESCRIPTION = "A namespace was called directly instead of a specific function."

    def format_message(self) -> str:
        return f"'{self.match}' is a namespace, not a function."
