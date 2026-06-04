"""Base class for all bash-stdlib linter parsers."""

import abc
from typing import List, Optional


class ParserBase(abc.ABC):
    """Abstract base class for all parsers."""

    @abc.abstractmethod
    def parse(self, content: "str") -> "Optional[List[str]]":
        """Parse the given content and return a list of extracted items."""
        pass
