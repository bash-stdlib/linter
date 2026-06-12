"""Base class for linter errors."""

from ..base import LinterIssueBase
from ..enum import Severity


class LinterErrorBase(LinterIssueBase):
    """Base class for all specific linting errors."""
    SEVERITY = Severity.ERROR
