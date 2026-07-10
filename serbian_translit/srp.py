"""Serbian (`srp`) script conversion — Cyrillic ↔ Latin."""

from __future__ import annotations

from ._rule import load

_LAT_TO_CYR = load("srp-latn", "srp-cyrl")
_CYR_TO_LAT = load("srp-cyrl", "srp-latn")


def to_cyr(text: str) -> str:
    return _LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    return _CYR_TO_LAT.apply(text)
