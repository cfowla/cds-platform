"""Focused tests for canonical renal-dose response mapping."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.domain.support import EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import ValueWithUnit
from cds.mappers.renal_dose_response import (
    dumps_renal_dose_response,
    map_renal_dose_response,
)
from cds.validation.models import ValidationIssue, ValidationResult


@dataclass(frozen=True, slots=True, kw_only=True)
class _UseCaseResult:
    validation: ValidationResult
    rule_result: RuleResult


def _complete_result() -> _UseCaseResult:
    source_time = datetime(
        2026,
        7,
        23,
        8,
        15,
        tzinfo=timezone(timedelta(hours=-4)),
    )
    return _UseCaseResult(
        validation=ValidationResult(
            is_valid=True,
            issues=[
                ValidationIssue(
                    code="review_warning",
                    message="Synthetic warning retained for response-shape verification.",
                    severity="warning",
                    field_path="medication_order",
                )
            ],
        ),
        rule_result=RuleResult(
            rule_id="renal-dose-cefepime",
            patient_id="synthetic-patient-response-001",
            status=ResultStatus.SUCCESS_WITH_WARNINGS,
            applied=True,
            passed=True,
            renal_function_result=RenalFunctionResult(
                method=RenalMethod.COCKCROFT_GAULT,
                value=ValueWithUnit(value=Decimal("31.20"), unit="mL/min"),
                evaluation_date=date(2026, 7, 23),
                calculated_at=source_time,
            ),
            evaluated_at=source_time,
            supporting_data={
                "content_version": "cefepime-1",
                "matched_band_id": "crcl_30_to_59",
            },
            warnings=[
                WarningNote(
                    code="synthetic_warning",
                    message="Synthetic warning.",
                    severity="warning",
                    provenance=Provenance(
                        source_type="rule_content",
                        source_name="synthetic-content",
                        captured_at=source_time,
                        version="cefepime-1",
                    ),
                )
            ],
            evidence=[
                EvidenceItem(
                    summary="Synthetic evidence.",
                    level="guideline",
                    citation="Synthetic citation.",
                    source_version="2026-01",
                    provenance=Provenance(
                        source_type="rule_content",
                        source_identifier="cefepime-source",
                        captured_at=source_time,
                        version="cefepime-1",
                    ),
                )
            ],
            provenance=Provenance(
                source_type="calculated",
                source_name="renal-dose-use-case",
                captured_at=source_time,
                version="renal-dose-use-case-1",
            ),
        ),
    )


def test_response_mapper_emits_stable_canonical_shape() -> None:
    response = map_renal_dose_response(_complete_result())  # type: ignore[arg-type]

    assert list(response) == ["validation", "rule_result"]
    assert response["validation"] == {
        "is_valid": True,
        "issues": [
            {
                "code": "review_warning",
                "message": "Synthetic warning retained for response-shape verification.",
                "severity": "warning",
                "field_path": "medication_order",
            }
        ],
    }
    rule_result = response["rule_result"]
    assert rule_result["rule_id"] == "renal-dose-cefepime"
    assert rule_result["status"] == "success_with_warnings"
    assert rule_result["evaluated_at"] == "2026-07-23T12:15:00Z"
    assert rule_result["renal_function_result"]["evaluation_date"] == "2026-07-23"
    assert rule_result["renal_function_result"]["value"] == {
        "value": "31.20",
        "unit": "mL/min",
    }
    assert rule_result["supporting_data"]["content_version"] == "cefepime-1"
    assert rule_result["warnings"][0]["provenance"]["version"] == "cefepime-1"
    assert rule_result["warnings"][0]["provenance"]["captured_at"] == (
        "2026-07-23T12:15:00Z"
    )
    assert rule_result["evidence"][0]["source_version"] == "2026-01"
    assert rule_result["provenance"]["source_type"] == "calculated"


def test_response_mapper_preserves_missing_false_and_zero_values() -> None:
    response = map_renal_dose_response(  # type: ignore[arg-type]
        _UseCaseResult(
            validation=ValidationResult(is_valid=False),
            rule_result=RuleResult(
                status=ResultStatus.INCOMPLETE,
                applied=False,
                passed=None,
                supporting_data={"validation_issue_count": 0},
            ),
        )
    )

    assert response["validation"]["is_valid"] is False
    assert response["rule_result"]["applied"] is False
    assert response["rule_result"]["passed"] is None
    assert response["rule_result"]["supporting_data"]["validation_issue_count"] == 0
    assert response["rule_result"]["recommendations"] == []


def test_response_json_is_compact_and_deterministic() -> None:
    result = _complete_result()

    first = dumps_renal_dose_response(result)  # type: ignore[arg-type]
    second = dumps_renal_dose_response(result)  # type: ignore[arg-type]

    assert first == second
    assert '"value":"31.20"' in first
    assert '"evaluated_at":"2026-07-23T12:15:00Z"' in first
    assert '"content_version":"cefepime-1"' in first
    assert ": " not in first
    assert ", " not in first


def test_response_mapper_rejects_non_result_objects() -> None:
    with pytest.raises(TypeError, match="RenalDoseUseCaseResult"):
        map_renal_dose_response(object())  # type: ignore[arg-type]


def test_response_mapper_does_not_assume_timezone_for_naive_datetimes() -> None:
    result = _UseCaseResult(
        validation=ValidationResult(is_valid=True),
        rule_result=RuleResult(evaluated_at=datetime(2026, 7, 23, 12, 15)),
    )

    with pytest.raises(ValueError, match="timezone-aware"):
        map_renal_dose_response(result)  # type: ignore[arg-type]
