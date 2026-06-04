"""Validator to prevent calling namespaces directly."""

from typing import Optional

from errors import STD003
from errors.base import LinterError
from validators.base import Validator


class NotNamespaceCallValidator(Validator):
    """Checks if the call is actually a namespace, which is not allowed."""

    def check(
        self, call: str, file: str, line: int, column: int
    ) -> Optional[LinterError]:
        if call in self.namespaces:
            return STD003(file, line, column, call)
        return None
