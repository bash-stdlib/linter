"""FormatterBase for human-readable text output."""

from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class TextFormatterBase(FormatterBase):
    def format(self, errors: "List[LinterErrorBase]") -> "str":
        if not errors:
            return "No errors found."

        lines = []
        for error in errors:
            lines.append(
                "{}:{}:{} - [{}:{}] {}".format(
                    error.file,
                    error.line,
                    error.column,
                    error.SEVERITY.value,
                    error.CODE,
                    error.message,
                )
            )
        return "\n".join(lines)
