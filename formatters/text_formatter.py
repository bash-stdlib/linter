"""Formatter for human-readable text output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Formatter

if TYPE_CHECKING:
    from errors.base import LinterIssue


class TextFormatter(Formatter):
    def format(self, issues: list[LinterIssue]) -> str:
        if not issues:
            return "No issues found."

        lines = []
        for issue in issues:
            lines.append(
                f"{issue.file}:{issue.line}:{issue.column} - "
                f"[{issue.CODE}] {issue.message}"
            )
        return "\n".join(lines)
