from datetime import date

import pytest

from src.evaluator import evaluate_lineage
from src.models import (
    AcquisitionMode,
    CitizenshipEvent,
    LineageLink,
    OverallStatus,
    Person,
    TransmissionStatus,
)


@pytest.fixture
def base_ancestor():
    return Person(
        id="a1",
        name="Giorgio",
        birth_date=date(1890, 5, 1),
        birth_country="Italy",
    )


def test_requires_italian_birth_anchor():
    ancestor = Person(
        id="a1",
        name="Giorgio",
        birth_date=date(1890, 5, 1),
        birth_country="USA",
    )
    child = Person(
        id="a2",
        name="Maria",
        birth_date=date(1920, 6, 1),
        birth_country="Argentina",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1990, 7, 1),
        birth_country="USA",
    )

    lineage = [
        LineageLink(parent=ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="father"),
    ]

    result = evaluate_lineage(lineage)

    assert result.overall_status == OverallStatus.NOT_ELIGIBLE_NO_ITALIAN_LINEAGE
    assert result.acquisition_mode == AcquisitionMode.UNKNOWN
    assert not result.needs_lawyer
    assert any(
        outcome.status == TransmissionStatus.NO_ITALIAN_LINEAGE_ANCHOR
        for outcome in result.rule_outcomes
    )


def test_clean_classic_case(base_ancestor):
    child = Person(
        id="a2",
        name="Maria",
        birth_date=date(1920, 6, 1),
        birth_country="Argentina",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1990, 7, 1),
        birth_country="USA",
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="father"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.CLEAR_ADMIN_ELIGIBLE
    assert result.acquisition_mode == AcquisitionMode.AUTOMATIC_BY_BLOOD
    assert not result.needs_lawyer


def test_1948_maternal_case(base_ancestor):
    child = Person(
        id="a2",
        name="Anna",
        birth_date=date(1930, 6, 1),
        birth_country="Argentina",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1960, 7, 1),
        birth_country="USA",
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="mother"),
        LineageLink(parent=child, child=applicant, relationship="father"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.COURT_ONLY_1948
    assert result.needs_lawyer


def test_minor_issue_block(base_ancestor):
    naturalization = CitizenshipEvent(
        kind="naturalization_foreign",
        date=date(1940, 1, 1),
        country="USA",
        metadata={"co_resident_child": True, "jus_soli_country": True},
    )
    base_ancestor.events.append(naturalization)
    child = Person(
        id="a2",
        name="Giulia",
        birth_date=date(1930, 6, 1),
        birth_country="USA",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1960, 7, 1),
        birth_country="USA",
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="mother"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.BLOCKED_ADMIN_MINOR_ISSUE
    assert result.needs_lawyer


def test_minor_issue_edge_case(base_ancestor):
    naturalization = CitizenshipEvent(
        kind="naturalization_foreign",
        date=date(1940, 1, 1),
        country="USA",
        metadata={"co_resident_child": False, "jus_soli_country": True, "child_emancipated": True},
    )
    base_ancestor.events.append(naturalization)
    child = Person(
        id="a2",
        name="Giulia",
        birth_date=date(1930, 6, 1),
        birth_country="USA",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1960, 7, 1),
        birth_country="USA",
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="mother"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.INDETERMINATE_COMPLEX_CASE
    assert result.needs_lawyer


def test_reform_non_exempt(base_ancestor):
    child = Person(
        id="a2",
        name="Laura",
        birth_date=date(2025, 1, 1),
        birth_country="USA",
        other_citizenships_at_birth=["USA"],
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(2048, 7, 1),
        birth_country="USA",
        other_citizenships_at_birth=["USA"],
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="mother"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.BLOCKED_REFORM_NO_EXEMPTION
    assert result.acquisition_mode == AcquisitionMode.NOT_AUTOMATIC_POST_REFORM
    assert result.needs_lawyer


def test_alternative_residence_path(base_ancestor):
    child = Person(
        id="a2",
        name="Laura",
        birth_date=date(2025, 1, 1),
        birth_country="USA",
        other_citizenships_at_birth=["USA"],
        notes={"tajani_exemption": True, "resident_in_italy_as_descendant": True},
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(2048, 7, 1),
        birth_country="USA",
        other_citizenships_at_birth=["USA"],
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="mother"),
    ]
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.POTENTIAL_VIA_RESIDENCE
    assert result.acquisition_mode == AcquisitionMode.BY_RESIDENCE
    assert result.needs_lawyer


def test_naturalization_breaks_chain(base_ancestor):
    naturalization = CitizenshipEvent(
        kind="naturalization_foreign",
        date=date(1910, 1, 1),
        country="USA",
    )
    base_ancestor.events.append(naturalization)
    child = Person(
        id="a2",
        name="Giulio",
        birth_date=date(1920, 6, 1),
        birth_country="USA",
    )
    applicant = Person(
        id="app",
        name="Applicant",
        birth_date=date(1950, 7, 1),
        birth_country="USA",
    )
    lineage = [
        LineageLink(parent=base_ancestor, child=child, relationship="father"),
        LineageLink(parent=child, child=applicant, relationship="mother"),
    ]
    # Trigger feature computation
    result = evaluate_lineage(lineage)
    assert result.overall_status == OverallStatus.INDETERMINATE_COMPLEX_CASE
    assert result.needs_lawyer
    assert any(
        outcome.status == TransmissionStatus.BROKEN_NATURALIZATION for outcome in result.rule_outcomes
    )
