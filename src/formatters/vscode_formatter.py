"""FormatterBase for VS Code diagnostic data."""

import json
from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterIssueBase


class VSCodeFormatterBase(FormatterBase):
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        diagnostics = []
        for issue in issues:
            # VS Code positions are 0-indexed
            # We also provide a range covering the match
            start_line = max(0, issue.line - 1)
            start_char = max(0, issue.column - 1)
            end_char = start_char + len(issue.match)

            diagnostics.append(
                {
                    "range": {
                        "start": {"line": start_line, "character": start_char},
                        "end": {"line": start_line, "character": end_char},
                    },
                    "severity": issue.SEVERITY.vscode_severity,
                    "code": issue.CODE,
                    "source": "bash-stdlib-lint",
                    "message": issue.message,
                    "file": issue.file,
                }
            )
        return json.dumps(diagnostics, indent=4)
