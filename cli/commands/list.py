"""CLI command to list all available error codes and their descriptions."""

from errors import get_all_issues
from .base import Command


class ListErrorCodesCommand(Command):
    COMMAND_NAME = "list"

    def execute(self, args):
        print("BASH STDLIB Linter - Error Codes:")
        print("-" * 40)
        for issue_class in get_all_issues():
            print(f"{issue_class.CODE}: {issue_class.TITLE}")
            print(f"      {issue_class.DESCRIPTION}")
            print()
