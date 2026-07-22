"""Pure structural validation for first-slice serum-creatinine facts."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from cds.domain.clinical import LabResult
from cds.validation.models import ValidationIssue, ValidationResult

__all__ = ["validate_serum_creatinine_structure"]


def _error(*, code: str, message: str, field_path: str) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="error",
        field_path=field_path,
    )


def _has_usable_utc_offset(value: object) -> bool:
    if not isinstance(value, datetime) or value.tzinfo is None:
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


def _is_missing_text(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_serum_creatinine_structure(
    lab_result: LabResult,
    *,
    evaluation_at: datetime,
) -> ValidationResult:
    """Validate first-slice serum-creatinine structure without clinical inference.

    Expected missing, invalid, unsupported, and chronologically inconsistent
    source facts are returned as error-severity issues. The supplied laboratory
    result and all nested traceability objects are preserved unchanged.
    """

    issues: list[ValidationIssue] = []

    evaluation_is_usable = _has_usable_utc_offset(evaluation_at)
    if not evaluation_is_usable:
        issues.append(
            _error(
                code="evaluation_timezone_required",
                message="Evaluation time must include a usable UTC offset.",
                field_path="evaluation_at",
            )
        )

    serum_creatinine_value = lab_result.value.value
    if serum_creatinine_value is None:
        issues.append(
            _error(
                code="missing_serum_creatinine_value",
                message="Serum creatinine requires a numeric value.",
                field_path="value.value",
            )
        )
    elif not _is_finite_positive_decimal(serum_creatinine_value):
        issues.append(
            _error(
                code="invalid_serum_creatinine_value",
                message="Serum creatinine must be a finite positive Decimal.",
                field_path="value.value",
            )
        )

    serum_creatinine_unit = lab_result.value.unit
    if _is_missing_text(serum_creatinine_unit):
        issues.append(
            _error(
                code="missing_serum_creatinine_unit",
                message="Serum creatinine requires the exact unit mg/dL.",
                field_path="value.unit",
            )
        )
    elif serum_creatinine_unit != "mg/dL":
        issues.append(
            _error(
                code="unsupported_serum_creatinine_unit",
                message="Only the exact first-slice serum-creatinine unit mg/dL is supported.",
                field_path="value.unit",
            )
        )

    status = lab_result.status
    if _is_missing_text(status):
        issues.append(
            _error(
                code="missing_lab_status",
                message="Laboratory status is required.",
                field_path="status",
            )
        )
    elif status not in {"final", "corrected"}:
        issues.append(
            _error(
                code="unsupported_lab_status",
                message="Only exact final or corrected laboratory status is supported.",
                field_path="status",
            )
        )

    collected_at = lab_result.collected_at
    collection_is_usable = False
    if collected_at is None:
        issues.append(
            _error(
                code="missing_collection_time",
                message="Serum creatinine requires a collection time.",
                field_path="collected_at",
            )
        )
    elif not _has_usable_utc_offset(collected_at):
        issues.append(
            _error(
                code="collection_timezone_required",
                message="Collection time must include a usable UTC offset.",
                field_path="collected_at",
            )
        )
    else:
        collection_is_usable = True

    if collection_is_usable and evaluation_is_usable and collected_at > evaluation_at:
        issues.append(
            _error(
                code="collection_after_evaluation",
                message="Collection time cannot be after the evaluation time.",
                field_path="collected_at",
            )
        )

    resulted_at = lab_result.resulted_at
    result_is_usable = resulted_at is None
    if resulted_at is not None:
        result_is_usable = _has_usable_utc_offset(resulted_at)
        if not result_is_usable:
            issues.append(
                _error(
                    code="result_timezone_required",
                    message="Result time must include a usable UTC offset when supplied.",
                    field_path="resulted_at",
                )
            )

    if (
        resulted_at is not None
        and result_is_usable
        and collection_is_usable
        and resulted_at < collected_at
    ):
        issues.append(
            _error(
                code="result_before_collection",
                message="Result time cannot be before the collection time.",
                field_path="resulted_at",
            )
        )

    if (
        resulted_at is not None
        and result_is_usable
        and evaluation_is_usable
        and resulted_at > evaluation_at
    ):
        issues.append(
            _error(
                code="result_after_evaluation",
                message="Result time cannot be after the evaluation time.",
                field_path="resulted_at",
            )
        )

    return ValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )
