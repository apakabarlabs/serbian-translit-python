"""Word-level case detection and reapplication.

Whole-word case is the invariant used across the engine: after lowering
the word for lookup, the same pattern is reapplied at the end.
"""

from __future__ import annotations

from enum import Enum


class CasePattern(Enum):
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    MIXED = "mixed"


def detect(text: str) -> CasePattern:
    if text.islower():
        return CasePattern.LOWER
    if text.isupper():
        return CasePattern.UPPER
    if len(text) > 1 and text[0].isupper() and text[1:].islower():
        return CasePattern.TITLE
    return CasePattern.MIXED


def apply(text: str, pattern: CasePattern) -> str:
    match pattern:
        case CasePattern.LOWER:
            return text.lower()
        case CasePattern.UPPER:
            return text.upper()
        case CasePattern.TITLE:
            return text[0].upper() + text[1:].lower()
        case CasePattern.MIXED:
            return text
