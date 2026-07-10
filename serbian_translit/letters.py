"""Char-by-char letter map, digraph-first."""

from __future__ import annotations

from dataclasses import dataclass

_DIGRAPH_WIDTH = 2
_SINGLE_WIDTH = 1
_LOOKUP_WIDTHS = (_DIGRAPH_WIDTH, _SINGLE_WIDTH)


@dataclass(frozen=True)
class LetterMap:
    digraphs: dict[str, str]
    singles: dict[str, str]

    def convert(self, lowered: str) -> str:
        result: list[str] = []
        i = 0
        while i < len(lowered):
            replacement, width = self._match_at(lowered, i)
            result.append(replacement)
            i += width
        return "".join(result)

    def _match_at(self, lowered: str, i: int) -> tuple[str, int]:
        for width in _LOOKUP_WIDTHS:
            if i + width > len(lowered):
                continue
            candidate = lowered[i : i + width]
            if candidate in self.digraphs:
                return self.digraphs[candidate], width
        ch = lowered[i]
        return self.singles.get(ch, ch), _SINGLE_WIDTH
