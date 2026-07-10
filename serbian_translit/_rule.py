"""One source→target script mapping, loaded from ``data/rules.yaml``.

The engine is language-agnostic: everything script-specific (digraphs,
pre-char remaps, extra word-characters, non-native letters,
never_roman blacklist) lives in the YAML file. This module is the
runtime shape of one such entry plus its ``apply()`` method.
"""

from __future__ import annotations

import re
import unicodedata
from pathlib import Path
from typing import TypedDict

import yaml

from . import _case, _roman
from ._protection import ProtectedRegions


class RuleData(TypedDict, total=False):
    source: str
    target: str
    digraphs: dict[str, str]
    pre_char: dict[str, str]
    singles: dict[str, str]
    extras_in_word: str
    non_native_letters: str
    never_roman: list[str]


class _RulesFile(TypedDict):
    rules: list[RuleData]


_DIGRAPH_WIDTH = 2
_SINGLE_WIDTH = 1
_LOOKUP_WIDTHS = (_DIGRAPH_WIDTH, _SINGLE_WIDTH)


class Rule:
    def __init__(self, data: RuleData) -> None:
        self.source: str = data["source"]
        self.target: str = data["target"]
        self.digraphs: dict[str, str] = {k.lower(): v for k, v in data.get("digraphs", {}).items()}
        self.pre_char: dict[str, str] = data.get("pre_char") or {}
        self.singles: dict[str, str] = data.get("singles") or {}
        self.extras_in_word: str = data.get("extras_in_word") or ""
        self.non_native_letters: set[str] = set(data.get("non_native_letters") or "")
        self.never_roman: set[str] = {w.upper() for w in data.get("never_roman") or []}
        self.word_split_re = re.compile(rf"(\s+|[^\w{re.escape(self.extras_in_word)}]+)")

    def apply(self, text: str) -> str:
        # macOS clipboard hands out NFD; the base ASCII would leak through
        # the digraph lookup and drop its combining mark.
        text = unicodedata.normalize("NFC", text)

        protection = ProtectedRegions()
        protected = protection.stash_all(text)

        rendered = "".join(self._convert_part(p) for p in self.word_split_re.split(protected) if p)
        return protection.restore(rendered)

    def _convert_part(self, part: str) -> str:
        # Whitespace/punctuation runs and digit-only chunks pass through;
        # everything with at least one letter goes to the word converter.
        if any(ch.isalpha() for ch in part):
            return self._convert_word(part)
        return part

    def _convert_word(self, word: str) -> str:
        if self._is_foreign_inclusion(word):
            return word
        if self._is_roman_numeral(word):
            return word

        # Ð/Đ and ð/đ collapse before we look at case, so the character
        # count of the word is stable for the case-pattern step.
        word = self._normalise_pre_char(word)

        case = _case.detect(word)
        # A brand or acronym in the middle of prose (`iPhone`, `mRNA`)
        # cannot survive a lowercased conversion; the round-trip loses
        # its casing. Two-char MIXED (`lJ`, `nJ`) is the digraph edge
        # case we do want to convert.
        if case is _case.CasePattern.MIXED and len(word) > _DIGRAPH_WIDTH:
            return word

        mapped = self._map_letters(word.lower())
        return _case.apply(mapped, case)

    def _is_foreign_inclusion(self, word: str) -> bool:
        return bool(self.non_native_letters and self.non_native_letters.intersection(word))

    def _is_roman_numeral(self, word: str) -> bool:
        return _roman.is_numeral(word) and word.upper() not in self.never_roman

    def _normalise_pre_char(self, word: str) -> str:
        if not self.pre_char:
            return word
        return "".join(self.pre_char.get(ch, ch) for ch in word)

    def _map_letters(self, lowered: str) -> str:
        result: list[str] = []
        i = 0
        while i < len(lowered):
            replacement, width = self._match_here(lowered, i)
            result.append(replacement)
            i += width
        return "".join(result)

    def _match_here(self, lowered: str, i: int) -> tuple[str, int]:
        for width in _LOOKUP_WIDTHS:
            if i + width > len(lowered):
                continue
            candidate = lowered[i : i + width]
            if candidate in self.digraphs:
                return self.digraphs[candidate], width
        ch = lowered[i]
        return self.singles.get(ch, ch), 1


def _rules_table() -> dict[tuple[str, str], Rule]:
    path = Path(__file__).parent / "data" / "rules.yaml"
    with path.open(encoding="utf-8") as f:
        data: _RulesFile = yaml.safe_load(f)
    return {(entry["source"], entry["target"]): Rule(entry) for entry in data["rules"]}


_TABLE = _rules_table()

SRP_LAT_TO_CYR = _TABLE["srp-latn", "srp-cyrl"]
SRP_CYR_TO_LAT = _TABLE["srp-cyrl", "srp-latn"]
CNR_LAT_TO_CYR = _TABLE["cnr-latn", "cnr-cyrl"]
CNR_CYR_TO_LAT = _TABLE["cnr-cyrl", "cnr-latn"]
