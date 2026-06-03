"""Subpackage for linter CLI command implementations."""

from .base import Command
from .cache import RebuildCacheCommand
from .check import LintCommand
from .list import ListErrorCodesCommand


def get_command_map():
    """Retrieve a mapping of command names to their respective classes."""
    return {
        cmd.COMMAND_NAME: cmd
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
