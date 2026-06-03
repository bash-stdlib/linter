"""Enhanced shlex implementation for detecting unquoted special characters."""

import io
import shlex
from typing import Iterator, List, NamedTuple, Optional, Set, Union


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


class TokenScanState(NamedTuple):
    """State tracker for scanning a token through source."""
    char_index: int
    unquoted_specials: Set[str]
    current_quote: Optional[str]
    is_escaped: bool
    is_ansi_c_quote: bool


class EnhancedShlex(shlex.shlex):
    """A shlex subclass that detects quoting and unquoted special characters."""

    def __init__(
        self,
        instream: Union[str, io.StringIO],
        posix: bool = True,
        target_chars: Optional[List[str]] = None,
        punctuation_chars: Union[bool, str] = False,
    ) -> None:
        self.source_str: str = self._load_source(instream)
        
        # Protect ANSI-C quotes: $'...' and $"..." become placeholders
        self._protected_ansi_c: "List[tuple[str, str]]" = []
        # Protect command substitutions with quotes to prevent shlex from splitting on special chars
        self._protected_cmd_subs: "List[tuple[str, str]]" = []
        self._offset_map: "List[int]" = []
        self._protected_str: str = self._handle_ansi_c_quotes(self.source_str)
        self._protected_str = self._protect_cmd_subs_with_quotes(self._protected_str)
        
        super(EnhancedShlex, self).__init__(
            io.StringIO(self._protected_str), posix=posix, punctuation_chars=punctuation_chars
        )
        self.target_chars: Set[str] = set(target_chars or [])
        self.source_ptr: int = 0

        if "#" in self.target_chars:
            self.commenters = ""

    def _load_source(self, instream: Union[str, io.StringIO]) -> str:
        """Load source from string or file-like object."""
        if isinstance(instream, str):
            return instream
        return instream.read()

    def read_token(self) -> Optional[AdvancedToken]:
        """Read a token and determine its quoting status."""
        raw_token: Optional[str] = super(EnhancedShlex, self).read_token()
        if raw_token is None:
            return None
        
        restored_token = self._restore_ansi_c_quotes(raw_token)
        restored_token = self._restore_cmd_subs_with_quotes(restored_token)
        self._skip_leading_whitespace_and_comments()
        
        token_start = self.source_ptr
        state = self._scan_token_in_source(raw_token)
        
        original_start = self._map_protected_to_original_offset(token_start)
        original_end = self._map_protected_to_original_offset(self.source_ptr)
        is_fully_quoted = self._is_token_fully_quoted(restored_token, original_start, original_end)
        line_num = self._calculate_line_number(original_start)
        
        return AdvancedToken(
            restored_token,
            is_fully_quoted,
            state.unquoted_specials,
            original_start,
            original_end,
            line_num,
        )

    def _should_stop_scanning(self, state: TokenScanState, raw_token: str, protected_src: str) -> bool:
        """Check if we've finished matching the token."""
        if state.char_index != len(raw_token) or state.current_quote or state.is_escaped:
            return False
        
        # Punctuation tokens (single or multi-char like <() are single entities
        if all(c in self.target_chars for c in raw_token):
            return True
        
        # Words continue if next char is a quote
        if self.source_ptr >= len(protected_src) or protected_src[self.source_ptr] not in self.quotes:
            return True
        
        return False

    def _handle_escaped_char(self, state: TokenScanState, char: str, raw_token: str) -> TokenScanState:
        """Handle a character that follows an escape sequence."""
        if state.char_index < len(raw_token) and char == raw_token[state.char_index]:
            char_index = state.char_index + 1
        else:
            char_index = state.char_index
        
        return TokenScanState(
            char_index=char_index,
            unquoted_specials=state.unquoted_specials,
            current_quote=state.current_quote,
            is_escaped=False,
            is_ansi_c_quote=state.is_ansi_c_quote,
        )

    def _handle_quoted_char(self, state: TokenScanState, char: str, raw_token: str) -> TokenScanState:
        """Handle a character inside a quote."""
        if char == state.current_quote:
            return TokenScanState(
                char_index=state.char_index,
                unquoted_specials=state.unquoted_specials,
                current_quote=None,
                is_escaped=False,
                is_ansi_c_quote=False,
            )
        
        if state.char_index < len(raw_token) and char == raw_token[state.char_index]:
            char_index = state.char_index + 1
        else:
            char_index = state.char_index
        
        return TokenScanState(
            char_index=char_index,
            unquoted_specials=state.unquoted_specials,
            current_quote=state.current_quote,
            is_escaped=False,
            is_ansi_c_quote=state.is_ansi_c_quote,
        )

    def _handle_unquoted_char(
        self,
        state: TokenScanState,
        char: str,
        raw_token: str,
        escape_char: Optional[str],
        protected_src: str,
    ) -> TokenScanState:
        """Handle a character outside quotes."""
        # Check for ANSI-C quote start
        if self._is_ansi_c_quote_in_token(state, char, raw_token):
            return TokenScanState(
                char_index=state.char_index,
                unquoted_specials=state.unquoted_specials,
                current_quote="'",
                is_escaped=False,
                is_ansi_c_quote=True,
            )
        
        # Check for escape char
        if escape_char and char == escape_char:
            return TokenScanState(
                char_index=state.char_index,
                unquoted_specials=state.unquoted_specials,
                current_quote=state.current_quote,
                is_escaped=True,
                is_ansi_c_quote=state.is_ansi_c_quote,
            )
        
        # Check for quote start
        if char in self.quotes:
            return TokenScanState(
                char_index=state.char_index,
                unquoted_specials=state.unquoted_specials,
                current_quote=char,
                is_escaped=False,
                is_ansi_c_quote=state.is_ansi_c_quote,
            )
        
        # Collect unquoted special chars
        new_specials = state.unquoted_specials.copy()
        if char in self.target_chars:
            if state.char_index == 0 and char != raw_token[0]:
                # This char doesn't match the start of raw_token, stop here
                return state
            new_specials.add(char)
        
        # Match char if it's in the raw token
        if state.char_index < len(raw_token) and char == raw_token[state.char_index]:
            char_index = state.char_index + 1
        else:
            char_index = state.char_index
        
        return TokenScanState(
            char_index=char_index,
            unquoted_specials=new_specials,
            current_quote=state.current_quote,
            is_escaped=False,
            is_ansi_c_quote=state.is_ansi_c_quote,
        )

    def _handle_ansi_c_quotes(self, content: str) -> str:
        """Protect ANSI-C quotes with placeholders and offset map."""
        return self._protect_ansi_c_quotes(content)

    def _skip_leading_whitespace_and_comments(self) -> None:
        """Advance past leading whitespace or comments in protected source."""
        protected_src = self._protected_str
        
        while self.source_ptr < len(protected_src):
            char = protected_src[self.source_ptr]
            
            if char in self.whitespace:
                self.source_ptr += 1
            elif char in self.commenters:
                self._skip_comment()
            else:
                break

    def _skip_comment(self) -> None:
        """Skip from current position to end of line."""
        protected_src = self._protected_str
        
        while self.source_ptr < len(protected_src) and protected_src[self.source_ptr] != "\n":
            self.source_ptr += 1
        
        if self.source_ptr < len(protected_src):
            self.source_ptr += 1

    def _scan_token_in_source(self, raw_token: str) -> TokenScanState:
        """Scan through source to match token and collect metadata."""
        protected_src = self._protected_str
        escape_char = "\\" if getattr(self, "posix", True) else None
        
        state = TokenScanState(
            char_index=0,
            unquoted_specials=set(),
            current_quote=None,
            is_escaped=False,
            is_ansi_c_quote=False,
        )
        
        # Handle empty tokens (e.g., '' or "")
        if not raw_token:
            if self.source_ptr < len(protected_src) and protected_src[self.source_ptr] in self.quotes:
                quote_char = protected_src[self.source_ptr]
                self.source_ptr += 1
                # Skip to closing quote
                while self.source_ptr < len(protected_src) and protected_src[self.source_ptr] != quote_char:
                    self.source_ptr += 1
                if self.source_ptr < len(protected_src):
                    self.source_ptr += 1
            return state
        
        while self.source_ptr < len(protected_src):
            if self._should_stop_scanning(state, raw_token, protected_src):
                break
            
            char = protected_src[self.source_ptr]
            
            if state.is_escaped:
                state = self._handle_escaped_char(state, char, raw_token)
            elif state.current_quote:
                state = self._handle_quoted_char(state, char, raw_token)
            else:
                state = self._handle_unquoted_char(state, char, raw_token, escape_char, protected_src)
            
            self.source_ptr += 1
        
        return state

    def _map_protected_to_original_offset(self, protected_offset: int) -> int:
        """Map protected string offset to original string offset."""
        if not self._offset_map or protected_offset >= len(self._offset_map):
            if self._offset_map:
                return self._offset_map[-1] + 1
            return protected_offset
        return self._offset_map[protected_offset] if protected_offset < len(self._offset_map) else len(self.source_str)

    def _is_token_fully_quoted(self, token: str, start_offset: int, end_offset: int) -> bool:
        """Check if token is completely wrapped in quotes."""
        if start_offset >= len(self.source_str):
            return False
        
        first_char = self.source_str[start_offset]
        token_len = end_offset - start_offset
        
        return (first_char in self.quotes) and (token_len == len(token) + 2)

    def _calculate_line_number(self, offset: int) -> int:
        """Calculate line number at given offset (1-indexed)."""
        return (
            self.source_str.count("\n", 0, offset)
            + self.source_str.count("\x0b", 0, offset)
            + 1
        )

    def _restore_ansi_c_quotes(self, token: str) -> str:
        """Restore ANSI-C quotes in a token that was protected during parsing."""
        result = token
        for placeholder, original in self._protected_ansi_c:
            result = result.replace(placeholder, original)
        return result

    def _restore_cmd_subs_with_quotes(self, token: str) -> str:
        """Restore command substitutions that were protected."""
        result = token
        for placeholder, original in self._protected_cmd_subs:
            result = result.replace(placeholder, original)
        return result

    def _protect_cmd_subs_with_quotes(self, content: str) -> str:
        """Protect command substitutions that contain quotes.
        
        When a command substitution $(...) contains quoted strings with special
        characters, shlex may incorrectly split on those characters. By protecting
        these command substitutions before tokenization, we prevent shlex from
        treating special chars inside the quotes as token boundaries.
        """
        result: List[str] = []
        pos = 0
        placeholder_idx = 0
        
        while pos < len(content):
            # Look for command substitution: $(...)
            if content[pos:pos+2] == '$(':
                start = pos
                pos += 2
                depth = 1
                has_quotes = False
                
                # Scan to find matching closing paren, tracking quotes
                while pos < len(content) and depth > 0:
                    if content[pos] == '\\' and pos + 1 < len(content):
                        # Skip escaped character
                        pos += 2
                    elif content[pos] in ('"', "'"):
                        has_quotes = True
                        pos += 1
                    elif content[pos] == '(':
                        depth += 1
                        pos += 1
                    elif content[pos] == ')':
                        depth -= 1
                        pos += 1
                    else:
                        pos += 1
                
                # If this command sub has quotes, protect it
                if has_quotes:
                    cmd_sub = content[start:pos]
                    placeholder = "__CMDSUB_{0}__".format(placeholder_idx)
                    self._protected_cmd_subs.append((placeholder, cmd_sub))
                    result.append(placeholder)
                    placeholder_idx += 1
                else:
                    result.append(content[start:pos])
            else:
                result.append(content[pos])
                pos += 1
        
        return "".join(result)


    def _protect_ansi_c_quotes(self, content: str) -> str:
        """Replace ANSI-C quotes with placeholders and build offset map."""
        result: List[str] = []
        offset_map: List[int] = []
        pos = 0
        placeholder_idx = 0
        original_pos = 0
        
        while pos < len(content):
            if self._is_ansi_c_quote_start(content, pos):
                quote_char = content[pos + 1]
                close_pos = self._find_ansi_c_quote_end(content, pos + 2, quote_char)
                
                if close_pos is not None:
                    # Found complete ANSI-C quote
                    original_quote = content[pos:close_pos + 1]
                    placeholder = "__ANSI_C_{0}__".format(placeholder_idx)
                    self._protected_ansi_c.append((placeholder, original_quote))
                    result.append(placeholder)
                    
                    # Record offset mapping for each char in placeholder
                    for _ in range(len(placeholder)):
                        offset_map.append(original_pos)
                    original_pos += len(original_quote)
                    
                    pos = close_pos + 1
                    placeholder_idx += 1
                else:
                    # Unclosed quote - append as-is
                    result.append(content[pos])
                    offset_map.append(original_pos)
                    original_pos += 1
                    pos += 1
            else:
                # Regular character
                result.append(content[pos])
                offset_map.append(original_pos)
                original_pos += 1
                pos += 1
        
        self._offset_map = offset_map
        return "".join(result)

    def _is_ansi_c_quote_start(self, text: str, pos: int) -> bool:
        """Check if position is the start of an ANSI-C quote ($' or $\")."""
        return (
            pos < len(text) - 1
            and text[pos] == "$"
            and text[pos + 1] in ("'", '"')
        )

    def _find_ansi_c_quote_end(self, content: str, start: int, quote_char: str) -> "Optional[int]":
        """Find the closing quote of an ANSI-C quote."""
        pos = start
        while pos < len(content):
            current_char = content[pos]
            
            if self._should_skip_escaped_char(content, pos, quote_char):
                pos += 2
                continue
            
            if current_char == quote_char:
                return pos
            
            pos += 1
        
        return None

    def _should_skip_escaped_char(self, text: str, pos: int, quote_char: str) -> bool:
        """Check if current position has an escape sequence we should skip."""
        if pos >= len(text) - 1 or text[pos] != "\\":
            return False
        
        next_char = text[pos + 1]
        
        if quote_char == "'":
            # In $'...', backslash escapes any next character
            return True
        else:
            # In $"...", only \$ and \" are escape sequences
            return next_char in ("$", '"')

    def _is_ansi_c_quote_in_token(self, state: TokenScanState, char: str, raw_token: str) -> bool:
        """Check if this is the start of an ANSI-C quote within a token."""
        return (
            not state.current_quote
            and state.char_index > 0
            and raw_token[state.char_index - 1] == "$"
            and char == "'"
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
        # Sync instream with current source_ptr before reading
        if hasattr(self.instream, "seek"):
            self.instream.seek(self.source_ptr)
        line = self.instream.readline()
        self.source_ptr += len(line)

