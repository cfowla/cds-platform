"""End-to-end public contract coverage for the renal-dose interface boundary.

Prototype only. All identifiers and clinical facts are synthetic, and outputs are not for direct
clinical use.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path

import cds.app.dto as dto_module
import cds.interfaces.cli as cli_module
import cds.mappers.renal_dose_request as request_module
import cds.mappers.renal_dose_response as response_module
from cds.app.dto import RenalDoseCLIRequest
from cds.domain.enums import RenalMethod, ResultStatus, Sex, WeightType
from cds.domain.outputs import (
    CDSRecommendation,
    DoseRecommendation,
    RenalFunctionResult,
    RuleResult,
)
from cds.domain.support import EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import ValueWithUnit
from cds.interfaces.cli import (
    CLI_EXIT_CONTENT_FAILURE,
    CLI_EXIT_INPUT_ERROR,
    CLI_EXIT_SUCCESS,
    CLI_EXIT_SYSTEM_FAILURE,
    CLI_EXIT_UNSUPPORTED,
    main,
    run_renal_dose_cli,
)
from cds.mappers.renal_dose_request import (
    RenalDoseMappedInput,
    RequestMappingError,
    dto_from_mapping,
    map_renal_dose_request,
)
from cds.mappers.renal_dose_response import (
    dumps_renal_dose_response,
    map_renal_dose_response,
)
from cds.validation.models import ValidationIssue, ValidationResult


MODULE_EXPORTS = (
    (dto_module, ("RenalDoseCLIRequest",)),
    (
        request_module,
        (
            "RenalDoseMappedInput",
            "RequestMappingError",
            "dto_from_mapping",
            "map_renal_dose_request",
        ),
    ),
    (
        response_module,
        ("dumps_renal_dose_response", "map_renal_dose_response"),
    ),
    (
        cli_module,
        (
            "CLI_EXIT_CONTENT_FAILURE",
            "CLI_EXIT_INPUT_ERROR",
            "CLI_EXIT_SUCCESS",
            "CLI_EXIT_SYSTEM_FAILURE",
            "CLI_EXIT_UNSUPPORTED",
            "main",
            "run_renal_dose_cli",
        ),
    ),
)

PUBLIC_OBJECTS = (
    (RenalDoseCLIRequest, "cds.app.dto"),
    (RenalDoseMappedInput, "cds.mappers.renal_dose_request"),
    (RequestMappingError, "cds.mappers.renal_dose_request"),
    (dto_from_mapping, "cds.mappers.renal_dose_request"),
    (map_renal_dose_request, "cds.mappers.renal_dose_request"),
    (dumps_renal_dose_response, "cds.mappers.renal_dose_response"),
    (map_renal_dose_response, "cds.mappers.renal_dose_response"),
    (main, "cds.interfaces.cli"),
    (run_renal_dose_cli, "cds.interfaces.cli"),
)

RULE_RESULT_KEYS = (
    "alerts",
    "applied",
    "assumptions",
    "encounter_id",
    "evaluated_at",
    "evidence",
    "passed",
    "patient_id",
    "provenance",
    "recommendations",
    "renal_function_result",
    "rule_id",
    "status",
    "summary",
    "supporting_data",
    "warnings",
)
RENAL_RESULT_KEYS = (
    "age_years",
    "assumptions",
    "calculated_at",
    "encounter_id",
    "evaluation_date",
    "evidence",
    "measured_period",
    "method",
    "normalized_to_bsa",
    "patient_id",
    "provenance",
    "result_id",
    "serum_creatinine",
    "serum_creatinine_collected_at",
    "serum_creatinine_result_id",
    "sex",
    "value",
    "warnings",
    "weight_type_used",
    "weight_used",
)
RECOMMENDATION_KEYS = (
    "action",
    "assumptions",
    "contraindications",
    "dose_recommendation",
    "encounter_id",
    "evidence",
    "linked_order_id",
    "linked_rule_id",
    "patient_id",
    "provenance",
    "rationale",
    "recommendation_id",
    "renal_function_result",
    "strength",
    "suggested_monitoring",
    "summary",
    "title",
    "warnings",
)
DOSE_RECOMMENDATION_KEYS = (
    "assumptions",
    "evidence",
    "frequency_interval",
    "infusion_duration",
    "max_daily_dose",
    "max_single_dose",
    "medication",
    "provenance",
    "rationale",
    "recommended_dose",
    "recommended_route",
    "regimen_variant",
    "warnings",
)
PROVENANCE_KEYS = (
    "author",
    "captured_at",
    "source_identifier",
    "source_name",
    "source_type",
    "version",
)


@dataclass(slots=True, kw_only=True)
class _UseCaseResult:
    validation: ValidationResult
    rule_result: RuleResult


class _ConfiguredUseCase:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def evaluate(self, **kwargs: object) -> _UseCaseResult:
        self.calls.append(kwargs)
        patient = kwargs["patient"]
        lab = kwargs["serum_creatinine_result"]
        order = kwargs["medication_order"]
        evaluated_at = kwargs["evaluated_at"]
        evaluation_date = kwargs["evaluation_date"]
        weight_type = kwargs["weight_type"]
        regimen_id = kwargs["regimen_id"]

        trace = Provenance(
            source_type="rule_content",
            source_name="synthetic-contract-content",
            source_identifier="synthetic-content-cefepime-contract",
            captured_at=evaluated_at,
            author="Synthetic software fixture",
            version="2026.7-contract-reviewed",
        )
        renal = RenalFunctionResult(
            result_id="synthetic-renal-contract-001",
            patient_id=patient.patient_id,
            encounter_id=order.encounter_id,
            method=RenalMethod.COCKCROFT_GAULT,
            value=ValueWithUnit(value=Decimal("31.2000"), unit="mL/min"),
            normalized_to_bsa=False,
            evaluation_date=evaluation_date,
            serum_creatinine_result_id=lab.result_id,
            serum_creatinine=lab.value,
            serum_creatinine_collected_at=lab.collected_at,
            age_years=46,
            sex=patient.sex,
            weight_used=patient.actual_body_weight,
            weight_type_used=weight_type,
            calculated_at=evaluated_at,
            evidence=[
                EvidenceItem(
                    summary="Synthetic Cockcroft-Gault contract evidence.",
                    level="computed",
                    source_version="renal-service-contract-1",
                    provenance=Provenance(
                        source_type="calculated",
                        source_name="synthetic-renal-calculator",
                        captured_at=evaluated_at,
                        version="renal-service-contract-1",
                    ),
                )
            ],
            provenance=Provenance(
                source_type="calculated",
                source_name="synthetic-renal-calculator",
                source_identifier="cockcroft-gault-contract",
                captured_at=evaluated_at,
                version="renal-service-contract-1",
            ),
        )
        dose = DoseRecommendation(
            medication=order.medication,
            recommended_dose=ValueWithUnit(value=Decimal("1.00"), unit="g"),
            recommended_route=order.route,
            frequency_interval=ValueWithUnit(value=Decimal("12.0"), unit="hours"),
            infusion_duration=ValueWithUnit(value=Decimal("30"), unit="minutes"),
            regimen_variant=regimen_id,
            rationale="Synthetic response-shape fixture; not clinical guidance.",
            provenance=trace,
        )
        recommendation = CDSRecommendation(
            recommendation_id="synthetic-recommendation-contract-001",
            patient_id=patient.patient_id,
            encounter_id=order.encounter_id,
            title="Synthetic contract recommendation; not for direct clinical use.",
            action="adjust_dose",
            strength="recommend",
            summary="Preserve the structured response contract only.",
            rationale="Synthetic software verification fixture.",
            renal_function_result=renal,
            dose_recommendation=dose,
            suggested_monitoring=["Synthetic monitoring statement."],
            linked_order_id=order.order_id,
            linked_rule_id="renal-dose-cefepime-contract-v1",
            warnings=[
                WarningNote(
                    code="synthetic_contract_warning",
                    message="Synthetic warning retained for contract verification.",
                    severity="warning",
                    provenance=trace,
                )
            ],
            evidence=[
                EvidenceItem(
                    summary="Synthetic reviewed-content contract evidence.",
                    level="guideline",
                    source_document="Synthetic content fixture",
                    source_version="2026.7-contract-reviewed",
                    provenance=trace,
                )
            ],
            provenance=trace,
        )
        return _UseCaseResult(
            validation=ValidationResult(
                is_valid=True,
                issues=[
                    ValidationIssue(
                        code="synthetic_contract_warning",
                        message="Synthetic warning retained at the validation boundary.",
                        severity="warning",
                        field_path="medication_order",
                    )
                ],
            ),
            rule_result=RuleResult(
                rule_id="renal-dose-cefepime-contract-v1",
                patient_id=patient.patient_id,
                encounter_id=order.encounter_id,
                status=ResultStatus.SUCCESS_WITH_WARNINGS,
                applied=True,
                passed=True,
                summary=(
                    "Prototype synthetic contract output; not for direct clinical use."
                ),
                renal_function_result=renal,
                recommendations=[recommendation],
                supporting_data={
                    "content_version": "2026.7-contract-reviewed",
                    "renal_band_id": "crcl_30_to_below_60",
                    "renal_value": "31.2000",
                    "review_status": "reviewed",
                },
                evaluated_at=evaluated_at,
                warnings=recommendation.warnings.copy(),
                evidence=recommendation.evidence.copy(),
                provenance=trace,
            ),
        )


def _request_payload() -> dict[str, object]:
    return {
        "patient_id": "synthetic-patient-contract-001",
        "birth_date": "1980-01-01",
        "sex": "female",
        "weight_value": "70.00",
        "weight_unit": "kg",
        "weight_type": "actual",
        "serum_creatinine_result_id": "synthetic-lab-contract-001",
        "serum_creatinine_value": "1.20",
        "serum_creatinine_unit": "mg/dL",
        "serum_creatinine_collected_at": "2026-07-24T07:30:00-04:00",
        "serum_creatinine_status": "final",
        "renal_function_stable": True,
        "renal_replacement_therapy": False,
        "pregnant_or_lactating": False,
        "medication_order_id": "synthetic-order-contract-001",
        "medication_system": "cds-medication-id",
        "medication_code": "cefepime",
        "regimen_id": "cefepime_severe_infection_iv_2g_q8h_30min",
        "formulation_id": "cefepime_injection",
        "dose_value": "2.00",
        "dose_unit": "g",
        "route_system": "cds-route-id",
        "route_code": "iv",
        "frequency_interval_value": "8",
        "frequency_interval_unit": "hours",
        "indication_system": "cds-indication-id",
        "indication_code": "severe_infection",
        "infusion_duration_value": "30",
        "infusion_duration_unit": "minutes",
        "requested_content_version": "2026.7-contract-reviewed",
        "evaluation_date": "2026-07-24",
        "evaluated_at": "2026-07-24T08:15:30.120000-04:00",
    }


def _write_request(tmp_path: Path) -> Path:
    path = tmp_path / "synthetic-renal-dose-contract-request.json"
    path.write_text(json.dumps(_request_payload()), encoding="utf-8")
    return path


def test_non_domain_public_imports_and_exit_codes_are_stable() -> None:
    for module, expected_exports in MODULE_EXPORTS:
        assert tuple(module.__all__) == expected_exports

    for public_object, module_name in PUBLIC_OBJECTS:
        assert public_object.__module__ == module_name

    assert (
        CLI_EXIT_SUCCESS,
        CLI_EXIT_SYSTEM_FAILURE,
        CLI_EXIT_INPUT_ERROR,
        CLI_EXIT_UNSUPPORTED,
        CLI_EXIT_CONTENT_FAILURE,
    ) == (0, 1, 2, 3, 4)


def test_cli_emits_complete_canonical_response_contract(tmp_path: Path) -> None:
    use_case = _ConfiguredUseCase()
    stdout = StringIO()
    stderr = StringIO()

    exit_code = main(
        [str(_write_request(tmp_path))],
        use_case=use_case,
        stdout=stdout,
        stderr=stderr,
    )

    assert exit_code == CLI_EXIT_SUCCESS
    assert stderr.getvalue() == ""
    assert len(use_case.calls) == 1
    call = use_case.calls[0]
    assert call["patient"].sex is Sex.FEMALE
    assert call["patient"].actual_body_weight == ValueWithUnit(
        value=Decimal("70.00"),
        unit="kg",
    )
    assert call["serum_creatinine_result"].value == ValueWithUnit(
        value=Decimal("1.20"),
        unit="mg/dL",
    )
    assert call["weight_type"] is WeightType.ACTUAL
    assert call["evaluated_at"].utcoffset() == timedelta(hours=-4)

    raw = stdout.getvalue()
    assert raw.endswith("\n")
    assert ": " not in raw
    assert ", " not in raw
    response = json.loads(raw)

    assert tuple(response) == ("rule_result", "validation")
    assert tuple(response["validation"]) == ("is_valid", "issues")
    assert tuple(response["rule_result"]) == RULE_RESULT_KEYS

    rule_result = response["rule_result"]
    renal = rule_result["renal_function_result"]
    recommendation = rule_result["recommendations"][0]
    dose = recommendation["dose_recommendation"]

    assert tuple(renal) == RENAL_RESULT_KEYS
    assert tuple(recommendation) == RECOMMENDATION_KEYS
    assert tuple(dose) == DOSE_RECOMMENDATION_KEYS
    assert tuple(rule_result["provenance"]) == PROVENANCE_KEYS
    assert tuple(recommendation["provenance"]) == PROVENANCE_KEYS

    assert rule_result["status"] == "success_with_warnings"
    assert renal["method"] == "cockcroft_gault"
    assert renal["sex"] == "female"
    assert renal["weight_type_used"] == "actual"
    assert renal["value"] == {"unit": "mL/min", "value": "31.2000"}
    assert renal["weight_used"] == {"unit": "kg", "value": "70.00"}
    assert dose["recommended_dose"] == {"unit": "g", "value": "1.00"}
    assert dose["frequency_interval"] == {"unit": "hours", "value": "12.0"}

    assert rule_result["evaluated_at"] == "2026-07-24T12:15:30.120000Z"
    assert renal["calculated_at"] == "2026-07-24T12:15:30.120000Z"
    assert rule_result["provenance"]["captured_at"] == (
        "2026-07-24T12:15:30.120000Z"
    )

    assert rule_result["rule_id"] == "renal-dose-cefepime-contract-v1"
    assert recommendation["linked_rule_id"] == "renal-dose-cefepime-contract-v1"
    assert rule_result["supporting_data"]["content_version"] == (
        "2026.7-contract-reviewed"
    )
    assert recommendation["provenance"]["version"] == "2026.7-contract-reviewed"
    assert recommendation["evidence"][0]["source_version"] == (
        "2026.7-contract-reviewed"
    )
    assert "not for direct clinical use" in rule_result["summary"]
