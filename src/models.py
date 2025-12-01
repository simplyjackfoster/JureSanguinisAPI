from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List, Optional, Dict, Any


class TransmissionStatus(str, Enum):
    INTACT = "INTACT"
    BROKEN_NATURALIZATION = "BROKEN_NATURALIZATION"
    COURT_ONLY_1948 = "COURT_ONLY_1948"
    BLOCKED_ADMIN_MINOR_ISSUE = "BLOCKED_ADMIN_MINOR_ISSUE"
    CONTESTED_EDGE_CASE = "CONTESTED_EDGE_CASE"
    BLOCKED_REFORM_NO_EXEMPTION = "BLOCKED_REFORM_NO_EXEMPTION"
    ALTERNATIVE_PATH = "ALTERNATIVE_PATH"
    NO_ITALIAN_LINEAGE_ANCHOR = "NO_ITALIAN_LINEAGE_ANCHOR"


class AcquisitionMode(str, Enum):
    AUTOMATIC_BY_BLOOD = "AUTOMATIC_BY_BLOOD"
    NOT_AUTOMATIC_POST_REFORM = "NOT_AUTOMATIC_POST_REFORM"
    BENEFIT_OF_LAW = "BENEFIT_OF_LAW"
    BY_RESIDENCE = "BY_RESIDENCE"
    UNKNOWN = "UNKNOWN"


class OverallStatus(str, Enum):
    CLEAR_ADMIN_ELIGIBLE = "CLEAR_ADMIN_ELIGIBLE"
    COURT_ONLY_1948 = "COURT_ONLY_1948"
    BLOCKED_ADMIN_MINOR_ISSUE = "BLOCKED_ADMIN_MINOR_ISSUE"
    BLOCKED_REFORM_NO_EXEMPTION = "BLOCKED_REFORM_NO_EXEMPTION"
    POTENTIAL_VIA_RESIDENCE = "POTENTIAL_VIA_RESIDENCE"
    INDETERMINATE_COMPLEX_CASE = "INDETERMINATE_COMPLEX_CASE"
    NOT_ELIGIBLE_NO_ITALIAN_LINEAGE = "NOT_ELIGIBLE_NO_ITALIAN_LINEAGE"


class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class CourtViability(str, Enum):
    NONE = "NONE"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class CitizenshipEvent:
    kind: str
    date: Optional[date] = None
    country: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Person:
    id: str
    name: str
    birth_date: Optional[date] = None
    birth_country: Optional[str] = None
    other_citizenships_at_birth: List[str] = field(default_factory=list)
    events: List[CitizenshipEvent] = field(default_factory=list)
    acquisition_mode: AcquisitionMode = AcquisitionMode.UNKNOWN
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LineageLink:
    parent: Person
    child: Person
    relationship: str
    parent_citizenship_status_at_birth: TransmissionStatus = TransmissionStatus.INTACT
    notes: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RuleOutcome:
    rule_id: str
    status: TransmissionStatus
    notes: str
    confidence: Confidence = Confidence.MEDIUM
    needs_lawyer: bool = False


@dataclass
class EvaluationResult:
    lineage: List[LineageLink]
    overall_status: OverallStatus
    confidence: Confidence
    court_viability: CourtViability
    needs_lawyer: bool
    acquisition_mode: AcquisitionMode
    explanations: List[str] = field(default_factory=list)
    rule_outcomes: List[RuleOutcome] = field(default_factory=list)


@dataclass
class Rule:
    id: str
    description: str
    preconditions: Dict[str, Any]
    condition: Dict[str, Any]
    effects: Dict[str, Any]
    sources: List[str] = field(default_factory=list)
    effective_date: Optional[str] = None
    contested: bool = False

