"""Regions of text that must round-trip untouched.

Two kinds of regions get stashed before the word tokeniser sees them:
paired quoted regions and URL/email/handle tokens. Each region is
replaced with a per-call sentinel whose UUID prefix guarantees no
collision with any substring the user could plausibly type.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable

# Quotes pair asymmetrically (an opener owns one specific closer).
# A symmetric character class would happily pair `»…«` or `„…„`.
_QUOTED_RE = re.compile(
    r"„[^„”“]*?[”“\"]"
    r"|«[^«»]*?»"
    r"|“[^“”]*?”"
    r"|\"[^\"]*?\"",
    re.DOTALL,
)

# A URL/email/handle terminates at whitespace or angle brackets. Anything
# inside those bounds is a foreign token.
_STOP = r"\s<>"
_TOKEN_RE = re.compile(
    rf"[a-zA-Z][a-zA-Z0-9+.\-]*://[^{_STOP}]+"
    rf"|www\.[^{_STOP}]+"
    rf"|[^{_STOP}@]+@[^{_STOP}@]+\.[^{_STOP}@]+"
    rf"|#[^{_STOP}#@]+"
    rf"|@[^{_STOP}#@]+",
)


class ProtectedRegions:
    """Stash-and-restore machinery for a single conversion.

    The sentinel prefix is regenerated per instance so two concurrent
    calls cannot alias each other's slot table, and no user payload
    can spoof a slot key.
    """

    def __init__(self) -> None:
        self._slots: dict[str, str] = {}
        self._counter = 0
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


# Public alias for tests and the engine — keeps the callable form
# available if we later swap the class for a plain closure.
Stash = Callable[[str], str]
