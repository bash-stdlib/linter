"""Formatter for standard JSON output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .base import Formatter

if TYPE_CHECKING:
    from errors.base import LinterError


class JSONFormatter(Formatter):
    def format(self, errors: list[LinterError]) -> str:
        return json.dumps([error.to_dict() for error in errors], indent=4)
