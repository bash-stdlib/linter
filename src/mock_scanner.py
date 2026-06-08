from typing import List

from functions.scope import FunctionScope
from mock.manager import MockManager
from parsers.token_iterators import ShlexTokenIterator


class MockScanner:
    """Helper class to scan Bash content for function scopes and mock lifetimes."""

    def __init__(self, mock_manager: MockManager) -> None:
        self.mock_manager = mock_manager

    def discover_scopes(self, content: str) -> List[FunctionScope]:
        scopes = []
        iterator = ShlexTokenIterator(content)
        try:
            for token in iterator:
                if (
                    hasattr(token, "is_fully_quoted")
                    and not token.is_fully_quoted
                    and (
                        token == "function"
                        or iterator.is_preceded_by_function_keyword(
                            content[: token.start_offset]
                        )
                    )
                ):
                    # Potential function definition
                    name = token
                    if name == "function":
                        name = next(iterator)

                    # Look for opening brace
                    found_brace = False
                    for t in iterator:
                        if (
                            hasattr(t, "is_fully_quoted")
                            and not t.is_fully_quoted
                            and "{" in t.unquoted_specials
                        ):
                            found_brace = True
                            break
                        if (
                            hasattr(t, "is_fully_quoted")
                            and not t.is_fully_quoted
                            and t in [";", "\n"]
                        ):
                            continue
                        break

                    if found_brace:
                        start_offset = t.start_offset
                        end_offset = iterator.skip_to_balanced_bracket()
                        if end_offset:
                            scopes.append(FunctionScope(name, start_offset, end_offset))
        except (StopIteration, ValueError):
            pass
        return scopes

    def discover_mock_creations(self, content: str) -> None:
        iterator = ShlexTokenIterator(content)
        try:
            for token in iterator:
                if token == "_mock.create":
                    try:
                        mock_name = next(iterator)
                        # Use end_offset to ensure it's created AFTER the token
                        self.mock_manager.create_mock(mock_name, token.end_offset)
                    except StopIteration:
                        pass
        except (StopIteration, ValueError):
            pass

    def track_mock_lifetimes(self, line_content: str, line_offset: int) -> None:
        iterator = ShlexTokenIterator(line_content)
        try:
            for token in iterator:
                if token == "_mock.delete":
                    try:
                        mock_name = next(iterator)
                        self.mock_manager.delete_mock(
                            mock_name, line_offset + token.start_offset
                        )
                    except StopIteration:
                        pass
                elif token == "_mock.reset_all":
                    self.mock_manager.reset_all(line_offset + token.start_offset)
        except (StopIteration, ValueError):
            pass
