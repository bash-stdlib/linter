"""Formatter for human-readable text output."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Formatter

if TYPE_CHECKING:
    from errors.base import LinterError


class TextFormatter(Formatter):
    def format(self, errors: list[LinterError]) -> str:
        if not errors:
            return "No errors found."

        lines = []
        for error in errors:
            lines.append(
                f"{error.file}:{error.line}:{error.column} - "
                f"[{error.CODE}] {error.message}"
            )
        return "\n".join(lines)
