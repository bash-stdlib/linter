"""Unit tests for the BashArgumentsParser."""

import unittest

from parsers.bash_arguments import BashArgumentsParser


class TestBashArgumentsParser(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = BashArgumentsParser()

    def test_parse__basic_arguments__returns_list(self) -> None:
        content = "arg1 'arg 2' arg3"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg 2", "arg3"])

    def test_parse__standard_redirect_out__filters_out_redirect(self) -> None:
        content = "arg1 > file arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__standard_redirect_append__filters_out_redirect(self) -> None:
        content = "arg1 >> file arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__standard_redirect_in__filters_out_redirect(self) -> None:
        content = "arg1 < file arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__here_string__filters_out_redirect(self) -> None:
        content = "arg1 <<< 'string' arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__here_doc_marker__filters_out_redirect_and_marker(self) -> None:
        content = "arg1 << EOF arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__fd_redirect_no_space__filters_out_redirect(self) -> None:
        content = "arg1 2>file arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__fd_redirect_with_space__filters_out_redirect(self) -> None:
        content = "arg1 2> file arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__fd_to_fd_redirect__filters_out_redirect(self) -> None:
        content = "arg1 2>&1 arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__fd_to_fd_redirect_with_space__filters_out_redirect(self) -> None:
        content = "arg1 2>& 1 arg2"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__subshell_dollar_paren__counts_as_one_argument(self) -> None:
        content = "arg1 $(echo foo bar) arg2"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("$("))
        self.assertTrue(result[1].endswith(")"))

    def test_parse__nested_subshell__counts_as_one_argument(self) -> None:
        content = "arg1 $(echo $(nested)) arg2"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("$("))
        self.assertTrue(result[1].endswith(")"))

    def test_parse__parameter_expansion__counts_as_one_argument(self) -> None:
        content = "arg1 ${VAR:-default} arg2"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("${"))
        self.assertTrue(result[1].endswith("}"))

    def test_parse__quoted_subshell__counts_as_one_argument(self) -> None:
        content = 'arg1 "$(echo foo bar)" arg2'

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("$("))
        self.assertTrue(result[1].endswith(")"))

    def test_parse__backticks__counts_as_one_argument(self) -> None:
        content = "arg1 `echo foo` arg2"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("`"))
        self.assertTrue(result[1].endswith("`"))

    def test_parse__nested_backticks__counts_as_one_argument(self) -> None:
        content = "arg1 `echo \\`echo nested\\`` arg2"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[2], "arg2")
        self.assertTrue(result[1].startswith("`"))
        self.assertTrue(result[1].endswith("`"))

    def test_parse__command_separator_semicolon__stops_at_separator(self) -> None:
        content = "arg1 arg2 ; next_cmd"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__nested_in_subshell__stops_at_closing_paren(self) -> None:
        content = "arg1 arg2 ) next_cmd"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__nested_in_braces__stops_at_closing_brace(self) -> None:
        content = "arg1 arg2 } next_cmd"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__newline__stops_at_newline(self) -> None:
        content = "arg1 arg2\nnext_cmd"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2"])

    def test_parse__line_continuation__merges_lines(self) -> None:
        content = "arg1 arg2 \\\narg3"

        result = self.parser.parse(content)

        self.assertEqual(result, ["arg1", "arg2", "arg3"])

    def test_parse__unbalanced_quotes__returns_none(self) -> None:
        content = 'arg1 "unbalanced quote'

        result = self.parser.parse(content)

        self.assertIsNone(result)

    def test_parse__complex_mixed__correctly_identifies_arguments(self) -> None:
        content = "arg1 'quoted arg' 2>/dev/null arg2 $(subshell) arg3\nnext_line"

        result = self.parser.parse(content)

        assert result is not None
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], "arg1")
        self.assertEqual(result[1], "quoted arg")
        self.assertEqual(result[2], "arg2")
        self.assertEqual(result[4], "arg3")

if __name__ == "__main__":
    unittest.main()
