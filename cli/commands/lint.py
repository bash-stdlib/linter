"""CLI command to perform linting on shell scripts."""

import json
import sys

from cache import load_cache, save_cache
from exceptions.empty_cache import EmptyCacheError
from stdlib_html.fetcher import HTMLFetcher
from .base import Command


class LintCommand(Command):
    def execute(self, args):
        from linter import Linter

        metadata = load_cache()
        if not metadata:
            fetcher = HTMLFetcher()
            metadata = fetcher.fetch()
            if metadata:
                save_cache(metadata)
            else:
                raise EmptyCacheError(
                    "Cache is empty and failed to fetch documentation."
                )

        linter = Linter(metadata)
        all_errors = []
        for filepath in args.files:
            all_errors.extend(linter.lint(filepath))

        print(json.dumps([e.to_dict() for e in all_errors], indent=2))
        if all_errors:
            sys.exit(1)
