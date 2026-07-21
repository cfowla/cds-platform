"""Tests for medication-order, laboratory-result, and vital-sign truth objects."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cds.domain.models import (
    CodeableConcept,
    LabResult,
    MedicationOrder,
    Provenance,
    TimeRange,
    ValueWithUnit,
    VitalSign,
    WarningNote,
)


@pytest.mark.parametrize("model_type", [MedicationOrder, LabResult, VitalSign])
def test_medication_and_observation_models_have_safe_partial_defaults(
    model_type: type[object],
) -> None:
    """Each truth object can represent a source record before facts arrive."""
    assert isinstance(model_type(), model_type)


def test_medication_order_preserves_partial_regimen_data_and_units() -> None:
    """A representative order retains supplied coding, timing, and unit-bearing values."""
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


def test_lab_result_preserves_partial_observation_data_and_units() -> None:
    """A representative result retains the measured value and collection metadata."""
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


def test_vital_sign_preserves_partial_measurement_data_and_units() -> None:
    """A representative vital sign retains its source concept, unit, and context."""
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
    """Absent observations are never encoded as a numeric zero."""
    missing_quantity = missing.dose if isinstance(missing, MedicationOrder) else missing.value
    zero_quantity = zero.dose if isinstance(zero, MedicationOrder) else zero.value

    assert missing_quantity.value is None
    assert zero_quantity.value == Decimal("0")
    assert missing_quantity != zero_quantity


def test_medication_and_observation_mutable_defaults_are_independent() -> None:
    """Nested quantities, concepts, and traceability collections are never shared."""
    first_order, second_order = MedicationOrder(), MedicationOrder()
    first_result, second_result = LabResult(), LabResult()
    first_vital, second_vital = VitalSign(), VitalSign()

    first_order.dose.unit = "mg"
    first_result.warnings.append(WarningNote(code="result-warning"))
    first_vital.vital.text = "Heart rate"

    assert second_order.dose.unit is None
    assert second_result.warnings == []
    assert second_vital.vital.text is None


@pytest.mark.parametrize(
    "model",
    [MedicationOrder(), LabResult(), VitalSign()],
)
def test_default_medication_and_observation_models_have_json_safe_dicts(
    model: MedicationOrder | LabResult | VitalSign,
) -> None:
    """Default instances convert to JSON-safe primitive dictionaries."""
    serialized = json.loads(json.dumps(asdict(model)))

    assert isinstance(serialized, dict)
    assert serialized["provenance"] == asdict(Provenance())
