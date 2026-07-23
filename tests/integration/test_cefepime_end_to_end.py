"""Day 49 integration coverage for the first-slice cefepime evaluation flow."""

from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path

from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.outputs import RenalFunctionResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    InMemoryRenalDoseContentRepository,
    RenalDoseContent,
    RenalDoseContentKey,
)
from cds.repositories.yaml_renal_content import YamlRenalDoseContentRepository
from cds.rules.cefepime import evaluate_cefepime_rule
from cds.services.renal import calculate_cockcroft_gault
from cds.utils.serialization import to_jsonable
from cds.validation.lab import validate_serum_creatinine_structure
from cds.validation.medication import validate_medication_order_sufficiency
from cds.validation.patient import validate_patient_structure
from cds.validation.renal import validate_renal_sufficiency

EVALUATED_AT = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
COLLECTED_AT = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
CONTENT_KEY = RenalDoseContentKey(
    medication_id="cefepime",
    regimen_id="synthetic_fixture_iv_regimen",
    content_version="0.1.0-draft",
)
FIXTURE_PATH = (
    Path(__file__).parents[2]
    / "src"
    / "cds"
    / "content"
    / "renal"
    / "cefepime_synthetic_fixture.yaml"
)


def _patient() -> Patient:
    return Patient(
        patient_id="synthetic-patient-day-49",
        birth_date=date(1966, 7, 22),
        sex=Sex.MALE,
        actual_body_weight=ValueWithUnit(value=Decimal("72"), unit="kg"),
    )


def _serum_creatinine() -> LabResult:
    return LabResult(
        result_id="synthetic-scr-day-49",
        patient_id="synthetic-patient-day-49",
        encounter_id="synthetic-encounter-day-49",
        test=CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0"),
        value=ValueWithUnit(value=Decimal("1.6"), unit="mg/dL"),
        collected_at=COLLECTED_AT,
        resulted_at=COLLECTED_AT,
        status="final",
    )


def _order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order-day-49",
        patient_id="synthetic-patient-day-49",
        encounter_id="synthetic-encounter-day-49",
        medication=CodeableConcept(text="Cefepime", system="local", code="cefepime"),
        dose=ValueWithUnit(value=Decimal("1"), unit="mg"),
        route=CodeableConcept(text="Intravenous", system="local", code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("1"), unit="hours"),
        indication=CodeableConcept(
            text="Synthetic fixture indication",
            system="local",
            code="synthetic_fixture_indication",
        ),
        infusion_duration=ValueWithUnit(value=Decimal("1"), unit="minutes"),
    )


def _load_content(*, reviewed_for_test: bool) -> RenalDoseContent:
    yaml_repository = YamlRenalDoseContentRepository([FIXTURE_PATH])
    loaded = yaml_repository.get(CONTENT_KEY)
    if not reviewed_for_test:
        return loaded

    test_content_version = "0.1.0-integration-test-reviewed"
    reviewed = replace(
        loaded,
        content_version=test_content_version,
        review=replace(
            loaded.review,
            status="reviewed",
            reviewed_content_version=test_content_version,
            reviewer="Synthetic integration-test reviewer",
            reviewer_role="Software test fixture reviewer",
            reviewed_on=date(2026, 7, 22),
            notes="Test-only eligibility override; not clinical review or guidance.",
        ),
    )
    return InMemoryRenalDoseContentRepository([reviewed]).get(reviewed.key)


def _calculate_validated_renal_result() -> RenalFunctionResult:
    patient = _patient()
    serum_creatinine = _serum_creatinine()

    patient_validation = validate_patient_structure(
        patient,
        evaluation_at=EVALUATED_AT,
        declared_weight_type=WeightType.ACTUAL,
    )
    lab_validation = validate_serum_creatinine_structure(
        serum_creatinine,
        evaluation_at=EVALUATED_AT,
    )
    renal_validation = validate_renal_sufficiency(
        patient=patient,
        serum_creatinine=serum_creatinine,
        declared_weight_type=WeightType.ACTUAL,
        renal_function_stable=True,
        receiving_renal_replacement_therapy=False,
        pregnant_or_lactating=False,
    )

    assert patient_validation.is_valid is True
    assert lab_validation.is_valid is True
    assert renal_validation.is_valid is True

    renal_result = calculate_cockcroft_gault(
        patient=patient,
        serum_creatinine_result=serum_creatinine,
        weight=patient.actual_body_weight,
        weight_type=WeightType.ACTUAL,
        evaluation_date=EVALUATED_AT.date(),
        calculated_at=EVALUATED_AT,
    )
    assert renal_result.value.value == Decimal("50")
    return renal_result


def _assert_valid_order(order: MedicationOrder) -> None:
    validation = validate_medication_order_sufficiency(
        order=order,
        regimen_identifier="synthetic_fixture_iv_regimen",
        expected_medication_system="local",
        expected_medication_code="cefepime",
        expected_regimen_identifier="synthetic_fixture_iv_regimen",
        require_route=True,
        require_dose=True,
        require_frequency=True,
        require_indication=True,
        require_infusion_duration=True,
    )
    assert validation.is_valid is True


def test_exact_boundary_flows_end_to_end_to_canonical_result() -> None:
    order = _order()
    _assert_valid_order(order)
    renal_result = _calculate_validated_renal_result()
    content = _load_content(reviewed_for_test=True)

    result = evaluate_cefepime_rule(
        order=order,
        renal_function=renal_result,
        regimen_id="synthetic_fixture_iv_regimen",
        formulation_id="injectable",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        requested_content_version=content.content_version,
        content=content,
        evaluated_at=EVALUATED_AT,
    )

    assert result.status is ResultStatus.SUCCESS
    assert result.applied is True
    assert result.passed is True
    assert result.supporting_data["outcome_category"] == "recommendation"
    assert result.supporting_data["renal_band_id"] == "synthetic_fixture_upper_band"
    assert result.supporting_data["renal_value"] == "50"
    assert len(result.recommendations) == 1
    assert result.recommendations[0].dose_recommendation is not None

    payload = to_jsonable(result)
    assert isinstance(payload, dict)
    assert payload["status"] == "success"
    assert payload["renal_function_result"]["value"] == {
        "value": "50",
        "unit": "mL/min",
    }
    assert payload["recommendations"][0]["linked_order_id"] == order.order_id
    assert (
        payload["supporting_data"]["content_version"]
        == "0.1.0-integration-test-reviewed"
    )


def test_yaml_loaded_draft_content_remains_ineligible_after_validated_calculation() -> None:
    order = _order()
    _assert_valid_order(order)
    renal_result = _calculate_validated_renal_result()
    content = _load_content(reviewed_for_test=False)

    result = evaluate_cefepime_rule(
        order=order,
        renal_function=renal_result,
        regimen_id="synthetic_fixture_iv_regimen",
        formulation_id="injectable",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        requested_content_version=content.content_version,
        content=content,
        evaluated_at=EVALUATED_AT,
    )

    assert content.review.status == "draft"
    assert result.status is ResultStatus.INCOMPLETE
    assert result.applied is False
    assert result.passed is None
    assert result.supporting_data["outcome_category"] == "incomplete"
    assert result.recommendations == []
