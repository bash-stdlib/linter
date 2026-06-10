"""Unit tests for EnhancedShlex quote and escape handling."""

import unittest

from parsers.token_iterators.enhanced_shlex import EnhancedShlex


class TestEnhancedShlexSingleQuotes(unittest.TestCase):
    """Tests for single-quoted string handling."""

    def test_read_token__single_quoted_literal_backslash__preserves_as_literal(
        self,
    ) -> None:
        content = "'hello\\nworld'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "hello\\nworld")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__single_quoted_backslash_t__preserves_as_literal(
        self,
    ) -> None:
        content = "'test\\ttab'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "test\\ttab")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__single_quoted_multiple_backslashes__preserves_all_literal(
        self,
    ) -> None:
        content = "'\\\\double\\\\slash'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "\\\\double\\\\slash")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__single_quoted_with_dollar__preserves_as_literal(
        self,
    ) -> None:
        content = "'$VAR'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "$VAR")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__single_quoted_empty__marks_as_fully_quoted(
        self,
    ) -> None:
        content = "''"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "")
        self.assertTrue(result.is_fully_quoted)


class TestEnhancedShlexDoubleQuotes(unittest.TestCase):
    """Tests for double-quoted string handling."""

    def test_read_token__double_quoted_with_backslash_n__marks_as_fully_quoted(
        self,
    ) -> None:
        content = '"hello\\nworld"'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "hello\\nworld")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__double_quoted_with_dollar_expansion__marks_as_fully_quoted(
        self,
    ) -> None:
        content = '"${VAR}"'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "${VAR}")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__double_quoted_empty__marks_as_fully_quoted(
        self,
    ) -> None:
        content = '""'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "")
        self.assertTrue(result.is_fully_quoted)


class TestEnhancedShlexParameterExpansion(unittest.TestCase):
    """Tests for complex parameter expansion patterns."""

    def test_read_token__double_quoted_parameter_substitution__marks_as_fully_quoted(
        self,
    ) -> None:
        content = '"${1//pattern/replacement}"'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "${1//pattern/replacement}")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__double_quoted_nested_param_escaped_var__marks_as_fully_quoted(
        self,
    ) -> None:
        content = '"${1//\\${delimiter}/}"'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "${1//\\${delimiter}/}")
        self.assertTrue(result.is_fully_quoted)

    def test_read_token__single_quoted_parameter_like_text__marks_as_fully_quoted(
        self,
    ) -> None:
        content = "'${1//pattern/}'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "${1//pattern/}")
        self.assertTrue(result.is_fully_quoted)


class TestEnhancedShlexComplexCommand(unittest.TestCase):
    """Tests for complex multi-token commands with quoting."""

    def test_read_token__printf_with_single_quoted_format__all_tokens_correct(
        self,
    ) -> None:
        content = "builtin printf '%s\\n' arg"
        lexer = EnhancedShlex(content, target_chars=[])

        result = [str(t) for t in lexer]

        self.assertEqual(result, ["builtin", "printf", "%s\\n", "arg"])

    def test_read_token__printf_with_single_quoted_format__format_marked_as_quoted(
        self,
    ) -> None:
        content = "builtin printf '%s\\n' arg"
        lexer = EnhancedShlex(content, target_chars=[])

        tokens = list(lexer)

        self.assertTrue(tokens[2].is_fully_quoted)

    def test_read_token__printf_and_double_quoted_expansion__both_marked_as_quoted(
        self,
    ) -> None:
        content = "builtin printf '%s\\n' \"${1//\\${delimiter}/}\""
        lexer = EnhancedShlex(content, target_chars=[])

        tokens = list(lexer)

        self.assertEqual(len(tokens), 4)
        self.assertEqual(tokens[0], "builtin")
        self.assertFalse(tokens[0].is_fully_quoted)
        self.assertEqual(tokens[1], "printf")
        self.assertFalse(tokens[1].is_fully_quoted)
        self.assertEqual(tokens[2], "%s\\n")
        self.assertTrue(tokens[2].is_fully_quoted)
        self.assertEqual(tokens[3], "${1//\\${delimiter}/}")
        self.assertTrue(tokens[3].is_fully_quoted)

    def test_read_token__original_issue_case__all_tokens_parse_correctly(
        self,
    ) -> None:
        content = "builtin printf '%s\\n' \"${1//${delimiter}/}\""
        lexer = EnhancedShlex(content, target_chars=[])

        result = [str(t) for t in lexer]

        self.assertEqual(result, ["builtin", "printf", "%s\\n", "${1//${delimiter}/}"])


class TestEnhancedShlexUnquotedEscapes(unittest.TestCase):
    """Tests for escape handling outside quotes."""

    def test_read_token__escaped_dollar_outside_quotes__produces_unquoted_token(
        self,
    ) -> None:
        content = "\\$var"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "$var")
        self.assertFalse(result.is_fully_quoted)

    def test_read_token__escaped_space_outside_quotes__combines_into_one_token(
        self,
    ) -> None:
        content = "hello\\ world"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "hello world")
        self.assertFalse(result.is_fully_quoted)

    def test_read_token__escaped_backslash_outside_quotes__produces_single_backslash(
        self,
    ) -> None:
        content = "test\\\\value"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "test\\value")
        self.assertFalse(result.is_fully_quoted)


class TestEnhancedShlexMixedQuoting(unittest.TestCase):
    """Tests for mixed quoting scenarios."""

    def test_read_token__single_then_double_quotes__produces_combined_token(
        self,
    ) -> None:
        content = "'hello'\"world\""
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "helloworld")

    def test_read_token__quote_after_plain_text__produces_combined_token(
        self,
    ) -> None:
        content = "test'value'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "testvalue")

    def test_read_token__empty_quotes_between_text__combines_correctly(
        self,
    ) -> None:
        content = "a''b"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result, "ab")


class TestEnhancedShlexOffsets(unittest.TestCase):
    """Tests for offset and range tracking."""

    def test_read_token__single_quoted__start_and_end_offsets_correct(
        self,
    ) -> None:
        content = "'hello'"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result.start_offset, 0)
        self.assertEqual(result.end_offset, 7)
        self.assertEqual(content[result.start_offset : result.end_offset], "'hello'")

    def test_read_token__double_quoted__start_and_end_offsets_correct(
        self,
    ) -> None:
        content = '"test"'
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result.start_offset, 0)
        self.assertEqual(result.end_offset, 6)
        self.assertEqual(content[result.start_offset : result.end_offset], '"test"')

    def test_read_token__unquoted__start_and_end_offsets_correct(
        self,
    ) -> None:
        content = "word"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result.start_offset, 0)
        self.assertEqual(result.end_offset, 4)
        self.assertEqual(content[result.start_offset : result.end_offset], "word")

    def test_read_token__multiple_tokens__offsets_span_literals_correctly(
        self,
    ) -> None:
        content = "cmd 'arg'"
        lexer = EnhancedShlex(content, target_chars=[])

        tokens = list(lexer)

        self.assertEqual(content[tokens[0].start_offset : tokens[0].end_offset], "cmd")
        self.assertEqual(
            content[tokens[1].start_offset : tokens[1].end_offset], "'arg'"
        )


class TestEnhancedShlexSpecialCharacters(unittest.TestCase):
    """Tests for target_chars detection within quoted strings."""

    def test_read_token__pipe_in_single_quotes__not_in_unquoted_specials(
        self,
    ) -> None:
        content = "'|'"
        lexer = EnhancedShlex(content, target_chars=["|"])

        result = next(lexer)

        self.assertTrue(result.is_fully_quoted)
        self.assertNotIn("|", result.unquoted_specials)

    def test_read_token__pipe_unquoted__in_unquoted_specials(
        self,
    ) -> None:
        content = "|"
        lexer = EnhancedShlex(content, target_chars=["|"])

        result = next(lexer)

        self.assertFalse(result.is_fully_quoted)
        self.assertIn("|", result.unquoted_specials)

    def test_read_token__hash_in_double_quotes__not_in_unquoted_specials(
        self,
    ) -> None:
        content = '"#"'
        lexer = EnhancedShlex(content, target_chars=["#"])

        result = next(lexer)

        self.assertTrue(result.is_fully_quoted)
        self.assertNotIn("#", result.unquoted_specials)

    def test_read_token__hash_unquoted__in_unquoted_specials(
        self,
    ) -> None:
        content = "#"
        lexer = EnhancedShlex(content, target_chars=["#"])

        result = next(lexer)

        self.assertFalse(result.is_fully_quoted)
        self.assertIn("#", result.unquoted_specials)


class TestEnhancedShlexConsecutiveParens(unittest.TestCase):
    """Tests for consecutive parentheses tokenization (arithmetic expressions)."""

    def test_read_token__double_close_paren_before_pipe__returns_separate_tokens(
        self,
    ) -> None:
        content = "required_options)) ||"
        lexer = EnhancedShlex(content, target_chars=["(", ")", "{", "}"])

        tokens = [str(t) for t in lexer]

        self.assertEqual(tokens, ["required_options", ")", "|", "|"])

    def test_read_token__arithmetic_expr_with_or__all_parens_returned_separately(
        self,
    ) -> None:
        content = "(( x == 1 )) || echo"
        lexer = EnhancedShlex(content, target_chars=["(", ")", "{", "}"])

        tokens = [str(t) for t in lexer]

        expected_parens = ["(", "(", ")", ")", "|", "|"]
        actual_parens = [t for t in tokens if t in "()|"]

        self.assertEqual(actual_parens, expected_parens)

    def test_read_token__consecutive_close_parens__each_in_separate_token(
        self,
    ) -> None:
        content = ")) ||"
        lexer = EnhancedShlex(content, target_chars=["(", ")", "{", "}"])

        tokens = [str(t) for t in lexer]

        self.assertEqual(tokens, [")", ")", "|", "|"])


class TestEnhancedShlexLineNumbers(unittest.TestCase):
    """Tests for line number tracking."""

    def test_read_token__single_line__line_num_is_one(self) -> None:
        content = "test"
        lexer = EnhancedShlex(content, target_chars=[])

        result = next(lexer)

        self.assertEqual(result.line_num, 1)

    def test_read_token__after_newline__line_num_incremented(self) -> None:
        content = "line1\nline2"
        lexer = EnhancedShlex(content, target_chars=[])

        first = next(lexer)
        second = next(lexer)

        self.assertEqual(first.line_num, 1)
        self.assertEqual(second.line_num, 2)

    def test_read_token__multiple_newlines__line_num_correctly_counted(
        self,
    ) -> None:
        content = "line1\nline2\nline3"
        lexer = EnhancedShlex(content, target_chars=[])

        tokens = list(lexer)

        self.assertEqual(tokens[0].line_num, 1)
        self.assertEqual(tokens[1].line_num, 2)
        self.assertEqual(tokens[2].line_num, 3)


if __name__ == "__main__":
    unittest.main()
