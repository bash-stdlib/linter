"""Subpackage for linter CLI command implementations."""

from typing import Dict, Type

from .base import CommandBase
from .cache import RebuildCacheCommand
from .check import LintCommand
from .list import ListErrorCodesCommand


def get_command_map() -> "Dict[str, Type[CommandBase]]":
    """Retrieve a mapping of command names to their respective classes."""
    return {
        str(cmd.COMMAND_NAME): cmd
        for cmd in CommandBase.__subclasses__() if cmd.COMMAND_NAME is not None
    }


__all__ = [
    "CommandBase",
    "RebuildCacheCommand",
    "LintCommand",
    "ListErrorCodesCommand",
    "get_command_map",
]
