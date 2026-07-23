"""Focused tests for exact piperacillin-tazobactam renal-dose rule coverage."""

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
from cds.rules.piperacillin_tazobactam import (
    PIPERACILLIN_TAZOBACTAM_RULE_IMPLEMENTATION_VERSION,
    evaluate_piperacillin_tazobactam_rule,
)

EVALUATED_AT = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)

VARIANTS = (
    (
        "standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes",
        "adult_intra_abdominal_infection",
        "powder_for_solution",
        "3.375",
        "6",
        "30",
        "40",
        "2.25",
        "6",
        "3.375",
        "6",
    ),
    (
        "standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes",
        "adult_nosocomial_pneumonia_initial_presumptive_with_aminoglycoside_context",
        "powder_for_solution",
        "4.5",
        "6",
        "30",
        "40",
        "3.375",
        "6",
        "4.5",
        "6",
    ),
    (
        "extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes",
        "hospitalized_serious_gram_negative_infection",
        None,
        "3.375",
        "8",
        "240",
        "20",
        "3.375",
        "12",
        "3.375",
        "8",
    ),
)


def _quantity(value: str, unit: str) -> RenalDoseQuantity:
    return RenalDoseQuantity(value=Decimal(value), unit=unit)


def _recommendation(
    *,
    dose_value: str,
    frequency_value: str,
    infusion_value: str,
    action: str,
) -> RenalDoseRecommendationContent:
    return RenalDoseRecommendationContent(
        action=action,  # type: ignore[arg-type]
        dose=_quantity(dose_value, "g"),
        route_id="iv",
        frequency_interval=_quantity(frequency_value, "hours"),
        infusion_duration=_quantity(infusion_value, "minutes"),
        rationale="Synthetic software fixture only; not clinical guidance.",
        monitoring=("Synthetic monitoring text.",),
    )


def _content(
    *,
    regimen_id: str = VARIANTS[0][0],
    indication_id: str = VARIANTS[0][1],
    formulation_id: str | None = VARIANTS[0][2],
    base_dose: str = VARIANTS[0][3],
    base_frequency: str = VARIANTS[0][4],
    infusion: str = VARIANTS[0][5],
    threshold: str = VARIANTS[0][6],
    lower_dose: str = VARIANTS[0][7],
    lower_frequency: str = VARIANTS[0][8],
    upper_dose: str = VARIANTS[0][9],
    upper_frequency: str = VARIANTS[0][10],
    review_status: ContentReviewStatus = "reviewed",
    reviewed_content_version: str | None = "1.0.0",
) -> RenalDoseContent:
    reviewed = review_status == "reviewed"
    return RenalDoseContent(
        schema_version="1",
        content_id=f"renal_dose_piperacillin_tazobactam_{regimen_id}_synthetic",
        content_version="1.0.0",
        rule_id=f"piperacillin_tazobactam_{regimen_id}_renal_rule",
        medication=RenalDoseMedicationContent(
            id="piperacillin_tazobactam",
            display="Piperacillin–tazobactam",
        ),
        regimen=RenalDoseRegimenContent(
            id=regimen_id,
            display="Synthetic piperacillin–tazobactam regimen — not clinical guidance",
            indication_ids=(indication_id,),
            route_id="iv",
            formulation_id=formulation_id,
            base_dose=_quantity(base_dose, "g"),
            frequency_interval=_quantity(base_frequency, "hours"),
            infusion_duration=_quantity(infusion, "minutes"),
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
                id=f"at_or_below_{threshold}",
                lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
                upper=RenalContentEndpoint(value=Decimal(threshold), inclusive=True),
                outcome="recommendation",
                recommendation=_recommendation(
                    dose_value=lower_dose,
                    frequency_value=lower_frequency,
                    infusion_value=infusion,
                    action="adjust_dose",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(),
            ),
            RenalDoseBandContent(
                id=f"above_{threshold}",
                lower=RenalContentEndpoint(value=Decimal(threshold), inclusive=False),
                upper=None,
                outcome="recommendation",
                recommendation=_recommendation(
                    dose_value=upper_dose,
                    frequency_value=upper_frequency,
                    infusion_value=infusion,
                    action="continue",
                ),
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
            status=review_status,
            reviewed_content_version=reviewed_content_version if reviewed else None,
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
        medication=CodeableConcept(
            code="piperacillin_tazobactam",
            text="Piperacillin–tazobactam",
        ),
        dose=ValueWithUnit(
            value=content.regimen.base_dose.value,
            unit=content.regimen.base_dose.unit,
        ),
        route=CodeableConcept(code="iv"),
        frequency_interval=ValueWithUnit(
            value=content.regimen.frequency_interval.value,
            unit=content.regimen.frequency_interval.unit,
        ),
        indication=CodeableConcept(code=content.regimen.indication_ids[0]),
        infusion_duration=ValueWithUnit(
            value=content.regimen.infusion_duration.value,
            unit=content.regimen.infusion_duration.unit,
        ),
    )


def _renal(value: str = "40") -> RenalFunctionResult:
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
    regimen_id: str | None | object = ...,
    formulation_id: str | None | object = ...,
    renal_function_stable: bool | None = True,
    renal_replacement_therapy: bool | None = False,
    requested_content_version: str | None = "1.0.0",
):
    content = content or _content()
    if regimen_id is ...:
        regimen_id = content.regimen.id
    if formulation_id is ...:
        formulation_id = content.regimen.formulation_id
    return evaluate_piperacillin_tazobactam_rule(
        order=order or _order(content),
        renal_function=renal or _renal(),
        regimen_id=regimen_id,  # type: ignore[arg-type]
        formulation_id=formulation_id,  # type: ignore[arg-type]
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=renal_replacement_therapy,
        requested_content_version=requested_content_version,
        content=content,
        evaluated_at=EVALUATED_AT,
    )


@pytest.mark.parametrize("variant", VARIANTS)
def test_each_selected_regimen_exact_context_returns_structured_recommendation(variant) -> None:
    content = _content(
        regimen_id=variant[0],
        indication_id=variant[1],
        formulation_id=variant[2],
        base_dose=variant[3],
        base_frequency=variant[4],
        infusion=variant[5],
        threshold=variant[6],
        lower_dose=variant[7],
        lower_frequency=variant[8],
        upper_dose=variant[9],
        upper_frequency=variant[10],
    )

    result = _evaluate(content=content, renal=_renal(variant[6]))

    assert result.status is ResultStatus.SUCCESS
    assert result.applied is True
    assert result.passed is True
    assert result.supporting_data["outcome_category"] == "recommendation"
    assert result.supporting_data["rule_implementation_version"] == (
        PIPERACILLIN_TAZOBACTAM_RULE_IMPLEMENTATION_VERSION
    )
    assert result.supporting_data["renal_band_id"] == f"at_or_below_{variant[6]}"
    assert len(result.recommendations) == 1
    recommendation = result.recommendations[0]
    assert recommendation.title == "Piperacillin–tazobactam renal-dose recommendation"
    assert recommendation.linked_rule_id == content.rule_id
    assert recommendation.dose_recommendation is not None
    assert recommendation.dose_recommendation.recommended_dose.value == Decimal(variant[7])
    assert recommendation.dose_recommendation.recommended_dose.unit == "g"
    assert recommendation.provenance.version == "1.0.0"


@pytest.mark.parametrize(
    ("variant", "renal_value", "expected_band", "expected_frequency"),
    [
        (VARIANTS[0], "40", "at_or_below_40", "6"),
        (VARIANTS[0], "40.000000000000000001", "above_40", "6"),
        (VARIANTS[2], "20", "at_or_below_20", "12"),
        (VARIANTS[2], "20.000000000000000001", "above_20", "8"),
    ],
)
def test_unrounded_boundaries_select_one_exact_band(
    variant,
    renal_value: str,
    expected_band: str,
    expected_frequency: str,
) -> None:
    content = _content(
        regimen_id=variant[0],
        indication_id=variant[1],
        formulation_id=variant[2],
        base_dose=variant[3],
        base_frequency=variant[4],
        infusion=variant[5],
        threshold=variant[6],
        lower_dose=variant[7],
        lower_frequency=variant[8],
        upper_dose=variant[9],
        upper_frequency=variant[10],
    )

    result = _evaluate(content=content, renal=_renal(renal_value))

    assert result.supporting_data["renal_band_id"] == expected_band
    dose = result.recommendations[0].dose_recommendation
    assert dose is not None
    assert dose.frequency_interval.value == Decimal(expected_frequency)
    assert dose.frequency_interval.unit == "hours"


def test_extended_infusion_exact_null_formulation_is_supported() -> None:
    variant = VARIANTS[2]
    content = _content(
        regimen_id=variant[0],
        indication_id=variant[1],
        formulation_id=None,
        base_dose=variant[3],
        base_frequency=variant[4],
        infusion=variant[5],
        threshold=variant[6],
        lower_dose=variant[7],
        lower_frequency=variant[8],
        upper_dose=variant[9],
        upper_frequency=variant[10],
    )

    result = _evaluate(content=content, formulation_id=None, renal=_renal("20"))

    assert result.status is ResultStatus.SUCCESS
    assert result.recommendations[0].dose_recommendation is not None
    assert result.recommendations[0].dose_recommendation.infusion_duration.value == Decimal("240")


def test_total_product_grams_are_preserved_without_hidden_component_conversion() -> None:
    result = _evaluate(renal=_renal("40"))

    dose = result.recommendations[0].dose_recommendation
    assert dose is not None
    assert dose.recommended_dose.value == Decimal("2.25")
    assert dose.recommended_dose.unit == "g"


@pytest.mark.parametrize(
    ("case", "warning_code"),
    [
        ("regimen", "unsupported_piperacillin_tazobactam_regimen"),
        ("indication", "unsupported_piperacillin_tazobactam_indication"),
        ("route", "unsupported_piperacillin_tazobactam_route"),
        ("formulation", "unsupported_piperacillin_tazobactam_formulation"),
        ("dose", "unsupported_piperacillin_tazobactam_dose"),
        ("frequency", "unsupported_piperacillin_tazobactam_frequency"),
        ("infusion", "unsupported_piperacillin_tazobactam_infusion"),
        ("renal_method", "unsupported_piperacillin_tazobactam_renal_method"),
        ("renal_unit", "unsupported_piperacillin_tazobactam_renal_unit"),
        ("unstable", "unsupported_unstable_renal_function"),
        ("rrt", "unsupported_renal_replacement_therapy"),
    ],
)
def test_nonexact_or_unsupported_context_fails_closed_with_warning(
    case: str,
    warning_code: str,
) -> None:
    content = _content()
    order = _order(content)
    renal = _renal()
    kwargs: dict[str, object] = {}

    if case == "regimen":
        kwargs["regimen_id"] = f"{content.regimen.id} "
    elif case == "indication":
        order = replace(order, indication=CodeableConcept(code="unsupported_indication"))
    elif case == "route":
        order = replace(order, route=CodeableConcept(code="IV"))
    elif case == "formulation":
        kwargs["formulation_id"] = "injectable"
    elif case == "dose":
        order = replace(order, dose=ValueWithUnit(value=Decimal("3375"), unit="mg"))
    elif case == "frequency":
        order = replace(order, frequency_interval=ValueWithUnit(value=Decimal("6"), unit="Hours"))
    elif case == "infusion":
        order = replace(order, infusion_duration=ValueWithUnit(value=Decimal("0.5"), unit="hours"))
    elif case == "renal_method":
        renal = replace(renal, method=RenalMethod.CKD_EPI)
    elif case == "renal_unit":
        renal = replace(renal, value=ValueWithUnit(value=Decimal("40"), unit="mL/min/1.73m2"))
    elif case == "unstable":
        kwargs["renal_function_stable"] = False
    elif case == "rrt":
        kwargs["renal_replacement_therapy"] = True

    result = _evaluate(
        content=content, order=order, renal=renal, **kwargs
    )  # type: ignore[arg-type]

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.supporting_data["outcome_category"] == "unsupported"
    assert result.applied is False
    assert result.passed is None
    assert result.recommendations == []
    assert [warning.code for warning in result.warnings] == [warning_code]


@pytest.mark.parametrize("missing", ["medication", "regimen", "dose", "version", "stable"])
def test_missing_required_context_is_incomplete_without_recommendation(missing: str) -> None:
    content = _content()
    order = _order(content)
    kwargs: dict[str, object] = {}

    if missing == "medication":
        order = replace(order, medication=CodeableConcept(code=None))
    elif missing == "regimen":
        kwargs["regimen_id"] = None
    elif missing == "dose":
        order = replace(order, dose=ValueWithUnit(value=None, unit="g"))
    elif missing == "version":
        kwargs["requested_content_version"] = None
    elif missing == "stable":
        kwargs["renal_function_stable"] = None

    result = _evaluate(content=content, order=order, **kwargs)  # type: ignore[arg-type]

    assert result.status is ResultStatus.INCOMPLETE
    assert result.supporting_data["outcome_category"] == "incomplete"
    assert result.applied is False
    assert result.passed is None
    assert result.warnings == []
    assert result.recommendations == []


def test_non_piperacillin_tazobactam_medication_is_not_applicable() -> None:
    content = _content()
    order = replace(_order(content), medication=CodeableConcept(code="cefepime"))

    result = _evaluate(content=content, order=order)

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.supporting_data["outcome_category"] == "not_applicable"
    assert result.warnings == []
    assert result.recommendations == []


@pytest.mark.parametrize("review_status", ["draft", "retired"])
def test_unreviewed_or_retired_content_is_never_eligible(
    review_status: ContentReviewStatus,
) -> None:
    result = _evaluate(content=_content(review_status=review_status))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.supporting_data["outcome_category"] == "incomplete"
    assert result.applied is False
    assert result.recommendations == []


def test_reviewed_content_version_must_match_immutable_document_version() -> None:
    result = _evaluate(content=_content(reviewed_content_version="0.9.0"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.recommendations == []


def test_patient_identity_mismatch_is_incomplete() -> None:
    result = _evaluate(renal=replace(_renal(), patient_id="different-patient"))

    assert result.status is ResultStatus.INCOMPLETE
    assert result.supporting_data["outcome_category"] == "incomplete"
    assert result.recommendations == []
