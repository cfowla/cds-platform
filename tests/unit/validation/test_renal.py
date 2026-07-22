"""Focused tests for pure first-slice renal task-sufficiency validation."""

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from cds.domain.clinical import LabResult, Patient
from cds.domain.enums import Sex, WeightType
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.validation.renal import validate_renal_sufficiency


UTC_COLLECTION = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)


def _patient(
    *,
    birth_date: date | None = date(1980, 1, 1),
    sex: Sex = Sex.MALE,
    weight: Decimal | None = Decimal("70"),
    weight_unit: str | None = "kg",
) -> Patient:
    return Patient(
        patient_id="synthetic-patient-renal-001",
        birth_date=birth_date,
        sex=sex,
        actual_body_weight=ValueWithUnit(value=weight, unit=weight_unit),
    )


def _serum_creatinine(
    *,
    value: Decimal | None = Decimal("1.2"),
    unit: str | None = "mg/dL",
    collected_at: datetime | None = UTC_COLLECTION,
) -> LabResult:
    return LabResult(
        result_id="synthetic-lab-renal-001",
        patient_id="synthetic-patient-renal-001",
        test=CodeableConcept(text="Synthetic serum creatinine"),
        value=ValueWithUnit(value=value, unit=unit),
        collected_at=collected_at,
        status="final",
    )


def _validate(
    *,
    patient: Patient | None = None,
    serum_creatinine: LabResult | None = None,
    declared_weight_type: WeightType | None = WeightType.ACTUAL,
    renal_function_stable: bool | None = True,
    receiving_renal_replacement_therapy: bool | None = False,
    pregnant_or_lactating: bool | None = False,
):
    return validate_renal_sufficiency(
        patient=patient if patient is not None else _patient(),
        serum_creatinine=(
            serum_creatinine if serum_creatinine is not None else _serum_creatinine()
        ),
        declared_weight_type=declared_weight_type,
        renal_function_stable=renal_function_stable,
        receiving_renal_replacement_therapy=receiving_renal_replacement_therapy,
        pregnant_or_lactating=pregnant_or_lactating,
    )


def _codes(result: object) -> list[str | None]:
    return [issue.code for issue in result.issues]


def test_sufficient_male_case() -> None:
    result = _validate(patient=_patient(sex=Sex.MALE))

    assert result.is_valid is True
    assert result.issues == []


def test_sufficient_female_case() -> None:
    result = _validate(patient=_patient(sex=Sex.FEMALE))

    assert result.is_valid is True
    assert result.issues == []


def test_missing_birth_date_is_insufficient() -> None:
    result = _validate(patient=_patient(birth_date=None))

    assert _codes(result) == ["missing_age_source"]
    assert result.issues[0].field_path == "patient.birth_date"
    assert result.is_valid is False


@pytest.mark.parametrize("sex", [Sex.UNKNOWN, Sex.OTHER])
def test_unsupported_sex_is_insufficient(sex: Sex) -> None:
    result = _validate(patient=_patient(sex=sex))

    assert _codes(result) == ["unsupported_sex_for_cockcroft_gault"]
    assert result.issues[0].field_path == "patient.sex"
    assert result.is_valid is False


def test_missing_weight_value_is_insufficient() -> None:
    result = _validate(patient=_patient(weight=None))

    assert _codes(result) == ["missing_weight_value"]
    assert result.issues[0].field_path == "patient.actual_body_weight.value"


@pytest.mark.parametrize("unit", [None, "", " ", "\t\n"])
def test_missing_weight_unit_is_distinguished(unit: str | None) -> None:
    result = _validate(patient=_patient(weight_unit=unit))

    assert _codes(result) == ["missing_weight_unit"]
    assert result.issues[0].field_path == "patient.actual_body_weight.unit"


@pytest.mark.parametrize("unit", [" kg ", "KG", "kgs", "lb", "g"])
def test_noncanonical_weight_units_are_unsupported_without_normalization(unit: str) -> None:
    patient = _patient(weight_unit=unit)

    result = _validate(patient=patient)

    assert _codes(result) == ["unsupported_weight_unit"]
    assert patient.actual_body_weight.unit == unit
    assert patient.actual_body_weight.value == Decimal("70")


@pytest.mark.parametrize("declared_weight_type", [None, WeightType.UNKNOWN])
def test_missing_declared_weight_type_is_insufficient(
    declared_weight_type: WeightType | None,
) -> None:
    result = _validate(declared_weight_type=declared_weight_type)

    assert _codes(result) == ["missing_declared_weight_type"]
    assert result.issues[0].field_path == "declared_weight_type"


@pytest.mark.parametrize(
    "declared_weight_type",
    [WeightType.ACTUAL, WeightType.IDEAL, WeightType.ADJUSTED, WeightType.OTHER],
)
def test_each_explicit_nonunknown_weight_type_is_sufficient(
    declared_weight_type: WeightType,
) -> None:
    result = _validate(declared_weight_type=declared_weight_type)

    assert result.is_valid is True
    assert result.issues == []


def test_missing_serum_creatinine_value_is_insufficient() -> None:
    result = _validate(serum_creatinine=_serum_creatinine(value=None))

    assert _codes(result) == ["missing_serum_creatinine_value"]
    assert result.issues[0].field_path == "serum_creatinine.value.value"


@pytest.mark.parametrize("unit", [None, "", " ", "\t\n"])
def test_missing_serum_creatinine_unit_is_distinguished(unit: str | None) -> None:
    result = _validate(serum_creatinine=_serum_creatinine(unit=unit))

    assert _codes(result) == ["missing_serum_creatinine_unit"]
    assert result.issues[0].field_path == "serum_creatinine.value.unit"


@pytest.mark.parametrize("unit", [" mg/dL ", "MG/DL", "mg%", "mg/L", "µmol/L"])
def test_noncanonical_serum_creatinine_units_are_unsupported_without_conversion(
    unit: str,
) -> None:
    lab = _serum_creatinine(unit=unit)

    result = _validate(serum_creatinine=lab)

    assert _codes(result) == ["unsupported_serum_creatinine_unit"]
    assert lab.value.unit == unit
    assert lab.value.value == Decimal("1.2")


def test_missing_collection_time_is_insufficient() -> None:
    result = _validate(serum_creatinine=_serum_creatinine(collected_at=None))

    assert _codes(result) == ["missing_collection_time"]
    assert result.issues[0].field_path == "serum_creatinine.collected_at"


def test_missing_renal_stability_status_is_insufficient() -> None:
    result = _validate(renal_function_stable=None)

    assert _codes(result) == ["missing_renal_stability_status"]
    assert result.issues[0].field_path == "renal_function_stable"


def test_explicitly_unstable_renal_function_is_out_of_scope() -> None:
    result = _validate(renal_function_stable=False)

    assert _codes(result) == ["unstable_renal_function"]
    assert result.is_valid is False


def test_missing_renal_replacement_therapy_status_is_insufficient() -> None:
    result = _validate(receiving_renal_replacement_therapy=None)

    assert _codes(result) == ["missing_renal_replacement_therapy_status"]
    assert result.issues[0].field_path == "receiving_renal_replacement_therapy"


def test_renal_replacement_therapy_is_out_of_scope() -> None:
    result = _validate(receiving_renal_replacement_therapy=True)

    assert _codes(result) == ["renal_replacement_therapy_present"]
    assert result.is_valid is False


def test_missing_pregnancy_or_lactation_status_is_insufficient() -> None:
    result = _validate(pregnant_or_lactating=None)

    assert _codes(result) == ["missing_pregnancy_or_lactation_status"]
    assert result.issues[0].field_path == "pregnant_or_lactating"


def test_pregnancy_or_lactation_is_out_of_scope() -> None:
    result = _validate(pregnant_or_lactating=True)

    assert _codes(result) == ["pregnancy_or_lactation_present"]
    assert result.is_valid is False


def test_multiple_findings_follow_requirement_order_exactly() -> None:
    result = _validate(
        patient=_patient(
            birth_date=None,
            sex=Sex.UNKNOWN,
            weight=None,
            weight_unit=" KG ",
        ),
        serum_creatinine=_serum_creatinine(
            value=None,
            unit="mmol/L",
            collected_at=None,
        ),
        declared_weight_type=WeightType.UNKNOWN,
        renal_function_stable=None,
        receiving_renal_replacement_therapy=True,
        pregnant_or_lactating=None,
    )

    assert _codes(result) == [
        "missing_age_source",
        "unsupported_sex_for_cockcroft_gault",
        "missing_weight_value",
        "unsupported_weight_unit",
        "missing_declared_weight_type",
        "missing_serum_creatinine_value",
        "unsupported_serum_creatinine_unit",
        "missing_collection_time",
        "missing_renal_stability_status",
        "renal_replacement_therapy_present",
        "missing_pregnancy_or_lactation_status",
    ]
    assert all(issue.severity == "error" for issue in result.issues)
    assert all(issue.field_path for issue in result.issues)
    assert all(issue.message and issue.message.strip() for issue in result.issues)
    assert result.is_valid is False


def test_result_and_issue_lists_are_independent_between_calls() -> None:
    first = _validate(patient=_patient(birth_date=None))
    second = _validate(patient=_patient(birth_date=None))

    assert first is not second
    assert first.issues is not second.issues
    assert first.issues[0] is not second.issues[0]

    first.issues.clear()

    assert _codes(second) == ["missing_age_source"]


def test_validator_does_not_mutate_domain_objects_or_traceability_fields() -> None:
    patient = _patient()
    lab = _serum_creatinine()
    patient.assumptions.append(
        Assumption(code="synthetic_fixture", description="Synthetic test data.")
    )
    patient.warnings.append(WarningNote(code="synthetic_warning", message="Synthetic."))
    patient.evidence.append(EvidenceItem(summary="Synthetic patient evidence."))
    patient.provenance = Provenance(
        source_type="manual_entry",
        source_identifier="synthetic-patient-source-001",
    )
    lab.assumptions.append(
        Assumption(code="synthetic_fixture", description="Synthetic test data.")
    )
    lab.warnings.append(WarningNote(code="synthetic_warning", message="Synthetic."))
    lab.evidence.append(EvidenceItem(summary="Synthetic laboratory evidence."))
    lab.provenance = Provenance(
        source_type="manual_entry",
        source_identifier="synthetic-lab-source-001",
    )
    patient_before = deepcopy(patient)
    lab_before = deepcopy(lab)

    result = _validate(patient=patient, serum_creatinine=lab)

    assert result.is_valid is True
    assert patient == patient_before
    assert lab == lab_before
    assert patient.assumptions is not result.issues
    assert patient.warnings is not result.issues
    assert patient.evidence is not result.issues
    assert lab.assumptions is not result.issues
    assert lab.warnings is not result.issues
    assert lab.evidence is not result.issues


def test_validator_adds_no_calculation_or_derived_clinical_attributes() -> None:
    patient = _patient()
    lab = _serum_creatinine()

    result = _validate(patient=patient, serum_creatinine=lab)

    assert result.is_valid is True
    for target in (patient, lab, result):
        for derived_name in (
            "age",
            "age_years",
            "sex_coefficient",
            "ideal_body_weight",
            "adjusted_body_weight",
            "weight_used",
            "creatinine_clearance",
            "crcl",
            "renal_function",
            "recommendation",
        ):
            assert not hasattr(target, derived_name)
