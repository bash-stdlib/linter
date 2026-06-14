"""Model for storing metadata of bash-stdlib functions."""

from typing import Any, Dict, List, Optional


class TypedEntity:
    """Represents an entity (argument, keyword, or global) with a name and type."""

    def __init__(self, name: "str", entity_type: "str") -> "None":
        self.name = name
        self.type = entity_type

    def to_dict(self) -> "Dict[str, str]":
        """Convert the entity to a dictionary for JSON serialization."""
        return {"name": self.name, "type": self.type}


class FunctionMetadata:
    """Stores metadata extracted from function documentation."""

    def __init__(
        self,
        name: "str",
        arguments: "Optional[List[TypedEntity]]" = None,
        keywords: "Optional[List[TypedEntity]]" = None,
        globals: "Optional[List[TypedEntity]]" = None,
        min_args: "int" = 0,
        max_args: "int" = 0,
        is_testing: "bool" = False,
    ) -> "None":
        self.name = name
        self.arguments = arguments if arguments is not None else []
        self.keywords = keywords if keywords is not None else []
        self.globals = globals if globals is not None else []
        self.min_args = min_args
        self.max_args = max_args
        self.is_testing = is_testing

    def to_dict(self) -> "Dict[str, Any]":
        """Convert the metadata to a dictionary for JSON serialization."""
        return {
            "name": self.name,
            "arguments": [arg.to_dict() for arg in self.arguments],
            "keywords": [kw.to_dict() for kw in self.keywords],
            "globals": [g.to_dict() for g in self.globals],
            "min_args": self.min_args,
            "max_args": self.max_args,
            "is_testing": self.is_testing,
        }
