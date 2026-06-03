"""FormatterBase for VS Code diagnostic data."""

import json
from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class VSCodeFormatterBase(FormatterBase):

    def format(self, errors: "List[LinterErrorBase]") -> "str":
        diagnostics = []
        for error in errors:
            # VS Code positions are 0-indexed
            # We also provide a range covering the match
            start_line = max(0, error.line - 1)
            start_char = max(0, error.column - 1)
            end_char = start_char + len(error.match)

            diagnostics.append({
                "range": {
                    "start": {
                        "line": start_line,
                        "character": start_char
                    },
                    "end": {
                        "line": start_line,
                        "character": end_char
                    },
                },
                "severity": 1,  # Error
                "code": error.CODE,
                "source": "bash-stdlib-lint",
                "message": error.message,
            })
        return json.dumps(diagnostics, indent=4)
