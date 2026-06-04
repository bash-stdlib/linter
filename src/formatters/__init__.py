"""Output formatters for linter errors."""

from typing import TYPE_CHECKING, Any, Dict, Type, Union

from .json_formatter import JSONFormatterBase
from .text_formatter import TextFormatterBase
from .vscode_formatter import VSCodeFormatterBase

if TYPE_CHECKING:
    from .base import FormatterBase


def get_formatter(format_name: "str") -> "FormatterBase":
    """Retrieve a formatter class by its name."""
    mapping: "Dict[str, Type[Union[JSONFormatterBase, TextFormatterBase, VSCodeFormatterBase]]]" = {
        "json": JSONFormatterBase,
        "text": TextFormatterBase,
        "vscode": VSCodeFormatterBase,
    }
    formatter_class = mapping.get(format_name, JSONFormatterBase)
    return formatter_class()
