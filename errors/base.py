"""Base class for representing specific linting issues."""

from abc import ABC, abstractmethod


class LinterIssue(ABC):
    """Base class for all specific linting errors and warnings."""

    CODE = None
    TITLE = None
    DESCRIPTION = None

    def __init__(self, file, line, column, match):
        self.validate_metadata()
        self.file = file
        self.line = line
        self.column = column
        self.match = match
        self.message = self.format_message()

    def validate_metadata(self):
        """Ensure subclasses define required metadata."""
        if any(attr is None for attr in (self.CODE, self.TITLE, self.DESCRIPTION)):
            error_msg = f"Subclass {self.__class__.__name__} must define metadata."
            raise NotImplementedError(error_msg)

    @abstractmethod
    def format_message(self):
        """Format the specific error message for this issue."""
        pass

    def to_dict(self):
        """Convert the issue to a dictionary for JSON output."""
        return {
            "code": self.CODE,
            "title": self.TITLE,
            "file": self.file,
            "line": self.line,
            "column": self.column,
            "message": self.message,
            "match": self.match,
        }
