"""Montenegrin (`cnr`) script conversion — same engine as Serbian plus
the language-only letters ``ś``/``ź`` and their Cyrillic decompositions.
"""

from __future__ import annotations

from ._rule import load

_LAT_TO_CYR = load("cnr-latn", "cnr-cyrl")
_CYR_TO_LAT = load("cnr-cyrl", "cnr-latn")


def to_cyr(text: str) -> str:
    return _LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    return _CYR_TO_LAT.apply(text)
