"""Focused tests for passive clinical source-of-truth models."""

from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from cds.domain.clinical import (
    Allergy,
    Encounter,
    LabResult,
    MedicationOrder,
    Patient,
    Problem,
    VitalSign,
)
from cds.domain.enums import Severity, Sex
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit


def test_patient_defaults_preserve_missing_data() -> None:
    patient = Patient()

    assert patient.patient_id is None
    assert patient.birth_date is None
    assert patient.sex is Sex.UNKNOWN
    assert patient.actual_body_weight == ValueWithUnit()
    assert patient.height == ValueWithUnit()
    assert patient.assumptions == []
    assert patient.warnings == []
    assert patient.evidence == []


def test_patient_preserves_partial_source_data_without_derived_fields() -> None:
    patient = Patient(
        patient_id="patient-123",
        birth_date=date(1950, 6, 1),
        sex=Sex.FEMALE,
        actual_body_weight=ValueWithUnit(value=Decimal("72.4"), unit="kg"),
    )

    assert patient.patient_id == "patient-123"
    assert patient.actual_body_weight == ValueWithUnit(value=Decimal("72.4"), unit="kg")
    assert patient.height.value is None
    for derived_field in (
        "age",
        "age_years",
        "bmi",
        "ideal_body_weight",
        "adjusted_body_weight",
    ):
        assert not hasattr(patient, derived_field)


def test_encounter_preserves_partial_source_data() -> None:
    admitted_at = datetime(2026, 7, 21, 14, tzinfo=UTC)
    encounter = Encounter(
        encounter_id="encounter-456",
        patient_id="patient-123",
        encounter_type=CodeableConcept(text="Inpatient", system="HL7", code="IMP"),
        period=TimeRange(start=admitted_at),
        location="4 East",
    )

    assert encounter.encounter_type.code == "IMP"
    assert encounter.period.start == admitted_at
    assert encounter.period.end is None
    assert encounter.location == "4 East"
    assert encounter.service_line is None


def test_medication_order_preserves_regimen_data_and_units() -> None:
    started_at = datetime(2026, 7, 21, 20, tzinfo=UTC)
    order = MedicationOrder(
        order_id="order-123",
        patient_id="patient-123",
        encounter_id="encounter-456",
        medication=CodeableConcept(text="Cefepime", system="RxNorm", code="20481"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(text="Intravenous", system="HL7", code="IV"),
        frequency_interval=ValueWithUnit(value=Decimal("8"), unit="h"),
        ordered_period=TimeRange(start=started_at),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="min"),
    )

    assert order.medication.code == "20481"
    assert order.dose == ValueWithUnit(value=Decimal("2"), unit="g")
    assert order.frequency_interval.unit == "h"
    assert order.ordered_period.end is None
    assert order.prn is None


def test_lab_result_preserves_observation_data_and_units() -> None:
    collected_at = datetime(2026, 7, 21, 19, 45, tzinfo=UTC)
    result = LabResult(
        result_id="lab-123",
        patient_id="patient-123",
        encounter_id="encounter-456",
        test=CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0"),
        value=ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
        collected_at=collected_at,
        status="final",
    )

    assert result.test.code == "2160-0"
    assert result.value == ValueWithUnit(value=Decimal("1.8"), unit="mg/dL")
    assert result.collected_at == collected_at
    assert result.resulted_at is None
    assert result.reference_range_low.value is None


def test_vital_sign_preserves_measurement_data_and_explicit_false() -> None:
    measured_at = datetime(2026, 7, 21, 19, 50, tzinfo=UTC)
    vital = VitalSign(
        vital_id="vital-123",
        patient_id="patient-123",
        encounter_id="encounter-456",
        vital=CodeableConcept(text="Oxygen saturation", system="LOINC", code="59408-5"),
        value=ValueWithUnit(value=Decimal("96"), unit="%"),
        measured_at=measured_at,
        supplemental_oxygen=False,
    )

    assert vital.vital.code == "59408-5"
    assert vital.value == ValueWithUnit(value=Decimal("96"), unit="%")
    assert vital.measured_at == measured_at
    assert vital.supplemental_oxygen is False
    assert vital.position is None


@pytest.mark.parametrize(
    ("missing", "zero"),
    [
        (
            MedicationOrder(dose=ValueWithUnit(unit="mg")),
            MedicationOrder(dose=ValueWithUnit(value=Decimal("0"), unit="mg")),
        ),
        (
            LabResult(value=ValueWithUnit(unit="mg/dL")),
            LabResult(value=ValueWithUnit(value=Decimal("0"), unit="mg/dL")),
        ),
        (
            VitalSign(value=ValueWithUnit(unit="%")),
            VitalSign(value=ValueWithUnit(value=Decimal("0"), unit="%")),
        ),
    ],
)
def test_missing_numeric_value_is_distinct_from_true_zero(
    missing: MedicationOrder | LabResult | VitalSign,
    zero: MedicationOrder | LabResult | VitalSign,
) -> None:
    missing_quantity = missing.dose if isinstance(missing, MedicationOrder) else missing.value
    zero_quantity = zero.dose if isinstance(zero, MedicationOrder) else zero.value

    assert missing_quantity.value is None
    assert zero_quantity.value == Decimal("0")
    assert missing_quantity != zero_quantity


def test_problem_supports_text_only_concept_without_fabricated_coding() -> None:
    problem = Problem(
        problem_id="problem-123",
        patient_id="patient-123",
        problem=CodeableConcept(text="Chronic kidney disease"),
        onset_period=TimeRange(start=datetime(2025, 4, 1, tzinfo=UTC)),
        status="active",
        severity=Severity.HIGH,
    )

    assert problem.problem.text == "Chronic kidney disease"
    assert problem.problem.system is None
    assert problem.problem.code is None
    assert problem.severity is Severity.HIGH


def test_allergy_supports_text_only_substance_and_reaction() -> None:
    allergy = Allergy(
        allergy_id="allergy-123",
        patient_id="patient-123",
        substance=CodeableConcept(text="Penicillin"),
        reaction=CodeableConcept(text="Pruritic rash"),
        severity=Severity.MODERATE,
        verification_status="confirmed",
    )

    assert allergy.substance == CodeableConcept(text="Penicillin")
    assert allergy.reaction == CodeableConcept(text="Pruritic rash")
    assert allergy.substance.system is None
    assert allergy.substance.code is None
    assert allergy.reaction.system is None
    assert allergy.reaction.code is None


def test_unknown_reaction_and_severity_are_explicit() -> None:
    problem = Problem()
    allergy = Allergy()

    assert problem.severity is Severity.UNKNOWN
    assert allergy.reaction == CodeableConcept()
    assert allergy.reaction.text is None
    assert allergy.severity is Severity.UNKNOWN
