"""Enhanced shlex implementation for detecting unquoted special characters."""

import io
import shlex
from typing import Iterator, List, Optional, Set, Union


class AdvancedToken(str):
    """A string subclass that tracks quoting status and unquoted special characters."""

    end_offset: "int"
    is_fully_quoted: "bool"
    start_offset: "int"
    unquoted_specials: "Set[str]"

    def __new__(
        cls,
        value: str,
        is_fully_quoted: bool,
        unquoted_specials: Set[str],
        start_offset: int = 0,
        end_offset: int = 0,
    ) -> "AdvancedToken":
        instance = super(AdvancedToken, cls).__new__(cls, value)
        instance.is_fully_quoted = is_fully_quoted
        instance.unquoted_specials = unquoted_specials
        instance.start_offset = start_offset
        instance.end_offset = end_offset
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
        if isinstance(instream, str):
            self.source_str: str = instream
        else:
            self.source_str = instream.read()

        super(EnhancedShlex, self).__init__(
            io.StringIO(self.source_str),
            posix=posix,
            punctuation_chars=punctuation_chars,
        )
        self.target_chars: Set[str] = set(target_chars or [])
        self.source_ptr: int = 0
        self.is_posix: bool = posix

        if "#" in self.target_chars:
            self.commenters = ""

    def read_token(self) -> Optional[AdvancedToken]:
        """Read a token and determine its quoting status and source offsets."""
        raw_token: Optional[str] = super(EnhancedShlex, self).read_token()
        if raw_token is None:
            return None

        # 1. Skip leading whitespace/comments to find the start of the token
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
                if self.source_ptr < len(self.source_str):
                    self.source_ptr += 1
            else:
                break

        start_ptr = self.source_ptr
        unquoted_specials: Set[str] = set()

        # 2. Reconstruction loop to find the end of the token and unquoted specials.
        end_ptr = start_ptr
        current_quote: Optional[str] = None
        escaped: bool = False
        escape_char: Optional[str] = "\\" if self.is_posix else None

        match_idx = 0
        if not self.is_posix:
            end_ptr += len(raw_token)
            for ch in raw_token:
                if ch in self.target_chars:
                    unquoted_specials.add(ch)
            is_fully_quoted = (
                len(raw_token) >= 2
                and raw_token[0] in self.quotes
                and raw_token[-1] == raw_token[0]
            )
        else:
            while end_ptr < len(self.source_str):
                if (
                    match_idx >= len(raw_token)
                    and current_quote is None
                    and not escaped
                ):
                    if (
                        end_ptr < len(self.source_str)
                        and self.source_str[end_ptr] in self.quotes
                    ):
                        pass
                    else:
                        break

                ch = self.source_str[end_ptr]

                if escaped:
                    escaped = False
                    if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                        match_idx += 1
                    end_ptr += 1
                    continue

                if escape_char and ch == escape_char:
                    if current_quote == "'":
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                    else:
                        escaped = True
                    end_ptr += 1
                    continue

                if current_quote:
                    if ch == current_quote:
                        current_quote = None
                    else:
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                    end_ptr += 1
                else:
                    if ch in self.quotes:
                        current_quote = ch
                        end_ptr += 1
                    else:
                        if ch in self.target_chars:
                            unquoted_specials.add(ch)
                        if match_idx < len(raw_token) and ch == raw_token[match_idx]:
                            match_idx += 1
                        end_ptr += 1

        self.source_ptr = end_ptr

        literal_len = end_ptr - start_ptr
        first_char = self.source_str[start_ptr] if literal_len > 0 else ""
        is_fully_quoted = (first_char in self.quotes) and (
            literal_len == len(raw_token) + 2
        )

        return AdvancedToken(
            raw_token,
            is_fully_quoted,
            unquoted_specials,
            start_offset=start_ptr,
            end_offset=end_ptr,
        )

    def __next__(self) -> AdvancedToken:
        token = self.read_token()
        if token is None:
            raise StopIteration
        return token

    def __iter__(self) -> Iterator[AdvancedToken]:  # type: ignore[override]
        return self
