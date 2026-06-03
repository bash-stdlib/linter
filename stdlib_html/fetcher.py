"""HTTP client for fetching bash-stdlib documentation from remote URLs."""

import sys
import urllib.request

from constants import URL_STANDARD_DOC, URL_TESTING_DOC
from .parser import HTMLParser


class HTMLFetcher:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def fetch(self):
        print("Fetching documentation to build cache...", file=sys.stderr)
        all_functions = self._extract_functions()

        if not all_functions:
            print("Error: No functions found. Cache not updated.", file=sys.stderr)
            return None

        namespaces = self._build_namespaces(all_functions)

        return {
            "functions": sorted(list(all_functions)),
            "namespaces": sorted(list(namespaces)),
        }

    def _extract_functions(self):
        functions = set()
        for url in [URL_STANDARD_DOC, URL_TESTING_DOC]:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode("utf-8")
                    parser = HTMLParser()
                    functions.update(parser.parse(content))
            except Exception as e:
                print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)
        return functions

    def _build_namespaces(self, functions):
        namespaces = set()
        for func in functions:
            parts = func.split(".")
            for i in range(1, len(parts)):
                namespaces.add(".".join(parts[:i]))
        return namespaces
