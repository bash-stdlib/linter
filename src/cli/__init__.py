"""CLI package for the bash-stdlib linter."""

import argparse
import sys
from typing import TYPE_CHECKING

from exceptions.base import BaseLinterException
from exceptions.empty_cache import EmptyCacheError
from .commands import get_command_map

if TYPE_CHECKING:
    from .commands import CommandBase as CommandBase


def get_parser() -> argparse.ArgumentParser:
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
    check_parser = subparsers.add_parser("check", help="Lint specified shell scripts")
    check_parser.add_argument("files", nargs="+", help="Shell script files to check")
    check_parser.add_argument(
        "--format",
        "-f",
        choices=["json", "text", "vscode"],
        default="json",
        help="Output format (default: json)",
    )
    check_parser.add_argument(
        "--ignore",
        "-i",
        action="append",
        default=[],
        help="Error codes to ignore",
    )
    check_parser.add_argument(
        "--extra-namespace",
        "-ns",
        action="append",
        default=[],
        help="Additional namespaces to ignore (wildcard match)",
    )
    check_parser.add_argument(
        "--extra-function",
        "-fn",
        action="append",
        default=[],
        help="Additional functions to ignore (exact match)",
    )

    # List command
    subparsers.add_parser("list", help="List all linter error codes and explanations")

    return parser


def run_cli() -> None:
    parser = get_parser()
    args = parser.parse_args()
    command_map = get_command_map()

    try:
        command_class = command_map.get(str(args.command))
        if command_class:
            command_class().execute(args)
        else:
            parser.print_help()
    except (BaseLinterException, EmptyCacheError) as e:
        print("Error: {}".format(e), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print("An unexpected error occurred: {}".format(e), file=sys.stderr)
        sys.exit(1)
