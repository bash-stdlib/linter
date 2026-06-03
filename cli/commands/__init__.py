"""Subpackage for linter CLI command implementations."""

from __future__ import annotations

from .base import Command
from .cache import RebuildCacheCommand
from .check import LintCommand
from .list import ListErrorCodesCommand


def get_command_map() -> dict[str, type[Command]]:
    """Retrieve a mapping of command names to their respective classes."""
    return {
        str(cmd.COMMAND_NAME): cmd
        for cmd in Command.__subclasses__()
        if cmd.COMMAND_NAME is not None
    }


__all__ = [
    "Command",
    "RebuildCacheCommand",
    "LintCommand",
    "ListErrorCodesCommand",
    "get_command_map",
]
