from typing import Any, Dict, Set


class LinterState:
    """Encapsulates the current state of the linter during a run."""

    def __init__(self, metadata: Any) -> None:
        self.base_functions: Set[str] = set(metadata["functions"].keys())
        self.base_namespaces: Set[str] = set(metadata["namespaces"])
        self.base_metadata: Dict[str, Any] = metadata["functions"]

        self.functions: Set[str] = self.base_functions.copy()
        self.namespaces: Set[str] = self.base_namespaces.copy()
        self.metadata: Dict[str, Any] = self.base_metadata.copy()

    def reset(self) -> None:
        """Reset state to base metadata."""
        self.functions = self.base_functions.copy()
        self.namespaces = self.base_namespaces.copy()
        self.metadata = self.base_metadata.copy()
