from __future__ import annotations

from datetime import date
from typing import Any, Dict

from rest_framework import serializers
from src.models import CitizenshipEvent, LineageLink, Person


class CitizenshipEventSerializer(serializers.Serializer):
    kind = serializers.CharField()
    date = serializers.DateField(required=False, allow_null=True)
    country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    metadata = serializers.DictField(required=False, default=dict)

    def create(self, validated_data: Dict[str, Any]) -> CitizenshipEvent:
        return CitizenshipEvent(**validated_data)


class PersonSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    birth_date = serializers.DateField(required=False, allow_null=True)
    birth_country = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    other_citizenships_at_birth = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    events = CitizenshipEventSerializer(many=True, required=False, default=list)
    notes = serializers.DictField(required=False, default=dict)

    def create(self, validated_data: Dict[str, Any]) -> Person:
        events_data = validated_data.pop("events", [])
        events = [CitizenshipEvent(**event) for event in events_data]
        return Person(events=events, **validated_data)


class LineageLinkSerializer(serializers.Serializer):
    parent_id = serializers.CharField()
    child_id = serializers.CharField()
    relationship = serializers.CharField()
    notes = serializers.DictField(required=False, default=dict)


class ContextSerializer(serializers.Serializer):
    process_type = serializers.ChoiceField(
        choices=["ADMIN", "COURT"], required=False, allow_null=True
    )
    appointment_filed_date = serializers.DateField(required=False, allow_null=True)
    country_of_filing = serializers.CharField(required=False, allow_null=True, allow_blank=True)


class EvaluationRequestSerializer(serializers.Serializer):
    applicant = PersonSerializer()
    ancestors = PersonSerializer(many=True)
    lineage_links = LineageLinkSerializer(many=True)
    context = ContextSerializer(required=False)

    def create(self, validated_data: Dict[str, Any]):
        raise NotImplementedError("Creation is handled in the view")

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        applicant_id = attrs["applicant"]["id"]
        ancestor_ids = {person["id"] for person in attrs.get("ancestors", [])}
        if applicant_id in ancestor_ids:
            raise serializers.ValidationError("Applicant id must be distinct from ancestors")
        return attrs

    @staticmethod
    def build_person_index(data: Dict[str, Any]) -> Dict[str, Person]:
        applicant_serializer = PersonSerializer(data=data["applicant"])
        applicant_serializer.is_valid(raise_exception=True)
        applicant: Person = applicant_serializer.save()

        people = {applicant.id: applicant}
        for ancestor in data.get("ancestors", []):
            ancestor_serializer = PersonSerializer(data=ancestor)
            ancestor_serializer.is_valid(raise_exception=True)
            person: Person = ancestor_serializer.save()
            people[person.id] = person
        return people

    @staticmethod
    def build_lineage_links(data: Dict[str, Any], people: Dict[str, Person]) -> list[LineageLink]:
        links: list[LineageLink] = []
        for link_data in data.get("lineage_links", []):
            parent_id = link_data["parent_id"]
            child_id = link_data["child_id"]
            if parent_id not in people:
                raise serializers.ValidationError(f"Unknown parent_id '{parent_id}' in lineage")
            if child_id not in people:
                raise serializers.ValidationError(f"Unknown child_id '{child_id}' in lineage")
            links.append(
                LineageLink(
                    parent=people[parent_id],
                    child=people[child_id],
                    relationship=link_data["relationship"],
                    notes=link_data.get("notes", {}),
                )
            )
        return links

    @staticmethod
    def normalize_context(data: Dict[str, Any]) -> Dict[str, Any]:
        context = data.get("context") or {}
        normalized = dict(context)
        filed_date = normalized.get("appointment_filed_date")
        if isinstance(filed_date, date):
            normalized["appointment_filed_date"] = filed_date.isoformat()
        return normalized
