"""Entry point for the bash-stdlib linter application."""

import sys

from cli import run_cli


def main() -> None:
    run_cli()


if __name__ == "__main__":
    if sys.version_info < (3, 6):
        sys.stderr.write("Error: Python 3.6 or higher is required.\n")
        sys.exit(1)

    main()
