import unittest
from unittest.mock import MagicMock, patch

from stdlib_html.fetcher import HTMLFetcher


class TestHTMLFetcher(unittest.TestCase):

    def setUp(self) -> None:
        self.fetcher = HTMLFetcher()

    def test_build_namespaces__multiple_functions__creates_correct_hierarchy(
            self) -> None:
        functions = {"stdlib.array.assert.is_array", "stdlib.string.args.join"}

        result = self.fetcher._build_namespaces(functions)

        expected = {
            "stdlib",
            "stdlib.array",
            "stdlib.array.assert",
            "stdlib.string",
            "stdlib.string.args",
        }
        self.assertEqual(result, expected)

    @patch("urllib.request.urlopen")
    def test_extract_functions__valid_html__fetches_and_parses_content(
        self,
        mock_urlopen: MagicMock,
    ) -> None:
        mock_response = MagicMock()
        mock_response.read.return_value = b"<html>stdlib.func1</html>"
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response

        result = self.fetcher._extract_functions()

        self.assertIn("stdlib.func1", result)
        self.assertEqual(mock_urlopen.call_count, 2)

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("stdlib_html.fetcher.HTMLFetcher._extract_functions")
    def test_fetch__functions_found__returns_formatted_metadata(
        self,
        mock_extract: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        mock_extract.return_value = {"stdlib.a.b"}

        result = self.fetcher.fetch()

        self.assertIsNotNone(result)
        if result:
            self.assertEqual(result["functions"], ["stdlib.a.b"])
            self.assertEqual(result["namespaces"], ["stdlib", "stdlib.a"])

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("stdlib_html.fetcher.HTMLFetcher._extract_functions")
    def test_fetch__no_functions_found__returns_none(
        self,
        mock_extract: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        mock_extract.return_value = set()

        result = self.fetcher.fetch()

        self.assertIsNone(result)

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("stdlib_html.fetcher.HTMLFetcher._extract_functions")
    def test_fetch__always__prints_fetching_message(
        self,
        mock_extract: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        mock_extract.return_value = {"stdlib.a"}

        self.fetcher.fetch()

        mock_stderr.write.assert_any_call("Fetching documentation to build cache...")

    @patch("sys.stderr", new_callable=MagicMock)
    @patch("stdlib_html.fetcher.HTMLFetcher._extract_functions")
    def test_fetch__no_functions__prints_error_message(
        self,
        mock_extract: MagicMock,
        mock_stderr: MagicMock,
    ) -> None:
        mock_extract.return_value = set()

        self.fetcher.fetch()

        mock_stderr.write.assert_any_call("Error: No functions found. Cache not updated.")


if __name__ == "__main__":
    unittest.main()
