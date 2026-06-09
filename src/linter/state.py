"""State object for the linter."""

from typing import Any, Dict, List, Optional, Set


class LinterState:
    """Holds the configuration and metadata for the linter."""

    def __init__(
        self,
        metadata: Any,
        ignored_codes: Optional[List[str]] = None,
        appendum: Optional[List[str]] = None,
    ) -> None:
        self.functions: Set[str] = set(metadata["functions"].keys())
        self.namespaces: Set[str] = set(metadata["namespaces"])
        self.metadata: Dict[str, Any] = metadata["functions"]
        self.ignored_codes: Set[str] = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.appendum: Set[str] = set(appendum) if appendum else set()
