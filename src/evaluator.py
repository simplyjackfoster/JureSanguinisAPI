from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from src.models import EvaluationResult, LineageLink
from src.rule_engine.features import build_feature_flags
from src.rule_engine.loader import RuleLoader
from src.rule_engine.pipeline import EvaluationContext, RuleEngine


DEFAULT_RULE_PATHS = [
    "rules/classical.yaml",
    "rules/maternal1948.yaml",
    "rules/minor_issue.yaml",
    "rules/reform.yaml",
]


def evaluate_lineage(
    lineage_chain: List[LineageLink], process_context: Dict | None = None, rule_paths=None
) -> EvaluationResult:
    process_context = process_context or {}
    rule_paths = rule_paths or DEFAULT_RULE_PATHS

    features = build_feature_flags(lineage_chain)
    rules = RuleLoader(rule_paths).load()
    engine = RuleEngine(rules)
    context = EvaluationContext(
        lineage_chain=lineage_chain,
        process_context=process_context,
        now=datetime.utcnow(),
        features=features,
    )
    return engine.evaluate(context)


__all__ = ["evaluate_lineage", "DEFAULT_RULE_PATHS"]
