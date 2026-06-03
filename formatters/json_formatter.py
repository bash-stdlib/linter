"""Formatter for standard JSON output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .base import Formatter

if TYPE_CHECKING:
    from errors.base import LinterIssue


class JSONFormatter(Formatter):
    def format(self, issues: list[LinterIssue]) -> str:
        return json.dumps([issue.to_dict() for issue in issues], indent=4)
