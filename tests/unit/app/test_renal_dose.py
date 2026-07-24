"""Focused tests for renal-dose application orchestration."""
from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from cds.app.renal_dose import RenalDoseUseCase
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.exceptions import ContentNotFound
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

    def evaluate(self, context, renal_function, content, /) -> RuleResult:
        self.calls.append((context, renal_function, content))
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

    with pytest.raises(ContentNotFound, match="exact key absent"):
        _evaluate(order=order, repository=repository)

    assert repository.keys[0].medication_id == "CEFEPIME"


def test_repository_exception_mapping_is_deferred_to_the_next_task() -> None:
    repository = _Repository(_content())
    repository.error = ContentNotFound("missing exact content")

    with pytest.raises(ContentNotFound, match="missing exact content"):
        _evaluate(repository=repository)


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
