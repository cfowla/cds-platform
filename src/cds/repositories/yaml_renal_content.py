"""YAML-backed renal-dose content repository.

This module is the file and mapping boundary for versioned renal-dose content. It reads only the
explicit YAML paths supplied by the caller, validates each document with the normative version 1
schema, converts the validated mapping into immutable typed content, and stores it by the exact
case-sensitive ``(medication_id, regimen_id, content_version)`` key.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any, Iterable, Mapping, cast

from cds.domain.exceptions import ContentNotFound
from cds.repositories.renal_content import (
    ContentBandOutcome,
    ContentEvidenceLevel,
    ContentRecommendationAction,
    ContentReviewStatus,
    RenalContentEndpoint,
    RenalContentInterval,
    RenalDoseBandContent,
    RenalDoseContent,
    RenalDoseContentKey,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRecommendationContent,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSourceContent,
    RenalDoseSupportedContext,
)
from cds.repositories.renal_content_schema import load_renal_dose_content_yaml

__all__ = ["YamlRenalDoseContentRepository"]


class YamlRenalDoseContentRepository:
    """Exact-key repository built from explicitly supplied YAML files.

    Construction performs all file reads, YAML parsing, schema validation, and typed conversion.
    No directory discovery, identifier normalization, fallback, version selection, review-status
    filtering, or later file access occurs.
    """

    def __init__(self, content_paths: Iterable[str | Path] = ()) -> None:
        stored: dict[RenalDoseContentKey, RenalDoseContent] = {}
        for supplied_path in content_paths:
            path = Path(supplied_path)
            try:
                yaml_text = path.read_text(encoding="utf-8")
            except FileNotFoundError as exc:
                raise ContentNotFound(f"renal-dose content file not found: {path}") from exc

            validated = load_renal_dose_content_yaml(yaml_text)
            content = _content_from_validated_mapping(validated)
            key = content.key
            if key in stored:
                raise ValueError(f"duplicate renal-dose content key {key!r}")
            stored[key] = content
        self._contents = stored

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        """Return content for the exact key or raise ``ContentNotFound`` without fallback."""

        try:
            return self._contents[key]
        except KeyError:
            raise ContentNotFound(
                f"renal-dose content not found for exact key {key!r}"
            ) from None


def _content_from_validated_mapping(document: Mapping[str, Any]) -> RenalDoseContent:
    medication = _mapping(document["medication"])
    regimen = _mapping(document["regimen"])
    supported_context = _mapping(document["supported_context"])
    renal_domain = _mapping(document["renal_domain"])
    review = _mapping(document["review"])

    return RenalDoseContent(
        schema_version=document["schema_version"],
        content_id=document["content_id"],
        content_version=document["content_version"],
        rule_id=document["rule_id"],
        medication=RenalDoseMedicationContent(
            id=medication["id"],
            display=medication["display"],
        ),
        regimen=RenalDoseRegimenContent(
            id=regimen["id"],
            display=regimen["display"],
            indication_ids=tuple(regimen["indication_ids"]),
            route_id=regimen["route_id"],
            formulation_id=regimen["formulation_id"],
            base_dose=_quantity(_mapping(regimen["base_dose"])),
            frequency_interval=_quantity(_mapping(regimen["frequency_interval"])),
            infusion_duration=_nullable_quantity(regimen["infusion_duration"]),
        ),
        supported_context=RenalDoseSupportedContext(
            minimum_age_years=supported_context["minimum_age_years"],
            renal_method=supported_context["renal_method"],
            renal_unit=supported_context["renal_unit"],
            renal_function_stable=supported_context["renal_function_stable"],
            renal_replacement_therapy=supported_context["renal_replacement_therapy"],
            limitations=tuple(supported_context["limitations"]),
        ),
        renal_domain=RenalContentInterval(
            lower=_nullable_endpoint(renal_domain["lower"]),
            upper=_nullable_endpoint(renal_domain["upper"]),
        ),
        renal_bands=tuple(_band(_mapping(item)) for item in document["renal_bands"]),
        sources=tuple(_source(_mapping(item)) for item in document["sources"]),
        review=RenalDoseReviewContent(
            status=cast(ContentReviewStatus, review["status"]),
            reviewed_content_version=review["reviewed_content_version"],
            reviewer=review["reviewer"],
            reviewer_role=review["reviewer_role"],
            reviewed_on=_nullable_date(review["reviewed_on"]),
            notes=review["notes"],
        ),
        limitations=tuple(document["limitations"]),
    )


def _band(value: Mapping[str, Any]) -> RenalDoseBandContent:
    recommendation = value["recommendation"]
    return RenalDoseBandContent(
        id=value["id"],
        lower=_nullable_endpoint(value["lower"]),
        upper=_nullable_endpoint(value["upper"]),
        outcome=cast(ContentBandOutcome, value["outcome"]),
        recommendation=(
            None if recommendation is None else _recommendation(_mapping(recommendation))
        ),
        no_recommendation_reason=value["no_recommendation_reason"],
        source_ids=tuple(value["source_ids"]),
        limitations=tuple(value["limitations"]),
    )


def _recommendation(value: Mapping[str, Any]) -> RenalDoseRecommendationContent:
    return RenalDoseRecommendationContent(
        action=cast(ContentRecommendationAction, value["action"]),
        dose=_nullable_quantity(value["dose"]),
        route_id=value["route_id"],
        frequency_interval=_nullable_quantity(value["frequency_interval"]),
        infusion_duration=_nullable_quantity(value["infusion_duration"]),
        rationale=value["rationale"],
        monitoring=tuple(value["monitoring"]),
    )


def _source(value: Mapping[str, Any]) -> RenalDoseSourceContent:
    return RenalDoseSourceContent(
        id=value["id"],
        evidence_level=cast(ContentEvidenceLevel, value["evidence_level"]),
        citation=value["citation"],
        source_document=value["source_document"],
        source_version=value["source_version"],
        publication_date=_nullable_date(value["publication_date"]),
        url=value["url"],
    )


def _quantity(value: Mapping[str, Any]) -> RenalDoseQuantity:
    return RenalDoseQuantity(value=Decimal(value["value"]), unit=value["unit"])


def _nullable_quantity(value: object) -> RenalDoseQuantity | None:
    if value is None:
        return None
    return _quantity(_mapping(value))


def _nullable_endpoint(value: object) -> RenalContentEndpoint | None:
    if value is None:
        return None
    endpoint = _mapping(value)
    return RenalContentEndpoint(
        value=Decimal(endpoint["value"]),
        inclusive=endpoint["inclusive"],
    )


def _nullable_date(value: object) -> date | None:
    if value is None:
        return None
    return date.fromisoformat(cast(str, value))


def _mapping(value: object) -> Mapping[str, Any]:
    """Narrow a mapping already proven by the closed schema validator."""

    return cast(Mapping[str, Any], value)
