"""FormatterBase for human-readable text output."""

from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class TextFormatterBase(FormatterBase):
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        if not issues:
            return "No issues found."

        lines = []
        for error in issues:
            lines.append(
                "{}:{}:{} - [{}] [{}] {}".format(
                    error.file,
                    error.line,
                    error.column,
                    error.SEVERITY.level.upper(),
                    error.CODE,
                    error.message,
                )
            )
        return "\n".join(lines)
