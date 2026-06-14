"""Enumerations for documentation parsing and metadata storage."""

import enum


class FunctionArgumentType(enum.Enum):
    """Supported data types for function arguments and variables."""

    ARRAY = "array"
    BOOLEAN = "boolean"
    INTEGER = "integer"
    STRING = "string"


class FunctionModifierType(enum.Enum):
    """Modifiers that define the scope or nature of an input."""

    GLOBAL = "global"
    KEYWORD = "keyword"
    RESERVED = "reserved"


class DocumentationIndicator(enum.Enum):
    """Indicators used within documentation to signal specific properties."""

    OPTIONAL = "optional"


class DocumentationSection(enum.Enum):
    """Headings for specific documentation sections."""

    ARGUMENTS = "Arguments"
    VARIABLES_SET = "Variables set"
