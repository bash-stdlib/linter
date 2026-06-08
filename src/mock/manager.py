from typing import Any, Dict, List, Optional, Set

from constants import GLOBAL_GRANTING_FUNCTIONS
from functions.scope import FunctionScope
from .instance import MockInstance


class MockManager:
    def __init__(self, functions_metadata: Dict[str, Dict[str, Any]]) -> None:
        self.functions_metadata = functions_metadata
        self.mock_templates = {
            name: meta
            for name, meta in functions_metadata.items()
            if meta.get("is_mock_template")
        }
        self.all_mocks: List[MockInstance] = []
        self.function_scopes: List[FunctionScope] = []
        self.discovered_names: Set[str] = set()

    def set_function_scopes(self, scopes: List[FunctionScope]) -> None:
        self.function_scopes = scopes

    def record_discovered_name(self, name: str) -> None:
        self.discovered_names.add(name)

    def create_mock(self, name: str, offset: int) -> None:
        scope = self._get_scope_for_offset(offset)
        if scope and scope.name in GLOBAL_GRANTING_FUNCTIONS:
            scope = None
        self.all_mocks.append(MockInstance(name, offset, scope))

    def delete_mock(self, name: str, offset: int) -> None:
        # Find the most recently created mock with this name that hasn't
        # been deleted yet
        for mock in reversed(self.all_mocks):
            if (
                mock.name == name
                and mock.deletion_offset is None
                and mock.creation_offset <= offset
            ):
                mock.deletion_offset = offset
                break

    def reset_all(self, offset: int) -> None:
        for mock in self.all_mocks:
            if mock.deletion_offset is None and mock.creation_offset <= offset:
                mock.deletion_offset = offset

    def clear(self) -> None:
        """Completely clear all mocks and scopes (for a new file)."""
        self.all_mocks = []
        self.function_scopes = []
        self.discovered_names = set()

    def clear_instances(self) -> None:
        """Clear active mock instances but keep discovered names and scopes."""
        self.all_mocks = []

    def get_active_mock_names(self, offset: int) -> Set[str]:
        return {mock.name for mock in self.all_mocks if mock.is_active(offset)}

    def get_all_possible_mock_names(self) -> Set[str]:
        return self.discovered_names

    def get_mock_function_metadata(self, mock_name: str) -> Dict[str, Dict[str, Any]]:
        mock_functions: Dict[str, Dict[str, Any]] = {}
        for template_name, template_meta in self.mock_templates.items():
            actual_name = template_name.replace("object", mock_name)
            meta = template_meta.copy()
            meta["name"] = actual_name
            meta["is_mock_template"] = False
            mock_functions[actual_name] = meta
        return mock_functions

    def _get_scope_for_offset(self, offset: int) -> Optional[FunctionScope]:
        # Return the innermost scope (shortest length)
        matching_scopes = [s for s in self.function_scopes if s.is_inside(offset)]
        if not matching_scopes:
            return None

        # Innermost means the one whose START is closest to the current offset
        # from the left
        return max(matching_scopes, key=lambda s: s.start_offset)

    def is_mock_active(self, name: str, offset: int) -> bool:
        return any(m.name == name and m.is_active(offset) for m in self.all_mocks)

    def is_mock_method_active(self, call_name: str, offset: int) -> bool:
        active_names = self.get_active_mock_names(offset)
        for mock_name in active_names:
            if call_name == mock_name:
                return True
            for template_name in self.mock_templates.keys():
                if call_name == template_name.replace("object", mock_name):
                    return True
        return False
