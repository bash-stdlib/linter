"""Exports all linter rules for easy access."""

from .invalid_function import InvalidFunctionRule
from .invalid_namespace import InvalidNamespaceRule
from .namespace_as_function import NamespaceAsFunctionRule
from .unknown_call import UnknownCallRule

__all__ = [
    "InvalidFunctionRule",
    "InvalidNamespaceRule",
    "NamespaceAsFunctionRule",
    "UnknownCallRule",
]
