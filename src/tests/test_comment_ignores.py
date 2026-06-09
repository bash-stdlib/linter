import unittest
from typing import Any, Dict

from linter.line_iterators.comment_ignores import CommentIgnores
from linter.state import LinterState


class TestCommentIgnores(unittest.TestCase):
    def _create_state(self, content: str) -> LinterState:
        metadata: Dict[str, Any] = {"functions": {}, "namespaces": []}
        state = LinterState(metadata)
        iterator = CommentIgnores(state)

        for i, line in enumerate(content.splitlines(True)):
            iterator.process_line(line, i + 1)

        return state

    def test_is_ignored__file_level_after_shebang__returns_true(self) -> None:
        content = "#!/bin/bash\n# stdlib: disable STD001, STD002\nstdlib.namespace"

        state = self._create_state(content)

        self.assertTrue(state.is_ignored("STD001", 3))
        self.assertTrue(state.is_ignored("STD002", 10))
        self.assertFalse(state.is_ignored("STD003", 3))

    def test_is_ignored__same_line__returns_true(self) -> None:
        content = "echo foo\nstdlib.namespace # stdlib: disable STD003\necho bar"

        state = self._create_state(content)

        self.assertTrue(state.is_ignored("STD003", 2))
        self.assertFalse(state.is_ignored("STD003", 1))
        self.assertFalse(state.is_ignored("STD003", 3))

    def test_is_ignored__previous_line__returns_true(self) -> None:
        content = "echo foo\n# stdlib: disable STD004\nstdlib.namespace\necho bar"

        state = self._create_state(content)

        self.assertTrue(state.is_ignored("STD004", 3))
        self.assertFalse(state.is_ignored("STD004", 1))
        self.assertFalse(state.is_ignored("STD004", 2))

    def test_is_ignored__multiple_directives__accumulates_ignores(self) -> None:
        content = "# stdlib: disable STD001\n# stdlib: disable STD002\nstdlib.namespace"

        state = self._create_state(content)

        self.assertTrue(state.is_ignored("STD001", 3))
        self.assertTrue(state.is_ignored("STD002", 3))

    def test_is_ignored__case_insensitive__returns_true(self) -> None:
        content = "# STDLIB: DISABLE std001"

        state = self._create_state(content)

        self.assertTrue(state.is_ignored("STD001", 1))

    def test_get_unused_ignores__not_used__returns_code_and_line(self) -> None:
        content = "# stdlib: disable STD001\necho hello"

        state = self._create_state(content)
        unused = state.get_unused_ignores()

        self.assertEqual(len(unused), 1)
        self.assertEqual(unused[0], ("STD001", 1))

    def test_get_unused_ignores__used__returns_empty(self) -> None:
        content = "# stdlib: disable STD001\nstdlib.namespace"

        state = self._create_state(content)
        state.is_ignored("STD001", 2)
        unused = state.get_unused_ignores()

        self.assertEqual(len(unused), 0)


if __name__ == "__main__":
    unittest.main()
