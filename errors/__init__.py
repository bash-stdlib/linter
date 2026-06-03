"""Linter errors and issues package."""

from .base import LinterIssue
from .std000 import STD000
from .std001 import STD001
from .std002 import STD002
from .std003 import STD003
from .std004 import STD004


def get_all_issues():
    """Retrieve all defined LinterIssue subclasses."""
    return LinterIssue.__subclasses__()


__all__ = ["STD000", "STD001", "STD002", "STD003", "STD004", "get_all_issues"]
