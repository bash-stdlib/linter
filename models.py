"""Data structures used for reporting and internal metadata representation."""

from enum import Enum
from typing import NamedTuple

class ErrorCode(Enum):
    """Enumeration of linter error codes."""
    STD000 = ("system error", "An error occurred while accessing the filesystem or network.")
    STD001 = ("invalid namespace", "The specified namespace does not exist in the BASH standard library.")
    STD002 = ("invalid function", "The function name is incorrect, but the namespace is valid.")
    STD003 = ("namespace called as function", "A namespace was called directly instead of a specific function.")
    STD004 = ("unknown namespace or function", "The call does not match any known stdlib pattern.")

    def __init__(self, title, description):
        self.title = title
        self.description = description

class LinterError(NamedTuple):
    """Represents a single linting error."""
    code: str
    file: str
    line: int
    column: int
    message: str
    match: str

    def to_dict(self):
        """Converts the error to a dictionary for JSON serialization."""
        return self._asdict()
