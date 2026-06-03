"""Output formatters for linter errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .json_formatter import JSONFormatterBase
from .text_formatter import TextFormatterBase
from .vscode_formatter import VSCodeFormatterBase

if TYPE_CHECKING:
    from .base import FormatterBase


def get_formatter(format_name: str) -> FormatterBase:
    """Retrieve a formatter class by its name."""
    mapping: dict[str, type[JSONFormatterBase | TextFormatterBase | VSCodeFormatterBase]] = {
        "json": JSONFormatterBase,
        "text": TextFormatterBase,
        "vscode": VSCodeFormatterBase,
    }
    formatter_class = mapping.get(format_name, JSONFormatterBase)
    return formatter_class()
