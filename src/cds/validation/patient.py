"""Pure structural validation for patient facts used by CDS workflows."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from cds.domain.clinical import Patient
from cds.domain.enums import WeightType
from cds.validation.models import ValidationIssue, ValidationResult

__all__ = ["validate_patient_structure"]


def _error(*, code: str, message: str, field_path: str) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="error",
        field_path=field_path,
    )


def _has_usable_utc_offset(value: datetime) -> bool:
    if value.tzinfo is None:
        return False
    try:
        return value.utcoffset() is not None
    except (TypeError, ValueError, OverflowError):
        return False


def _is_finite_positive_decimal(value: object) -> bool:
    if not isinstance(value, Decimal) or not value.is_finite():
        return False
    try:
        return value > Decimal("0")
    except (TypeError, ValueError, ArithmeticError):
        return False


def _has_nonblank_unit(unit: object) -> bool:
    return isinstance(unit, str) and bool(unit.strip())


def _has_reached_adult_boundary(*, birth_date: date, evaluation_date: date) -> bool:
    year_difference = evaluation_date.year - birth_date.year
    if year_difference != 18:
        return year_difference > 18
    return (evaluation_date.month, evaluation_date.day) >= (
        birth_date.month,
        birth_date.day,
    )


def validate_patient_structure(
    patient: Patient,
    *,
    evaluation_at: datetime,
    declared_weight_type: WeightType = WeightType.UNKNOWN,
) -> ValidationResult:
    """Validate structural patient facts without deriving clinical values.

    Expected missing, invalid, and out-of-scope facts are returned as validation
    issues. The supplied patient and its nested traceability objects are not
    mutated.
    """

    issues: list[ValidationIssue] = []

    evaluation_date: date | None = None
    if not _has_usable_utc_offset(evaluation_at):
        issues.append(
            _error(
                code="evaluation_timezone_required",
                message="Evaluation time must include a usable UTC offset.",
                field_path="evaluation_at",
            )
        )
    else:
        evaluation_date = evaluation_at.date()

    if patient.birth_date is not None and evaluation_date is not None:
        if patient.birth_date > evaluation_date:
            issues.append(
                _error(
                    code="birth_date_after_evaluation",
                    message="Birth date cannot be after the evaluation date.",
                    field_path="birth_date",
                )
            )
        elif not _has_reached_adult_boundary(
            birth_date=patient.birth_date,
            evaluation_date=evaluation_date,
        ):
            issues.append(
                _error(
                    code="outside_adult_scope",
                    message="Patient is outside the supported adult population.",
                    field_path="birth_date",
                )
            )

    weight_value = patient.actual_body_weight.value
    if weight_value is not None:
        if not _is_finite_positive_decimal(weight_value):
            issues.append(
                _error(
                    code="invalid_actual_body_weight",
                    message="Actual body weight must be a finite positive Decimal when supplied.",
                    field_path="actual_body_weight.value",
                )
            )
        if not _has_nonblank_unit(patient.actual_body_weight.unit):
            issues.append(
                _error(
                    code="missing_actual_body_weight_unit",
                    message="Actual body weight requires a nonblank unit when a value is supplied.",
                    field_path="actual_body_weight.unit",
                )
            )

    height_value = patient.height.value
    if height_value is not None:
        if not _is_finite_positive_decimal(height_value):
            issues.append(
                _error(
                    code="invalid_height",
                    message="Height must be a finite positive Decimal when supplied.",
                    field_path="height.value",
                )
            )
        if not _has_nonblank_unit(patient.height.unit):
            issues.append(
                _error(
                    code="missing_height_unit",
                    message="Height requires a nonblank unit when a value is supplied.",
                    field_path="height.unit",
                )
            )

    if weight_value is not None:
        if declared_weight_type == WeightType.UNKNOWN:
            issues.append(
                _error(
                    code="weight_type_required",
                    message="A body-weight type must be declared when actual body weight is supplied.",
                    field_path="declared_weight_type",
                )
            )
        elif isinstance(declared_weight_type, WeightType) and (
            declared_weight_type is not WeightType.ACTUAL
        ):
            issues.append(
                _error(
                    code="conflicting_weight_type",
                    message=(
                        "Patient.actual_body_weight cannot be declared as a non-actual "
                        "body-weight type."
                    ),
                    field_path="declared_weight_type",
                )
            )

    return ValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )
