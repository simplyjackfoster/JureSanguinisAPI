from __future__ import annotations

import json
from typing import Any, Dict, List

from src.models import Rule


class RuleLoader:
    def __init__(self, rule_paths: List[str]):
        self.rule_paths = rule_paths

    def load(self) -> List[Rule]:
        rules: List[Rule] = []
        for path in self.rule_paths:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            for item in data.get("rules", []):
                rules.append(
                    Rule(
                        id=item["id"],
                        description=item.get("description", ""),
                        preconditions=item.get("preconditions", {}),
                        condition=item.get("condition", {}),
                        effects=item.get("effects", {}),
                        sources=item.get("sources", []),
                        effective_date=item.get("effective_date"),
                        contested=item.get("contested", False),
                    )
                )
        return rules
