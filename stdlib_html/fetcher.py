import urllib.request
import sys
from .parser import HTMLParser
from constants import URL_STANDARD_DOC, URL_TESTING_DOC

class HTMLFetcher:
    def __init__(self):
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}

    def fetch_stdlib_metadata(self):
        print("Fetching documentation to build cache...")
        all_functions = set()
        for url in [URL_STANDARD_DOC, URL_TESTING_DOC]:
            try:
                req = urllib.request.Request(url, headers=self.headers)
                with urllib.request.urlopen(req) as response:
                    content = response.read().decode('utf-8')
                    parser = HTMLParser()
                    parser.feed(content)
                    all_functions.update(parser.functions)
            except Exception as e:
                print(f"Warning: Failed to fetch {url}: {e}", file=sys.stderr)

        if not all_functions:
            print("Error: No functions found. Cache not updated.", file=sys.stderr)
            return None

        # Build namespaces
        namespaces = set()
        for func in all_functions:
            parts = func.split('.')
            # If func is stdlib.array.assert.is_array
            # namespaces are: stdlib, stdlib.array, stdlib.array.assert
            for i in range(1, len(parts)):
                namespaces.add('.'.join(parts[:i]))

        return {
            "functions": sorted(list(all_functions)),
            "namespaces": sorted(list(namespaces))
        }
