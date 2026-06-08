"""FormatterBase for standard JSON output."""

import json
from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterIssueBase


class JSONFormatterBase(FormatterBase):
    def format(self, issues: "List[LinterIssueBase]") -> "str":
        return json.dumps([issue.to_dict() for issue in issues], indent=4)
