"""Base class for linter CLI commands."""

import argparse
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    import argparse


class CommandBase:
    COMMAND_NAME: "Optional[str]" = None

    def execute(self, args: "argparse.Namespace") -> "None":
        raise NotImplementedError
