"""CLI command to rebuild the local metadata cache."""

from __future__ import annotations

from typing import TYPE_CHECKING

from cache import save_cache
from exceptions.empty_cache import EmptyCacheError
from stdlib_html.fetcher import HTMLFetcher
from .base import Command

if TYPE_CHECKING:
    import argparse


class RebuildCacheCommand(Command):
    COMMAND_NAME = "cache"

    def execute(self, args: argparse.Namespace) -> None:
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch()
        if metadata:
            save_cache(metadata)
        else:
            raise EmptyCacheError()
