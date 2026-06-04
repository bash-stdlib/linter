"""CLI command to rebuild the local metadata cache."""



from typing import TYPE_CHECKING
import argparse

from cache import save_cache
from exceptions.empty_cache import EmptyCacheError
from stdlib_html.fetcher import HTMLFetcher
from .base import CommandBase

if TYPE_CHECKING:
    import argparse


class RebuildCacheCommand(CommandBase):
    COMMAND_NAME = "cache"

    def execute(self, args: argparse.Namespace) -> None:
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch()
        if metadata:
            save_cache(metadata)
        else:
            raise EmptyCacheError()
