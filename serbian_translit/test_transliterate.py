from pathlib import Path

import pytest
import yaml

from serbian_translit import cnr, srp

_MODULES = {"srp": srp, "cnr": cnr}


def load_test_cases():
    path = Path(__file__).parent / "data" / "tests.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    cases = []
    for section in data["tests"]:
        for case in section["cases"]:
            cases.append((section["section"], section["lang"], section["direction"], case["text"], case["want"]))
    return cases


@pytest.mark.parametrize("section,lang,direction,text,want", load_test_cases())
def test_transliterate(section, lang, direction, text, want):
    func = getattr(_MODULES[lang], direction)
    result = func(text)
    assert result == want, f"[{section}] {lang}.{direction}('{text}'): got '{result}', want '{want}'"
