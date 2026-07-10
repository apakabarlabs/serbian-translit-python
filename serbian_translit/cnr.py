"""Montenegrin (`cnr`) script conversion: same engine as Serbian plus
the language-only letters ``ś``/``ź`` and their Cyrillic decompositions.
"""

from __future__ import annotations

from ._rule import CNR_CYR_TO_LAT, CNR_LAT_TO_CYR


def to_cyr(text: str) -> str:
    """Montenegrin Latin → Cyrillic."""
    return CNR_LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    """Montenegrin Cyrillic → Latin."""
    return CNR_CYR_TO_LAT.apply(text)
