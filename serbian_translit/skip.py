"""Word-level policies that pass a token through unchanged."""

from __future__ import annotations

from dataclasses import dataclass

from . import roman


@dataclass(frozen=True)
class SkipPolicy:
    non_native_letters: set[str]
    never_roman: set[str]

    def is_foreign(self, word: str) -> bool:
        return bool(self.non_native_letters and self.non_native_letters.intersection(word))

    def is_roman_numeral(self, word: str) -> bool:
        return roman.is_numeral(word) and word.upper() not in self.never_roman
