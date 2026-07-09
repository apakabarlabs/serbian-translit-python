from pathlib import Path

import pytest
import yaml

from serbian_translit import Transliterator


def load_test_cases():
    path = Path(__file__).parent / "data" / "tests.yaml"
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)

    cases = []
    for section in data["tests"]:
        section_name = section["section"]
        source = section["source"]
        target = section["target"]
        for case in section["cases"]:
            cases.append((section_name, source, target, case["text"], case["want"]))
    return cases


@pytest.mark.parametrize("section,source,target,text,want", load_test_cases())
def test_transliterate(section, source, target, text, want):
    translit = Transliterator(source, target)
    result = translit(text)
    assert result == want, f"[{section}] {source}→{target} '{text}': got '{result}', want '{want}'"
