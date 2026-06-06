import unittest
from parsers.comment_ignores import CommentIgnores


class TestCommentIgnores(unittest.TestCase):
    def _create_ignores(self, content: str) -> CommentIgnores:
        ignores = CommentIgnores()

        for i, line in enumerate(content.splitlines(True)):
            ignores.process_line(line, i + 1)

        return ignores

    def test_is_ignored__file_level_after_shebang__returns_true(self):
        content = "#!/bin/bash\n# stdlib: disable STD001, STD002\nstdlib.namespace"

        ignores = self._create_ignores(content)

        self.assertTrue(ignores.is_ignored("STD001", 3))
        self.assertTrue(ignores.is_ignored("STD002", 10))
        self.assertFalse(ignores.is_ignored("STD003", 3))

    def test_is_ignored__same_line__returns_true(self):
        content = "echo foo\nstdlib.namespace # stdlib: disable STD003\necho bar"

        ignores = self._create_ignores(content)

        self.assertTrue(ignores.is_ignored("STD003", 2))
        self.assertFalse(ignores.is_ignored("STD003", 1))
        self.assertFalse(ignores.is_ignored("STD003", 3))

    def test_is_ignored__previous_line__returns_true(self):
        content = "echo foo\n# stdlib: disable STD004\nstdlib.namespace\necho bar"

        ignores = self._create_ignores(content)

        self.assertTrue(ignores.is_ignored("STD004", 3))
        self.assertFalse(ignores.is_ignored("STD004", 1))
        self.assertFalse(ignores.is_ignored("STD004", 2))

    def test_is_ignored__multiple_directives__accumulates_ignores(self):
        content = "# stdlib: disable STD001\n# stdlib: disable STD002\nstdlib.namespace"

        ignores = self._create_ignores(content)

        self.assertTrue(ignores.is_ignored("STD001", 3))
        self.assertTrue(ignores.is_ignored("STD002", 3))

    def test_is_ignored__case_insensitive__returns_true(self):
        content = "# STDLIB: DISABLE std001"

        ignores = self._create_ignores(content)

        self.assertTrue(ignores.is_ignored("STD001", 1))

    def test_get_unused_ignores__not_used__returns_code_and_line(self):
        content = "# stdlib: disable STD001\necho hello"

        ignores = self._create_ignores(content)
        unused = ignores.get_unused_ignores()

        self.assertEqual(len(unused), 1)
        self.assertEqual(unused[0], ("STD001", 1))

    def test_get_unused_ignores__used__returns_empty(self):
        content = "# stdlib: disable STD001\nstdlib.namespace"

        ignores = self._create_ignores(content)
        ignores.is_ignored("STD001", 2)
        unused = ignores.get_unused_ignores()

        self.assertEqual(len(unused), 0)


if __name__ == "__main__":
    unittest.main()
