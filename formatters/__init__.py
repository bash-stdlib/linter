"""Output formatters for linter issues."""

from .json_formatter import JSONFormatter
from .text_formatter import TextFormatter
from .vscode_formatter import VSCodeFormatter

FORMATTERS = {"json": JSONFormatter, "text": TextFormatter, "vscode": VSCodeFormatter}


def get_formatter(format_name):
    """Retrieve a formatter class by its name."""
    return FORMATTERS.get(format_name, JSONFormatter)()
