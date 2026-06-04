"""Output formatters for linter errors."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .json_formatter import JSONFormatter
from .text_formatter import TextFormatter
from .vscode_formatter import VSCodeFormatter

if TYPE_CHECKING:
    from .base import Formatter


def get_formatter(format_name: str) -> Formatter:
    """Retrieve a formatter class by its name."""
    mapping: dict[str, type[JSONFormatter | TextFormatter | VSCodeFormatter]] = {
        "json": JSONFormatter,
        "text": TextFormatter,
        "vscode": VSCodeFormatter,
    }
    formatter_class = mapping.get(format_name, JSONFormatter)
    return formatter_class()
