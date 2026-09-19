"""Roman-numeral detection for the transliteration passthrough."""

from __future__ import annotations

import re

_CANONICAL = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")

_MIN_NUMERAL_LEN = 2


def is_numeral(word: str) -> bool:
    return len(word) >= _MIN_NUMERAL_LEN and bool(_CANONICAL.match(word))
