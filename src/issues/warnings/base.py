"""Base class for linter warnings."""

from ..base import LinterIssueBase
from ..enum import Severity


class LinterWarningBase(LinterIssueBase):
    """Base class for all specific linting warnings."""
    SEVERITY = Severity.WARNING
