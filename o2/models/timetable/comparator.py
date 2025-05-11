"""COMPARATOR enum for defining comparison operations."""

from enum import Enum


class COMPARATOR(str, Enum):
    """Different types of comparators."""

    LESS_THEN = "<"
    LESS_THEN_OR_EQUAL = "<="
    GREATER_THEN = ">"
    GREATER_THEN_OR_EQUAL = ">="
    EQUAL = "="
