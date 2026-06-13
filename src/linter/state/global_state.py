"""Global state object for the linter."""

from typing import Any, Dict, List, Optional, Set


class GlobalLinterState:
    """Holds the global configuration and metadata for the linter."""

    MOCK_META_PREFIX = "object.mock."

    def __init__(
        self,
        metadata: Any,
        ignored_codes: Optional[List[str]] = None,
        extra_namespaces: Optional[List[str]] = None,
        extra_functions: Optional[List[str]] = None,
    ) -> None:
        self.functions: Set[str] = set(metadata.get("functions", {}).keys())
        self.namespaces: Set[str] = set(metadata.get("namespaces", []))
        self.metadata: Dict[str, Any] = metadata.get("functions", {})
        self.ignored_codes: Set[str] = (
            {c.upper() for c in ignored_codes} if ignored_codes else set()
        )
        self.extra_namespaces: Set[str] = set(extra_namespaces) if extra_namespaces else set()
        self.extra_functions: Set[str] = set(extra_functions) if extra_functions else set()
        self.mock_methods: Set[str] = self._derive_mock_methods()

    def _derive_mock_methods(self) -> Set[str]:
        """Derive valid mock methods from the loaded metadata."""
        methods = set()
        for func_name in self.functions:
            if func_name.startswith(self.MOCK_META_PREFIX):
                method = func_name[len(self.MOCK_META_PREFIX):]
                methods.add(method)
        return methods
