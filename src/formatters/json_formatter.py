"""FormatterBase for standard JSON output."""

import json
from typing import TYPE_CHECKING, List

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterIssue


class JSONFormatterBase(FormatterBase):
    def format(self, errors: "List[LinterIssue]") -> "str":
        return json.dumps([error.to_dict() for error in errors], indent=4)
