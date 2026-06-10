"""Discovery iterator that skips comments in the token stream."""

from typing import TYPE_CHECKING

from linter.discovery_iterators.base import DiscoveryIteratorBase

if TYPE_CHECKING:
    from parsers.token_iterators.enhanced_shlex import AdvancedToken


class CommentDiscoveryIterator(DiscoveryIteratorBase):
    """Filters out tokens that are within Bash comments."""

    def handle_token(self, token: "AdvancedToken") -> bool:
        """Track comment state and mark tokens for skipping."""
        if not token.is_fully_quoted:
            if "#" in token.unquoted_specials and token.startswith("#"):
                # Returning False here will signal DiscoveryPipeline to stop
                # processing this token. However, shlex itself needs to skip
                # to the newline to avoid quote-splitting issues.
                # We handle the actual skip in the Pipeline loop for now.
                return False

        return True
