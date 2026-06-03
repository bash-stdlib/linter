"""CLI command to list all available error codes and their descriptions."""

from errors import ALL_ISSUES
from .base import Command


class ListErrorCodesCommand(Command):
    def execute(self, args):
        print("BASH STDLIB Linter - Error Codes:")
        print("-" * 40)
        for issue_class in ALL_ISSUES:
            print(f"{issue_class.CODE}: {issue_class.TITLE}")
            print(f"      {issue_class.DESCRIPTION}")
            print()
