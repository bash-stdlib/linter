from typing import TYPE_CHECKING, List, Optional

from errors import STD002
from validators.base import ValidatorBase

if TYPE_CHECKING:
    from errors.base import LinterErrorBase


class MockVisibilityValidator(ValidatorBase):
    """Checks if a mock call is active at the current offset."""

    def check(
        self,
        call: str,
        filepath: str,
        line: int,
        column: int,
        args: Optional[List[str]] = None,
    ) -> "Optional[LinterErrorBase]":
        # We need an absolute offset here. But check() only gets line/column.
        # Actually, Linter can pass the offset as part of the context or we can
        # recalculate it if needed.
        # But wait, the ValidatorBase has access to self.state.
        # Maybe we should pass the current absolute offset to check()?
        # For now, let's assume we can get it from state if we store it there
        # during the linting pass.

        offset = self.state.current_absolute_offset

        if self.state.mock_manager.is_mock_method_active(call, offset):
            return None

        # Check if call is a mock name itself or a mock method
        is_mock_related = any(
            call == m or call.startswith(m + ".mock.")
            for m in self.state.mock_manager.get_all_possible_mock_names()
        )

        # Also check if it's a known mock method template being used on SOMETHING
        if not is_mock_related:
            for template_name in self.state.mock_manager.mock_templates.keys():
                if ".mock." in template_name:
                    suffix = template_name.replace("object", "")
                    if call.endswith(suffix):
                        is_mock_related = True
                        break

        if is_mock_related:
            # It matches a mock template but is NOT active
            namespace = ".".join(call.split(".")[:-1])
            return STD002(filepath, line, column, call, namespace)

        return None
