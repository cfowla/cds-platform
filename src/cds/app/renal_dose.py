"""Application orchestration for one renal-dose evaluation."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import cast

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, WeightType
from cds.domain.outputs import RuleResult
from cds.repositories.renal_content import (
    RenalDoseContentKey,
    RenalDoseContentRepository,
)
from cds.rules.engine import RenalDoseRuleEngine
from cds.services.renal import calculate_cockcroft_gault
from cds.validation.lab import validate_serum_creatinine_structure
from cds.validation.medication import validate_medication_order_sufficiency
from cds.validation.models import ValidationIssue, ValidationResult
from cds.validation.patient import validate_patient_structure
from cds.validation.renal import validate_renal_sufficiency

__all__ = ["RenalDoseUseCase", "RenalDoseUseCaseResult"]


@dataclass(slots=True, kw_only=True)
class RenalDoseUseCaseResult:
    """Carry validation findings beside the standard structured rule result."""

    validation: ValidationResult
    rule_result: RuleResult


class RenalDoseUseCase:
    """Coordinate validation, exact content retrieval, calculation, and rule evaluation.

    Expected validation gaps return an incomplete result before calculation or matching.
    Unexpected repository, calculation, or rule failures are intentionally not mapped here;
    structured exception mapping is the next bounded task.
    """

    def __init__(
        self,
        *,
        content_repository: RenalDoseContentRepository,
        rule_engine: RenalDoseRuleEngine,
        medication_identifier_system: str,
    ) -> None:
        if not isinstance(medication_identifier_system, str) or not medication_identifier_system:
            raise ValueError("Medication identifier system must be a nonempty exact value.")
        self._content_repository = content_repository
        self._rule_engine = rule_engine
        self._medication_identifier_system = medication_identifier_system

    def evaluate(
        self,
        *,
        patient: Patient,
        serum_creatinine_result: LabResult,
        medication_order: MedicationOrder,
        weight_type: WeightType,
        regimen_id: str | None,
        formulation_id: str | None,
        renal_function_stable: bool | None,
        renal_replacement_therapy: bool | None,
        pregnant_or_lactating: bool | None,
        requested_content_version: str | None,
        evaluation_date: date,
        evaluated_at: datetime,
    ) -> RenalDoseUseCaseResult:
        """Run one fail-closed renal-dose workflow using exact supplied identifiers."""

        validation = _initial_validation(
            patient=patient,
            serum_creatinine_result=serum_creatinine_result,
            medication_order=medication_order,
            weight_type=weight_type,
            regimen_id=regimen_id,
            renal_function_stable=renal_function_stable,
            renal_replacement_therapy=renal_replacement_therapy,
            pregnant_or_lactating=pregnant_or_lactating,
            requested_content_version=requested_content_version,
            evaluation_date=evaluation_date,
            evaluated_at=evaluated_at,
            expected_medication_system=self._medication_identifier_system,
        )
        if validation.is_valid is not True:
            return RenalDoseUseCaseResult(
                validation=validation,
                rule_result=_incomplete_result(
                    patient=patient,
                    order=medication_order,
                    evaluated_at=evaluated_at,
                    validation=validation,
                ),
            )

        medication_id = cast(str, medication_order.medication.code)
        exact_regimen_id = cast(str, regimen_id)
        exact_content_version = cast(str, requested_content_version)

        content = self._content_repository.get(
            RenalDoseContentKey(
                medication_id=medication_id,
                regimen_id=exact_regimen_id,
                content_version=exact_content_version,
            )
        )

        medication_validation = validate_medication_order_sufficiency(
            order=medication_order,
            regimen_identifier=regimen_id,
            expected_medication_system=self._medication_identifier_system,
            expected_medication_code=content.medication.id,
            expected_regimen_identifier=content.regimen.id,
            require_route=True,
            require_dose=True,
            require_frequency=True,
            require_indication=bool(content.regimen.indication_ids),
            require_infusion_duration=content.regimen.infusion_duration is not None,
        )
        validation = _combine_validation(validation, medication_validation)
        if content.regimen.formulation_id is not None and formulation_id is None:
            validation.issues.append(
                _error(
                    code="missing_required_formulation_identifier",
                    message="A formulation identifier is required for the selected regimen.",
                    field_path="formulation_id",
                )
            )
            validation.is_valid = False

        if validation.is_valid is not True:
            return RenalDoseUseCaseResult(
                validation=validation,
                rule_result=_incomplete_result(
                    patient=patient,
                    order=medication_order,
                    evaluated_at=evaluated_at,
                    validation=validation,
                ),
            )

        context = RenalDoseEvaluationContext(
            patient=patient,
            serum_creatinine_result=serum_creatinine_result,
            supplied_weight=patient.actual_body_weight,
            weight_type=weight_type,
            medication_order=medication_order,
            regimen_id=regimen_id,
            formulation_id=formulation_id,
            renal_function_stable=renal_function_stable,
            renal_replacement_therapy=renal_replacement_therapy,
            requested_content_version=requested_content_version,
            evaluation_date=evaluation_date,
            evaluated_at=evaluated_at,
        )
        renal_function = calculate_cockcroft_gault(
            patient=patient,
            serum_creatinine_result=serum_creatinine_result,
            weight=context.supplied_weight,
            weight_type=weight_type,
            evaluation_date=evaluation_date,
            calculated_at=evaluated_at,
        )
        rule_result = self._rule_engine.evaluate(context, renal_function, content)
        if rule_result.renal_function_result is None:
            rule_result.renal_function_result = renal_function
        if rule_result.patient_id is None:
            rule_result.patient_id = medication_order.patient_id or patient.patient_id
        if rule_result.encounter_id is None:
            rule_result.encounter_id = medication_order.encounter_id
        if rule_result.evaluated_at is None:
            rule_result.evaluated_at = evaluated_at

        return RenalDoseUseCaseResult(validation=validation, rule_result=rule_result)


def _initial_validation(
    *,
    patient: Patient,
    serum_creatinine_result: LabResult,
    medication_order: MedicationOrder,
    weight_type: WeightType,
    regimen_id: str | None,
    renal_function_stable: bool | None,
    renal_replacement_therapy: bool | None,
    pregnant_or_lactating: bool | None,
    requested_content_version: str | None,
    evaluation_date: date,
    evaluated_at: datetime,
    expected_medication_system: str,
) -> ValidationResult:
    results = [
        validate_patient_structure(
            patient,
            evaluation_at=evaluated_at,
            declared_weight_type=weight_type,
        ),
        validate_serum_creatinine_structure(
            serum_creatinine_result,
            evaluation_at=evaluated_at,
        ),
        validate_renal_sufficiency(
            patient=patient,
            serum_creatinine=serum_creatinine_result,
            declared_weight_type=weight_type,
            renal_function_stable=renal_function_stable,
            receiving_renal_replacement_therapy=renal_replacement_therapy,
            pregnant_or_lactating=pregnant_or_lactating,
        ),
    ]
    validation = _combine_validation(*results)
    validation.issues.extend(
        _application_issues(
            patient=patient,
            serum_creatinine_result=serum_creatinine_result,
            medication_order=medication_order,
            regimen_id=regimen_id,
            requested_content_version=requested_content_version,
            evaluation_date=evaluation_date,
            evaluated_at=evaluated_at,
            expected_medication_system=expected_medication_system,
        )
    )
    validation.is_valid = not any(issue.severity == "error" for issue in validation.issues)
    return validation


def _application_issues(
    *,
    patient: Patient,
    serum_creatinine_result: LabResult,
    medication_order: MedicationOrder,
    regimen_id: str | None,
    requested_content_version: str | None,
    evaluation_date: date,
    evaluated_at: datetime,
    expected_medication_system: str,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    if patient.patient_id is None:
        issues.append(
            _error(
                "missing_patient_identifier",
                "Patient identifier is required.",
                "patient.patient_id",
            )
        )
    if medication_order.order_id is None:
        issues.append(
            _error(
                "missing_order_identifier",
                "Medication-order identifier is required.",
                "medication_order.order_id",
            )
        )
    if medication_order.patient_id != patient.patient_id:
        issues.append(
            _error(
                "order_patient_mismatch",
                "Medication order and patient identifiers must match.",
                "medication_order.patient_id",
            )
        )
    if serum_creatinine_result.patient_id != patient.patient_id:
        issues.append(
            _error(
                "lab_patient_mismatch",
                "Serum creatinine and patient identifiers must match.",
                "serum_creatinine_result.patient_id",
            )
        )
    if (
        medication_order.encounter_id is not None
        and serum_creatinine_result.encounter_id is not None
        and medication_order.encounter_id != serum_creatinine_result.encounter_id
    ):
        issues.append(
            _error(
                "encounter_mismatch",
                "Medication order and serum creatinine encounters must match.",
                "medication_order.encounter_id",
            )
        )
    if medication_order.medication.system != expected_medication_system:
        issues.append(
            _error(
                "unsupported_medication_system",
                "Medication coding system must exactly match the configured system.",
                "medication_order.medication.system",
            )
        )
    if not medication_order.medication.code:
        issues.append(
            _error(
                "missing_medication_code",
                "An exact medication code is required.",
                "medication_order.medication.code",
            )
        )
    if not regimen_id:
        issues.append(
            _error(
                "missing_regimen_identifier",
                "An exact regimen identifier is required.",
                "regimen_id",
            )
        )
    if not requested_content_version:
        issues.append(
            _error(
                "missing_content_version",
                "An exact content version is required.",
                "requested_content_version",
            )
        )
    try:
        evaluated_date = evaluated_at.date()
    except (AttributeError, OverflowError, ValueError):
        evaluated_date = None
    if evaluated_date is not None and evaluation_date != evaluated_date:
        issues.append(
            _error(
                "evaluation_date_mismatch",
                "Evaluation date must match the date represented by evaluated_at.",
                "evaluation_date",
            )
        )
    return issues


def _combine_validation(*results: ValidationResult) -> ValidationResult:
    issues = [issue for result in results for issue in result.issues]
    return ValidationResult(
        is_valid=all(result.is_valid is True for result in results) and not any(
            issue.severity == "error" for issue in issues
        ),
        issues=issues,
    )


def _incomplete_result(
    *,
    patient: Patient,
    order: MedicationOrder,
    evaluated_at: datetime,
    validation: ValidationResult,
) -> RuleResult:
    codes = ",".join(issue.code or "unknown" for issue in validation.issues)
    return RuleResult(
        patient_id=order.patient_id or patient.patient_id,
        encounter_id=order.encounter_id,
        status=ResultStatus.INCOMPLETE,
        applied=False,
        passed=None,
        summary="Validation did not permit renal calculation or rule evaluation.",
        evaluated_at=evaluated_at,
        supporting_data={
            "outcome_category": "incomplete",
            "validation_issue_count": len(validation.issues),
            "validation_issue_codes": codes,
        },
    )


def _error(code: str, message: str, field_path: str) -> ValidationIssue:
    return ValidationIssue(code=code, message=message, severity="error", field_path=field_path)
