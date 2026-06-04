"""CLI command to list all available error codes and their descriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from errors import get_all_errors
from .base import Command

if TYPE_CHECKING:
    import argparse


class ListErrorCodesCommand(Command):
    COMMAND_NAME = "list"

    def execute(self, args: argparse.Namespace) -> None:
        print("BASH STDLIB Linter - Error Codes:")
        print("-" * 40)
        for error_class in get_all_errors():
            print(f"{error_class.CODE}: {error_class.TITLE}")
            print(f"      {error_class.DESCRIPTION}")
            print()
