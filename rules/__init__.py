"""Export all rules for the linter."""

from rules.namespace_call import NamespaceCallRule
from rules.valid_function import ValidFunctionRule

__all__ = ["NamespaceCallRule", "ValidFunctionRule"]
