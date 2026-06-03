"""HTTP client for fetching bash-stdlib documentation from remote URLs."""

import sys
import urllib.request
from typing import Any, Dict, Optional, Set

from constants import URL_STANDARD_DOC, URL_TESTING_DOC
from .parser import HTMLParser


class HTMLFetcher:
    def __init__(self) -> "None":
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
        }

    def fetch(self) -> "Optional[Dict[str, Any]]":
        print("Fetching documentation to build cache...", file=sys.stderr)
        all_metadata = self._extract_functions()

        if not all_metadata:
            print("Error: No functions found. Cache not updated.", file=sys.stderr)
            return None

        namespaces = self._build_namespaces(set(all_metadata.keys()))

        return {
            "functions": dict(
                (name, meta.to_dict()) for name, meta in all_metadata.items()
            ),
            "namespaces": sorted(list(namespaces)),
        }

    def _extract_functions(self) -> "Dict[str, Any]":
        functions_metadata = {}
        for url in [URL_STANDARD_DOC, URL_TESTING_DOC]:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode("utf-8")
                    parser = HTMLParser()
                    functions_metadata.update(parser.parse(content))
            except Exception as e:
                print(
                    "Warning: Failed to fetch {url}: {e}".format(url=url, e=e),
                    file=sys.stderr,
                )
        return functions_metadata

    def _build_namespaces(self, function_names: "Set[str]") -> "Set[str]":
        namespaces: "Set[str]" = set()
        for func in function_names:
            parts = func.split(".")
            for i in range(1, len(parts)):
                namespaces.add(".".join(parts[:i]))
        return namespaces
