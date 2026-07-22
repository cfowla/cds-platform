"""Tests for renal-function and dosing-output support models."""

from datetime import UTC, date, datetime
from decimal import Decimal

from cds.domain.enums import RenalMethod, Severity, Sex, WeightType
from cds.domain.models import (
    CodeableConcept,
    Contraindication,
    DoseRecommendation,
    RenalFunctionResult,
    ValueWithUnit,
)


def test_renal_function_defaults_do_not_claim_a_method_or_result() -> None:
    result = RenalFunctionResult()

    assert result.method is RenalMethod.UNKNOWN
    assert result.value == ValueWithUnit()
    assert result.normalized_to_bsa is None
    assert result.evaluation_date is None
    assert result.serum_creatinine == ValueWithUnit()
    assert result.age_years is None
    assert result.sex is Sex.UNKNOWN
    assert result.weight_used == ValueWithUnit()
    assert result.weight_type_used is WeightType.UNKNOWN


def test_renal_function_result_preserves_reproducible_input_context() -> None:
    collected_at = datetime(2026, 7, 21, 14, tzinfo=UTC)
    calculated_at = datetime(2026, 7, 21, 15, tzinfo=UTC)
    result = RenalFunctionResult(
        result_id="renal-123",
        patient_id="patient-123",
        encounter_id="encounter-123",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=Decimal("31.2"), unit="mL/min"),
        normalized_to_bsa=False,
        evaluation_date=date(2026, 7, 21),
        serum_creatinine_result_id="lab-123",
        serum_creatinine=ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
        serum_creatinine_collected_at=collected_at,
        age_years=76,
        sex=Sex.FEMALE,
        weight_used=ValueWithUnit(value=Decimal("72.4"), unit="kg"),
        weight_type_used=WeightType.ACTUAL,
        calculated_at=calculated_at,
    )

    assert result.value == ValueWithUnit(value=Decimal("31.2"), unit="mL/min")
    assert result.normalized_to_bsa is False
    assert result.serum_creatinine_result_id == "lab-123"
    assert result.serum_creatinine_collected_at == collected_at
    assert result.weight_type_used is WeightType.ACTUAL
    assert result.calculated_at == calculated_at


def test_contraindication_distinguishes_unevaluated_from_not_applicable() -> None:
    unevaluated = Contraindication()
    negative = Contraindication(
        code="synthetic-renal-contraindication",
        summary="Synthetic contraindication for testing.",
        applies=False,
        severity=Severity.HIGH,
    )

    assert unevaluated.applies is None
    assert unevaluated.severity is Severity.UNKNOWN
    assert negative.applies is False
    assert negative.severity is Severity.HIGH


def test_dose_recommendation_preserves_explicit_units_and_text_only_medication() -> None:
    recommendation = DoseRecommendation(
        medication=CodeableConcept(text="Cefepime"),
        recommended_dose=ValueWithUnit(value=Decimal("1"), unit="g"),
        recommended_route=CodeableConcept(text="Intravenous"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="h"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="min"),
        regimen_variant="standard-infusion",
    )

    assert recommendation.medication.system is None
    assert recommendation.medication.code is None
    assert recommendation.recommended_dose == ValueWithUnit(value=Decimal("1"), unit="g")
    assert recommendation.frequency_interval.unit == "h"
    assert recommendation.infusion_duration.unit == "min"


def test_missing_recommended_dose_is_distinct_from_true_zero() -> None:
    missing = DoseRecommendation(recommended_dose=ValueWithUnit(unit="mg"))
    zero = DoseRecommendation(
        recommended_dose=ValueWithUnit(value=Decimal("0"), unit="mg")
    )

    assert missing.recommended_dose.value is None
    assert zero.recommended_dose.value == Decimal("0")
    assert missing.recommended_dose != zero.recommended_dose
