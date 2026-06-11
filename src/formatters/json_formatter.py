"""FormatterBase for standard JSON output."""

import json
from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from issues.base import LinterIssueBase


class JSONFormatterBase(FormatterBase):
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        return json.dumps([error.to_dict() for error in issues], indent=4)
