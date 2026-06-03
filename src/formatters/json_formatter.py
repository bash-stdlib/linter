"""FormatterBase for standard JSON output."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

from .base import FormatterBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class JSONFormatterBase(FormatterBase):
    def format(self, errors: list[LinterErrorBase]) -> str:
        return json.dumps([error.to_dict() for error in errors], indent=4)
