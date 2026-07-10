"""Serbian (`srp`) script conversion, Cyrillic ↔ Latin."""

from __future__ import annotations

from .table import SRP_CYR_TO_LAT, SRP_LAT_TO_CYR


def to_cyr(text: str) -> str:
    """Serbian Latin → Cyrillic."""
    return SRP_LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    """Serbian Cyrillic → Latin."""
    return SRP_CYR_TO_LAT.apply(text)
