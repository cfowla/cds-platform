"""Tests for CDS recommendation, alert, and rule-result models."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.models import (
    Alert,
    CDSRecommendation,
    CodeableConcept,
    Contraindication,
    DoseRecommendation,
    EvidenceItem,
    Provenance,
    RenalFunctionResult,
    RuleResult,
    ValueWithUnit,
    WarningNote,
)


@pytest.mark.parametrize("model_type", [CDSRecommendation, Alert, RuleResult])
def test_cds_output_models_have_safe_partial_defaults(model_type: type[object]) -> None:
    """Each output object can exist before optional evaluation facts are available."""
    assert isinstance(model_type(), model_type)


def test_recommendation_defaults_do_not_invent_an_action_or_strength() -> None:
    """An incomplete recommendation does not fabricate a clinical action or confidence."""
    recommendation = CDSRecommendation()

    assert recommendation.action == "unknown"
    assert recommendation.strength == "unknown"
    assert recommendation.renal_function_result is None
    assert recommendation.dose_recommendation is None
    assert recommendation.contraindications == []


def test_recommendation_links_renal_and_dose_outputs_with_explicit_units() -> None:
    """A recommendation can retain the exact renal result and proposed regimen."""
    renal = RenalFunctionResult(
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=Decimal("31.2"), unit="mL/min"),
    )
    dose = DoseRecommendation(
        medication=CodeableConcept(text="Cefepime"),
        recommended_dose=ValueWithUnit(value=Decimal("1"), unit="g"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="h"),
    )
    recommendation = CDSRecommendation(
        recommendation_id="recommendation-1",
        title="Adjust cefepime for renal function",
        action="adjust_dose",
        strength="recommend",
        renal_function_result=renal,
        dose_recommendation=dose,
        contraindications=[Contraindication(code="synthetic", applies=False)],
    )

    assert recommendation.renal_function_result.value.unit == "mL/min"
    assert recommendation.dose_recommendation.recommended_dose.unit == "g"
    assert recommendation.contraindications[0].applies is False


def test_alert_does_not_silently_choose_interruptive_policy() -> None:
    """An unassigned display policy remains distinct from explicit non-interruption."""
    alert = Alert()
    non_interruptive = Alert(interruptive=False)

    assert alert.category == "unknown"
    assert alert.severity == "unknown"
    assert alert.interruptive is None
    assert non_interruptive.interruptive is False


def test_alert_can_link_a_recommendation_without_embedding_policy() -> None:
    """Alert data may reference a recommendation while presentation stays external."""
    recommendation = CDSRecommendation(title="Review renal dose")
    alert = Alert(
        alert_id="alert-1",
        category="dosing",
        severity="warning",
        recommendation=recommendation,
        deduplication_key="renal-dose:order-1",
    )

    assert alert.recommendation is recommendation
    assert alert.deduplication_key == "renal-dose:order-1"


def test_rule_result_defaults_to_incomplete_and_unevaluated() -> None:
    """A new result cannot be mistaken for a completed negative evaluation."""
    result = RuleResult()

    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is None
    assert result.passed is None
    assert result.renal_function_result is None
    assert result.recommendations == []
    assert result.alerts == []
    assert result.supporting_data == {}


def test_rule_result_distinguishes_false_from_missing_evaluation_state() -> None:
    """Explicit false outcomes remain distinct from rules that were not evaluated."""
    not_run = RuleResult()
    failed_match = RuleResult(applied=True, passed=False, status=ResultStatus.SUCCESS)

    assert not_run.applied is None
    assert not_run.passed is None
    assert failed_match.applied is True
    assert failed_match.passed is False


def test_rule_result_carries_linked_outputs_and_primitive_supporting_data() -> None:
    """A representative result retains outputs, audit data, and evaluation time."""
    evaluated_at = datetime(2026, 7, 21, 21, tzinfo=UTC)
    renal = RenalFunctionResult(
        value=ValueWithUnit(value=Decimal("31.2"), unit="mL/min")
    )
    recommendation = CDSRecommendation(title="Adjust dose")
    alert = Alert(title="Renal dose review")
    result = RuleResult(
        rule_id="renal-dose-cefepime",
        patient_id="patient-1",
        status=ResultStatus.SUCCESS_WITH_WARNINGS,
        applied=True,
        passed=True,
        renal_function_result=renal,
        recommendations=[recommendation],
        alerts=[alert],
        supporting_data={"content_version": "2026-07", "matched_band": 30},
        evaluated_at=evaluated_at,
    )

    assert result.renal_function_result.value.unit == "mL/min"
    assert result.recommendations == [recommendation]
    assert result.alerts == [alert]
    assert result.supporting_data["matched_band"] == 30
    assert result.evaluated_at == evaluated_at


def test_cds_output_mutable_defaults_are_independent() -> None:
    """Nested collections and traceability objects are never shared across instances."""
    first_recommendation, second_recommendation = CDSRecommendation(), CDSRecommendation()
    first_alert, second_alert = Alert(), Alert()
    first_result, second_result = RuleResult(), RuleResult()

    first_recommendation.warnings.append(WarningNote(code="recommendation-warning"))
    first_alert.evidence.append(EvidenceItem(summary="synthetic"))
    first_result.supporting_data["matched"] = True
    first_result.recommendations.append(CDSRecommendation(title="Synthetic"))

    assert second_recommendation.warnings == []
    assert second_alert.evidence == []
    assert second_result.supporting_data == {}
    assert second_result.recommendations == []


@pytest.mark.parametrize("model", [CDSRecommendation(), Alert(), RuleResult()])
def test_default_cds_output_models_have_json_safe_dicts(
    model: CDSRecommendation | Alert | RuleResult,
) -> None:
    """Default output models convert to JSON-safe primitive dictionaries."""
    serialized = json.loads(json.dumps(asdict(model)))

    assert isinstance(serialized, dict)
    assert serialized["provenance"] == asdict(Provenance())
