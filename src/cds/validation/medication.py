"""Pure task-sufficiency validation for first-slice medication orders."""

from __future__ import annotations

from cds.domain.clinical import MedicationOrder
from cds.validation.models import ValidationIssue, ValidationResult

__all__ = ["validate_medication_order_sufficiency"]


def _error(*, code: str, message: str, field_path: str) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="error",
        field_path=field_path,
    )


def _is_missing_text(value: object) -> bool:
    return value is None or (isinstance(value, str) and not value.strip())


def validate_medication_order_sufficiency(
    *,
    order: MedicationOrder,
    regimen_identifier: str | None,
    expected_medication_system: str,
    expected_medication_code: str,
    expected_regimen_identifier: str,
    require_route: bool,
    require_dose: bool,
    require_frequency: bool,
    require_indication: bool,
    require_infusion_duration: bool,
) -> ValidationResult:
    """Validate facts required for later exact medication-content matching.

    Expected identifiers and requirement flags are treated as validated internal
    configuration. This function performs no normalization, inference, content
    loading, calculation, rule matching, mutation, logging, or I/O.
    """

    issues: list[ValidationIssue] = []

    medication_system = order.medication.system
    medication_code = order.medication.code
    medication_system_missing = _is_missing_text(medication_system)
    medication_code_missing = _is_missing_text(medication_code)

    if medication_system_missing:
        issues.append(
            _error(
                code="missing_medication_system",
                message="An exact medication coding system is required.",
                field_path="order.medication.system",
            )
        )

    if medication_code_missing:
        issues.append(
            _error(
                code="missing_medication_code",
                message="An exact medication code is required.",
                field_path="order.medication.code",
            )
        )

    if not medication_system_missing and not medication_code_missing:
        if (
            medication_system != expected_medication_system
            or medication_code != expected_medication_code
        ):
            issues.append(
                _error(
                    code="unsupported_medication_identifier",
                    message=(
                        "The supplied medication identifier does not exactly match "
                        "the expected identifier."
                    ),
                    field_path="order.medication",
                )
            )

    regimen_identifier_missing = _is_missing_text(regimen_identifier)
    if regimen_identifier_missing:
        issues.append(
            _error(
                code="missing_regimen_identifier",
                message="An explicit regimen identifier is required.",
                field_path="regimen_identifier",
            )
        )
    elif regimen_identifier != expected_regimen_identifier:
        issues.append(
            _error(
                code="unsupported_regimen_identifier",
                message=(
                    "The supplied regimen identifier does not exactly match "
                    "the expected identifier."
                ),
                field_path="regimen_identifier",
            )
        )

    if require_route:
        if _is_missing_text(order.route.system):
            issues.append(
                _error(
                    code="missing_required_route_system",
                    message="The required route coding system is missing.",
                    field_path="order.route.system",
                )
            )
        if _is_missing_text(order.route.code):
            issues.append(
                _error(
                    code="missing_required_route_code",
                    message="The required route code is missing.",
                    field_path="order.route.code",
                )
            )

    if require_dose:
        dose_value = order.dose.value
        if dose_value is None:
            issues.append(
                _error(
                    code="missing_required_dose_value",
                    message="A dose value is required for the selected rule.",
                    field_path="order.dose.value",
                )
            )
        elif dose_value <= 0:
            issues.append(
                _error(
                    code="nonpositive_required_dose",
                    message="The required dose value must be greater than zero.",
                    field_path="order.dose.value",
                )
            )
        if _is_missing_text(order.dose.unit):
            issues.append(
                _error(
                    code="missing_required_dose_unit",
                    message="A dose unit is required for the selected rule.",
                    field_path="order.dose.unit",
                )
            )

    if require_frequency:
        frequency_value = order.frequency_interval.value
        if frequency_value is None:
            issues.append(
                _error(
                    code="missing_required_frequency_value",
                    message="A frequency interval value is required for the selected rule.",
                    field_path="order.frequency_interval.value",
                )
            )
        elif frequency_value <= 0:
            issues.append(
                _error(
                    code="nonpositive_required_frequency",
                    message="The required frequency interval must be greater than zero.",
                    field_path="order.frequency_interval.value",
                )
            )
        if _is_missing_text(order.frequency_interval.unit):
            issues.append(
                _error(
                    code="missing_required_frequency_unit",
                    message="A frequency interval unit is required for the selected rule.",
                    field_path="order.frequency_interval.unit",
                )
            )

    if require_indication:
        if _is_missing_text(order.indication.system):
            issues.append(
                _error(
                    code="missing_required_indication_system",
                    message="The required indication coding system is missing.",
                    field_path="order.indication.system",
                )
            )
        if _is_missing_text(order.indication.code):
            issues.append(
                _error(
                    code="missing_required_indication_code",
                    message="The required indication code is missing.",
                    field_path="order.indication.code",
                )
            )

    if require_infusion_duration:
        infusion_value = order.infusion_duration.value
        if infusion_value is None:
            issues.append(
                _error(
                    code="missing_required_infusion_duration_value",
                    message="An infusion-duration value is required for the selected rule.",
                    field_path="order.infusion_duration.value",
                )
            )
        elif infusion_value <= 0:
            issues.append(
                _error(
                    code="nonpositive_required_infusion_duration",
                    message="The required infusion duration must be greater than zero.",
                    field_path="order.infusion_duration.value",
                )
            )
        if _is_missing_text(order.infusion_duration.unit):
            issues.append(
                _error(
                    code="missing_required_infusion_duration_unit",
                    message="An infusion-duration unit is required for the selected rule.",
                    field_path="order.infusion_duration.unit",
                )
            )

    return ValidationResult(
        is_valid=not any(issue.severity == "error" for issue in issues),
        issues=issues,
    )
