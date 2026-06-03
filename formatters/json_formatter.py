"""Formatter for standard JSON output."""

import json

from .base import Formatter


class JSONFormatter(Formatter):
    def format(self, issues):
        return json.dumps([issue.to_dict() for issue in issues], indent=4)
