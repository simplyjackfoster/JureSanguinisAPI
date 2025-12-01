from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from src.models import (
    AcquisitionMode,
    Confidence,
    CourtViability,
    EvaluationResult,
    LineageLink,
    OverallStatus,
    Rule,
    RuleOutcome,
    TransmissionStatus,
)
from src.rule_engine.json_logic import JsonLogicEvaluator


@dataclass
class EvaluationContext:
    lineage_chain: List[LineageLink]
    process_context: Dict
    now: datetime
    features: Dict

    def to_dict(self) -> Dict:
        # Provide flattened context for json-logic expressions
        base = {
            "process_type": self.process_context.get("process_type"),
            "country_of_filing": self.process_context.get("country_of_filing"),
            "lineage_length": len(self.lineage_chain),
            "applicant_birth_country": self.lineage_chain[-1].child.birth_country
            if self.lineage_chain
            else None,
            "ancestor_birth_country": self.lineage_chain[0].parent.birth_country
            if self.lineage_chain
            else None,
        }
        base.update(self.features)
        return base


class RuleEngine:
    def __init__(self, rules: List[Rule]):
        self.rules = rules

    def evaluate(self, context: EvaluationContext) -> EvaluationResult:
        evaluator = JsonLogicEvaluator(context.to_dict())
        rule_outcomes: List[RuleOutcome] = []
        overall_status = OverallStatus.CLEAR_ADMIN_ELIGIBLE
        acquisition_mode = AcquisitionMode.AUTOMATIC_BY_BLOOD
        needs_lawyer = False
        court_viability = CourtViability.NONE
        confidence = Confidence.HIGH

        for rule in self.rules:
            if not self._preconditions_met(rule, context):
                continue
            if evaluator.evaluate(rule.condition):
                outcome = self._apply_effects(rule)
                rule_outcomes.append(outcome)
                # derive aggregate state
                overall_status = self._update_overall_status(overall_status, outcome.status)
                acquisition_mode = self._update_acquisition_mode(acquisition_mode, rule.effects)
                needs_lawyer = needs_lawyer or outcome.needs_lawyer
                court_viability = self._update_court_viability(court_viability, outcome)
                confidence = self._update_confidence(confidence, outcome)

        explanations = [f"{o.rule_id}: {o.notes}" for o in rule_outcomes]
        if not rule_outcomes:
            explanations.append(
                "No blocking rules triggered; defaulting to classical transmission pending document review."
            )

        return EvaluationResult(
            lineage=context.lineage_chain,
            overall_status=overall_status,
            confidence=confidence,
            court_viability=court_viability,
            needs_lawyer=needs_lawyer,
            acquisition_mode=acquisition_mode,
            explanations=explanations,
            rule_outcomes=rule_outcomes,
        )

    def _preconditions_met(self, rule: Rule, context: EvaluationContext) -> bool:
        required = rule.preconditions or {}
        if required.get("needs_lineage") and not context.lineage_chain:
            return False
        return True

    def _apply_effects(self, rule: Rule) -> RuleOutcome:
        status = TransmissionStatus(rule.effects.get("status", TransmissionStatus.INTACT))
        notes = rule.effects.get("notes", rule.description)
        confidence = Confidence(rule.effects.get("confidence", Confidence.MEDIUM))
        needs_lawyer = rule.effects.get("needs_lawyer", False) or rule.contested
        return RuleOutcome(
            rule_id=rule.id,
            status=status,
            notes=notes,
            confidence=confidence,
            needs_lawyer=needs_lawyer,
        )

    def _update_overall_status(
        self, current: OverallStatus, status: TransmissionStatus
    ) -> OverallStatus:
        priority = {
            TransmissionStatus.BLOCKED_REFORM_NO_EXEMPTION: OverallStatus.BLOCKED_REFORM_NO_EXEMPTION,
            TransmissionStatus.BLOCKED_ADMIN_MINOR_ISSUE: OverallStatus.BLOCKED_ADMIN_MINOR_ISSUE,
            TransmissionStatus.COURT_ONLY_1948: OverallStatus.COURT_ONLY_1948,
            TransmissionStatus.ALTERNATIVE_PATH: OverallStatus.POTENTIAL_VIA_RESIDENCE,
            TransmissionStatus.CONTESTED_EDGE_CASE: OverallStatus.INDETERMINATE_COMPLEX_CASE,
            TransmissionStatus.BROKEN_NATURALIZATION: OverallStatus.INDETERMINATE_COMPLEX_CASE,
        }
        return priority.get(status, current)

    def _update_acquisition_mode(self, current: AcquisitionMode, effects: Dict) -> AcquisitionMode:
        mode = effects.get("acquisition_mode")
        if mode:
            return AcquisitionMode(mode)
        return current

    def _update_court_viability(
        self, current: CourtViability, outcome: RuleOutcome
    ) -> CourtViability:
        if outcome.status in (
            TransmissionStatus.COURT_ONLY_1948,
            TransmissionStatus.BLOCKED_ADMIN_MINOR_ISSUE,
            TransmissionStatus.CONTESTED_EDGE_CASE,
        ):
            return CourtViability.HIGH
        return current

    def _update_confidence(self, current: Confidence, outcome: RuleOutcome) -> Confidence:
        if outcome.confidence == Confidence.LOW:
            return Confidence.LOW
        if outcome.confidence == Confidence.MEDIUM and current == Confidence.HIGH:
            return Confidence.MEDIUM
        return current

