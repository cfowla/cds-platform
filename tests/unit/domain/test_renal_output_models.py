"""Focused construction tests for renal and dose-output domain models."""

from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal
import json

from cds.domain.enums import RenalMethod, Severity, Sex, WeightType
from cds.domain.models import (
    CodeableConcept,
    Contraindication,
    DoseRecommendation,
    RenalFunctionResult,
    ValueWithUnit,
)

NOW = datetime(2026, 7, 21, 20, tzinfo=UTC)


def test_renal_function_result_has_safe_partial_defaults() -> None:
    result = RenalFunctionResult()

    assert result.method is RenalMethod.UNKNOWN
    assert result.value == ValueWithUnit()
    assert result.normalized_to_bsa is None
    assert result.serum_creatinine == ValueWithUnit()
    assert result.age_years is None
    assert result.sex is Sex.UNKNOWN
    assert result.weight_used == ValueWithUnit()
    assert result.weight_type_used is WeightType.UNKNOWN
    assert result.measured_period == ValueWithUnit()
    assert result.assumptions == []
    assert result.warnings == []
    assert result.evidence == []
    assert result.provenance.source_type == "unknown"


def test_renal_function_result_preserves_reproducible_input_snapshot() -> None:
    result = RenalFunctionResult(
        result_id="renal-123",
        patient_id="patient-123",
        encounter_id="encounter-123",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=Decimal("31.2"), unit="mL/min"),
        normalized_to_bsa=False,
        serum_creatinine=ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
        serum_creatinine_collected_at=NOW,
        age_years=76,
        sex=Sex.FEMALE,
        weight_used=ValueWithUnit(value=Decimal("72.4"), unit="kg"),
        weight_type_used=WeightType.ACTUAL,
        calculated_at=NOW,
    )

    assert result.value.value == Decimal("31.2")
    assert result.value.unit == "mL/min"
    assert result.normalized_to_bsa is False
    assert result.serum_creatinine.value == Decimal("1.8")
    assert result.serum_creatinine_collected_at is NOW
    assert result.age_years == 76
    assert result.sex is Sex.FEMALE
    assert result.weight_used.value == Decimal("72.4")
    assert result.weight_type_used is WeightType.ACTUAL


def test_renal_result_missing_value_is_distinct_from_zero() -> None:
    missing = RenalFunctionResult(value=ValueWithUnit(value=None, unit="mL/min"))
    measured_zero = RenalFunctionResult(
        value=ValueWithUnit(value=Decimal("0"), unit="mL/min")
    )

    assert missing.value.value is None
    assert measured_zero.value.value == Decimal("0")


def test_contraindication_distinguishes_unknown_from_false() -> None:
    unknown = Contraindication()
    not_present = Contraindication(applies=False)

    assert unknown.applies is None
    assert unknown.severity is Severity.UNKNOWN
    assert unknown.related_problem is None
    assert unknown.related_medication is None
    assert unknown.related_lab is None
    assert not_present.applies is False


def test_contraindication_preserves_related_source_concepts() -> None:
    contraindication = Contraindication(
        code="avoid_due_to_allergy",
        summary="Avoid the proposed medication.",
        applies=True,
        rationale="A confirmed related allergy is present.",
        severity=Severity.HIGH,
        related_medication=CodeableConcept(text="Cefepime", system="RxNorm", code="20481"),
    )

    assert contraindication.applies is True
    assert contraindication.severity is Severity.HIGH
    assert contraindication.related_medication == CodeableConcept(
        text="Cefepime", system="RxNorm", code="20481"
    )


def test_dose_recommendation_allows_qualitative_partial_output() -> None:
    recommendation = DoseRecommendation(
        medication=CodeableConcept(text="Cefepime"),
        rationale="Insufficient data for a quantitative regimen.",
    )

    assert recommendation.medication.text == "Cefepime"
    assert recommendation.recommended_dose.value is None
    assert recommendation.recommended_dose.unit is None
    assert recommendation.frequency_interval.value is None
    assert recommendation.rationale == "Insufficient data for a quantitative regimen."


def test_dose_recommendation_preserves_explicit_regimen_units() -> None:
    recommendation = DoseRecommendation(
        medication=CodeableConcept(text="Cefepime", system="RxNorm", code="20481"),
        recommended_dose=ValueWithUnit(value=Decimal("1"), unit="g"),
        recommended_route=CodeableConcept(text="Intravenous", system="HL7", code="IV"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="h"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="min"),
        max_daily_dose=ValueWithUnit(value=Decimal("2"), unit="g/day"),
    )

    assert recommendation.recommended_dose == ValueWithUnit(value=Decimal("1"), unit="g")
    assert recommendation.frequency_interval == ValueWithUnit(value=Decimal("12"), unit="h")
    assert recommendation.infusion_duration == ValueWithUnit(value=Decimal("30"), unit="min")
    assert recommendation.max_daily_dose == ValueWithUnit(value=Decimal("2"), unit="g/day")


def test_nested_defaults_are_independent_across_output_models() -> None:
    first_renal = RenalFunctionResult()
    second_renal = RenalFunctionResult()
    first_dose = DoseRecommendation()
    second_dose = DoseRecommendation()
    first_contraindication = Contraindication()
    second_contraindication = Contraindication()

    assert first_renal.value is not second_renal.value
    assert first_renal.serum_creatinine is not second_renal.serum_creatinine
    assert first_renal.weight_used is not second_renal.weight_used
    assert first_renal.assumptions is not second_renal.assumptions
    assert first_dose.medication is not second_dose.medication
    assert first_dose.recommended_dose is not second_dose.recommended_dose
    assert first_dose.warnings is not second_dose.warnings
    assert first_contraindication.evidence is not second_contraindication.evidence
    assert first_contraindication.provenance is not second_contraindication.provenance


def test_empty_output_models_are_json_safe() -> None:
    payload = {
        "renal": asdict(RenalFunctionResult()),
        "contraindication": asdict(Contraindication()),
        "dose": asdict(DoseRecommendation()),
    }

    encoded = json.dumps(payload)

    assert '"method": "unknown"' in encoded
    assert '"applies": null' in encoded
    assert '"recommended_dose": {"value": null, "unit": null}' in encoded
