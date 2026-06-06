import unittest
from parsers.comment_ignores import CommentIgnores


class TestCommentIgnores(unittest.TestCase):
    def test_is_ignored__file_level_after_shebang__returns_true(self):
        content = "#!/bin/bash\n# stdlib: disable STD001, STD002\nstdlib.namespace"
        ignores = CommentIgnores(content)
        self.assertTrue(ignores.is_ignored("STD001", 3))
        self.assertTrue(ignores.is_ignored("STD002", 10))
        self.assertFalse(ignores.is_ignored("STD003", 3))

    def test_is_ignored__same_line__returns_true(self):
        content = "echo foo\nstdlib.namespace # stdlib: disable STD003\necho bar"
        ignores = CommentIgnores(content)
        self.assertTrue(ignores.is_ignored("STD003", 2))
        self.assertFalse(ignores.is_ignored("STD003", 1))
        # Now it should be false for the next line if it's a same-line ignore
        self.assertFalse(ignores.is_ignored("STD003", 3))

    def test_is_ignored__previous_line__returns_true(self):
        content = "echo foo\n# stdlib: disable STD004\nstdlib.namespace\necho bar"
        ignores = CommentIgnores(content)
        self.assertTrue(ignores.is_ignored("STD004", 3))
        self.assertFalse(ignores.is_ignored("STD004", 1))
        # Now it should be false for the comment line itself
        self.assertFalse(ignores.is_ignored("STD004", 2))

    def test_is_ignored__multiple_directives__accumulates_ignores(self):
        content = "# stdlib: disable STD001\n# stdlib: disable STD002\nstdlib.namespace"
        ignores = CommentIgnores(content)
        self.assertTrue(ignores.is_ignored("STD001", 3))
        self.assertTrue(ignores.is_ignored("STD002", 3))

    def test_is_ignored__case_insensitive__returns_true(self):
        content = "# STDLIB: DISABLE std001"
        ignores = CommentIgnores(content)
        self.assertTrue(ignores.is_ignored("STD001", 1))


if __name__ == "__main__":
    unittest.main()
