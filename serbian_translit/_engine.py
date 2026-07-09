"""YAML-driven engine for Serbian/Montenegrin script conversion.

The engine plays a source→target mapping loaded from ``data/rules.yaml``.
All script-specific facts (digraphs, pre-char remaps, extra word-characters,
non-native letters) live in the YAML file, not here. This module is
internal; the public API is ``serbian_translit.srp`` and
``serbian_translit.cnr``.

Word-level protection during a conversion:
  - Paired quoted regions (``„…"``, ``“…”``, ``"…"``, ``«…»``) round-trip
    verbatim so foreign quotes and brand names survive.
  - Roman numerals (``II``, ``XIV``, ``XX`` …) stay Latin in either direction.
  - A source-Latin word containing any letter in ``non_native_letters`` is
    treated as a foreign inclusion and left untouched.
"""

from __future__ import annotations

import re
import unicodedata
from enum import Enum
from functools import lru_cache
from pathlib import Path
from typing import TypedDict

import yaml


class _RuleData(TypedDict, total=False):
    """Shape of one entry in `data/rules.yaml`."""

    source: str
    target: str
    digraphs: dict[str, str]
    pre_char: dict[str, str]
    singles: dict[str, str]
    extras_in_word: str
    non_native_letters: str
    never_roman: list[str]


class _RulesFile(TypedDict):
    rules: list[_RuleData]


class _CasePattern(Enum):
    LOWER = "lower"
    UPPER = "upper"
    TITLE = "title"
    MIXED = "mixed"


def _detect_case(text: str) -> _CasePattern:
    if text.islower():
        return _CasePattern.LOWER
    if text.isupper():
        return _CasePattern.UPPER
    if len(text) > 1 and text[0].isupper() and text[1:].islower():
        return _CasePattern.TITLE
    return _CasePattern.MIXED


def _apply_case(text: str, pattern: _CasePattern) -> str:
    if pattern == _CasePattern.LOWER:
        return text.lower()
    if pattern == _CasePattern.UPPER:
        return text.upper()
    if pattern == _CasePattern.TITLE:
        return text[0].upper() + text[1:].lower() if text else text
    return text


# Canonical Roman numeral form: M{0,3} (CM|CD|D?C{0,3}) (XC|XL|L?X{0,3}) (IX|IV|V?I{0,3}).
# The naive `[IVXLCDM]{2,}` fired on common Serbian all-caps words made of
# only those letters — `MI` (мы), `LI` (ли), `VI` (ви), `CI` (ти-dat),
# `CIVIL`, `MILD`, `DA LI` — corrupting them into untouched Latin.
# The ≥2 guard drops single-letter numerals (`I`, `V`, `X`) so they still
# transliterate as words; anything ≥2 letters must match the canonical
# shape to survive.
_ROMAN_RE = re.compile(r"^M{0,3}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$")


def _is_roman(word: str) -> bool:
    return len(word) >= 2 and bool(_ROMAN_RE.match(word))


# Quotes are paired asymmetrically: an opener maps to a specific closer.
# A symmetric character class would happily match `»backwards«` or
# `„open ASCII"` with a Serbian-low opener that owns nothing — corrupting
# real text. Explicit alternation, non-greedy, no opener repetition inside.
# The re.DOTALL flag lets a quoted region span a newline (card bodies do).
_QUOTED_RE = re.compile(
    r"„[^„”“]*?[”“\"]"  # German/Serbian: „ … followed by ” (U+201D) / “ (U+201C) / ASCII "
    r"|«[^«»]*?»"  # French: « … »
    r"|“[^“”]*?”"  # English curly: “ … ” (opener U+201C — order matters, German alt tried first)
    r"|\"[^\"]*?\"",  # ASCII: " … "
    re.DOTALL,
)

# URLs, email addresses, hashtags and @-mentions must round-trip verbatim.
# Order matters — URL alt runs first (its `://` distinguishes from bare
# domains); `www.` shorthand catches schemeless URLs; then email, hashtag,
# handle. The stop set (whitespace, control, common punctuation) is a
# conservative envelope: real-world URLs may contain more (parens, semis),
# but they are also the characters that terminate a URL in prose. If a
# real URL contains those, wrap it in angle brackets and it will still be
# protected as a foreign token by the enclosing whitespace boundary.
_TOKEN_STOP = r"\s<>"  # noqa: S105 — regex character class, not a password
_TOKEN_RE = re.compile(
    rf"[a-zA-Z][a-zA-Z0-9+.\-]*://[^{_TOKEN_STOP}]+"  # scheme://rest
    rf"|www\.[^{_TOKEN_STOP}]+"  # www.rest
    rf"|[^{_TOKEN_STOP}@]+@[^{_TOKEN_STOP}@]+\.[^{_TOKEN_STOP}@]+"  # user@host.tld
    rf"|#[^{_TOKEN_STOP}#@]+"  # #hashtag
    rf"|@[^{_TOKEN_STOP}#@]+",  # @mention
)


class _Rule:
    """One source→target mapping loaded from rules.yaml."""

    def __init__(self, data: _RuleData) -> None:
        self.source: str = data["source"]
        self.target: str = data["target"]
        self.digraphs: dict[str, str] = {k.lower(): v for k, v in data.get("digraphs", {}).items()}
        self.pre_char: dict[str, str] = data.get("pre_char") or {}
        self.singles: dict[str, str] = data.get("singles") or {}
        self.extras_in_word: str = data.get("extras_in_word") or ""
        self.non_native_letters: set[str] = set(data.get("non_native_letters") or "")
        self.never_roman: set[str] = {w.upper() for w in data.get("never_roman") or []}
        self.word_split_re = re.compile(rf"(\s+|[^\w{re.escape(self.extras_in_word)}]+)")

    def _convert_word(self, word: str) -> str:
        if self.non_native_letters and self.non_native_letters.intersection(word):
            return word
        if _is_roman(word) and word.upper() not in self.never_roman:
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
        # MIXED case in a longer word means a brand name / acronym
        # (`iPhone`, `iOS`, `mRNA`) whose casing carries meaning we cannot
        # preserve after a lowercased conversion — leave it untouched.
        # 2-char MIXED words are the irregular digraph edge cases
        # (`lJ`, `nJ`, `dŽ`) that the flowbot original converted; keep
        # that behaviour.
        if case == _CasePattern.MIXED and len(word) > 2:
            return word
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

        # Normalise to NFC. macOS clipboard, iOS filenames, and many web
        # sources hand out NFD; without this, `č` (c + U+030C) would split
        # into `c` → `ц` and a leaking combining mark. NB: Montenegrin
        # `с́`/`з́` are already-decomposed forms with no NFC equivalent —
        # they survive normalisation and are handled as digraphs downstream.
        text = unicodedata.normalize("NFC", text)

        slots: dict[str, str] = {}
        counter = 0

        def _stash(match: re.Match[str]) -> str:
            nonlocal counter
            key = f"\x00Q{counter}\x00"
            slots[key] = match.group(0)
            counter += 1
            return key

        # Order: URLs/emails/handles first (may sit inside quoted regions —
        # rare but possible; either way we stash them so their characters
        # never see the tokeniser), then quoted regions.
        protected = _TOKEN_RE.sub(_stash, text)
        protected = _QUOTED_RE.sub(_stash, protected)

        parts = self.word_split_re.split(protected)
        rendered: list[str] = []
        for part in parts:
            if not part:
                continue
            # A word may start with a digit but still contain letters that
            # must transliterate (`2brzo`, `100dinara`). Gate on "contains
            # any alpha", not on the first character.
            if any(ch.isalpha() for ch in part):
                rendered.append(self._convert_word(part))
            else:
                rendered.append(part)

        result = "".join(rendered)
        for key, original in slots.items():
            result = result.replace(key, original)
        return result


@lru_cache(maxsize=1)
def _load_rules_table() -> dict[tuple[str, str], _Rule]:
    """Load and index rules.yaml once. Cached for the process lifetime."""
    path = Path(__file__).parent / "data" / "rules.yaml"
    with path.open(encoding="utf-8") as f:
        data: _RulesFile = yaml.safe_load(f)
    return {(entry["source"], entry["target"]): _Rule(entry) for entry in data["rules"]}


def _load_rule(source: str, target: str) -> _Rule:
    """Return the compiled rule for a source→target pair."""
    try:
        return _load_rules_table()[(source, target)]
    except KeyError as exc:
        msg = f"No rule for {source} → {target} in rules.yaml"
        raise ValueError(msg) from exc
