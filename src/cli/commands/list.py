"""CLI command to list all available issue codes and their descriptions."""

import argparse

from issues import get_all_issues
from .base import CommandBase


class ListErrorCodesCommand(CommandBase):
    COMMAND_NAME = "list"

    def execute(self, args: argparse.Namespace) -> None:
        print("BASH STDLIB Linter - Issue Codes:")
        print("-" * 40)
        for issue_class in get_all_issues():
            print(f"{issue_class.CODE}: {issue_class.TITLE}")
            print(f"  {issue_class.DESCRIPTION}")
            print()
