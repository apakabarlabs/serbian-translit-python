"""Serbian/Montenegrin script conversion driven by a YAML rule table.

The engine is language-agnostic: it plays a source→target mapping from
`data/rules.yaml`. All script-specific facts (which digraphs, which pre-char
remaps, which extra word-characters, which non-native letters) live in the
YAML file, not in this code.

Word-level protection:
  - Text inside paired quotation marks („…" “…” "…" «…») round-trips verbatim.
  - Roman numerals (II, XIV, XX…) stay Latin regardless of direction.
  - A source-Latin word containing any letter in ``non_native_letters`` is
    treated as a foreign inclusion and left untouched.
"""

from __future__ import annotations

import re
from enum import Enum
from pathlib import Path

import yaml


class CasePattern(Enum):
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    MIXED = "mixed"


def _detect_case(text: str) -> CasePattern:
    if text.islower():
        return CasePattern.LOWER
    if text.isupper():
        return CasePattern.UPPER
    if len(text) > 1 and text[0].isupper() and text[1:].islower():
        return CasePattern.TITLE
    return CasePattern.MIXED


def _apply_case(text: str, pattern: CasePattern) -> str:
    if pattern == CasePattern.LOWER:
        return text.lower()
    if pattern == CasePattern.UPPER:
        return text.upper()
    if pattern == CasePattern.TITLE:
        return text[0].upper() + text[1:].lower() if text else text
    return text


_ROMAN_RE = re.compile(r"^[IVXLCDM]{2,}$")
# Quotes are paired asymmetrically: an opener maps to a specific closer.
# A symmetric character class would happily match `»backwards«` or
# `„open ASCII"` with a Serbian-low opener that owns nothing — corrupting
# real text. Explicit alternation, non-greedy, no opener repetition inside.
# The re.DOTALL flag lets a quoted region span a newline (card bodies do).
_QUOTED_RE = re.compile(
    r"„[^„”“]*?[”“\"]"  # German/Serbian: „ … followed by ” (U+201D) / “ (U+201C) / ASCII "
    r"|«[^«»]*?»"       # French: « … »
    r"|“[^“”]*?”"       # English curly: “ … ” (opener U+201C — order matters, German alt tried first)
    r"|\"[^\"]*?\"",    # ASCII: " … "
    re.DOTALL,
)


class _Rule:
    """One source→target mapping loaded from rules.yaml."""

    def __init__(self, data: dict):
        self.source: str = data["source"]
        self.target: str = data["target"]
        self.digraphs: dict[str, str] = {k.lower(): v for k, v in data.get("digraphs", {}).items()}
        self.pre_char: dict[str, str] = data.get("pre_char", {}) or {}
        self.singles: dict[str, str] = data.get("singles", {}) or {}
        self.extras_in_word: str = data.get("extras_in_word", "") or ""
        self.non_native_letters: set[str] = set(data.get("non_native_letters", "") or "")

        self.word_split_re = re.compile(rf"(\s+|[^\w{re.escape(self.extras_in_word)}]+)")

    def _convert_word(self, word: str) -> str:
        if self.non_native_letters and self.non_native_letters.intersection(word):
            return word
        if _ROMAN_RE.match(word):
            return word

        # pre_char runs on the original casing (Ð/Đ pair, ð/đ pair). Handled
        # before case-normalisation so upper-vs-lower is still visible.
        if self.pre_char:
            word = "".join(self.pre_char.get(ch, ch) for ch in word)

        # Determine the case pattern from the WHOLE word (not each digraph):
        # in cyrillic→latin the source digraph is a single glyph (Џ, Њ, Љ),
        # so its own case tells us UPPER even when the word is TITLE.
        # Convert to lowercase, do the mapping, apply the word-level pattern
        # to the joined output at the end.
        case = _detect_case(word)
        lower_word = word.lower()

        result: list[str] = []
        i = 0
        while i < len(lower_word):
            matched = False
            for width in (2, 1):
                if i + width > len(lower_word):
                    continue
                candidate = lower_word[i : i + width]
                if candidate in self.digraphs:
                    result.append(self.digraphs[candidate])
                    i += width
                    matched = True
                    break
            if matched:
                continue

            ch = lower_word[i]
            result.append(self.singles.get(ch, ch))
            i += 1

        return _apply_case("".join(result), case)

    def apply(self, text: str) -> str:
        if not text:
            return ""

        slots: dict[str, str] = {}
        counter = 0

        def _stash(match: re.Match) -> str:
            nonlocal counter
            key = f"\x00Q{counter}\x00"
            slots[key] = match.group(0)
            counter += 1
            return key

        protected = _QUOTED_RE.sub(_stash, text)

        parts = self.word_split_re.split(protected)
        rendered: list[str] = []
        for part in parts:
            if not part:
                continue
            if not part[0].isalpha():
                rendered.append(part)
            else:
                rendered.append(self._convert_word(part))

        result = "".join(rendered)
        for key, original in slots.items():
            result = result.replace(key, original)
        return result


class Transliterator:
    """Convert text between two Serbian/Montenegrin scripts.

    ``source`` and ``target`` are the script codes from ``rules.yaml`` — one of
    ``srp-latn``, ``srp-cyrl``, ``cnr-latn``, ``cnr-cyrl``.
    """

    _rules_cache: list[_Rule] | None = None

    def __init__(self, source: str, target: str):
        self._rule = self._find_rule(source, target)

    @classmethod
    def _load_rules(cls) -> list[_Rule]:
        if cls._rules_cache is None:
            path = Path(__file__).parent / "data" / "rules.yaml"
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
            cls._rules_cache = [_Rule(entry) for entry in data["rules"]]
        return cls._rules_cache

    @classmethod
    def _find_rule(cls, source: str, target: str) -> _Rule:
        for rule in cls._load_rules():
            if rule.source == source and rule.target == target:
                return rule
        raise ValueError(f"No rule for {source} → {target}. Add it to rules.yaml.")

    def __call__(self, text: str) -> str:
        return self._rule.apply(text)
