"""CLI command to rebuild the local metadata cache."""

from cache import save_cache
from exceptions.empty_cache import EmptyCacheError
from stdlib_html.fetcher import HTMLFetcher
from .base import Command


class RebuildCacheCommand(Command):
    COMMAND_NAME = "cache"

    def execute(self, args):
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch()
        if metadata:
            save_cache(metadata)
        else:
            raise EmptyCacheError()
