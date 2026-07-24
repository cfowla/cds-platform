"""Focused tests for synthetic renal-dose request mapping."""

from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from cds.app.dto import RenalDoseCLIRequest
from cds.domain.enums import Sex, WeightType
from cds.mappers.renal_dose_request import (
    RequestMappingError,
    dto_from_mapping,
    map_renal_dose_request,
)


def _payload() -> dict[str, object]:
    return {
        "patient_id": "synthetic-patient-cli-001",
        "birth_date": "1980-01-01",
        "sex": "female",
        "weight_value": "70.0",
        "weight_unit": "kg",
        "weight_type": "actual",
        "serum_creatinine_result_id": "synthetic-lab-cli-001",
        "serum_creatinine_value": "1.20",
        "serum_creatinine_unit": "mg/dL",
        "serum_creatinine_collected_at": "2026-07-23T08:00:00-04:00",
        "serum_creatinine_status": "final",
        "renal_function_stable": True,
        "renal_replacement_therapy": False,
        "pregnant_or_lactating": False,
        "medication_order_id": "synthetic-order-cli-001",
        "medication_system": "cds-medication-id",
        "medication_code": "cefepime",
        "regimen_id": "cefepime_severe_infection_iv_2g_q8h_30min",
        "formulation_id": "cefepime_injection",
        "dose_value": "2.00",
        "dose_unit": "g",
        "route_system": "cds-route-id",
        "route_code": "iv",
        "frequency_interval_value": "8",
        "frequency_interval_unit": "h",
        "indication_system": "cds-indication-id",
        "indication_code": "severe_infection",
        "infusion_duration_value": "30",
        "infusion_duration_unit": "min",
        "requested_content_version": "cefepime-1",
        "evaluation_date": "2026-07-23",
        "evaluated_at": "2026-07-23T12:05:00+00:00",
    }


def test_dto_mapping_preserves_exact_wire_values_and_missing_fields() -> None:
    request = dto_from_mapping(
        {
            "patient_id": "  synthetic-patient-cli-001  ",
            "weight_unit": "KG",
            "renal_function_stable": False,
        }
    )

    assert request.patient_id == "  synthetic-patient-cli-001  "
    assert request.weight_unit == "KG"
    assert request.renal_function_stable is False
    assert request.weight_value is None
    assert request.evaluated_at is None


@pytest.mark.parametrize(
    ("payload", "message_fragment"),
    [
        ({"extra": "value"}, "Unknown request field"),
        ({"weight_value": 70.0}, "weight_value"),
        ({"renal_function_stable": 1}, "renal_function_stable"),
    ],
)
def test_dto_mapping_rejects_unknown_fields_and_wrong_wire_types(
    payload: dict[str, object],
    message_fragment: str,
) -> None:
    with pytest.raises(RequestMappingError, match=message_fragment):
        dto_from_mapping(payload)


def test_complete_request_maps_to_exact_typed_application_inputs() -> None:
    mapped = map_renal_dose_request(dto_from_mapping(_payload()))

    assert mapped.patient.patient_id == "synthetic-patient-cli-001"
    assert mapped.patient.birth_date == date(1980, 1, 1)
    assert mapped.patient.sex is Sex.FEMALE
    assert mapped.patient.actual_body_weight.value == Decimal("70.0")
    assert mapped.patient.actual_body_weight.unit == "kg"
    assert mapped.weight_type is WeightType.ACTUAL

    assert mapped.serum_creatinine_result.result_id == "synthetic-lab-cli-001"
    assert mapped.serum_creatinine_result.patient_id == mapped.patient.patient_id
    assert mapped.serum_creatinine_result.value.value == Decimal("1.20")
    assert mapped.serum_creatinine_result.value.unit == "mg/dL"
    assert mapped.serum_creatinine_result.collected_at == datetime(
        2026,
        7,
        23,
        8,
        0,
        tzinfo=timezone(timedelta(hours=-4)),
    )
    assert mapped.serum_creatinine_result.status == "final"
    assert mapped.serum_creatinine_result.test.code is None

    assert mapped.medication_order.order_id == "synthetic-order-cli-001"
    assert mapped.medication_order.patient_id == mapped.patient.patient_id
    assert mapped.medication_order.medication.system == "cds-medication-id"
    assert mapped.medication_order.medication.code == "cefepime"
    assert mapped.medication_order.medication.text is None
    assert mapped.medication_order.dose.value == Decimal("2.00")
    assert mapped.medication_order.dose.unit == "g"
    assert mapped.medication_order.route.system == "cds-route-id"
    assert mapped.medication_order.route.code == "iv"
    assert mapped.medication_order.frequency_interval.value == Decimal("8")
    assert mapped.medication_order.frequency_interval.unit == "h"
    assert mapped.medication_order.indication.system == "cds-indication-id"
    assert mapped.medication_order.indication.code == "severe_infection"
    assert mapped.medication_order.infusion_duration.value == Decimal("30")
    assert mapped.medication_order.infusion_duration.unit == "min"

    assert mapped.regimen_id == "cefepime_severe_infection_iv_2g_q8h_30min"
    assert mapped.formulation_id == "cefepime_injection"
    assert mapped.renal_function_stable is True
    assert mapped.renal_replacement_therapy is False
    assert mapped.pregnant_or_lactating is False
    assert mapped.requested_content_version == "cefepime-1"
    assert mapped.evaluation_date == date(2026, 7, 23)
    assert mapped.evaluated_at == datetime(2026, 7, 23, 12, 5, tzinfo=timezone.utc)


def test_missing_values_map_without_fabrication() -> None:
    mapped = map_renal_dose_request(RenalDoseCLIRequest())

    assert mapped.patient.patient_id is None
    assert mapped.patient.birth_date is None
    assert mapped.patient.sex is Sex.UNKNOWN
    assert mapped.patient.actual_body_weight.value is None
    assert mapped.patient.actual_body_weight.unit is None
    assert mapped.serum_creatinine_result.value.value is None
    assert mapped.serum_creatinine_result.value.unit is None
    assert mapped.serum_creatinine_result.collected_at is None
    assert mapped.medication_order.dose.value is None
    assert mapped.medication_order.route.code is None
    assert mapped.weight_type is WeightType.UNKNOWN
    assert mapped.renal_function_stable is None
    assert mapped.renal_replacement_therapy is None
    assert mapped.pregnant_or_lactating is None
    assert mapped.evaluation_date is None
    assert mapped.evaluated_at is None


def test_mapper_preserves_clinically_invalid_values_for_validation_layer() -> None:
    request = RenalDoseCLIRequest(
        sex="other",
        weight_value="0",
        weight_unit="lb",
        weight_type="other",
        serum_creatinine_value="NaN",
        serum_creatinine_unit="umol/L",
        serum_creatinine_status="PRELIMINARY",
    )

    mapped = map_renal_dose_request(request)

    assert mapped.patient.sex is Sex.OTHER
    assert mapped.patient.actual_body_weight.value == Decimal("0")
    assert mapped.patient.actual_body_weight.unit == "lb"
    assert mapped.weight_type is WeightType.OTHER
    assert mapped.serum_creatinine_result.value.value.is_nan()
    assert mapped.serum_creatinine_result.value.unit == "umol/L"
    assert mapped.serum_creatinine_result.status == "PRELIMINARY"


@pytest.mark.parametrize(
    ("changes", "message_fragment"),
    [
        ({"weight_value": "not-a-number"}, "weight_value"),
        ({"birth_date": "01/01/1980"}, "birth_date"),
        ({"sex": "Female"}, "sex"),
        ({"weight_type": "ACTUAL"}, "weight_type"),
        (
            {"serum_creatinine_collected_at": "2026-07-23T08:00:00"},
            "serum_creatinine_collected_at",
        ),
        ({"evaluated_at": "2026-07-23T12:05:00"}, "evaluated_at"),
    ],
)
def test_mapper_rejects_unrepresentable_or_ambiguous_typed_values(
    changes: dict[str, object],
    message_fragment: str,
) -> None:
    payload = _payload()
    payload.update(changes)

    with pytest.raises(RequestMappingError, match=message_fragment):
        map_renal_dose_request(dto_from_mapping(payload))


def test_mapper_requires_the_wire_preserving_request_dto() -> None:
    with pytest.raises(TypeError, match="RenalDoseCLIRequest"):
        map_renal_dose_request(object())  # type: ignore[arg-type]
