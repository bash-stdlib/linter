import re
import difflib
from models import LinterError
from constants import STDLIB_PATTERN

class Linter:
    def __init__(self, metadata):
        self.functions = set(metadata['functions'])
        self.namespaces = set(metadata['namespaces'])
        self.stdlib_call_pattern = re.compile(STDLIB_PATTERN)

    def lint(self, filepath):
        errors = []
        file_content = self._read_file(filepath, errors)
        if file_content is None:
            return errors

        for match in self.stdlib_call_pattern.finditer(file_content):
            errors.extend(self._process_match(match, file_content, filepath))

        return errors

    def _read_file(self, filepath, errors):
        try:
            with open(filepath, 'r') as f:
                return f.read()
        except Exception as e:
            errors.append(LinterError(
                file=filepath,
                line=0,
                column=0,
                message=f"Failed to read file: {e}",
                match=""
            ))
            return None

    def _process_match(self, match, content, filepath):
        call_name = self._get_call_name(match)
        line_number = self._get_line_number(content, match.start())
        column_number = self._get_column_number(content, match.start())

        is_valid, error_message = self._validate_call(call_name)
        if not is_valid:
            return [LinterError(
                file=filepath,
                line=line_number,
                column=column_number,
                message=error_message,
                match=call_name
            )]
        return []

    def _get_call_name(self, match):
        call = match.group(1)
        if call.endswith('.'):
            return call[:-1]
        return call

    def _get_line_number(self, content, offset):
        return content.count('\n', 0, offset) + 1

    def _get_column_number(self, content, offset):
        last_newline = content.rfind('\n', 0, offset)
        return offset - last_newline if last_newline != -1 else offset + 1

    def _validate_call(self, call):
        if call in self.functions:
            return True, None

        if call in self.namespaces:
            return False, f"'{call}' is a namespace, not a function."

        return False, self._generate_error_message(call)

    def _generate_error_message(self, call):
        longest_namespace = self._find_longest_namespace_prefix(call)

        if longest_namespace:
            if self._is_immediate_child_of_namespace(call, longest_namespace):
                message = f"Invalid function '{call}' in valid namespace '{longest_namespace}'."
                suggestion = self._get_suggestion(call, longest_namespace)
                if suggestion:
                    message += f" Did you mean '{suggestion}'?"
                return message

            invalid_namespace = self._extract_invalid_namespace(call, longest_namespace)
            return f"Invalid namespace '{invalid_namespace}'."

        return f"Invalid namespace or function '{call}'."

    def _find_longest_namespace_prefix(self, call):
        parts = call.split('.')
        for i in range(len(parts) - 1, 0, -1):
            prefix = '.'.join(parts[:i])
            if prefix in self.namespaces:
                return prefix
        return None

    def _is_immediate_child_of_namespace(self, call, namespace):
        parts = call.split('.')
        return namespace == '.'.join(parts[:-1])

    def _get_suggestion(self, call, namespace):
        possible_functions = [f for f in self.functions if f.startswith(namespace + ".")]
        suggestions = difflib.get_close_matches(call, possible_functions, n=1)
        return suggestions[0] if suggestions else None

    def _extract_invalid_namespace(self, call, longest_valid_prefix):
        parts = call.split('.')
        valid_parts_count = len(longest_valid_prefix.split('.'))
        return '.'.join(parts[:valid_parts_count + 1])
