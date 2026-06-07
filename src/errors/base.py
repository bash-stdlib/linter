"""Base classes for linter exceptions and reported errors."""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Optional


class Severity(Enum):
    """Severity levels for linter errors and warnings."""

    ERROR = "error"
    WARNING = "warning"


class BaseLinterException(Exception):
    """Base class for all internal linter exceptions."""

    pass


class LinterErrorBase(ABC):
    """Base class for all specific linting errors and warnings."""

    CODE: str = ""
    TITLE: str = ""
    DESCRIPTION: str = ""
    SEVERITY: Optional[Severity] = None

    def __init__(
        self,
        file: str,
        line: int,
        column: int,
        match: str,
    ) -> None:
        self.validate_metadata()
        self.file = file
        self.line = line
        self.column = column
        self.match = match
        self.message = self.format_message()

    def validate_metadata(self) -> None:
        """Ensure subclasses define required metadata."""
        if not all([self.CODE, self.TITLE, self.DESCRIPTION, self.SEVERITY]):
            error_msg = "Subclass {} must define metadata.".format(
                self.__class__.__name__
            )
            raise NotImplementedError(error_msg)

    @abstractmethod
    def format_message(self) -> "str":
        """Format the specific error message for this error."""
        pass

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the error to a dictionary for JSON output."""
        return {
            "code": self.CODE,
            "title": self.TITLE,
            "severity": self.SEVERITY.value if self.SEVERITY else None,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "match": self.match,
        }


class LinterError(LinterErrorBase):
    """Base class for actual linting errors."""

    SEVERITY = Severity.ERROR


class LinterWarning(LinterErrorBase):
    """Base class for linting warnings."""

    SEVERITY = Severity.WARNING
