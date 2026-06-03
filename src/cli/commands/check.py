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
    from issues.base import LinterIssueBase


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
            metadata,
            ignored_codes=args.ignore,
            extra_namespaces=args.extra_namespace,
            extra_functions=args.extra_function,
        )
        all_issues: "List[LinterIssueBase]" = []
        for filepath in args.files:
            all_issues.extend(linter.lint(filepath))

        formatter = get_formatter(args.format)
        print(formatter.format(all_issues))

        if all_issues:
            sys.exit(1)
