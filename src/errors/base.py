"""Base classes for linter exceptions and reported issues."""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Dict

from .enum import Severity

if TYPE_CHECKING:
    pass


class BaseLinterException(Exception):
    """Base class for all internal linter exceptions."""

    pass


class LinterIssueBase(ABC):
    """Base class for all specific linting errors and warnings."""

    CODE: str = ""
    TITLE: str = ""
    DESCRIPTION: str = ""
    SEVERITY: "Severity"

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
        if not all([self.CODE, self.TITLE, self.DESCRIPTION]):
            error_msg = "Subclass {} must define metadata.".format(
                self.__class__.__name__
            )
            raise NotImplementedError(error_msg)

    @abstractmethod
    def format_message(self) -> "str":
        """Format the specific message for this issue."""
        pass

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the issue to a dictionary for JSON output."""
        return {
            "code": self.CODE,
            "title": self.TITLE,
            "severity": self.SEVERITY.level,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "match": self.match,
        }


class LinterErrorBase(LinterIssueBase):
    """Base class for all linting errors."""

    SEVERITY = Severity.ERROR


class LinterWarningBase(LinterIssueBase):
    """Base class for all linting warnings."""

    SEVERITY = Severity.WARNING
