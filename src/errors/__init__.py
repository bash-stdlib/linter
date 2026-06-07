"""Linter errors package."""

from typing import List, Type

from .base import LinterError, LinterErrorBase, LinterWarning, Severity
from .std000 import STD000
from .std001 import STD001
from .std002 import STD002
from .std003 import STD003
from .std004 import STD004
from .std005 import STD005
from .std006 import STD006
from .std007 import STD007
from .std008 import STD008


def get_all_errors() -> "List[Type[LinterErrorBase]]":
    """Retrieve all defined LinterErrorBase leaf subclasses."""

    def _get_leaf_subclasses(cls: Type[LinterErrorBase]) -> List[Type[LinterErrorBase]]:
        leaves = []
        subclasses = cls.__subclasses__()
        if not subclasses:
            if cls.CODE:
                return [cls]
            return []
        for subclass in subclasses:
            leaves.extend(_get_leaf_subclasses(subclass))
        return leaves

    return _get_leaf_subclasses(LinterErrorBase)


__all__ = [
    "LinterError",
    "LinterWarning",
    "Severity",
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
