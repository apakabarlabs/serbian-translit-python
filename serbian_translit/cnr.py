"""Montenegrin (`cnr`) script conversion, Cyrillic ↔ Latin."""

from __future__ import annotations

from .table import CNR_CYR_TO_LAT, CNR_LAT_TO_CYR


def to_cyr(text: str) -> str:
    """Montenegrin Latin → Cyrillic."""
    return CNR_LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    """Montenegrin Cyrillic → Latin."""
    return CNR_CYR_TO_LAT.apply(text)
