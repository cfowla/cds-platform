"""Focused tests for the synthetic renal-dose CLI command."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest

from cds.domain.enums import Sex, WeightType
from cds.interfaces.cli import main, run_renal_dose_cli
from cds.mappers.renal_dose_request import RequestMappingError


@dataclass(slots=True)
class _UseCaseResult:
    validation: dict[str, object]
    rule_result: dict[str, object]


class _ConfiguredUseCase:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []
        self.result = _UseCaseResult(
            validation={"is_valid": True, "issues": []},
            rule_result={
                "status": "success",
                "evaluated_at": datetime(2026, 7, 23, 12, 5, tzinfo=timezone.utc),
                "renal_value": Decimal("64.73379629629629629629629630"),
            },
        )

    def evaluate(self, **kwargs: object) -> _UseCaseResult:
        self.calls.append(kwargs)
        return self.result


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


def _write_input(tmp_path: Path, payload: dict[str, object] | None = None) -> Path:
    input_path = tmp_path / "renal-dose-request.json"
    input_path.write_text(json.dumps(payload or _payload()), encoding="utf-8")
    return input_path


def test_command_maps_request_invokes_configured_use_case_and_writes_stdout(
    tmp_path: Path,
) -> None:
    use_case = _ConfiguredUseCase()
    stdout = StringIO()

    run_renal_dose_cli(_write_input(tmp_path), use_case=use_case, stdout=stdout)

    assert len(use_case.calls) == 1
    call = use_case.calls[0]
    assert call["patient"].patient_id == "synthetic-patient-cli-001"
    assert call["patient"].sex is Sex.FEMALE
    assert call["weight_type"] is WeightType.ACTUAL
    assert call["regimen_id"] == "cefepime_severe_infection_iv_2g_q8h_30min"
    assert call["evaluation_date"] == date(2026, 7, 23)
    assert call["evaluated_at"] == datetime(2026, 7, 23, 12, 5, tzinfo=timezone.utc)
    assert stdout.getvalue() == (
        '{"rule_result":{"evaluated_at":"2026-07-23T12:05:00Z",'
        '"renal_value":"64.73379629629629629629629630","status":"success"},'
        '"validation":{"is_valid":true,"issues":[]}}\n'
    )


def test_main_writes_optional_output_path_without_writing_stdout(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    stdout = StringIO()
    output_path = tmp_path / "renal-dose-response.json"

    exit_code = main(
        [str(_write_input(tmp_path)), "--output", str(output_path)],
        use_case=use_case,
        stdout=stdout,
    )

    assert exit_code == 0
    assert len(use_case.calls) == 1
    assert stdout.getvalue() == ""
    assert output_path.read_text(encoding="utf-8").endswith("\n")
    assert json.loads(output_path.read_text(encoding="utf-8"))["rule_result"]["status"] == "success"


@pytest.mark.parametrize("missing_field", ["evaluation_date", "evaluated_at"])
def test_command_requires_application_times_before_use_case_invocation(
    tmp_path: Path,
    missing_field: str,
) -> None:
    payload = _payload()
    payload[missing_field] = None
    use_case = _ConfiguredUseCase()

    with pytest.raises(RequestMappingError, match=missing_field):
        run_renal_dose_cli(_write_input(tmp_path, payload), use_case=use_case, stdout=StringIO())

    assert use_case.calls == []
