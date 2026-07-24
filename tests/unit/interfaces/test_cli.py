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
from cds.interfaces.cli import (
    CLI_EXIT_CONTENT_FAILURE,
    CLI_EXIT_INPUT_ERROR,
    CLI_EXIT_SUCCESS,
    CLI_EXIT_SYSTEM_FAILURE,
    CLI_EXIT_UNSUPPORTED,
    main,
    run_renal_dose_cli,
)
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


class _RaisingUseCase:
    def evaluate(self, **kwargs: object) -> _UseCaseResult:
        raise RuntimeError("sensitive synthetic payload detail")


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

    assert exit_code == CLI_EXIT_SUCCESS
    assert len(use_case.calls) == 1
    assert stdout.getvalue() == ""
    assert output_path.read_text(encoding="utf-8").endswith("\n")
    assert json.loads(output_path.read_text(encoding="utf-8"))["rule_result"]["status"] == (
        "success"
    )


def test_main_writes_optional_summary_to_stderr_without_contaminating_json(
    tmp_path: Path,
) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={
            "is_valid": True,
            "issues": [
                {
                    "severity": "warning",
                    "message": "Validation warning text.",
                }
            ],
        },
        rule_result={
            "status": "success_with_warnings",
            "renal_function_result": {
                "value": {
                    "value": Decimal("64.73379629629629629629629630"),
                    "unit": "mL/min",
                },
                "warnings": [{"message": "Renal result warning text."}],
                "evidence": [{"summary": "Cockcroft–Gault calculation evidence."}],
            },
            "recommendations": [
                {
                    "title": "Use the encoded cefepime renal regimen.",
                    "warnings": [{"message": "Recommendation warning text."}],
                    "evidence": [{"summary": "Reviewed cefepime content evidence."}],
                }
            ],
            "warnings": [{"message": "Rule warning text."}],
            "evidence": [{"summary": "Matched renal-dose rule evidence."}],
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path)), "--summary"],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_SUCCESS
    response = json.loads(stdout.getvalue())
    assert response["rule_result"]["status"] == "success_with_warnings"
    assert response["rule_result"]["renal_function_result"]["value"]["value"] == (
        "64.73379629629629629629629630"
    )
    assert stderr.getvalue() == (
        "PROTOTYPE — not for direct clinical use; use synthetic or properly de-identified data "
        "only.\n"
        "Status: success_with_warnings\n"
        "Renal result: 64.73379629629629629629629630 mL/min\n"
        "Recommendation:\n"
        "- Use the encoded cefepime renal regimen.\n"
        "Warnings:\n"
        "- Rule warning text.\n"
        "- Renal result warning text.\n"
        "- Recommendation warning text.\n"
        "- Validation warning text.\n"
        "Evidence:\n"
        "- Matched renal-dose rule evidence.\n"
        "- Cockcroft–Gault calculation evidence.\n"
        "- Reviewed cefepime content evidence.\n"
    )


def test_summary_marks_missing_result_fields_without_inventing_values(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={"is_valid": False, "issues": []},
        rule_result={"status": "incomplete", "recommendations": []},
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path)), "--summary"],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_INPUT_ERROR
    assert json.loads(stdout.getvalue())["rule_result"]["status"] == "incomplete"
    assert stderr.getvalue() == (
        "PROTOTYPE — not for direct clinical use; use synthetic or properly de-identified data "
        "only.\n"
        "Status: incomplete\n"
        "Renal result: not present in structured result.\n"
        "Recommendation: not present in structured result.\n"
        "Warnings: none recorded.\n"
        "Evidence: none recorded.\n"
        "Input error: structured validation did not permit renal-dose evaluation.\n"
    )


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


def test_main_maps_malformed_json_to_sanitized_input_error(tmp_path: Path) -> None:
    input_path = tmp_path / "invalid.json"
    input_path.write_text('{"patient_id":"sensitive-synthetic-id",', encoding="utf-8")
    use_case = _ConfiguredUseCase()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([str(input_path)], use_case=use_case, stdout=stdout, stderr=stderr)

    assert exit_code == CLI_EXIT_INPUT_ERROR
    assert use_case.calls == []
    assert stdout.getvalue() == ""
    assert "valid JSON object" in stderr.getvalue()
    assert "sensitive-synthetic-id" not in stderr.getvalue()
    assert "Traceback" not in stderr.getvalue()


def test_main_maps_request_mapping_error_without_exception_details(tmp_path: Path) -> None:
    payload = _payload()
    payload["weight_value"] = 70.0
    use_case = _ConfiguredUseCase()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path, payload))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_INPUT_ERROR
    assert use_case.calls == []
    assert stdout.getvalue() == ""
    assert "could not be mapped safely" in stderr.getvalue()
    assert "weight_value" not in stderr.getvalue()
    assert "Traceback" not in stderr.getvalue()


def test_main_maps_ambiguous_unit_result_to_input_exit_and_keeps_json(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={
            "is_valid": False,
            "issues": [
                {
                    "code": "unsupported_serum_creatinine_unit",
                    "severity": "error",
                    "message": "Only exact mg/dL is supported.",
                }
            ],
        },
        rule_result={"status": "incomplete", "recommendations": []},
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_INPUT_ERROR
    assert json.loads(stdout.getvalue())["rule_result"]["status"] == "incomplete"
    assert "ambiguous unit" in stderr.getvalue()
    assert "Only exact mg/dL" not in stderr.getvalue()


def test_main_maps_absent_exact_content_to_unsupported_exit(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={"is_valid": True, "issues": []},
        rule_result={
            "status": "failed",
            "recommendations": [],
            "supporting_data": {
                "failure_code": "content_not_found",
                "failure_stage": "content_repository",
            },
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_UNSUPPORTED
    assert json.loads(stdout.getvalue())["rule_result"]["recommendations"] == []
    assert "no exact medication, regimen, and content-version match" in stderr.getvalue()


def test_main_maps_content_repository_failure_to_content_exit(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={"is_valid": True, "issues": []},
        rule_result={
            "status": "failed",
            "recommendations": [],
            "supporting_data": {
                "failure_code": "unexpected_content_repository_failure",
                "failure_stage": "content_repository",
            },
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_CONTENT_FAILURE
    assert json.loads(stdout.getvalue())["rule_result"]["recommendations"] == []
    assert "Content failure" in stderr.getvalue()


def test_main_maps_structured_system_failure_to_system_exit(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={"is_valid": True, "issues": []},
        rule_result={
            "status": "failed",
            "recommendations": [],
            "supporting_data": {
                "failure_code": "calculation_failure",
                "failure_stage": "renal_calculation",
            },
        },
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_SYSTEM_FAILURE
    assert json.loads(stdout.getvalue())["rule_result"]["recommendations"] == []
    assert "returned a failed result" in stderr.getvalue()


def test_main_sanitizes_unexpected_interface_failure(tmp_path: Path) -> None:
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=_RaisingUseCase(),
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_SYSTEM_FAILURE
    assert stdout.getvalue() == ""
    assert "did not complete safely" in stderr.getvalue()
    assert "sensitive synthetic payload detail" not in stderr.getvalue()
    assert "Traceback" not in stderr.getvalue()


def test_main_maps_not_applicable_result_to_unsupported_exit(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    use_case.result = _UseCaseResult(
        validation={"is_valid": True, "issues": []},
        rule_result={"status": "not_applicable", "recommendations": []},
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_input(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_UNSUPPORTED
    assert json.loads(stdout.getvalue())["rule_result"]["status"] == "not_applicable"
    assert "not applicable" in stderr.getvalue()
