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

    def set_function_scopes(self, scopes: List[FunctionScope]) -> None:
        self.function_scopes = scopes

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

    def get_active_mock_names(self, offset: int) -> Set[str]:
        return {mock.name for mock in self.all_mocks if mock.is_active(offset)}

    def get_all_possible_mock_names(self) -> Set[str]:
        return {mock.name for mock in self.all_mocks}

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
        for scope in self.function_scopes:
            if scope.is_inside(offset):
                return scope
        return None

    def is_mock_active(self, name: str, offset: int) -> bool:
        return any(m.name == name and m.is_active(offset) for m in self.all_mocks)

    def is_mock_method_active(self, call_name: str, offset: int) -> bool:
        for mock_name in self.get_active_mock_names(offset):
            for template_name in self.mock_templates.keys():
                if call_name == template_name.replace("object", mock_name):
                    return True
        return False
