"""Severity enumeration for linter issues."""

from enum import Enum


class Severity(Enum):
    """Severity levels for linter errors and warnings."""

    ERROR = ("error", 1)
    WARNING = ("warning", 2)

    def __init__(self, level: str, vscode_severity: int) -> None:
        self.level = level
        self.vscode_severity = vscode_severity
