"""Discovery iterator that skips comments in the token stream."""

from typing import TYPE_CHECKING

from linter.discovery_iterators.base import DiscoveryIteratorBase

if TYPE_CHECKING:
    from parsers.token_iterators.enhanced_shlex import AdvancedToken


class CommentDiscoveryIterator(DiscoveryIteratorBase):
    """Filters out tokens that are within Bash comments."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.in_comment = False

    def handle_token(self, token: "AdvancedToken") -> bool:
        """Track comment state and mark tokens for skipping."""
        if not token.is_fully_quoted:
            if "#" in token.unquoted_specials and token.startswith("#"):
                self.in_comment = True
                return False
            elif "\n" in token.unquoted_specials:
                self.in_comment = False
                return True

        return not self.in_comment
