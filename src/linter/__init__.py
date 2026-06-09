"""Core linter logic for validating bash-stdlib function calls."""

import os
import re
from typing import TYPE_CHECKING, Any, List, Optional

from errors import STD000
from linter.discovery_pipeline import DiscoveryPipeline
from linter.state.file_state import FileLinterState
from linter.state.global_state import GlobalLinterState
from linter.validation_pipeline import ValidationPipeline
from parsers import BashArgumentsParser
from parsers.transformers import LineContinuationTransformer

if TYPE_CHECKING:
    from typing import Pattern

    from errors.base import LinterErrorBase


class Linter:
    def __init__(
        self,
        metadata: "Any",
        ignored_codes: "Optional[List[str]]" = None,
        appendum: "Optional[List[str]]" = None,
    ) -> "None":
        self.global_state = GlobalLinterState(metadata, ignored_codes, appendum)
        self.stdlib_call_pattern: "Pattern[str]" = self._build_call_pattern()
        self.argument_parser = BashArgumentsParser()
        self.line_continuation_transformer = LineContinuationTransformer()

    def lint(self, filepath: "str") -> "List[LinterErrorBase]":
        self.file_state = FileLinterState()
        filepath = os.path.abspath(filepath)

        try:
            with open(filepath, "r") as f:
                raw_content = f.read()
                file_content = self.line_continuation_transformer.transform(
                    raw_content, preserve_lines=True
                )
        except Exception as e:
            if not self._is_ignored("STD000", 1):
                return [STD000(filepath, str(e))]
            return []

        # Discovery Pass
        discovery = DiscoveryPipeline(self.global_state, self.file_state)
        discovery.run(file_content)

        # Validation Pass
        validation = ValidationPipeline(
            self.global_state,
            self.file_state,
            self.stdlib_call_pattern,
            self.argument_parser,
        )
        return validation.run(file_content, filepath)

    def _build_call_pattern(self) -> "Pattern[str]":
        dot_roots = set()
        underscore_roots = set()

        for name in (
            self.global_state.functions
            | self.global_state.namespaces
            | self.global_state.appendum
        ):
            if name.startswith("_"):
                # Handle cases like _testing.func or _testing.example
                dot_roots.add(name.split(".")[0])
            elif "." in name:
                dot_roots.add(name.split(".")[0])
            elif "_" in name:
                underscore_roots.add(name.split("_")[0] + "_")
            elif name.startswith("@"):
                # Always treat names starting with @ as dot-based roots
                dot_roots.add(name.split(".")[0])
            else:
                dot_roots.add(name)

        sorted_dot_roots = sorted(list(dot_roots), key=len, reverse=True)
        sorted_underscore_roots = sorted(list(underscore_roots), key=len, reverse=True)

        # Combine all roots into a single pattern.
        # dot_roots are names that should only match if they are either exactly the name
        # or followed by a dot (to avoid matching things like @parametrize_with_errors).
        # underscore_roots (like assert_) can be followed by anything.

        dot_pattern = (
            r"(?:{})(?:\.[a-z0-9._]*)?".format(
                "|".join(re.escape(r) for r in sorted_dot_roots)
            )
            if sorted_dot_roots
            else r"(?!)"
        )
        underscore_pattern = (
            r"(?:{})[a-z0-9._]*".format(
                "|".join(re.escape(r) for r in sorted_underscore_roots)
            )
            if sorted_underscore_roots
            else r"(?!)"
        )

        pattern = r"(?<!\w)({}|{})(?![a-z0-9._])".format(
            dot_pattern, underscore_pattern
        )

        return re.compile(pattern)

    def _is_ignored(
        self,
        code: str,
        line: int,
    ) -> bool:
        code = code.upper()
        if code in self.global_state.ignored_codes:
            return True
        if self.file_state.is_ignored(code, line):
            return True
        return False
