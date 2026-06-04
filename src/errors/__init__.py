"""Linter errors package."""

from typing import List, Type

from .base import LinterErrorBase
from .std000 import STD000
from .std001 import STD001
from .std002 import STD002
from .std003 import STD003
from .std004 import STD004
from .std005 import STD005
from .std006 import STD006


def get_all_errors() -> "List[Type[LinterErrorBase]]":
    """Retrieve all defined LinterErrorBase subclasses."""
    return LinterErrorBase.__subclasses__()


__all__ = [
    "STD000",
    "STD001",
    "STD002",
    "STD003",
    "STD004",
    "STD005",
    "STD006",
    "get_all_errors",
]
