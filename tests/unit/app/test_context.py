"""Focused tests for the passive renal-dose evaluation context."""

from dataclasses import FrozenInstanceError, fields
from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import Sex, WeightType
from cds.domain.value_objects import CodeableConcept, ValueWithUnit


def _context() -> RenalDoseEvaluationContext:
    patient = Patient(
        patient_id="synthetic-patient-context-001",
        birth_date=date(1980, 1, 1),
        sex=Sex.FEMALE,
        actual_body_weight=ValueWithUnit(value=Decimal("70"), unit="kg"),
    )
    serum_creatinine = LabResult(
        result_id="synthetic-lab-context-001",
        patient_id=patient.patient_id,
        encounter_id="synthetic-encounter-context-001",
        test=CodeableConcept(text="Synthetic serum creatinine", code="2160-0"),
        value=ValueWithUnit(value=Decimal("1.2"), unit="mg/dL"),
        collected_at=datetime(2026, 7, 23, 12, 0, tzinfo=timezone.utc),
        status="final",
    )
    order = MedicationOrder(
        order_id="synthetic-order-context-001",
        patient_id=patient.patient_id,
        encounter_id=serum_creatinine.encounter_id,
        medication=CodeableConcept(code="cefepime"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("8"), unit="h"),
        indication=CodeableConcept(code="severe_infection"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="min"),
    )
    return RenalDoseEvaluationContext(
        patient=patient,
        serum_creatinine_result=serum_creatinine,
        supplied_weight=patient.actual_body_weight,
        weight_type=WeightType.ACTUAL,
        medication_order=order,
        regimen_id="cefepime_severe_infection_iv_2g_q8h_30min",
        formulation_id="cefepime_injection",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        requested_content_version="cefepime-1",
        evaluation_date=date(2026, 7, 23),
        evaluated_at=datetime(2026, 7, 23, 12, 5, tzinfo=timezone.utc),
    )


def test_context_contains_only_required_or_exact_rule_facts() -> None:
    assert [field.name for field in fields(RenalDoseEvaluationContext)] == [
        "patient",
        "serum_creatinine_result",
        "supplied_weight",
        "weight_type",
        "medication_order",
        "regimen_id",
        "formulation_id",
        "renal_function_stable",
        "renal_replacement_therapy",
        "requested_content_version",
        "evaluation_date",
        "evaluated_at",
    ]


def test_context_preserves_validated_objects_and_exact_values() -> None:
    context = _context()

    assert context.supplied_weight is context.patient.actual_body_weight
    assert context.serum_creatinine_result.patient_id == context.patient.patient_id
    assert context.medication_order.patient_id == context.patient.patient_id
    assert context.regimen_id == "cefepime_severe_infection_iv_2g_q8h_30min"
    assert context.formulation_id == "cefepime_injection"
    assert context.requested_content_version == "cefepime-1"
    assert context.renal_function_stable is True
    assert context.renal_replacement_therapy is False


def test_context_is_frozen_and_has_no_behavior_methods() -> None:
    context = _context()

    with pytest.raises(FrozenInstanceError):
        context.regimen_id = "different"  # type: ignore[misc]

    assert not hasattr(context, "validate")
    assert not hasattr(context, "calculate")
    assert not hasattr(context, "evaluate")
    assert not hasattr(context, "load_content")


def test_optional_formulation_id_preserves_explicit_absence() -> None:
    values = {
        field.name: getattr(_context(), field.name)
        for field in fields(RenalDoseEvaluationContext)
    }
    values["formulation_id"] = None

    context = RenalDoseEvaluationContext(**values)

    assert context.formulation_id is None
