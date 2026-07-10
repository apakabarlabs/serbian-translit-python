from collections.abc import Callable
from pathlib import Path

import pytest
import yaml

from serbian_translit import cnr, srp

# Every port resolves (source, target) to its own call shape. Python's
# is a two-level module.function lookup; Swift/Kotlin use their own.
_ROUTES: dict[tuple[str, str], Callable[[str], str]] = {
    ("srp-latn", "srp-cyrl"): srp.to_cyr,
    ("srp-cyrl", "srp-latn"): srp.to_lat,
    ("cnr-latn", "cnr-cyrl"): cnr.to_cyr,
    ("cnr-cyrl", "cnr-latn"): cnr.to_lat,
}


def load_test_cases() -> list[tuple[str, str, str, str, str]]:
    path = Path(__file__).parent / "tests.yaml"
    with path.open(encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return [
        (section["section"], section["source"], section["target"], case["text"], case["want"])
        for section in data["tests"]
        for case in section["cases"]
    ]


@pytest.mark.parametrize(("section", "source", "target", "text", "want"), load_test_cases())
def test_transliterate(section: str, source: str, target: str, text: str, want: str) -> None:
    func = _ROUTES[(source, target)]
    result = func(text)
    assert result == want, f"[{section}] {source} → {target} ('{text}'): got '{result}', want '{want}'"


@pytest.mark.parametrize(
    "func",
    [srp.to_cyr, srp.to_lat, cnr.to_cyr, cnr.to_lat],
    ids=["srp.to_cyr", "srp.to_lat", "cnr.to_cyr", "cnr.to_lat"],
)
def test_empty_input_returns_empty_string(func: Callable[[str], str]) -> None:
    assert func("") == ""
