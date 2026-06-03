"""CLI command to list all available error codes and their descriptions."""

from models import ErrorCode
from .base import Command

class ListErrorCodesCommand(Command):
    def execute(self, args):
        print("BASH STDLIB Linter - Error Codes:")
        print("-" * 40)
        for member in ErrorCode:
            print(f"{member.name}: {member.title}")
            print(f"      {member.description}")
            print()
