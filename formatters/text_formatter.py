"""Formatter for human-readable text output."""

from .base import Formatter


class TextFormatter(Formatter):
    def format(self, issues):
        if not issues:
            return "No issues found."

        lines = []
        for issue in issues:
            lines.append(
                f"{issue.file}:{issue.line}:{issue.column} - "
                f"[{issue.CODE}] {issue.message}"
            )
        return "\n".join(lines)
