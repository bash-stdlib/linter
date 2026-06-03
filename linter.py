import re
import sys
import json
import difflib
from stdlib_html.fetcher import HTMLFetcher
from cache import save_cache, load_cache
from models import LinterError
from cli import parse_args

def validate_call(call, functions, namespaces):
    if call in functions:
        return True, None

    if call in namespaces:
        return False, f"'{call}' is a namespace, not a function."

    parts = call.split('.')
    # Try to find the longest valid namespace prefix
    longest_prefix = None
    for i in range(len(parts) - 1, 0, -1):
        prefix = '.'.join(parts[:i])
        if prefix in namespaces:
            longest_prefix = prefix
            break

    if longest_prefix:
        # If the prefix is everything except the last part, it's an invalid function in a valid namespace
        if longest_prefix == '.'.join(parts[:-1]):
            msg = f"Invalid function '{call}' in valid namespace '{longest_prefix}'."
            # Try to find a suggestion
            possible_funcs = [f for f in functions if f.startswith(longest_prefix + ".")]
            suggestions = difflib.get_close_matches(call, possible_funcs, n=1)
            if suggestions:
                msg += f" Did you mean '{suggestions[0]}'?"
            return False, msg
        else:
            # Otherwise, the part after the longest_prefix is an invalid namespace
            invalid_ns = '.'.join(parts[:len(longest_prefix.split('.')) + 1])
            return False, f"Invalid namespace '{invalid_ns}'."

    return False, f"Invalid namespace or function '{call}'."

def lint_file(filepath, metadata):
    functions = set(metadata['functions'])
    namespaces = set(metadata['namespaces'])
    errors = []

    stdlib_re = re.compile(r'\b(stdlib\.[a-z0-9._]+)\b')

    try:
        with open(filepath, 'r') as f:
            content = f.read()

        for match in stdlib_re.finditer(content):
            call = match.group(1)
            if call.endswith('.'):
                call = call[:-1]

            start_pos = match.start()

            line_no = content.count('\n', 0, start_pos) + 1
            last_newline = content.rfind('\n', 0, start_pos)
            column_no = start_pos - last_newline if last_newline != -1 else start_pos + 1

            is_valid, message = validate_call(call, functions, namespaces)
            if not is_valid:
                errors.append(LinterError(
                    file=filepath,
                    line=line_no,
                    column=column_no,
                    message=message,
                    match=call
                ))
    except Exception as e:
        errors.append(LinterError(
            file=filepath,
            line=0,
            column=0,
            message=f"Failed to read file: {e}",
            match=""
        ))

    return errors

def main():
    parser, args = parse_args()

    if args.rebuild:
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch_stdlib_metadata()
        if metadata:
            save_cache(metadata)
        return

    if not args.check:
        parser.print_help()
        return

    metadata = load_cache()
    if not metadata:
        fetcher = HTMLFetcher()
        metadata = fetcher.fetch_stdlib_metadata()
        if metadata:
            save_cache(metadata)
        else:
            print("Error: Cache is empty and failed to fetch documentation.", file=sys.stderr)
            sys.exit(1)

    all_errors = []
    for filepath in args.check:
        all_errors.extend(lint_file(filepath, metadata))

    print(json.dumps([e.to_dict() for e in all_errors], indent=2))
    if all_errors:
        sys.exit(1)

if __name__ == "__main__":
    main()
