from __future__ import annotations

from datetime import date
from typing import Dict, List

from src.models import LineageLink, TransmissionStatus, Person, CitizenshipEvent


POST_REFORM_EFFECTIVE_DATE = date(2024, 12, 23)


def _find_event(person: Person, kind: str) -> CitizenshipEvent | None:
    return next((event for event in person.events if event.kind == kind), None)


def build_feature_flags(lineage_chain: List[LineageLink]) -> Dict:
    flags = {
        "has_pre1948_maternal_link": False,
        "has_minor_issue_block": False,
        "has_minor_issue_edge": False,
        "has_automatic_loss_marriage": False,
        "tajani_non_exempt": False,
        "tajani_exempt": False,
        "alternative_path_by_residence": False,
        "parent_citizenship_status": TransmissionStatus.INTACT.value,
        "has_italian_birth_anchor": False,
    }

    for link in lineage_chain:
        parent = link.parent
        child = link.child

        # At least one person in the chain must be born in Italy for jure sanguinis.
        for person in (parent, child):
            birth_country = (person.birth_country or "").strip().lower()
            if birth_country == "italy":
                flags["has_italian_birth_anchor"] = True
        # 1948 maternal rule
        if link.relationship.lower().startswith("mother"):
            if child.birth_date and child.birth_date < date(1948, 1, 1):
                flags["has_pre1948_maternal_link"] = True

        # naturalization timing
        naturalization = _find_event(parent, "naturalization_foreign")
        if naturalization and child.birth_date and naturalization.date:
            if naturalization.date < child.birth_date:
                link.parent_citizenship_status_at_birth = TransmissionStatus.BROKEN_NATURALIZATION
                flags["parent_citizenship_status"] = (
                    TransmissionStatus.BROKEN_NATURALIZATION.value
                )

        # minor issue detection
        if naturalization and child.birth_date and naturalization.date:
            age_at_nat = (naturalization.date - child.birth_date).days / 365.25
            if age_at_nat < 18:
                co_resident = naturalization.metadata.get("co_resident_child", True)
                emancipated = naturalization.metadata.get("child_emancipated", False)
                jus_soli_country = naturalization.metadata.get("jus_soli_country", False)
                if co_resident and jus_soli_country and not emancipated:
                    flags["has_minor_issue_block"] = True
                elif not co_resident or emancipated:
                    flags["has_minor_issue_edge"] = True

        # automatic loss by marriage
        marriage_loss = _find_event(parent, "automatic_loss_by_marriage")
        if marriage_loss:
            flags["has_automatic_loss_marriage"] = True

        # Tajani-style reforms
        if child.birth_date and child.birth_date >= POST_REFORM_EFFECTIVE_DATE:
            if child.other_citizenships_at_birth:
                if not child.notes.get("tajani_exemption", False):
                    flags["tajani_non_exempt"] = True
                else:
                    flags["tajani_exempt"] = True

        # Residence-based alternative path
        if child.notes.get("resident_in_italy_as_descendant", False):
            flags["alternative_path_by_residence"] = True

    return flags
