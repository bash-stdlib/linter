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
                # if it is part of punctuation_chars and if raw_token starts with it
                # we don't break yet if we are looking for only punctuation
                break

        start_ptr = self.source_ptr
        unquoted_specials: Set[str] = set()
        current_quote: Optional[str] = None
        escaped: bool = False
        escape_char: Optional[str] = "\\" if getattr(self, "posix", True) else None
        match_idx = 0

        # 2. Reconstruct the literal token representation from the raw source
        while self.source_ptr < len(self.source_str):
            if (
                match_idx == len(raw_token)
                and current_quote is None
                and not escaped
                and (
                    self.source_ptr >= len(self.source_str)
                    or self.source_str[self.source_ptr] not in self.quotes
                )
            ):
                break

            ch = self.source_str[self.source_ptr]

            if escaped:
                escaped = False
                if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                    match_idx += 1
                self.source_ptr += 1
                continue

            if escape_char and ch == escape_char:
                escaped = True
                self.source_ptr += 1
                continue

            if current_quote:
                if ch == current_quote:
                    current_quote = None
                else:
                    if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                        match_idx += 1
                self.source_ptr += 1
            else:
                if ch in self.quotes:
                    current_quote = ch
                    self.source_ptr += 1
                else:
                    if ch in self.target_chars:
                        unquoted_specials.add(ch)
                    if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                        match_idx += 1
                    self.source_ptr += 1

        # 3. Explicitly verify if the original text was fully wrapped in quotes
        literal_len = self.source_ptr - start_ptr
        first_char = self.source_str[start_ptr] if literal_len > 0 else ""
        is_fully_quoted = (first_char in self.quotes) and (
            literal_len == len(raw_token) + 2
        )

        return AdvancedToken(
            raw_token,
            is_fully_quoted,
            unquoted_specials,
            start_ptr,
            self.source_ptr,
            self.lineno,
        )

    def __next__(self) -> AdvancedToken:
        token = self.read_token()
        if token is None:
            raise StopIteration
        return token

    def __iter__(self) -> Iterator[AdvancedToken]:  # type: ignore[override]
        return self
