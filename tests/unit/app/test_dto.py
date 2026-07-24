"""Focused tests for the passive renal-dose CLI request DTO."""

from dataclasses import FrozenInstanceError, fields

import pytest

from cds.app.dto import RenalDoseCLIRequest


def _request() -> RenalDoseCLIRequest:
    return RenalDoseCLIRequest(
        patient_id="synthetic-patient-cli-001",
        birth_date="1980-01-01",
        sex="female",
        weight_value="70.0",
        weight_unit="kg",
        weight_type="actual",
        serum_creatinine_result_id="synthetic-lab-cli-001",
        serum_creatinine_value="1.2",
        serum_creatinine_unit="mg/dL",
        serum_creatinine_collected_at="2026-07-23T12:00:00+00:00",
        serum_creatinine_status="final",
        renal_function_stable=True,
        renal_replacement_therapy=False,
        pregnant_or_lactating=False,
        medication_order_id="synthetic-order-cli-001",
        medication_system="cds-medication-id",
        medication_code="cefepime",
        regimen_id="cefepime_severe_infection_iv_2g_q8h_30min",
        formulation_id="cefepime_injection",
        dose_value="2",
        dose_unit="g",
        route_system="cds-route-id",
        route_code="iv",
        frequency_interval_value="8",
        frequency_interval_unit="h",
        indication_system="cds-indication-id",
        indication_code="severe_infection",
        infusion_duration_value="30",
        infusion_duration_unit="min",
        requested_content_version="cefepime-1",
        evaluation_date="2026-07-23",
        evaluated_at="2026-07-23T12:05:00+00:00",
    )


def test_request_contains_only_minimal_cli_wire_facts() -> None:
    assert [field.name for field in fields(RenalDoseCLIRequest)] == [
        "patient_id",
        "birth_date",
        "sex",
        "weight_value",
        "weight_unit",
        "weight_type",
        "serum_creatinine_result_id",
        "serum_creatinine_value",
        "serum_creatinine_unit",
        "serum_creatinine_collected_at",
        "serum_creatinine_status",
        "renal_function_stable",
        "renal_replacement_therapy",
        "pregnant_or_lactating",
        "medication_order_id",
        "medication_system",
        "medication_code",
        "regimen_id",
        "formulation_id",
        "dose_value",
        "dose_unit",
        "route_system",
        "route_code",
        "frequency_interval_value",
        "frequency_interval_unit",
        "indication_system",
        "indication_code",
        "infusion_duration_value",
        "infusion_duration_unit",
        "requested_content_version",
        "evaluation_date",
        "evaluated_at",
    ]


def test_request_preserves_exact_wire_values_without_conversion() -> None:
    request = _request()

    assert request.birth_date == "1980-01-01"
    assert request.sex == "female"
    assert request.weight_value == "70.0"
    assert request.serum_creatinine_value == "1.2"
    assert request.medication_system == "cds-medication-id"
    assert request.medication_code == "cefepime"
    assert request.regimen_id == "cefepime_severe_infection_iv_2g_q8h_30min"
    assert request.formulation_id == "cefepime_injection"
    assert request.evaluation_date == "2026-07-23"
    assert request.evaluated_at == "2026-07-23T12:05:00+00:00"


def test_request_defaults_missing_values_to_none_without_fabrication() -> None:
    request = RenalDoseCLIRequest()

    assert all(getattr(request, field.name) is None for field in fields(request))


def test_request_is_frozen_and_has_no_mapping_or_clinical_behavior() -> None:
    request = _request()

    with pytest.raises(FrozenInstanceError):
        request.medication_code = "different"  # type: ignore[misc]

    assert not hasattr(request, "from_dict")
    assert not hasattr(request, "to_dict")
    assert not hasattr(request, "validate")
    assert not hasattr(request, "map_to_domain")
    assert not hasattr(request, "calculate")
    assert not hasattr(request, "evaluate")
