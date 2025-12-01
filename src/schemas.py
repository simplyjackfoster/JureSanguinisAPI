from __future__ import annotations

import json
from typing import Any, Dict


def applicant_input_schema() -> Dict[str, Any]:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "JureSanguinisInput",
        "type": "object",
        "required": ["applicant", "ancestors", "lineage_links"],
        "properties": {
            "applicant": {"$ref": "#/definitions/person"},
            "ancestors": {
                "type": "array",
                "items": {"$ref": "#/definitions/person"},
            },
            "lineage_links": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["parent_id", "child_id", "relationship"],
                    "properties": {
                        "parent_id": {"type": "string"},
                        "child_id": {"type": "string"},
                        "relationship": {"type": "string"},
                        "notes": {"type": "object"},
                    },
                },
            },
            "context": {
                "type": "object",
                "properties": {
                    "process_type": {"enum": ["ADMIN", "COURT"]},
                    "appointment_filed_date": {"type": "string", "format": "date"},
                    "country_of_filing": {"type": "string"},
                },
            },
        },
        "definitions": {
            "citizenship_event": {
                "type": "object",
                "required": ["kind"],
                "properties": {
                    "kind": {"type": "string"},
                    "date": {"type": "string", "format": "date"},
                    "country": {"type": "string"},
                    "metadata": {"type": "object"},
                },
            },
            "person": {
                "type": "object",
                "required": ["id", "name"],
                "properties": {
                    "id": {"type": "string"},
                    "name": {"type": "string"},
                    "birth_date": {"type": "string", "format": "date"},
                    "birth_country": {"type": "string"},
                    "other_citizenships_at_birth": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                    "events": {
                        "type": "array",
                        "items": {"$ref": "#/definitions/citizenship_event"},
                    },
                    "notes": {"type": "object"},
                },
            },
        },
    }


def evaluation_output_schema() -> Dict[str, Any]:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "title": "JureSanguinisEvaluationOutput",
        "type": "object",
        "required": [
            "overall_status",
            "confidence",
            "court_viability",
            "needs_lawyer",
            "acquisition_mode",
            "explanations",
            "rule_outcomes",
        ],
        "properties": {
            "overall_status": {
                "enum": [
                    "CLEAR_ADMIN_ELIGIBLE",
                    "COURT_ONLY_1948",
                    "BLOCKED_ADMIN_MINOR_ISSUE",
                    "BLOCKED_REFORM_NO_EXEMPTION",
                    "POTENTIAL_VIA_RESIDENCE",
                    "INDETERMINATE_COMPLEX_CASE",
                ]
            },
            "confidence": {"enum": ["HIGH", "MEDIUM", "LOW"]},
            "court_viability": {"enum": ["NONE", "LOW", "MEDIUM", "HIGH"]},
            "needs_lawyer": {"type": "boolean"},
            "acquisition_mode": {
                "enum": [
                    "AUTOMATIC_BY_BLOOD",
                    "NOT_AUTOMATIC_POST_REFORM",
                    "BENEFIT_OF_LAW",
                    "BY_RESIDENCE",
                    "UNKNOWN",
                ]
            },
            "explanations": {"type": "array", "items": {"type": "string"}},
            "rule_outcomes": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["rule_id", "status", "notes"],
                    "properties": {
                        "rule_id": {"type": "string"},
                        "status": {"type": "string"},
                        "notes": {"type": "string"},
                        "confidence": {"type": "string"},
                        "needs_lawyer": {"type": "boolean"},
                    },
                },
            },
        },
    }


if __name__ == "__main__":
    print(json.dumps(applicant_input_schema(), indent=2))
    print(json.dumps(evaluation_output_schema(), indent=2))
