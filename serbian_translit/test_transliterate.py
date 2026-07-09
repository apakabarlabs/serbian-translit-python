from pathlib import Path

import pytest
import yaml

from serbian_translit import cnr, srp

# Portable YAML fixtures identify each section by (source, target). Every
# port resolves the pair to its own call shape — Python's is a two-level
# module.function lookup below; Swift/Kotlin ports will map the same
# YAML through their own naming.
_ROUTES = {
    ("srp-latn", "srp-cyrl"): srp.to_cyr,
    ("srp-cyrl", "srp-latn"): srp.to_lat,
    ("cnr-latn", "cnr-cyrl"): cnr.to_cyr,
    ("cnr-cyrl", "cnr-latn"): cnr.to_lat,
}


def load_test_cases() -> list[tuple[str, str, str, str, str]]:
    path = Path(__file__).parent / "data" / "tests.yaml"
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


def test_empty_input_returns_empty_string() -> None:
    assert srp.to_cyr("") == ""
    assert srp.to_lat("") == ""
    assert cnr.to_cyr("") == ""
    assert cnr.to_lat("") == ""


def test_unknown_rule_pair_raises_value_error() -> None:
    from serbian_translit._engine import _load_rule  # noqa: PLC0415

    with pytest.raises(ValueError, match="No rule for"):
        _load_rule("eng-latn", "srp-cyrl")
