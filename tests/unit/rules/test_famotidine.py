"""Focused tests for exact famotidine renal-dose rule coverage."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from cds.domain.clinical import MedicationOrder
from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.outputs import RenalFunctionResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    RenalContentEndpoint,
    RenalContentInterval,
    RenalDoseBandContent,
    RenalDoseContent,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRecommendationContent,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSourceContent,
    RenalDoseSupportedContext,
)
from cds.rules.famotidine import (
    FAMOTIDINE_RULE_IMPLEMENTATION_VERSION,
    evaluate_famotidine_rule,
)

EVALUATED_AT = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
REGIMEN_ID = "oral_film_coated_tablet_20_mg_every_12_hours"
INDICATION_ID = "adult_symptomatic_nonerosive_gerd"
FORMULATION_ID = "film_coated_tablet"


def _quantity(value: str, unit: str) -> RenalDoseQuantity:
    return RenalDoseQuantity(value=Decimal(value), unit=unit)


def _recommendation(frequency: str, action: str) -> RenalDoseRecommendationContent:
    return RenalDoseRecommendationContent(
        action=action,  # type: ignore[arg-type]
        dose=_quantity("20", "mg"),
        route_id="po",
        frequency_interval=_quantity(frequency, "hours"),
        infusion_duration=None,
        rationale="Synthetic software fixture only; not clinical guidance.",
        monitoring=("Synthetic monitoring text.",),
    )


def _content(*, reviewed: bool = True) -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="renal_dose_famotidine_synthetic",
        content_version="1.0.0",
        rule_id="famotidine_synthetic_renal_rule",
        medication=RenalDoseMedicationContent(id="famotidine", display="Famotidine"),
        regimen=RenalDoseRegimenContent(
            id=REGIMEN_ID,
            display="Synthetic famotidine regimen — not clinical guidance",
            indication_ids=(INDICATION_ID,),
            route_id="po",
            formulation_id=FORMULATION_ID,
            base_dose=_quantity("20", "mg"),
            frequency_interval=_quantity("12", "hours"),
            infusion_duration=None,
        ),
        supported_context=RenalDoseSupportedContext(
            minimum_age_years=18,
            renal_method="cockcroft_gault",
            renal_unit="mL/min",
            renal_function_stable=True,
            renal_replacement_therapy=False,
            limitations=("Synthetic software fixture only.",),
        ),
        renal_domain=RenalContentInterval(
            lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
            upper=None,
        ),
        renal_bands=(
            RenalDoseBandContent(
                id="below_30",
                lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
                upper=RenalContentEndpoint(value=Decimal("30"), inclusive=False),
                outcome="recommendation",
                recommendation=_recommendation("48", "adjust_dose"),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
            RenalDoseBandContent(
                id="crcl_30_to_below_60",
                lower=RenalContentEndpoint(value=Decimal("30"), inclusive=True),
                upper=RenalContentEndpoint(value=Decimal("60"), inclusive=False),
                outcome="recommendation",
                recommendation=_recommendation("24", "adjust_dose"),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
            RenalDoseBandContent(
                id="at_or_above_60",
                lower=RenalContentEndpoint(value=Decimal("60"), inclusive=True),
                upper=None,
                outcome="recommendation",
                recommendation=_recommendation("12", "continue"),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
        ),
        sources=(
            RenalDoseSourceContent(
                id="synthetic_source",
                evidence_level="expert_opinion",
                citation="Synthetic source with no clinical authority.",
                source_document="Synthetic fixture specification",
                source_version="1",
                publication_date=date(2026, 7, 23),
                url=None,
            ),
        ),
        review=RenalDoseReviewContent(
            status="reviewed" if reviewed else "draft",
            reviewed_content_version="1.0.0" if reviewed else None,
            reviewer="Synthetic Reviewer" if reviewed else None,
            reviewer_role="Software test fixture reviewer" if reviewed else None,
            reviewed_on=date(2026, 7, 23) if reviewed else None,
            notes="Synthetic fixture only; not clinical guidance.",
        ),
        limitations=("Prototype only — not for direct clinical use.",),
    )


def _order(content: RenalDoseContent | None = None) -> MedicationOrder:
    content = content or _content()
    return MedicationOrder(
        order_id="synthetic-order-1",
        patient_id="synthetic-patient-1",
        encounter_id="synthetic-encounter-1",
        medication=CodeableConcept(code="famotidine", text="Famotidine"),
        dose=ValueWithUnit(value=Decimal("20"), unit="mg"),
        route=CodeableConcept(code="po"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="hours"),
        indication=CodeableConcept(code=INDICATION_ID),
        infusion_duration=None,
    )


def _renal(value: str = "60") -> RenalFunctionResult:
    return RenalFunctionResult(
        result_id="synthetic-renal-1",
        patient_id="synthetic-patient-1",
        encounter_id="synthetic-encounter-1",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=Decimal(value), unit="mL/min"),
        normalized_to_bsa=False,
        age_years=65,
    )


def _evaluate(
    *,
    content: RenalDoseContent | None = None,
    order: MedicationOrder | None = None,
    renal: RenalFunctionResult | None = None,
    regimen_id: str | None = REGIMEN_ID,
    formulation_id: str | None = FORMULATION_ID,
    renal_function_stable: bool | None = True,
    renal_replacement_therapy: bool | None = False,
    requested_content_version: str | None = "1.0.0",
):
    content = content or _content()
    return evaluate_famotidine_rule(
        order=order or _order(content),
        renal_function=renal or _renal(),
        regimen_id=regimen_id,
        formulation_id=formulation_id,
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=renal_replacement_therapy,
        requested_content_version=requested_content_version,
        content=content,
        evaluated_at=EVALUATED_AT,
    )


@pytest.mark.parametrize(
    ("renal_value", "expected_band", "expected_frequency"),
    [
        ("29.999999999999999999", "below_30", "48"),
        ("30", "crcl_30_to_below_60", "24"),
        ("59.999999999999999999", "crcl_30_to_below_60", "24"),
        ("60", "at_or_above_60", "12"),
    ],
)
def test_exact_unrounded_boundaries_return_one_structured_recommendation(
    renal_value: str,
    expected_band: str,
    expected_frequency: str,
) -> None:
    result = _evaluate(renal=_renal(renal_value))

    assert result.status is ResultStatus.SUCCESS
    assert result.applied is True
    assert result.passed is True
    assert result.supporting_data["outcome_category"] == "recommendation"
    assert result.supporting_data["renal_band_id"] == expected_band
    assert result.supporting_data["rule_implementation_version"] == (
        FAMOTIDINE_RULE_IMPLEMENTATION_VERSION
    )
    assert len(result.recommendations) == 1
    recommendation = result.recommendations[0]
    assert recommendation.title == "Famotidine renal-dose recommendation"
    assert recommendation.linked_rule_id == "famotidine_synthetic_renal_rule"
    assert recommendation.dose_recommendation is not None
    assert recommendation.dose_recommendation.recommended_dose.value == Decimal("20")
    assert recommendation.dose_recommendation.recommended_dose.unit == "mg"
    assert recommendation.dose_recommendation.frequency_interval.value == Decimal(
        expected_frequency
    )
    assert recommendation.dose_recommendation.frequency_interval.unit == "hours"
    assert recommendation.dose_recommendation.infusion_duration is None


def test_draft_content_fails_closed_without_recommendation() -> None:
    result = _evaluate(content=_content(reviewed=False))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.passed is None
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "incomplete"


@pytest.mark.parametrize(
    ("change", "warning_code"),
    [
        ({"regimen_id": "oral_suspension_20_mg_every_12_hours"}, "unsupported_famotidine_regimen"),
        ({"formulation_id": "oral_suspension"}, "unsupported_famotidine_formulation"),
        ({"renal_function_stable": False}, "unsupported_unstable_renal_function"),
        ({"renal_replacement_therapy": True}, "unsupported_renal_replacement_therapy"),
    ],
)
def test_unsupported_context_fails_closed(change: dict[str, object], warning_code: str) -> None:
    result = _evaluate(**change)  # type: ignore[arg-type]

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.applied is False
    assert result.passed is False
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "unsupported"
    assert [warning.code for warning in result.warnings] == [warning_code]


def test_non_famotidine_order_is_not_applicable() -> None:
    order = replace(
        _order(),
        medication=CodeableConcept(code="cefepime", text="Cefepime"),
    )

    result = _evaluate(order=order)

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.applied is False
    assert result.passed is False
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "not_applicable"


def test_missing_required_formulation_is_incomplete() -> None:
    result = _evaluate(formulation_id=None)

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.passed is None
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "incomplete"
