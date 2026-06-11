"""CLI command to list all available error codes and their descriptions."""

import argparse

from issues import get_all_issues
from .base import CommandBase


class ListErrorCodesCommand(CommandBase):
    COMMAND_NAME = "list"

    def execute(self, args: argparse.Namespace) -> None:
        print("BASH STDLIB Linter - Error Codes:")
        print("-" * 40)
        for error_class in get_all_issues():
            print("{}: {}".format(error_class.CODE, error_class.TITLE))
            print("      {}".format(error_class.DESCRIPTION))
            print()
