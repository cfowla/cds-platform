"""Focused tests for pure structural patient validation."""

from copy import deepcopy
from datetime import date, datetime, timedelta, timezone, tzinfo
from decimal import Decimal

import pytest

from cds.domain.clinical import Patient
from cds.domain.enums import WeightType
from cds.domain.support import Assumption
from cds.domain.value_objects import ValueWithUnit
from cds.validation.patient import validate_patient_structure


UTC_EVALUATION = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)


def _patient(
    *,
    birth_date: date | None = date(1980, 1, 1),
    weight: Decimal | None = Decimal("70"),
    weight_unit: str | None = "kg",
    height: Decimal | None = Decimal("170"),
    height_unit: str | None = "cm",
) -> Patient:
    return Patient(
        patient_id="synthetic-patient-001",
        birth_date=birth_date,
        actual_body_weight=ValueWithUnit(value=weight, unit=weight_unit),
        height=ValueWithUnit(value=height, unit=height_unit),
    )


def _codes(result: object) -> list[str | None]:
    return [issue.code for issue in result.issues]


def test_structurally_valid_adult_patient() -> None:
    result = validate_patient_structure(
        _patient(),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True
    assert result.issues == []


def test_validation_results_and_issue_lists_are_independent() -> None:
    first = validate_patient_structure(
        _patient(weight=Decimal("0")),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )
    second = validate_patient_structure(
        _patient(),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    first.issues.clear()

    assert second.issues == []
    assert second.is_valid is True


@pytest.mark.parametrize(
    "evaluation_at",
    [
        UTC_EVALUATION,
        datetime(2026, 7, 22, 8, 0, tzinfo=timezone(timedelta(hours=-4))),
    ],
)
def test_aware_evaluation_datetimes_are_accepted(evaluation_at: datetime) -> None:
    result = validate_patient_structure(
        _patient(),
        evaluation_at=evaluation_at,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert "evaluation_timezone_required" not in _codes(result)
    assert result.is_valid is True


class _UnavailableOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> None:
        return None

    def dst(self, dt: datetime | None) -> None:
        return None


def test_naive_evaluation_datetime_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(),
        evaluation_at=datetime(2026, 7, 22, 12, 0),
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["evaluation_timezone_required"]
    assert result.is_valid is False


def test_datetime_with_unavailable_utc_offset_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(),
        evaluation_at=datetime(2026, 7, 22, 12, 0, tzinfo=_UnavailableOffset()),
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["evaluation_timezone_required"]
    assert result.is_valid is False


def test_invalid_evaluation_datetime_does_not_fabricate_birth_date_checks() -> None:
    result = validate_patient_structure(
        _patient(birth_date=date(2030, 1, 1)),
        evaluation_at=datetime(2026, 7, 22, 12, 0),
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["evaluation_timezone_required"]


def test_birth_date_after_evaluation_date_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(birth_date=date(2026, 7, 23)),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["birth_date_after_evaluation"]
    assert result.issues[0].field_path == "birth_date"
    assert result.is_valid is False


def test_day_before_18th_birthday_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(birth_date=date(2008, 7, 23)),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["outside_adult_scope"]
    assert result.is_valid is False


def test_exact_18th_birthday_is_accepted() -> None:
    result = validate_patient_structure(
        _patient(birth_date=date(2008, 7, 22)),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True
    assert result.issues == []


def test_evaluation_uses_local_calendar_date_without_utc_normalization() -> None:
    local_evaluation = datetime(
        2026,
        7,
        22,
        0,
        30,
        tzinfo=timezone(timedelta(hours=14)),
    )
    result = validate_patient_structure(
        _patient(birth_date=date(2008, 7, 22)),
        evaluation_at=local_evaluation,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True


def test_missing_birth_date_remains_structurally_representable() -> None:
    patient = _patient(birth_date=None)

    result = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True
    assert patient.birth_date is None


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_zero_and_negative_body_weight_are_rejected(value: Decimal) -> None:
    result = validate_patient_structure(
        _patient(weight=value),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["invalid_actual_body_weight"]
    assert result.issues[0].field_path == "actual_body_weight.value"


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_zero_and_negative_height_are_rejected(value: Decimal) -> None:
    result = validate_patient_structure(
        _patient(height=value),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["invalid_height"]
    assert result.issues[0].field_path == "height.value"


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_nonfinite_body_weight_is_rejected_without_crashing(value: Decimal) -> None:
    result = validate_patient_structure(
        _patient(weight=value),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["invalid_actual_body_weight"]


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_nonfinite_height_is_rejected_without_crashing(value: Decimal) -> None:
    result = validate_patient_structure(
        _patient(height=value),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["invalid_height"]


def test_missing_anthropometric_numerics_remain_distinct_from_zero() -> None:
    patient = _patient(weight=None, weight_unit=None, height=None, height_unit=None)

    result = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.UNKNOWN,
    )

    assert result.is_valid is True
    assert result.issues == []
    assert patient.actual_body_weight.value is None
    assert patient.height.value is None


def test_supplied_weight_without_unit_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(weight_unit=None),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["missing_actual_body_weight_unit"]
    assert result.issues[0].field_path == "actual_body_weight.unit"


def test_supplied_height_without_unit_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(height_unit=None),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["missing_height_unit"]
    assert result.issues[0].field_path == "height.unit"


@pytest.mark.parametrize("unit", ["", " ", "\t\n"])
def test_blank_weight_unit_is_treated_as_missing(unit: str) -> None:
    result = validate_patient_structure(
        _patient(weight_unit=unit),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["missing_actual_body_weight_unit"]


@pytest.mark.parametrize("unit", ["", " ", "\t\n"])
def test_blank_height_unit_is_treated_as_missing(unit: str) -> None:
    result = validate_patient_structure(
        _patient(height_unit=unit),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert _codes(result) == ["missing_height_unit"]


def test_supplied_weight_with_unknown_weight_type_is_rejected() -> None:
    result = validate_patient_structure(
        _patient(),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.UNKNOWN,
    )

    assert _codes(result) == ["weight_type_required"]
    assert result.issues[0].field_path == "declared_weight_type"


@pytest.mark.parametrize(
    "declared_weight_type",
    [WeightType.ACTUAL, WeightType.IDEAL, WeightType.ADJUSTED, WeightType.OTHER],
)
def test_nonunknown_declared_weight_type_is_preserved(
    declared_weight_type: WeightType,
) -> None:
    patient = _patient()

    result = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=declared_weight_type,
    )

    assert result.is_valid is True
    assert declared_weight_type is not WeightType.UNKNOWN
    assert patient.actual_body_weight.value == Decimal("70")


def test_missing_weight_with_unknown_weight_type_is_not_rejected() -> None:
    result = validate_patient_structure(
        _patient(weight=None, weight_unit=None),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.UNKNOWN,
    )

    assert "weight_type_required" not in _codes(result)
    assert result.is_valid is True


def test_multiple_findings_are_returned_in_deterministic_order() -> None:
    result = validate_patient_structure(
        _patient(
            birth_date=date(2026, 7, 23),
            weight=Decimal("0"),
            weight_unit=" ",
            height=Decimal("-1"),
            height_unit=None,
        ),
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.UNKNOWN,
    )

    assert _codes(result) == [
        "birth_date_after_evaluation",
        "invalid_actual_body_weight",
        "missing_actual_body_weight_unit",
        "invalid_height",
        "missing_height_unit",
        "weight_type_required",
    ]
    assert all(issue.severity == "error" for issue in result.issues)
    assert all(issue.message for issue in result.issues)
    assert result.is_valid is False


def test_validation_does_not_mutate_or_derive_clinical_values() -> None:
    patient = _patient()
    patient.assumptions.append(
        Assumption(code="synthetic_fixture", description="Synthetic test data.")
    )
    before = deepcopy(patient)

    result = validate_patient_structure(
        patient,
        evaluation_at=UTC_EVALUATION,
        declared_weight_type=WeightType.ACTUAL,
    )

    assert result.is_valid is True
    assert patient == before
    assert patient.assumptions is not result.issues
    for derived_name in (
        "age",
        "age_years",
        "bmi",
        "ideal_body_weight",
        "adjusted_body_weight",
        "creatinine_clearance",
    ):
        assert not hasattr(patient, derived_name)
