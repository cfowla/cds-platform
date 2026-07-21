"""Cross-model review tests for the completed Week 2 domain layer."""

from collections.abc import Callable
from dataclasses import asdict, fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal

import pytest

from cds.domain.enums import Severity, Sex
from cds.domain.models import (
    Allergy,
    Assumption,
    CodeableConcept,
    Encounter,
    EvidenceItem,
    LabResult,
    MedicationOrder,
    Patient,
    Problem,
    Provenance,
    TimeRange,
    ValueWithUnit,
    VitalSign,
    WarningNote,
)

START = datetime(2026, 7, 21, 12, tzinfo=UTC)
END = datetime(2026, 7, 21, 13, tzinfo=UTC)

WEEK_TWO_MODEL_CASES: list[tuple[type[object], Callable[[], object]]] = [
    (
        Provenance,
        lambda: Provenance(
            source_type="ehr",
            source_name="synthetic-ehr",
            source_identifier="source-123",
            captured_at=START,
        ),
    ),
    (
        EvidenceItem,
        lambda: EvidenceItem(
            summary="Reviewed renal guidance.",
            level="guideline",
            citation="Synthetic test citation.",
            provenance=Provenance(source_type="rule_content"),
        ),
    ),
    (
        Assumption,
        lambda: Assumption(
            code="stable_renal_function",
            description="The synthetic case declares renal function stable.",
            applies=True,
        ),
    ),
    (
        WarningNote,
        lambda: WarningNote(
            code="prototype_only",
            message="Not for direct clinical use.",
            severity="high",
        ),
    ),
    (
        ValueWithUnit,
        lambda: ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
    ),
    (
        CodeableConcept,
        lambda: CodeableConcept(
            text="Serum creatinine",
            system="LOINC",
            code="2160-0",
        ),
    ),
    (
        TimeRange,
        lambda: TimeRange(start=START, end=END),
    ),
    (
        Patient,
        lambda: Patient(
            patient_id="patient-123",
            birth_date=date(1950, 6, 1),
            sex=Sex.FEMALE,
            actual_body_weight=ValueWithUnit(value=Decimal("72.4"), unit="kg"),
            height=ValueWithUnit(value=Decimal("165"), unit="cm"),
        ),
    ),
    (
        Encounter,
        lambda: Encounter(
            encounter_id="encounter-123",
            patient_id="patient-123",
            encounter_type=CodeableConcept(text="Inpatient", system="HL7", code="IMP"),
            period=TimeRange(start=START, end=END),
            location="4 East",
        ),
    ),
    (
        MedicationOrder,
        lambda: MedicationOrder(
            order_id="order-123",
            patient_id="patient-123",
            encounter_id="encounter-123",
            medication=CodeableConcept(text="Cefepime", system="RxNorm", code="20481"),
            dose=ValueWithUnit(value=Decimal("2"), unit="g"),
            route=CodeableConcept(text="Intravenous", system="HL7", code="IV"),
            frequency_interval=ValueWithUnit(value=Decimal("8"), unit="h"),
            ordered_period=TimeRange(start=START, end=END),
            status="active",
        ),
    ),
    (
        LabResult,
        lambda: LabResult(
            result_id="lab-123",
            patient_id="patient-123",
            encounter_id="encounter-123",
            test=CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0"),
            value=ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
            collected_at=START,
            resulted_at=END,
            status="final",
        ),
    ),
    (
        VitalSign,
        lambda: VitalSign(
            vital_id="vital-123",
            patient_id="patient-123",
            encounter_id="encounter-123",
            vital=CodeableConcept(text="Body weight", system="LOINC", code="29463-7"),
            value=ValueWithUnit(value=Decimal("72.4"), unit="kg"),
            measured_at=START,
            status="final",
        ),
    ),
    (
        Problem,
        lambda: Problem(
            problem_id="problem-123",
            patient_id="patient-123",
            problem=CodeableConcept(text="Chronic kidney disease"),
            onset_period=TimeRange(start=START),
            status="active",
            severity=Severity.HIGH,
        ),
    ),
    (
        Allergy,
        lambda: Allergy(
            allergy_id="allergy-123",
            patient_id="patient-123",
            substance=CodeableConcept(text="Penicillin"),
            reaction=CodeableConcept(text="Pruritic rash"),
            status="active",
            verification_status="confirmed",
            severity=Severity.MODERATE,
        ),
    ),
]

MODELS_WITH_NESTED_DEFAULTS = [
    EvidenceItem,
    Assumption,
    WarningNote,
    Patient,
    Encounter,
    MedicationOrder,
    LabResult,
    VitalSign,
    Problem,
    Allergy,
]


@pytest.mark.parametrize(
    ("model_type", "representative_factory"),
    WEEK_TWO_MODEL_CASES,
    ids=[model_type.__name__ for model_type, _ in WEEK_TWO_MODEL_CASES],
)
def test_week_two_models_construct_incomplete_and_representative_instances(
    model_type: type[object],
    representative_factory: Callable[[], object],
) -> None:
    """Every Week 2 dataclass supports safe empty and populated construction."""
    incomplete = model_type()
    representative = representative_factory()

    assert isinstance(incomplete, model_type)
    assert isinstance(representative, model_type)
    assert asdict(incomplete) != asdict(representative)


@pytest.mark.parametrize(
    "model_type",
    MODELS_WITH_NESTED_DEFAULTS,
    ids=[model_type.__name__ for model_type in MODELS_WITH_NESTED_DEFAULTS],
)
def test_week_two_nested_mutable_defaults_are_independent(
    model_type: type[object],
) -> None:
    """Default factories never share nested dataclasses or collections."""
    first = model_type()
    second = model_type()
    checked_fields: list[str] = []

    for model_field in fields(first):
        first_value = getattr(first, model_field.name)
        second_value = getattr(second, model_field.name)

        if isinstance(first_value, list) or is_dataclass(first_value):
            checked_fields.append(model_field.name)
            assert first_value is not second_value

    assert checked_fields
