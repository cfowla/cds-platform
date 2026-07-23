"""Focused tests for deterministic exact renal-dose rule orchestration."""

from __future__ import annotations

from datetime import date, datetime, timezone
from decimal import Decimal

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, WeightType
from cds.domain.outputs import RuleResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    RenalContentInterval,
    RenalDoseContent,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSupportedContext,
)
from cds.rules.engine import RenalDoseRuleEngine
from cds.rules.registry import RenalDoseRuleRegistration, RenalDoseRuleRegistry

_EVALUATED_AT = datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc)


class _SyntheticRule:
    def __init__(self, result: RuleResult) -> None:
        self.result = result
        self.calls: list[tuple[RenalDoseEvaluationContext, RenalDoseContent]] = []

    def evaluate(
        self,
        context: RenalDoseEvaluationContext,
        content: RenalDoseContent,
        /,
    ) -> RuleResult:
        self.calls.append((context, content))
        return self.result


def _context(*, medication_id: str | None = "cefepime") -> RenalDoseEvaluationContext:
    patient = Patient(patient_id="synthetic-patient")
    order = MedicationOrder(
        order_id="synthetic-order",
        patient_id=patient.patient_id,
        encounter_id="synthetic-encounter",
        medication=CodeableConcept(code=medication_id),
    )
    return RenalDoseEvaluationContext(
        patient=patient,
        serum_creatinine_result=LabResult(patient_id=patient.patient_id),
        supplied_weight=ValueWithUnit(value=Decimal("70"), unit="kg"),
        weight_type=WeightType.ACTUAL,
        medication_order=order,
        regimen_id="cefepime-standard",
        formulation_id=None,
        renal_function_stable=True,
        renal_replacement_therapy=False,
        requested_content_version="2026.1",
        evaluation_date=date(2026, 7, 23),
        evaluated_at=_EVALUATED_AT,
    )


def _content(
    *,
    medication_id: str = "cefepime",
    rule_id: str = "cefepime-renal-v1",
    content_version: str = "2026.1",
) -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="synthetic-content",
        content_version=content_version,
        rule_id=rule_id,
        medication=RenalDoseMedicationContent(id=medication_id, display="Synthetic medication"),
        regimen=RenalDoseRegimenContent(
            id="cefepime-standard",
            display="Synthetic regimen",
            indication_ids=("synthetic-indication",),
            route_id="iv",
            formulation_id=None,
            base_dose=RenalDoseQuantity(value=Decimal("2"), unit="g"),
            frequency_interval=RenalDoseQuantity(value=Decimal("8"), unit="h"),
            infusion_duration=None,
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
            reviewed_content_version=content_version,
            reviewer="Synthetic Reviewer",
            reviewer_role="Clinical Pharmacist",
            reviewed_on=date(2026, 7, 23),
            notes=None,
        ),
        limitations=(),
    )


def _registration(*, rule_id: str, rule: _SyntheticRule) -> RenalDoseRuleRegistration:
    return RenalDoseRuleRegistration(
        medication_id="cefepime",
        rule_id=rule_id,
        rule=rule,
    )


def test_engine_evaluates_only_the_exact_content_rule_registration() -> None:
    context = _context()
    content = _content(rule_id="rule-z")
    earlier_rule = _SyntheticRule(RuleResult(rule_id="rule-a"))
    exact_result = RuleResult(
        rule_id="rule-z",
        patient_id="synthetic-patient",
        supporting_data={"content_version": "2026.1"},
    )
    exact_rule = _SyntheticRule(exact_result)
    registry = RenalDoseRuleRegistry(
        [
            _registration(rule_id="rule-z", rule=exact_rule),
            _registration(rule_id="rule-a", rule=earlier_rule),
        ]
    )

    result = RenalDoseRuleEngine(registry).evaluate(context, content)

    assert result is exact_result
    assert earlier_rule.calls == []
    assert exact_rule.calls == [(context, content)]


def test_engine_preserves_rule_result_identifiers_and_content_version() -> None:
    context = _context()
    content = _content()
    rule_result = RuleResult(
        rule_id=content.rule_id,
        patient_id="synthetic-patient",
        supporting_data={"content_version": content.content_version, "marker": "preserved"},
    )
    rule = _SyntheticRule(rule_result)
    registry = RenalDoseRuleRegistry(
        [_registration(rule_id=content.rule_id, rule=rule)]
    )

    result = RenalDoseRuleEngine(registry).evaluate(context, content)

    assert result is rule_result
    assert result.rule_id == content.rule_id
    assert result.supporting_data == {
        "content_version": content.content_version,
        "marker": "preserved",
    }


def test_engine_returns_explicit_unmatched_result_without_evaluating_other_rules() -> None:
    context = _context()
    content = _content(rule_id="unregistered-content-rule")
    rule = _SyntheticRule(RuleResult(rule_id="registered-rule"))
    registry = RenalDoseRuleRegistry(
        [_registration(rule_id="registered-rule", rule=rule)]
    )

    result = RenalDoseRuleEngine(registry).evaluate(context, content)

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.applied is False
    assert result.passed is None
    assert result.rule_id == content.rule_id
    assert result.recommendations == []
    assert result.supporting_data == {
        "outcome_category": "unmatched",
        "medication_id": "cefepime",
        "regimen_id": "cefepime-standard",
        "requested_content_version": "2026.1",
        "content_version": "2026.1",
        "content_rule_id": "unregistered-content-rule",
        "eligible_rule_count": 1,
    }
    assert rule.calls == []


def test_engine_returns_explicit_unsupported_result_for_unknown_exact_medication() -> None:
    context = _context(medication_id="CEFEPIME")
    content = _content()
    rule = _SyntheticRule(RuleResult(rule_id=content.rule_id))
    registry = RenalDoseRuleRegistry(
        [_registration(rule_id=content.rule_id, rule=rule)]
    )

    result = RenalDoseRuleEngine(registry).evaluate(context, content)

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.applied is False
    assert result.passed is None
    assert result.rule_id == content.rule_id
    assert result.patient_id == "synthetic-patient"
    assert result.encounter_id == "synthetic-encounter"
    assert result.evaluated_at == _EVALUATED_AT
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "unsupported"
    assert result.supporting_data["medication_id"] == "CEFEPIME"
    assert result.supporting_data["content_version"] == content.content_version
    assert result.supporting_data["eligible_rule_count"] == 0
    assert rule.calls == []


def test_engine_fails_closed_when_validated_context_lacks_a_medication_identifier() -> None:
    context = _context(medication_id=None)
    content = _content()

    result = RenalDoseRuleEngine(RenalDoseRuleRegistry()).evaluate(context, content)

    assert result.status is ResultStatus.NOT_APPLICABLE
    assert result.applied is False
    assert result.passed is None
    assert result.recommendations == []
    assert result.supporting_data["outcome_category"] == "unsupported"
    assert result.supporting_data["medication_id"] is None
