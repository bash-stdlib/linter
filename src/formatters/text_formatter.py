"""FormatterBase for human-readable text output."""

from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterIssueBase


class TextFormatterBase(FormatterBase):
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        if not issues:
            return "No issues found."

        lines = []
        for issue in issues:
            lines.append(
                "{}:{}:{} - [{}] {}".format(
                    issue.file, issue.line, issue.column, issue.CODE, issue.message
                )
            )
        return "\n".join(lines)
