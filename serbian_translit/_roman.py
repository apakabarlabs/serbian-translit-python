"""Roman-numeral detection for the transliteration passthrough."""

from __future__ import annotations

import re

# The naive `[IVXLCDM]{2,}` fires on Serbian pronouns and common words
# that happen to share the alphabet (`MI`, `LI`, `CIVIL`); canonical
# form is the whole point.
_CANONICAL = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")


def is_numeral(word: str) -> bool:
    # A single letter (`I`, `V`, `X`) is a word in this context, not a numeral.
    return len(word) >= 2 and bool(_CANONICAL.match(word))
