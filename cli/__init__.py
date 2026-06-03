"""CLI package for the bash-stdlib linter."""

import argparse
import sys
from errors import BaseLinterError, EmptyCacheError
from .commands.rebuild import RebuildCacheCommand
from .commands.lint import LintCommand
from .commands.list_codes import ListErrorCodesCommand

def run_cli():
    parser = argparse.ArgumentParser(description="BASH stdlib linter")
    parser.add_argument("-r", "--rebuild", action="store_true", help="Rebuild the cache from documentation")
    parser.add_argument("--check", nargs="+", help="Check the specified shell script files")
    parser.add_argument("--list-codes", action="store_true", help="List all linter error codes and explanations")

    args = parser.parse_args()

    try:
        if args.rebuild:
            RebuildCacheCommand().execute(args)
        elif args.check:
            LintCommand().execute(args)
        elif args.list_codes:
            ListErrorCodesCommand().execute(args)
        else:
            parser.print_help()
    except (BaseLinterError, EmptyCacheError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)
