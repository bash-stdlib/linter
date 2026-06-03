"""Linter issue STD004: Unknown stdlib call."""

from .base import LinterIssue


class STD004(LinterIssue):
    CODE = "STD004"
    TITLE = "unknown namespace or function"
    DESCRIPTION = "The call does not match any known stdlib pattern."

    def format_message(self):
        return f"Invalid namespace or function '{self.match}'."
