"""Formatter for VS Code diagnostic data."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .base import Formatter

if TYPE_CHECKING:
    from errors.base import LinterIssue


class VSCodeFormatter(Formatter):
    def format(self, issues: list[LinterIssue]) -> str:
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
                    "severity": 1,  # Error
                    "code": issue.CODE,
                    "source": "bash-stdlib-lint",
                    "message": issue.message,
                }
            )
        return json.dumps(diagnostics, indent=4)
