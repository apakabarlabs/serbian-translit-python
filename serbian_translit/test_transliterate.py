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


def load_test_cases():
    path = Path(__file__).parent / "data" / "tests.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cases = []
    for section in data["tests"]:
        source = section["source"]
        target = section["target"]
        for case in section["cases"]:
            cases.append((section["section"], source, target, case["text"], case["want"]))
    return cases


@pytest.mark.parametrize("section,source,target,text,want", load_test_cases())
def test_transliterate(section, source, target, text, want):
    func = _ROUTES[(source, target)]
    result = func(text)
    assert result == want, f"[{section}] {source} → {target} ('{text}'): got '{result}', want '{want}'"
