"""CLI command to perform linting on shell scripts."""

import sys

from cache import load_cache, save_cache
from exceptions.empty_cache import EmptyCacheError
from formatters import get_formatter
from stdlib_html.fetcher import HTMLFetcher
from .base import Command


class LintCommand(Command):
    COMMAND_NAME = "check"

    def execute(self, args):
        from linter import Linter

        metadata = load_cache()
        if not metadata:
            fetcher = HTMLFetcher()
            metadata = fetcher.fetch()
            if metadata:
                save_cache(metadata)
            else:
                raise EmptyCacheError()

        linter = Linter(metadata)
        all_issues = []
        for filepath in args.files:
            all_issues.extend(linter.lint(filepath))

        formatter = get_formatter(args.format)
        print(formatter.format(all_issues))

        if all_issues:
            sys.exit(1)
