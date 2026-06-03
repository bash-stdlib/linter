"""Data structures used for internal metadata representation."""

from enum import Enum


class ErrorCode(Enum):
    """Enumeration of linter error codes."""

    STD000 = (
        "system error",
        "An error occurred while accessing the filesystem or network.",
    )
    STD001 = (
        "invalid namespace",
        "The specified namespace does not exist in the BASH standard library.",
    )
    STD002 = (
        "invalid function",
        "The function name is incorrect, but the namespace is valid.",
    )
    STD003 = (
        "namespace called as function",
        "A namespace was called directly instead of a specific function.",
    )
    STD004 = (
        "unknown namespace or function",
        "The call does not match any known stdlib pattern.",
    )

    def __init__(self, title: str, description: str):
        self.title = title
        self.description = description
