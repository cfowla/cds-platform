"""Pure task-sufficiency validation for first-slice renal evaluation."""

from __future__ import annotations

from cds.domain.clinical import LabResult, Patient
from cds.domain.enums import Sex, WeightType
from cds.validation.models import ValidationIssue, ValidationResult

__all__ = ["validate_renal_sufficiency"]


def _error(*, code: str, message: str, field_path: str) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="error",
        field_path=field_path,
    )


def _is_missing_text(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_renal_sufficiency(
    *,
    patient: Patient,
    serum_creatinine: LabResult,
    declared_weight_type: WeightType | None,
    renal_function_stable: bool | None,
    receiving_renal_replacement_therapy: bool | None,
    pregnant_or_lactating: bool | None,
) -> ValidationResult:
    """Validate required facts for the frozen first-slice renal calculation.

    This validator checks task sufficiency only. It does not repeat structural
    validation, derive age or weight, infer population status, calculate renal
    function, or mutate any supplied object.
    """

    issues: list[ValidationIssue] = []

    if patient.birth_date is None:
        issues.append(
            _error(
                code="missing_age_source",
                message="Birth date is required as the implemented Cockcroft-Gault age source.",
                field_path="patient.birth_date",
            )
        )

    if patient.sex is not Sex.MALE and patient.sex is not Sex.FEMALE:
        issues.append(
            _error(
                code="unsupported_sex_for_cockcroft_gault",
                message=(
                    "The first-slice Cockcroft-Gault calculation supports only "
                    "Sex.MALE or Sex.FEMALE."
                ),
                field_path="patient.sex",
            )
        )

    weight_value = patient.actual_body_weight.value
    if weight_value is None:
        issues.append(
            _error(
                code="missing_weight_value",
                message="A supplied body-weight value is required for Cockcroft-Gault calculation.",
                field_path="patient.actual_body_weight.value",
            )
        )

    weight_unit = patient.actual_body_weight.unit
    if _is_missing_text(weight_unit):
        issues.append(
            _error(
                code="missing_weight_unit",
                message="Supplied body weight requires the exact canonical unit kg.",
                field_path="patient.actual_body_weight.unit",
            )
        )
    elif weight_unit != "kg":
        issues.append(
            _error(
                code="unsupported_weight_unit",
                message="Only the exact first-slice body-weight unit kg is supported.",
                field_path="patient.actual_body_weight.unit",
            )
        )

    if (
        not isinstance(declared_weight_type, WeightType)
        or declared_weight_type is WeightType.UNKNOWN
    ):
        issues.append(
            _error(
                code="missing_declared_weight_type",
                message=(
                    "A body-weight type other than WeightType.UNKNOWN must be "
                    "explicitly declared."
                ),
                field_path="declared_weight_type",
            )
        )

    serum_creatinine_value = serum_creatinine.value.value
    if serum_creatinine_value is None:
        issues.append(
            _error(
                code="missing_serum_creatinine_value",
                message="A serum-creatinine value is required for Cockcroft-Gault calculation.",
                field_path="serum_creatinine.value.value",
            )
        )

    serum_creatinine_unit = serum_creatinine.value.unit
    if _is_missing_text(serum_creatinine_unit):
        issues.append(
            _error(
                code="missing_serum_creatinine_unit",
                message="Serum creatinine requires the exact canonical unit mg/dL.",
                field_path="serum_creatinine.value.unit",
            )
        )
    elif serum_creatinine_unit != "mg/dL":
        issues.append(
            _error(
                code="unsupported_serum_creatinine_unit",
                message="Only the exact first-slice serum-creatinine unit mg/dL is supported.",
                field_path="serum_creatinine.value.unit",
            )
        )

    if serum_creatinine.collected_at is None:
        issues.append(
            _error(
                code="missing_collection_time",
                message="Serum creatinine requires an explicit collection time.",
                field_path="serum_creatinine.collected_at",
            )
        )

    if renal_function_stable is None:
        issues.append(
            _error(
                code="missing_renal_stability_status",
                message="Renal-function stability must be explicitly stated.",
                field_path="renal_function_stable",
            )
        )
    elif renal_function_stable is not True:
        issues.append(
            _error(
                code="unstable_renal_function",
                message="Unstable renal function is outside the first-slice calculation scope.",
                field_path="renal_function_stable",
            )
        )

    if receiving_renal_replacement_therapy is None:
        issues.append(
            _error(
                code="missing_renal_replacement_therapy_status",
                message="Renal-replacement-therapy status must be explicitly stated.",
                field_path="receiving_renal_replacement_therapy",
            )
        )
    elif receiving_renal_replacement_therapy is not False:
        issues.append(
            _error(
                code="renal_replacement_therapy_present",
                message="Renal replacement therapy is outside the first-slice calculation scope.",
                field_path="receiving_renal_replacement_therapy",
            )
        )

    if pregnant_or_lactating is None:
        issues.append(
            _error(
                code="missing_pregnancy_or_lactation_status",
                message="Pregnancy-or-lactation status must be explicitly stated.",
                field_path="pregnant_or_lactating",
            )
        )
    elif pregnant_or_lactating is not False:
        issues.append(
            _error(
                code="pregnancy_or_lactation_present",
                message="Pregnancy or lactation is outside the first-slice calculation scope.",
                field_path="pregnant_or_lactating",
            )
        )

    return ValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )
