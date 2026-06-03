"""Base classes for linter issues."""

from abc import ABC, abstractmethod
from typing import Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from .enum import Severity


class LinterIssueBase(ABC):
    """Base class for all specific linting issues (errors and warnings)."""

    CODE: str = ""
    SEVERITY: "Severity"
    TITLE: str = ""
    DESCRIPTION: str = ""

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
    def format_message(self) -> str:
        """Format the specific message for this issue."""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary for JSON output."""
        return {
            "code": self.CODE,
            "severity": self.SEVERITY.level,
            "title": self.TITLE,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "match": self.match,
        }
