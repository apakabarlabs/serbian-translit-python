"""Stash paired quotes and URL/email/handle tokens so they round-trip untouched."""

from __future__ import annotations

import re
import uuid

# Quotes pair asymmetrically (an opener owns one specific closer).
# A symmetric character class would happily pair `»…«` or `„…„`.
_QUOTED_RE = re.compile(
    r"„[^„”“]*?[”“\"]"
    r"|«[^«»]*?»"
    r"|“[^“”]*?”"
    r"|\"[^\"]*?\"",
    re.DOTALL,
)

_STOP = r"\s<>"
_TOKEN_RE = re.compile(
    rf"[a-zA-Z][a-zA-Z0-9+.\-]*://[^{_STOP}]+"
    rf"|www\.[^{_STOP}]+"
    rf"|[^{_STOP}@]+@[^{_STOP}@]+\.[^{_STOP}@]+"
    rf"|#[^{_STOP}#@]+"
    rf"|@[^{_STOP}#@]+",
)


class ProtectedRegions:
    def __init__(self) -> None:
        self._slots: dict[str, str] = {}
        self._counter = 0
        # Per-instance prefix so a user substring cannot spoof a slot key
        # and concurrent calls cannot alias each other's tables.
        self._prefix = uuid.uuid4().hex

    def stash_all(self, text: str) -> str:
        # URL tokens first so their inner punctuation cannot be mistaken
        # for a quote-region boundary in the second pass.
        text = _TOKEN_RE.sub(self._stash, text)
        return _QUOTED_RE.sub(self._stash, text)

    def restore(self, text: str) -> str:
        for key, original in self._slots.items():
            text = text.replace(key, original)
        return text

    def _stash(self, match: re.Match[str]) -> str:
        key = f"\x00Q_{self._prefix}_{self._counter}\x00"
        self._slots[key] = match.group(0)
        self._counter += 1
        return key
