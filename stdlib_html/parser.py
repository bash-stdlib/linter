import html.parser
import re

class HTMLParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.functions = set()

    def handle_data(self, data):
        # Extract potential function names starting with stdlib.
        matches = re.findall(r'stdlib\.[a-z0-9._]+', data)
        for func in matches:
            # Avoid trailing dots or underscores that might be part of the documentation text
            while func and (func.endswith('.') or func.endswith('_')):
                func = func[:-1]
            if '.' in func: # Must have at least one dot after stdlib.
                self.functions.add(func)
