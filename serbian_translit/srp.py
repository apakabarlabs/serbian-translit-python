"""Serbian (`srp`) script conversion.

Canonical shorthand for the Serbian language. Both directions preserve case
(``Njujork`` → ``Њујорк``, ``ЊУЈОРК`` → ``NJUJORK``), keep Roman numerals in
Latin, skip words containing non-native letters (``w``, ``x``, ``y``, ``q``),
and pass quoted regions through verbatim.
"""

from __future__ import annotations

from ._engine import _load_rule

_LAT_TO_CYR = _load_rule("srp-latn", "srp-cyrl")
_CYR_TO_LAT = _load_rule("srp-cyrl", "srp-latn")


def to_cyr(text: str) -> str:
    """Serbian Latin → Cyrillic."""
    return _LAT_TO_CYR.apply(text)


def to_lat(text: str) -> str:
    """Serbian Cyrillic → Latin."""
    return _CYR_TO_LAT.apply(text)
