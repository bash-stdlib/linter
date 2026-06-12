"""Linter issues package."""

from typing import List, Type

from .base import LinterIssueBase
from .errors.base import LinterErrorBase
from .warnings.base import LinterWarningBase
from .errors import (
    STD000,
    STD001,
    STD002,
    STD003,
    STD004,
    STD005,
    STD006,
    STD007,
    STD009,
)
from .warnings import (
    STD008,
)

__all__ = [
    "LinterIssueBase",
    "LinterErrorBase",
    "LinterWarningBase",
    "STD000",
    "STD001",
    "STD002",
    "STD003",
    "STD004",
    "STD005",
    "STD006",
    "STD007",
    "STD008",
    "STD009",
    "get_all_issues",
]


def get_all_issues() -> List[Type[LinterIssueBase]]:
    """Retrieve all defined LinterIssueBase subclasses."""
    issues: List[Type[LinterIssueBase]] = []

    # Get all subclasses of LinterErrorBase
    issues.extend(LinterErrorBase.__subclasses__())

    # Get all subclasses of LinterWarningBase
    issues.extend(LinterWarningBase.__subclasses__())

    return issues
