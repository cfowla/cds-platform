"""Day 77 bounded safety failure drill for the renal-dose prototype.

Prototype only. All identifiers and payload details are synthetic. These tests do not
constitute clinical review or authorize patient-care use.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from decimal import Decimal
from io import StringIO
from pathlib import Path

import pytest

from cds.app.renal_dose import RenalDoseUseCase
from cds.domain.enums import ResultStatus
from cds.domain.outputs import RuleResult
from cds.interfaces.cli import (
    CLI_EXIT_CONTENT_FAILURE,
    CLI_EXIT_INPUT_ERROR,
    CLI_EXIT_SYSTEM_FAILURE,
    CLI_EXIT_UNSUPPORTED,
    main,
)
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

AT = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)
PATIENT_ID = "synthetic-day-77-patient"
SENSITIVE_DETAIL = "synthetic-secret-payload-detail"
MEDICATION_SYSTEM = "urn:synthetic:medications"


class _Repository:
    def __init__(self, content: RenalDoseContent, error: Exception | None = None) -> None:
        self.content = content
        self.error = error
        self.keys: list[RenalDoseContentKey] = []

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        self.keys.append(key)
        if self.error is not None:
            raise self.error
        return self.content


class _Engine:
    def __init__(self, error: Exception | None = None) -> None:
        self.error = error
        self.calls: list[tuple[object, object, object]] = []

    def evaluate(self, context, renal_function, content, /) -> RuleResult:
        self.calls.append((context, renal_function, content))
        if self.error is not None:
            raise self.error
        return RuleResult(
            rule_id="synthetic-day-77-rule",
            status=ResultStatus.NOT_APPLICABLE,
            applied=False,
            passed=None,
            supporting_data={"outcome_category": "unsupported"},
        )


@dataclass(slots=True)
class _NeverCalledUseCase:
    called: bool = False

    def evaluate(self, **kwargs: object) -> object:
        self.called = True
        raise AssertionError("Malformed input must not reach the application use case.")


def _content() -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="synthetic-day-77-content",
        content_version="2026.77",
        rule_id="synthetic-day-77-rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Synthetic cefepime"),
        regimen=RenalDoseRegimenContent(
            id="synthetic-day-77-regimen",
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
            limitations=("Prototype only.",),
        ),
        renal_domain=RenalContentInterval(lower=None, upper=None),
        renal_bands=(),
        sources=(),
        review=RenalDoseReviewContent(
            status="reviewed",
            reviewed_content_version="2026.77",
            reviewer="Synthetic software fixture reviewer",
            reviewer_role="Safety drill fixture reviewer",
            reviewed_on=AT.date(),
            notes="Test-only eligibility; not clinical review.",
        ),
        limitations=("Prototype only.",),
    )


def _use_case(*, repository_error: Exception | None = None, engine_error: Exception | None = None):
    repository = _Repository(_content(), repository_error)
    engine = _Engine(engine_error)
    use_case = RenalDoseUseCase(
        content_repository=repository,
        rule_engine=engine,
        medication_identifier_system=MEDICATION_SYSTEM,
    )
    return use_case, repository, engine


def _payload() -> dict[str, object]:
    return {
        "patient_id": PATIENT_ID,
        "birth_date": "1980-01-01",
        "sex": "female",
        "weight_value": "70",
        "weight_unit": "kg",
        "weight_type": "actual",
        "serum_creatinine_result_id": "synthetic-day-77-lab",
        "serum_creatinine_value": "1.2",
        "serum_creatinine_unit": "mg/dL",
        "serum_creatinine_collected_at": "2026-07-24T11:00:00+00:00",
        "serum_creatinine_status": "final",
        "renal_function_stable": true,
        "renal_replacement_therapy": false,
        "pregnant_or_lactating": false,
        "medication_order_id": "synthetic-day-77-order",
        "medication_system": MEDICATION_SYSTEM,
        "medication_code": "cefepime",
        "regimen_id": "synthetic-day-77-regimen",
        "formulation_id": "synthetic-formulation",
        "dose_value": "2",
        "dose_unit": "g",
        "route_system": "urn:synthetic:routes",
        "route_code": "iv",
        "frequency_interval_value": "8",
        "frequency_interval_unit": "hours",
        "indication_system": "urn:synthetic:indications",
        "indication_code": "synthetic-indication",
        "infusion_duration_value": "30",
        "infusion_duration_unit": "minutes",
        "requested_content_version": "2026.77",
        "evaluation_date": "2026-07-24",
        "evaluated_at": "2026-07-24T12:00:00+00:00",
    }


def _write_payload(tmp_path: Path, payload: dict[str, object]) -> Path:
    path = tmp_path / "day-77-request.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def _assert_sanitized(stderr: str) -> None:
    assert "Traceback" not in stderr
    assert PATIENT_ID not in stderr
    assert SENSITIVE_DETAIL not in stderr


def test_corrupted_json_stops_before_mapping_or_application(tmp_path: Path) -> None:
    input_path = tmp_path / "corrupt-day-77.json"
    input_path.write_text(f'{{"patient_id":"{PATIENT_ID}",', encoding="utf-8")
    use_case = _NeverCalledUseCase()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main([str(input_path)], use_case=use_case, stdout=stdout, stderr=stderr)

    assert exit_code == CLI_EXIT_INPUT_ERROR
    assert use_case.called is False
    assert stdout.getvalue() == ""
    _assert_sanitized(stderr.getvalue())


def test_unsupported_context_fails_closed_before_content_access(tmp_path: Path) -> None:
    payload = _payload()
    payload["medication_system"] = "urn:synthetic:unsupported"
    use_case, repository, engine = _use_case()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_payload(tmp_path, payload))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    response = json.loads(stdout.getvalue())
    assert exit_code == CLI_EXIT_UNSUPPORTED
    assert response["rule_result"]["status"] == "incomplete"
    assert response["rule_result"]["recommendations"] == []
    assert repository.keys == []
    assert engine.calls == []
    _assert_sanitized(stderr.getvalue())


@pytest.mark.parametrize(
    ("repository_error", "engine_error", "expected_exit", "expected_stage"),
    [
        (
            RuntimeError(f"corrupt content: {SENSITIVE_DETAIL} for {PATIENT_ID}"),
            None,
            CLI_EXIT_CONTENT_FAILURE,
            "content_repository",
        ),
        (
            None,
            RuntimeError(f"rule failure: {SENSITIVE_DETAIL} for {PATIENT_ID}"),
            CLI_EXIT_SYSTEM_FAILURE,
            "rule_evaluation",
        ),
    ],
    ids=("corrupt-content", "unexpected-rule-error"),
)
def test_internal_failures_return_sanitized_failed_results(
    tmp_path: Path,
    repository_error: Exception | None,
    engine_error: Exception | None,
    expected_exit: int,
    expected_stage: str,
) -> None:
    use_case, _, _ = _use_case(
        repository_error=repository_error,
        engine_error=engine_error,
    )
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_payload(tmp_path, _payload()))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    response = json.loads(stdout.getvalue())
    rule_result = response["rule_result"]
    assert exit_code == expected_exit
    assert rule_result["status"] == "failed"
    assert rule_result["recommendations"] == []
    assert rule_result["supporting_data"]["failure_stage"] == expected_stage
    serialized = stdout.getvalue()
    assert "Traceback" not in serialized
    assert SENSITIVE_DETAIL not in serialized
    _assert_sanitized(stderr.getvalue())
