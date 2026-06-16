import unittest

from linter.token_iterators.shlex import ShlexTokenIterator


class TestIssueReproAssignments(unittest.TestCase):
    def test_is_at_command_position__assignment__returns_false(self) -> None:
        # KEYWORD="rm"
        # The match would be 'rm' at the end of the string.
        # But wait, ValidationPipeline._is_at_command_position passes
        # everything BEFORE the match.

        # Case 1: KEYWORD="rm"
        # Match is 'rm'. content_before is 'KEYWORD="'
        iterator = ShlexTokenIterator('KEYWORD="')
        self.assertFalse(
            iterator.is_at_command_position(),
            "Should NOT be at command position inside assignment value",
        )

        # Case 2: KEYWORD=rm
        # Match is 'rm'. content_before is 'KEYWORD='
        iterator = ShlexTokenIterator("KEYWORD=")
        self.assertFalse(
            iterator.is_at_command_position(),
            "Should NOT be at command position immediately after '='",
        )

    def test_is_at_command_position__assignment_with_whitespace__returns_true(
        self,
    ) -> None:
        # Case 3: VAR=val rm
        # Match is 'rm'. content_before is 'VAR=val '
        iterator = ShlexTokenIterator("VAR=val ")
        self.assertTrue(
            iterator.is_at_command_position(),
            "Should be at command position after assignment AND whitespace",
        )

    def test_is_at_command_position__unclosed_quote__returns_false(self) -> None:
        # Case 4: unclosed quote
        iterator = ShlexTokenIterator('KEYWORD="')
        # Currently it returns True because it doesn't see any tokens.
        self.assertFalse(
            iterator.is_at_command_position(),
            "Should NOT be at command position if there is a parsing error",
        )


if __name__ == "__main__":
    unittest.main()
