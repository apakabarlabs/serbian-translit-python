"""YAML-driven table of ready-built rules, one per source→target pair."""

from __future__ import annotations

from pathlib import Path
from typing import TypedDict

import yaml

from .rule import Rule, RuleData


class _RulesFile(TypedDict):
    rules: list[RuleData]


def _load() -> dict[tuple[str, str], Rule]:
    path = Path(__file__).parent / "data" / "rules.yaml"
    with path.open(encoding="utf-8") as f:
        data: _RulesFile = yaml.safe_load(f)
    return {(entry["source"], entry["target"]): Rule(entry) for entry in data["rules"]}


_TABLE = _load()

SRP_LAT_TO_CYR = _TABLE["srp-latn", "srp-cyrl"]
SRP_CYR_TO_LAT = _TABLE["srp-cyrl", "srp-latn"]
CNR_LAT_TO_CYR = _TABLE["cnr-latn", "cnr-cyrl"]
CNR_CYR_TO_LAT = _TABLE["cnr-cyrl", "cnr-latn"]
