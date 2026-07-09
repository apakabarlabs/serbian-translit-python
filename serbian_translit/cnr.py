"""Montenegrin (`cnr`) script conversion.

Same base engine as Serbian plus the Montenegrin-only letters ``ś``/``ź``
(Latin) and their Cyrillic counterparts ``с́``/``з́`` (base letter + combining
acute U+0301 — no precomposed codepoints exist).
"""

from __future__ import annotations

from ._engine import _load_rule

_LAT_TO_CYR = _load_rule("cnr-latn", "cnr-cyrl")
_CYR_TO_LAT = _load_rule("cnr-cyrl", "cnr-latn")


def to_cyr(text: str) -> str:
    """Montenegrin Latin → Cyrillic."""
    return _LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    """Montenegrin Cyrillic → Latin."""
    return _CYR_TO_LAT.apply(text)
