"""Enumerations for documentation parsing and metadata storage."""

import enum
from typing import Optional, Type, TypeVar

T = TypeVar("T", bound="EnumBase")


class EnumBase(enum.Enum):
    """Base class for enums with helper methods."""

    @classmethod
    def from_str(cls: Type[T], value: "Optional[str]") -> "Optional[T]":
        """Convert a string to an enum member."""
        if value is None:
            return None
        value = value.lower()
        for member in cls:
            if member.value == value:
                return member
        return None


class FunctionArgumentType(EnumBase):
    """Supported data types for function arguments and variables."""

    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"


class FunctionModifierType(EnumBase):
    """Modifiers that define the scope or nature of an input."""

    GLOBAL = "global"
    KEYWORD = "keyword"
    RESERVED = "reserved"


class DocumentationIndicator(EnumBase):
    """Indicators used within documentation to signal specific properties."""

    OPTIONAL = "optional"


class DocumentationSection(EnumBase):
    """Headings for specific documentation sections."""

    ARGUMENTS = "Arguments"
    VARIABLES_SET = "Variables set"

    @classmethod
    def from_str(cls: Type["DocumentationSection"], value: "Optional[str]") -> "Optional[DocumentationSection]":
        """Convert a string to an enum member (case-sensitive for sections)."""
        if value is None:
            return None
        for member in cls:
            if member.value == value:
                return member
        return None
