"""Enhanced shlex implementation for detecting unquoted special characters."""

import io
import shlex
from typing import Iterator, List, Optional, Set, Union


class AdvancedToken(str):
    """A string subclass that tracks quoting status and unquoted special characters."""

    is_fully_quoted: "bool"
    unquoted_specials: "Set[str]"
    start_offset: "int"
    end_offset: "int"
    line_num: "int"

    def __new__(
        cls,
        value: str,
        is_fully_quoted: bool,
        unquoted_specials: Set[str],
        start_offset: int,
        end_offset: int,
        line_num: int,
    ) -> "AdvancedToken":
        instance = super(AdvancedToken, cls).__new__(cls, value)
        instance.is_fully_quoted = is_fully_quoted
        instance.unquoted_specials = unquoted_specials
        instance.start_offset = start_offset
        instance.end_offset = end_offset
        instance.line_num = line_num
        return instance


class EnhancedShlex(shlex.shlex):
    """A shlex subclass that detects quoting and unquoted special characters."""

    def __init__(
        self,
        instream: Union[str, io.StringIO],
        posix: bool = True,
        target_chars: Optional[List[str]] = None,
        punctuation_chars: Union[bool, str] = False,
    ) -> None:
        # Save a clean copy of the entire source string for our parallel scanner
        if isinstance(instream, str):
            self.source_str: str = instream
            instream = io.StringIO(instream)
        else:
            self.source_str = instream.read()
            instream = io.StringIO(self.source_str)

        super(EnhancedShlex, self).__init__(
            instream, posix=posix, punctuation_chars=punctuation_chars
        )
        self.target_chars: Set[str] = set(target_chars or [])
        self.source_ptr: int = 0

        if "#" in self.target_chars:
            self.commenters = ""

    def read_token(self) -> Optional[AdvancedToken]:
        """Read a token and determine its quoting status."""
        raw_token: Optional[str] = super(EnhancedShlex, self).read_token()
        if raw_token is None:
            return None

        # 1. Advance our parallel pointer past leading whitespace or comments
        while self.source_ptr < len(self.source_str):
            ch = self.source_str[self.source_ptr]
            if ch in self.whitespace:
                self.source_ptr += 1
            elif ch in self.commenters:
                while (
                    self.source_ptr < len(self.source_str)
                    and self.source_str[self.source_ptr] != "\n"
                ):
                    self.source_ptr += 1
                self.source_ptr += 1
            else:
                break

        start_ptr = self.source_ptr
        unquoted_specials: Set[str] = set()
        current_quote: Optional[str] = None
        escaped: bool = False
        escape_char: Optional[str] = "\\" if getattr(self, "posix", True) else None
        match_idx = 0
        is_ansi_c_quote: bool = False
        brace_level = 0

        # 2. Reconstruct the literal token representation from the raw source
        while self.source_ptr < len(self.source_str):
            if match_idx == len(raw_token) and current_quote is None and not escaped and brace_level == 0:
                # We've matched all characters. Should we stop?
                # Punctuation tokens are always single-entity in our target_chars.
                if raw_token in self.target_chars:
                    break

                # For words, we only continue if the very next character is a quote
                # (to handle adjacent quoted strings like "abc"'def').
                # BUT ONLY if raw_token didn't end with a punctuation character,
                # which shlex would have split.
                if (
                    self.source_ptr >= len(self.source_str)
                    or self.source_str[self.source_ptr] not in self.quotes
                    or (raw_token and raw_token[-1] in self.target_chars)
                ):
                    break

            ch = self.source_str[self.source_ptr]

            if escaped:
                escaped = False
                if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                    match_idx += 1
                self.source_ptr += 1
                continue

            # Check for ANSI-C quoting: $'...' or Dollar quoting: $"..."
            # It can start at the beginning of a token or after a $
            if not current_quote and not escaped and ch in self.quotes:
                if match_idx > 0 and raw_token[match_idx - 1] == "$":
                    is_ansi_c_quote = (ch == "'")
                    current_quote = ch
                    self.source_ptr += 1
                    continue

            # Only treat backslash as escape when NOT inside regular single quotes
            # (inside regular single quotes, backslash is always literal in shell)
            # However, inside ANSI-C quotes ($'...'), backslash IS an escape char
            if (
                escape_char
                and ch == escape_char
                and (current_quote != "'" or is_ansi_c_quote)
            ):
                escaped = True
                self.source_ptr += 1
                continue

            if current_quote:
                if ch == current_quote:
                    current_quote = None
                    is_ansi_c_quote = False
                else:
                    if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                        match_idx += 1
                self.source_ptr += 1
            else:
                if ch in self.quotes:
                    current_quote = ch
                    self.source_ptr += 1
                else:
                    # Track brace level for expansions like ${...}
                    if ch == "$" and self.source_ptr + 1 < len(self.source_str) and self.source_str[self.source_ptr + 1] == "{":
                        if brace_level == 0 and match_idx < len(raw_token) and ch == raw_token[match_idx]:
                             # If we are starting an expansion, and it's part of THIS token
                             pass
                        else:
                             # Expansion might be a new token in shlex
                             if match_idx == len(raw_token):
                                 break

                        brace_level += 1
                        # Consume the ${
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                        self.source_ptr += 1
                        ch = self.source_str[self.source_ptr]
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                        self.source_ptr += 1
                        continue

                    if ch == "}" and brace_level > 0:
                        brace_level -= 1
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                        self.source_ptr += 1
                        continue

                    if ch in self.target_chars:
                        if brace_level == 0:
                            if match_idx == 0 and ch != raw_token[0]:
                                break
                            unquoted_specials.add(ch)
                        # If brace_level > 0, we don't treat it as unquoted special

                    if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                        match_idx += 1
                    else:
                        # If we are NOT matching raw_token, we should stop if we are at brace_level 0
                        if brace_level == 0:
                            break

                    self.source_ptr += 1

        # 3. Explicitly verify if the original text was fully wrapped in quotes
        literal_len = self.source_ptr - start_ptr
        first_char = self.source_str[start_ptr] if literal_len > 0 else ""

        # Determine if it's fully quoted, considering $ prefix for ANSI-C/Dollar quotes
        if first_char == "$" and literal_len > 1:
            second_char = self.source_str[start_ptr + 1]
            is_fully_quoted = (second_char in self.quotes) and (
                literal_len == len(raw_token) + 2
            )
        else:
            is_fully_quoted = (first_char in self.quotes) and (
                literal_len == len(raw_token) + 2
            )

        # 4. Calculate line number manually for accuracy
        # We count \n and \v (which acts as a line terminator in our linter)
        line_num = (
            self.source_str.count("\n", 0, start_ptr)
            + self.source_str.count("\x0b", 0, start_ptr)
            + 1
        )

        # Workaround for shlex behavior on $'...' and $"..."
        # If we have over-consumed the literal token compared to raw_token
        # and raw_token is just "$", it means shlex has already split it
        # but our reconstruction merged it.
        if raw_token == "$" and literal_len > 1:
            # We must backtrack source_ptr and re-evaluate literal_len
            self.source_ptr = start_ptr + 1
            literal_len = 1
            is_fully_quoted = False

        return AdvancedToken(
            raw_token,
            is_fully_quoted,
            unquoted_specials,
            start_ptr,
            self.source_ptr,
            line_num,
        )

    def __next__(self) -> AdvancedToken:
        token = self.read_token()
        if token is None:
            raise StopIteration
        return token

    def __iter__(self) -> Iterator[AdvancedToken]:  # type: ignore[override]
        return self

    def skip_to_newline(self) -> None:
        """Advance the lexer to the next newline character."""
        while self.source_ptr < len(self.source_str):
            ch = self.source_str[self.source_ptr]
            self.source_ptr += 1
            if ch == "\n":
                break
        # Synchronize shlex internal state
        if hasattr(self.instream, "seek"):
            self.instream.seek(self.source_ptr)
