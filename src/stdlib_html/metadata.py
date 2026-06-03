"""Model for storing metadata of bash-stdlib functions."""

from typing import Any, Dict, List, Optional


class FunctionMetadata:
    """Stores metadata extracted from function documentation."""

    def __init__(
        self,
        name: "str",
        arguments: "Optional[List[str]]" = None,
        keywords: "Optional[List[str]]" = None,
        globals: "Optional[List[str]]" = None,
    ) -> "None":
        self.name = name
        self.arguments = arguments if arguments is not None else []
        self.keywords = keywords if keywords is not None else []
        self.globals = globals if globals is not None else []

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the metadata to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "arguments": self.arguments,
            "keywords": self.keywords,
            "globals": self.globals,
        }
