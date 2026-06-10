"""Discovery iterator that skips comments in the token stream."""

from typing import TYPE_CHECKING

from linter.discovery_iterators.base import DiscoveryAction, DiscoveryIteratorBase

if TYPE_CHECKING:
    from parsers.token_iterators.enhanced_shlex import AdvancedToken


class CommentDiscoveryIterator(DiscoveryIteratorBase):
    """Filters out tokens that are within Bash comments."""

    def handle_token(self, token: "AdvancedToken") -> DiscoveryAction:
        """Track comment state and mark tokens for skipping."""
        if not token.is_fully_quoted:
            if "#" in token.unquoted_specials and token.startswith("#"):
                return DiscoveryAction.STOP_LINE

        return DiscoveryAction.CONTINUE
