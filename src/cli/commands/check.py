"""CLI command to perform linting on shell scripts."""

import argparse
import sys
from typing import TYPE_CHECKING, List

from cache import load_cache, save_cache
from exceptions.empty_cache import EmptyCacheError
from formatters import get_formatter
from stdlib_html.fetcher import HTMLFetcher
from .base import CommandBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class LintCommand(CommandBase):
    COMMAND_NAME = "check"

    def execute(self, args: argparse.Namespace) -> None:
        from linter import Linter

        metadata = load_cache()
        if not metadata:
            fetcher = HTMLFetcher()
            metadata = fetcher.fetch()
            if metadata:
                save_cache(metadata)
            else:
                raise EmptyCacheError()

        linter = Linter(
            metadata, ignored_codes=args.ignore, appendum=args.appendum
        )
        all_errors: "List[LinterErrorBase]" = []
        for filepath in args.files:
            all_errors.extend(linter.lint(filepath))

        formatter = get_formatter(args.format)
        print(formatter.format(all_errors))

        if all_errors:
            sys.exit(1)
