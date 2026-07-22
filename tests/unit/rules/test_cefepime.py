"""Focused tests for the exact-context cefepime renal-dose rule."""

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
    ContentReviewStatus,
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
from cds.rules.cefepime import CEFEPIME_RULE_IMPLEMENTATION_VERSION, evaluate_cefepime_rule

EVALUATED_AT = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)


def _quantity(value: str, unit: str) -> RenalDoseQuantity:
    return RenalDoseQuantity(value=Decimal(value), unit=unit)


def _recommendation(
    *,
    action: str,
    dose_value: str,
    dose_unit: str,
    frequency_value: str,
) -> RenalDoseRecommendationContent:
    return RenalDoseRecommendationContent(
        action=action,  # type: ignore[arg-type]
        dose=_quantity(dose_value, dose_unit),
        route_id="iv",
        frequency_interval=_quantity(frequency_value, "hours"),
        infusion_duration=_quantity("30", "minutes"),
        rationale="Synthetic software fixture only; not clinical guidance.",
        monitoring=("Synthetic monitoring text.",),
    )


def _content(
    *,
    review_status: ContentReviewStatus = "reviewed",
    reviewed_content_version: str | None = "1.0.0",
    bands: tuple[RenalDoseBandContent, ...] | None = None,
) -> RenalDoseContent:
    if bands is None:
        bands = (
            RenalDoseBandContent(
                id="below_30",
                lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
                upper=RenalContentEndpoint(value=Decimal("30"), inclusive=False),
                outcome="recommendation",
                recommendation=_recommendation(
                    action="adjust_dose",
                    dose_value="500",
                    dose_unit="mg",
                    frequency_value="24",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
            RenalDoseBandContent(
                id="at_or_above_30",
                lower=RenalContentEndpoint(value=Decimal("30"), inclusive=True),
                upper=None,
                outcome="recommendation",
                recommendation=_recommendation(
                    action="continue",
                    dose_value="2",
                    dose_unit="g",
                    frequency_value="12",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
        )

    reviewed = review_status == "reviewed"
    return RenalDoseContent(
        schema_version="1",
        content_id="renal_dose_cefepime_synthetic_iv_2_g_q12h",
        content_version="1.0.0",
        rule_id="cefepime_synthetic_renal_rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Cefepime"),
        regimen=RenalDoseRegimenContent(
            id="synthetic_iv_2_g_q12h_over_30_minutes",
            display="Synthetic cefepime regimen — not clinical guidance",
            indication_ids=("synthetic_indication",),
            route_id="iv",
            formulation_id="powder_for_solution",
            base_dose=_quantity("2", "g"),
            frequency_interval=_quantity("12", "hours"),
            infusion_duration=_quantity("30", "minutes"),
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
        renal_bands=bands,
        sources=(
            RenalDoseSourceContent(
                id="synthetic_source",
                evidence_level="expert_opinion",
                citation="Synthetic source with no clinical authority.",
                source_document="Synthetic fixture specification",
                source_version="1",
                publication_date=date(2026, 7, 22),
                url=None,
            ),
        ),
        review=RenalDoseReviewContent(
            status=review_status,
            reviewed_content_version=reviewed_content_version if reviewed else None,
            reviewer="Synthetic Reviewer" if reviewed else None,
            reviewer_role="Software test fixture reviewer" if reviewed else None,
            reviewed_on=date(2026, 7, 22) if reviewed else None,
            notes="Synthetic fixture only; not clinical guidance.",
        ),
        limitations=("Prototype only — not for direct clinical use.",),
    )


def _order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order-1",
        patient_id="synthetic-patient-1",
        encounter_id="synthetic-encounter-1",
        medication=CodeableConcept(code="cefepime", text="Cefepime"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="hours"),
        indication=CodeableConcept(code="synthetic_indication"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="minutes"),
    )


def _renal(value: str = "30") -> RenalFunctionResult:
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
    order: MedicationOrder | None = None,
    renal: RenalFunctionResult | None = None,
    content: RenalDoseContent | None = None,
    regimen_id: str | None = "synthetic_iv_2_g_q12h_over_30_minutes",
    formulation_id: str | None = "powder_for_solution",
    renal_function_stable: bool | None = True,
    renal_replacement_therapy: bool | None = False,
    requested_content_version: str | None = "1.0.0",
):
    return evaluate_cefepime_rule(
        order=order or _order(),
        renal_function=renal or _renal(),
        regimen_id=regimen_id,
        formulation_id=formulation_id,
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=renal_replacement_therapy,
        requested_content_version=requested_content_version,
        content=content or _content(),
        evaluated_at=EVALUATED_AT,
    )


def test_exact_reviewed_context_returns_structured_recommendation_and_versions() -> None:
    result = _evaluate()

    assert result.status is ResultStatus.SUCCESS
    assert result.applied is True
    assert result.passed is True
    assert result.rule_id == "cefepime_synthetic_renal_rule"
    assert result.supporting_data["content_version"] == "1.0.0"
    assert (
        result.supporting_data["rule_implementation_version"]
        == CEFEPIME_RULE_IMPLEMENTATION_VERSION
    )
    assert result.supporting_data["renal_band_id"] == "at_or_above_30"
    assert result.evaluated_at == EVALUATED_AT
    assert len(result.recommendations) == 1

    recommendation = result.recommendations[0]
    assert recommendation.linked_order_id == "synthetic-order-1"
    assert recommendation.linked_rule_id == "cefepime_synthetic_renal_rule"
    assert recommendation.action == "continue"
    assert recommendation.dose_recommendation is not None
    assert recommendation.dose_recommendation.recommended_dose.value == Decimal("2")
    assert recommendation.dose_recommendation.recommended_dose.unit == "g"
    assert recommendation.suggested_monitoring == ["Synthetic monitoring text."]
    assert recommendation.evidence[0].citation == "Synthetic source with no clinical authority."
    assert recommendation.provenance.version == "1.0.0"


def test_rule_preserves_source_dose_unit_without_hidden_conversion() -> None:
    result = _evaluate(renal=_renal("29.999999999999999999"))

    dose = result.recommendations[0].dose_recommendation
    assert result.supporting_data["renal_band_id"] == "below_30"
    assert dose is not None
    assert dose.recommended_dose.value == Decimal("500")
    assert dose.recommended_dose.unit == "mg"


@pytest.mark.parametrize(
    "case",
    [
        "medication",
        "regimen",
        "indication",
        "route",
        "formulation",
        "dose_value",
        "dose_unit",
        "frequency",
        "infusion",
        "age",
        "renal_method",
        "renal_unit",
        "indexed",
        "unstable",
        "rrt",
        "version",
        "patient",
    ],
)
def test_missing_or_nonexact_required_context_fails_closed(case: str) -> None:
    order = _order()
    renal = _renal()
    kwargs: dict[str, object] = {}

    if case == "medication":
        order = replace(order, medication=CodeableConcept(code="Cefepime"))
    elif case == "regimen":
        kwargs["regimen_id"] = "synthetic_iv_2_g_q12h_over_30_minutes "
    elif case == "indication":
        order = replace(order, indication=CodeableConcept(code="unsupported_indication"))
    elif case == "route":
        order = replace(order, route=CodeableConcept(code="IV"))
    elif case == "formulation":
        kwargs["formulation_id"] = "injectable"
    elif case == "dose_value":
        order = replace(order, dose=ValueWithUnit(value=Decimal("2000"), unit="g"))
    elif case == "dose_unit":
        order = replace(order, dose=ValueWithUnit(value=Decimal("2"), unit="G"))
    elif case == "frequency":
        order = replace(order, frequency_interval=ValueWithUnit(value=Decimal("12"), unit="Hours"))
    elif case == "infusion":
        order = replace(order, infusion_duration=ValueWithUnit(value=Decimal("0.5"), unit="hours"))
    elif case == "age":
        renal = replace(renal, age_years=None)
    elif case == "renal_method":
        renal = replace(renal, method=RenalMethod.CKD_EPI)
    elif case == "renal_unit":
        renal = replace(renal, value=ValueWithUnit(value=Decimal("30"), unit="mL/min/1.73m2"))
    elif case == "indexed":
        renal = replace(renal, normalized_to_bsa=True)
    elif case == "unstable":
        kwargs["renal_function_stable"] = False
    elif case == "rrt":
        kwargs["renal_replacement_therapy"] = True
    elif case == "version":
        kwargs["requested_content_version"] = "latest"
    elif case == "patient":
        renal = replace(renal, patient_id="different-patient")

    result = _evaluate(order=order, renal=renal, **kwargs)  # type: ignore[arg-type]

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.passed is None
    assert result.recommendations == []


@pytest.mark.parametrize("review_status", ["draft", "retired"])
def test_draft_or_retired_content_is_never_eligible(review_status: ContentReviewStatus) -> None:
    result = _evaluate(content=_content(review_status=review_status))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.recommendations == []


def test_reviewed_content_version_must_equal_the_immutable_document_version() -> None:
    result = _evaluate(content=_content(reviewed_content_version="0.9.0"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.recommendations == []


def test_zero_matching_bands_fails_closed_without_a_dose_recommendation() -> None:
    result = _evaluate(renal=_renal("0"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.recommendations == []


def test_multiple_matching_bands_fails_closed_without_selecting_one() -> None:
    overlapping_bands = (
        RenalDoseBandContent(
            id="first_overlap",
            lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
            upper=RenalContentEndpoint(value=Decimal("60"), inclusive=True),
            outcome="recommendation",
            recommendation=_recommendation(
                action="adjust_dose", dose_value="1", dose_unit="g", frequency_value="24"
            ),
            no_recommendation_reason=None,
            source_ids=("synthetic_source",),
            limitations=(),
        ),
        RenalDoseBandContent(
            id="second_overlap",
            lower=RenalContentEndpoint(value=Decimal("30"), inclusive=True),
            upper=None,
            outcome="recommendation",
            recommendation=_recommendation(
                action="continue", dose_value="2", dose_unit="g", frequency_value="12"
            ),
            no_recommendation_reason=None,
            source_ids=("synthetic_source",),
            limitations=(),
        ),
    )

    result = _evaluate(content=_content(bands=overlapping_bands), renal=_renal("45"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.recommendations == []
    assert "zero or multiple" in (result.summary or "")


def test_explicit_no_recommendation_band_contains_no_dose_recommendation() -> None:
    no_recommendation_band = RenalDoseBandContent(
        id="no_recommendation",
        lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
        upper=None,
        outcome="no_recommendation",
        recommendation=None,
        no_recommendation_reason="Synthetic no-recommendation outcome.",
        source_ids=("synthetic_source",),
        limitations=(),
    )

    result = _evaluate(content=_content(bands=(no_recommendation_band,)), renal=_renal("10"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is True
    assert result.passed is False
    assert result.recommendations == []
    assert result.summary == "Synthetic no-recommendation outcome."
