import unittest
from typing import Any
from linter import Linter
from linter.scope import FunctionScope

class TestFunctionScopes(unittest.TestCase):
    def setUp(self) -> None:
        metadata: Any = {"functions": {}, "namespaces": []}
        self.linter = Linter(metadata)

    def test_basic_function_scope(self) -> None:
        content = """
func() {
    echo "hello"
}
"""
        with open("test_basic.sh", "w") as f:
            f.write(content)

        self.linter.lint("test_basic.sh")
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        scope = scopes[0]
        self.assertEqual(scope.name, "func")
        self.assertEqual(scope.start_line, 2)
        self.assertTrue(scope.contains(3, 5))
        self.assertFalse(scope.contains(1, 0))
        self.assertFalse(scope.contains(5, 0))

    def test_function_keyword_scope(self) -> None:
        content = """
function func {
    echo "hello"
}
"""
        with open("test_keyword.sh", "w") as f:
            f.write(content)

        self.linter.lint("test_keyword.sh")
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        scope = scopes[0]
        self.assertEqual(scope.name, "func")
        self.assertEqual(scope.start_line, 2)

    def test_nested_functions(self) -> None:
        content = """
outer() {
    inner() {
        echo "inner"
    }
    echo "outer"
}
"""
        with open("test_nested.sh", "w") as f:
            f.write(content)

        self.linter.lint("test_nested.sh")
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 2)

        outer = next(s for s in scopes if s.name == "outer")
        inner = next(s for s in scopes if s.name == "inner")

        # print(f"Outer: {outer.start_line}-{outer.end_line}, Inner: {inner.start_line}-{inner.end_line}")

        self.assertTrue(outer.contains(4, 5)) # inside inner
        self.assertTrue(inner.contains(4, 5))
        self.assertTrue(outer.contains(7, 5)) # inside outer, but after inner
        self.assertFalse(inner.contains(7, 5))

    def test_unclosed_function_raises_error(self) -> None:
        content = """
func() {
    echo "hello"
"""
        with open("test_unclosed.sh", "w") as f:
            f.write(content)

        with self.assertRaises(RuntimeError):
            self.linter.lint("test_unclosed.sh")

    def test_quoted_braces_ignored(self) -> None:
        content = """
func() {
    echo "}"
}
"""
        with open("test_quoted.sh", "w") as f:
            f.write(content)

        self.linter.lint("test_quoted.sh")
        scopes = self.linter.file_state.function_scopes
        self.assertEqual(len(scopes), 1)
        self.assertEqual(scopes[0].end_line, 4)

if __name__ == "__main__":
    unittest.main()
