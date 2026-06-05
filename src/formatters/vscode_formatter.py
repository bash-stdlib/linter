"""FormatterBase for VS Code diagnostic data."""

from .json_formatter import JSONFormatterBase


class VSCodeFormatterBase(JSONFormatterBase):
    """VS Code diagnostic formatter, currently identical to JSON formatter."""
    pass
