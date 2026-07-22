"""Cross-validator safety contracts for the completed validation layer."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Callable

import pytest

from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import Sex, WeightType
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.validation.lab import validate_serum_creatinine_structure
from cds.validation.medication import validate_medication_order_sufficiency
from cds.validation.models import ValidationResult
from cds.validation.patient import validate_patient_structure
from cds.validation.renal import validate_renal_sufficiency

UTC_EVALUATION = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
UTC_COLLECTION = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
EXPECTED_MEDICATION_SYSTEM = "urn:synthetic:medication-system"
EXPECTED_MEDICATION_CODE = "synthetic-medication-code"
EXPECTED_REGIMEN_IDENTIFIER = "synthetic-regimen-identifier"


def _patient(
    *,
    birth_date: date | None = date(1980, 1, 1),
    sex: Sex = Sex.MALE,
    weight: Decimal | None = Decimal("70"),
    weight_unit: str | None = "kg",
) -> Patient:
    return Patient(
        patient_id="synthetic-matrix-patient-001",
        birth_date=birth_date,
        sex=sex,
        actual_body_weight=ValueWithUnit(value=weight, unit=weight_unit),
    )


def _serum_creatinine(
    *,
    value: Decimal | None = Decimal("1.2"),
    unit: str | None = "mg/dL",
    status: str | None = "final",
) -> LabResult:
    return LabResult(
        result_id="synthetic-matrix-lab-001",
        patient_id="synthetic-matrix-patient-001",
        test=CodeableConcept(text="Synthetic serum creatinine"),
        value=ValueWithUnit(value=value, unit=unit),
        collected_at=UTC_COLLECTION,
        status=status,
    )


def _medication_order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-matrix-order-001",
        patient_id="synthetic-matrix-patient-001",
        medication=CodeableConcept(
            text="Synthetic medication",
            system=EXPECTED_MEDICATION_SYSTEM,
            code=EXPECTED_MEDICATION_CODE,
        ),
    )


def _validate_minimal_medication(
    *,
    regimen_identifier: str | None = EXPECTED_REGIMEN_IDENTIFIER,
) -> ValidationResult:
    return validate_medication_order_sufficiency(
        order=_medication_order(),
        regimen_identifier=regimen_identifier,
        expected_medication_system=EXPECTED_MEDICATION_SYSTEM,
        expected_medication_code=EXPECTED_MEDICATION_CODE,
        expected_regimen_identifier=EXPECTED_REGIMEN_IDENTIFIER,
        require_route=False,
        require_dose=False,
        require_frequency=False,
        require_indication=False,
        require_infusion_duration=False,
    )


def test_structural_representability_does_not_imply_renal_sufficiency() -> None:
    patient = _patient(birth_date=None, weight=None, weight_unit=None)
    serum_creatinine = _serum_creatinine()
    patient_before = deepcopy(patient)
    lab_before = deepcopy(serum_creatinine)

    structural = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.UNKNOWN,
    )
    sufficiency = validate_renal_sufficiency(
        patient=patient,
        serum_creatinine=serum_creatinine,
        declared_weight_type=WeightType.UNKNOWN,
        renal_function_stable=True,
        receiving_renal_replacement_therapy=False,
        pregnant_or_lactating=False,
    )

    assert structural.is_valid is True
    assert structural.issues == []
    assert sufficiency.is_valid is False
    assert [issue.code for issue in sufficiency.issues] == [
        "missing_age_source",
        "missing_weight_value",
        "missing_weight_unit",
        "missing_declared_weight_type",
    ]
    assert all(issue.severity == "error" for issue in sufficiency.issues)
    assert patient == patient_before
    assert serum_creatinine == lab_before


def test_noncanonical_weight_unit_is_not_normalized_between_layers() -> None:
    patient = _patient(weight_unit="lb")
    serum_creatinine = _serum_creatinine()

    structural = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )
    sufficiency = validate_renal_sufficiency(
        patient=patient,
        serum_creatinine=serum_creatinine,
        declared_weight_type=WeightType.ACTUAL,
        renal_function_stable=True,
        receiving_renal_replacement_therapy=False,
        pregnant_or_lactating=False,
    )

    assert structural.is_valid is True
    assert structural.issues == []
    assert sufficiency.is_valid is False
    assert [(issue.code, issue.field_path) for issue in sufficiency.issues] == [
        ("unsupported_weight_unit", "patient.actual_body_weight.unit")
    ]
    assert patient.actual_body_weight == ValueWithUnit(value=Decimal("70"), unit="lb")


CriticalCase = tuple[
    Callable[[], ValidationResult],
    str,
    str,
]


CRITICAL_CASES: tuple[CriticalCase, ...] = (
    (
        lambda: validate_patient_structure(
            _patient(birth_date=date(2008, 7, 23)),
            evaluation_at=UTC_EVALUATION,
            declared_weight_type=WeightType.ACTUAL,
        ),
        "outside_adult_scope",
        "birth_date",
    ),
    (
        lambda: validate_serum_creatinine_structure(
            _serum_creatinine(status="preliminary"),
            evaluation_at=UTC_EVALUATION,
        ),
        "unsupported_lab_status",
        "status",
    ),
    (
        lambda: validate_renal_sufficiency(
            patient=_patient(),
            serum_creatinine=_serum_creatinine(),
            declared_weight_type=WeightType.ACTUAL,
            renal_function_stable=False,
            receiving_renal_replacement_therapy=False,
            pregnant_or_lactating=False,
        ),
        "unstable_renal_function",
        "renal_function_stable",
    ),
    (
        lambda: _validate_minimal_medication(
            regimen_identifier=f"{EXPECTED_REGIMEN_IDENTIFIER} "
        ),
        "unsupported_regimen_identifier",
        "regimen_identifier",
    ),
)


@pytest.mark.parametrize(("validate", "expected_code", "expected_field_path"), CRITICAL_CASES)
def test_critical_cases_share_the_fail_closed_result_contract(
    validate: Callable[[], ValidationResult],
    expected_code: str,
    expected_field_path: str,
) -> None:
    first = validate()
    second = validate()

    assert first == second
    assert first is not second
    assert first.issues is not second.issues
    assert first.is_valid is False
    assert len(first.issues) == 1

    issue = first.issues[0]
    assert issue.code == expected_code
    assert issue.field_path == expected_field_path
    assert issue.severity == "error"
    assert issue.message is not None
    assert issue.message.strip()
    assert issue is not second.issues[0]


def test_immediately_after_adult_boundary_remains_supported() -> None:
    result = validate_patient_structure(
        _patient(birth_date=date(2008, 7, 21)),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True
    assert result.issues == []
