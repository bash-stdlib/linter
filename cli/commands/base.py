"""Base class for linter CLI commands."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import argparse


class Command:
    COMMAND_NAME: Optional[str] = None

    def execute(self, args: argparse.Namespace) -> None:
        raise NotImplementedError
