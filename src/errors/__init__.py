"""Linter errors package."""

from typing import List, Type

from .base import LinterError, LinterIssue, LinterWarning
from .std000 import STD000
from .std001 import STD001
from .std002 import STD002
from .std003 import STD003
from .std004 import STD004
from .std005 import STD005
from .std006 import STD006
from .std007 import STD007
from .std008 import STD008


def get_all_errors() -> "List[Type[LinterIssue]]":
    """Retrieve all defined LinterIssue leaf subclasses."""
    all_issues = []
    # We want leaf subclasses (the actual error/warning classes)
    # LinterIssue -> [LinterError, LinterWarning]
    # LinterError -> [STD000, STD001, ...]
    # LinterWarning -> [STD008]
    for base in [LinterError, LinterWarning]:
        all_issues.extend(base.__subclasses__())
    return all_issues


__all__ = [
    "STD000",
    "STD001",
    "STD002",
    "STD003",
    "STD004",
    "STD005",
    "STD006",
    "STD007",
    "STD008",
    "get_all_errors",
]
