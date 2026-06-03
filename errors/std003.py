"""Linter issue STD003: Namespace called as a function."""

from .base import LinterIssue


class STD003(LinterIssue):
    CODE = "STD003"
    TITLE = "namespace called as function"
    DESCRIPTION = "A namespace was called directly instead of a specific function."

    def format_message(self):
        return f"'{self.match}' is a namespace, not a function."
