"""CLI package for the bash-stdlib linter."""

import argparse
import sys

from exceptions.base import BaseLinterException
from .commands.lint import LintCommand
from .commands.list_codes import ListErrorCodesCommand
from .commands.rebuild import RebuildCacheCommand


def run_cli():
    parser = argparse.ArgumentParser(description="BASH stdlib linter")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Cache command
    cache_parser = subparsers.add_parser(
        "cache", help="Manage the local metadata cache"
    )
    cache_parser.add_argument(
        "--rebuild",
        "-r",
        action="store_true",
        help="Rebuild the cache from documentation",
    )

    # Check command
    check_parser = subparsers.add_parser(
        "check", help="Lint specified shell script files"
    )
    check_parser.add_argument("files", nargs="+", help="Shell script files to check")

    # List command
    subparsers.add_parser("list", help="List all linter error codes and explanations")

    args = parser.parse_args()

    try:
        if args.command == "cache":
            RebuildCacheCommand().execute(args)
        elif args.command == "check":
            LintCommand().execute(args)
        elif args.command == "list":
            ListErrorCodesCommand().execute(args)
        else:
            parser.print_help()
    except BaseLinterException as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
