"""Global state object for the linter."""

from typing import Any, Dict, List, Optional, Set


class GlobalLinterState:
    """Holds the global configuration and metadata for the linter."""

    def __init__(
        self,
        metadata: Any,
        ignored_codes: Optional[List[str]] = None,
        extra_namespaces: Optional[List[str]] = None,
        extra_functions: Optional[List[str]] = None,
    ) -> None:
        self.functions: Set[str] = set(metadata["functions"].keys())
        self.namespaces: Set[str] = set(metadata["namespaces"])
        self.metadata: Dict[str, Any] = metadata["functions"]
        self.ignored_codes: Set[str] = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.extra_namespaces: Set[str] = set(extra_namespaces) if extra_namespaces else set()
        self.extra_functions: Set[str] = set(extra_functions) if extra_functions else set()
