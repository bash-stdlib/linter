"""CLI command to rebuild the local metadata cache."""

from stdlib_html.fetcher import HTMLFetcher
from cache import save_cache
from errors import EmptyCacheError
from .base import Command

class RebuildCacheCommand(Command):
    def execute(self, args):
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch()
        if metadata:
            save_cache(metadata)
        else:
            raise EmptyCacheError("Failed to fetch documentation and build cache.")
