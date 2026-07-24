"""Focused tests for renal-dose application orchestration."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

import cds.app.renal_dose as renal_dose_module
from cds.app.renal_dose import RenalDoseUseCase
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.exceptions import CalculationError, ContentNotFound, ValidationError
from cds.domain.outputs import RuleResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    RenalContentInterval,
    RenalDoseContent,
    RenalDoseContentKey,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSupportedContext,
)

EVALUATED_AT = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)
MEDICATION_SYSTEM = "urn:synthetic:medications"


class _Repository:
    def __init__(self, content: RenalDoseContent) -> None:
        self.content = content
        self.keys: list[RenalDoseContentKey] = []
        self.error: Exception | None = None

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        self.keys.append(key)
        if self.error is not None:
            raise self.error
        return self.content


class _Engine:
    def __init__(self, result: RuleResult | None = None) -> None:
        self.result = result or RuleResult(
            rule_id="synthetic-rule",
            status=ResultStatus.SUCCESS,
            applied=True,
            passed=True,
        )
        self.calls: list[tuple[object, object, object]] = []
        self.error: Exception | None = None

    def evaluate(self, context, renal_function, content, /) -> RuleResult:
        self.calls.append((context, renal_function, content))
        if self.error is not None:
            raise self.error
        return self.result


def _content() -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="synthetic-content",
        content_version="2026.1",
        rule_id="synthetic-rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Synthetic cefepime"),
        regimen=RenalDoseRegimenContent(
            id="cefepime-synthetic-regimen",
            display="Synthetic regimen",
            indication_ids=("synthetic-indication",),
            route_id="iv",
            formulation_id="synthetic-formulation",
            base_dose=RenalDoseQuantity(value=Decimal("2"), unit="g"),
            frequency_interval=RenalDoseQuantity(value=Decimal("8"), unit="hours"),
            infusion_duration=RenalDoseQuantity(value=Decimal("30"), unit="minutes"),
        ),
        supported_context=RenalDoseSupportedContext(
            minimum_age_years=18,
            renal_method="cockcroft_gault",
            renal_unit="mL/min",
            renal_function_stable=True,
            renal_replacement_therapy=False,
            limitations=(),
        ),
        renal_domain=RenalContentInterval(lower=None, upper=None),
        renal_bands=(),
        sources=(),
        review=RenalDoseReviewContent(
            status="reviewed",
            reviewed_content_version="2026.1",
            reviewer="Synthetic Reviewer",
            reviewer_role="Software fixture reviewer",
            reviewed_on=date(2026, 7, 23),
            notes="Synthetic fixture only.",
        ),
        limitations=("Prototype only.",),
    )


def _patient() -> Patient:
    return Patient(
        patient_id="synthetic-patient",
        birth_date=date(1980, 1, 1),
        sex=Sex.FEMALE,
        actual_body_weight=ValueWithUnit(value=Decimal("70"), unit="kg"),
    )


def _lab() -> LabResult:
    return LabResult(
        result_id="synthetic-lab",
        patient_id="synthetic-patient",
        encounter_id="synthetic-encounter",
        test=CodeableConcept(code="2160-0"),
        value=ValueWithUnit(value=Decimal("1.2"), unit="mg/dL"),
        collected_at=datetime(2026, 7, 23, 11, 0, tzinfo=timezone.utc),
        status="final",
    )


def _order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order",
        patient_id="synthetic-patient",
        encounter_id="synthetic-encounter",
        medication=CodeableConcept(system=MEDICATION_SYSTEM, code="cefepime"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(system="urn:synthetic:routes", code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("8"), unit="hours"),
        indication=CodeableConcept(
            system="urn:synthetic:indications",
            code="synthetic-indication",
        ),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="minutes"),
    )


def _evaluate(
    *,
    patient: Patient | None = None,
    lab: LabResult | None = None,
    order: MedicationOrder | None = None,
    repository: _Repository | None = None,
    engine: _Engine | None = None,
):
    repository = repository or _Repository(_content())
    engine = engine or _Engine()
    result = RenalDoseUseCase(
        content_repository=repository,
        rule_engine=engine,
        medication_identifier_system=MEDICATION_SYSTEM,
    ).evaluate(
        patient=patient or _patient(),
        serum_creatinine_result=lab or _lab(),
        medication_order=order or _order(),
        weight_type=WeightType.ACTUAL,
        regimen_id="cefepime-synthetic-regimen",
        formulation_id="synthetic-formulation",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        pregnant_or_lactating=False,
        requested_content_version="2026.1",
        evaluation_date=date(2026, 7, 23),
        evaluated_at=EVALUATED_AT,
    )
    return result, repository, engine


def test_use_case_runs_exact_ordered_flow_and_attaches_unrounded_renal_result() -> None:
    result, repository, engine = _evaluate()

    assert result.validation.is_valid is True
    assert repository.keys == [
        RenalDoseContentKey(
            medication_id="cefepime",
            regimen_id="cefepime-synthetic-regimen",
            content_version="2026.1",
        )
    ]
    assert len(engine.calls) == 1
    context, renal_function, content = engine.calls[0]
    assert context.regimen_id == "cefepime-synthetic-regimen"
    assert content is repository.content
    assert renal_function.value.unit == "mL/min"
    assert renal_function.value.value == Decimal("64.73379629629629629629629630")
    assert result.rule_result.renal_function_result is renal_function
    assert result.rule_result.evaluated_at == EVALUATED_AT


def test_initial_validation_failure_stops_before_repository_calculation_or_engine() -> None:
    patient = replace(_patient(), actual_body_weight=ValueWithUnit(value=None, unit="kg"))

    result, repository, engine = _evaluate(patient=patient)

    assert result.validation.is_valid is False
    assert result.rule_result.status is ResultStatus.INCOMPLETE
    assert result.rule_result.recommendations == []
    assert "missing_weight_value" in result.rule_result.supporting_data["validation_issue_codes"]
    assert repository.keys == []
    assert engine.calls == []


def test_content_specific_medication_validation_stops_before_calculation_and_engine() -> None:
    order = replace(_order(), dose=ValueWithUnit(value=None, unit="g"))

    result, repository, engine = _evaluate(order=order)

    assert result.validation.is_valid is False
    assert repository.keys == [repository.content.key]
    assert engine.calls == []
    assert result.rule_result.renal_function_result is None
    assert result.rule_result.recommendations == []


def test_exact_identifier_values_are_not_normalized_before_repository_lookup() -> None:
    order = replace(
        _order(),
        medication=CodeableConcept(system=MEDICATION_SYSTEM, code="CEFEPIME"),
    )
    repository = _Repository(_content())
    repository.error = ContentNotFound("exact key absent")

    result, _, _ = _evaluate(order=order, repository=repository)

    assert repository.keys[0].medication_id == "CEFEPIME"
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.supporting_data["failure_code"] == "content_not_found"


def test_content_not_found_maps_to_failed_result_without_exception_details() -> None:
    repository = _Repository(_content())
    repository.error = ContentNotFound("missing exact content for synthetic-patient")

    result, _, engine = _evaluate(repository=repository)

    assert result.validation.is_valid is True
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.applied is False
    assert result.rule_result.passed is None
    assert result.rule_result.patient_id == "synthetic-patient"
    assert result.rule_result.encounter_id == "synthetic-encounter"
    assert result.rule_result.evaluated_at == EVALUATED_AT
    assert result.rule_result.rule_id is None
    assert result.rule_result.renal_function_result is None
    assert result.rule_result.recommendations == []
    assert result.rule_result.alerts == []
    assert result.rule_result.supporting_data == {
        "outcome_category": "failed",
        "failure_code": "content_not_found",
        "failure_stage": "content_repository",
        "medication_id": "cefepime",
        "regimen_id": "cefepime-synthetic-regimen",
        "requested_content_version": "2026.1",
        "content_version": None,
    }
    rendered = repr(result)
    assert "missing exact content" not in rendered
    assert "synthetic-patient" in rendered
    assert engine.calls == []


def test_unexpected_content_repository_failure_maps_without_exception_details() -> None:
    repository = _Repository(_content())
    repository.error = RuntimeError("repository payload for synthetic-patient")

    result, _, engine = _evaluate(repository=repository)

    assert result.validation.is_valid is True
    assert result.rule_result.status is ResultStatus.FAILED
    assert (
        result.rule_result.supporting_data["failure_code"]
        == "unexpected_content_repository_failure"
    )
    assert result.rule_result.supporting_data["failure_stage"] == "content_repository"
    assert "repository payload" not in repr(result)
    assert engine.calls == []


def test_unexpected_application_failure_maps_without_exception_details(monkeypatch) -> None:
    def fail_context(**kwargs):
        raise RuntimeError("application payload for synthetic-patient")

    monkeypatch.setattr(renal_dose_module, "RenalDoseEvaluationContext", fail_context)

    result, repository, engine = _evaluate()

    assert result.validation.is_valid is True
    assert repository.keys == [repository.content.key]
    assert result.rule_result.status is ResultStatus.FAILED
    assert (
        result.rule_result.supporting_data["failure_code"]
        == "unexpected_application_failure"
    )
    assert result.rule_result.supporting_data["failure_stage"] == "context_assembly"
    assert result.rule_result.rule_id == "synthetic-rule"
    assert "application payload" not in repr(result)
    assert engine.calls == []


def test_validation_error_maps_to_failed_result_without_exception_details(monkeypatch) -> None:
    def fail_validation(*args, **kwargs):
        raise ValidationError("validation payload for synthetic-patient")

    monkeypatch.setattr(renal_dose_module, "validate_patient_structure", fail_validation)

    result, repository, engine = _evaluate()

    assert result.validation.is_valid is None
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.supporting_data["failure_code"] == "validation_boundary_failure"
    assert result.rule_result.supporting_data["failure_stage"] == "initial_validation"
    assert "validation payload" not in repr(result)
    assert repository.keys == []
    assert engine.calls == []


def test_calculation_error_maps_to_failed_result_after_successful_validation(monkeypatch) -> None:
    def fail_calculation(**kwargs):
        raise CalculationError("creatinine detail for synthetic-patient")

    monkeypatch.setattr(renal_dose_module, "calculate_cockcroft_gault", fail_calculation)

    result, repository, engine = _evaluate()

    assert result.validation.is_valid is True
    assert repository.keys == [repository.content.key]
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.rule_id == "synthetic-rule"
    assert result.rule_result.renal_function_result is None
    assert result.rule_result.supporting_data["failure_code"] == "calculation_failure"
    assert result.rule_result.supporting_data["failure_stage"] == "renal_calculation"
    assert result.rule_result.supporting_data["content_version"] == "2026.1"
    assert "creatinine detail" not in repr(result)
    assert engine.calls == []


def test_unexpected_rule_failure_maps_to_failed_result_and_preserves_renal_audit() -> None:
    engine = _Engine()
    engine.error = RuntimeError("rule payload for synthetic-patient")

    result, _, _ = _evaluate(engine=engine)

    assert result.validation.is_valid is True
    assert len(engine.calls) == 1
    _, renal_function, _ = engine.calls[0]
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.rule_id == "synthetic-rule"
    assert result.rule_result.renal_function_result is renal_function
    assert result.rule_result.supporting_data["failure_code"] == "unexpected_rule_failure"
    assert result.rule_result.supporting_data["failure_stage"] == "rule_evaluation"
    assert result.rule_result.recommendations == []
    assert "rule payload" not in repr(result)


def test_expected_unsupported_rule_outcome_remains_not_applicable() -> None:
    engine = _Engine(
        RuleResult(
            rule_id="synthetic-rule",
            status=ResultStatus.NOT_APPLICABLE,
            applied=False,
            passed=None,
            supporting_data={"outcome_category": "unsupported"},
        )
    )

    result, _, _ = _evaluate(engine=engine)

    assert result.rule_result.status is ResultStatus.NOT_APPLICABLE
    assert result.rule_result.supporting_data == {"outcome_category": "unsupported"}
    assert result.rule_result.renal_function_result is not None


def test_evaluation_date_mismatch_fails_closed_before_repository_access() -> None:
    repository = _Repository(_content())
    engine = _Engine()
    use_case = RenalDoseUseCase(
        content_repository=repository,
        rule_engine=engine,
        medication_identifier_system=MEDICATION_SYSTEM,
    )

    result = use_case.evaluate(
        patient=_patient(),
        serum_creatinine_result=_lab(),
        medication_order=_order(),
        weight_type=WeightType.ACTUAL,
        regimen_id="cefepime-synthetic-regimen",
        formulation_id="synthetic-formulation",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        pregnant_or_lactating=False,
        requested_content_version="2026.1",
        evaluation_date=date(2026, 7, 22),
        evaluated_at=EVALUATED_AT,
    )

    assert result.validation.is_valid is False
    assert any(issue.code == "evaluation_date_mismatch" for issue in result.validation.issues)
    assert repository.keys == []
    assert engine.calls == []
