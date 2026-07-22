"""Public contract tests for CDS domain imports and canonical serialization."""

from __future__ import annotations

from dataclasses import fields
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from enum import StrEnum
from typing import Any

import pytest

import cds.domain.models as compatibility_models
from cds.domain.clinical import (
    Allergy,
    Encounter,
    LabResult,
    MedicationOrder,
    Patient,
    Problem,
    VitalSign,
)
from cds.domain.enums import RenalMethod, ResultStatus, Severity, Sex, WeightType
from cds.domain.outputs import (
    Alert,
    CDSRecommendation,
    Contraindication,
    DoseRecommendation,
    RenalFunctionResult,
    RuleResult,
)
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit
from cds.utils.serialization import dumps_json, to_jsonable


FOCUSED_PUBLIC_OBJECTS = (
    (Patient, "cds.domain.clinical"),
    (MedicationOrder, "cds.domain.clinical"),
    (RuleResult, "cds.domain.outputs"),
    (RenalFunctionResult, "cds.domain.outputs"),
    (Provenance, "cds.domain.support"),
    (WarningNote, "cds.domain.support"),
    (CodeableConcept, "cds.domain.value_objects"),
    (ValueWithUnit, "cds.domain.value_objects"),
    (Sex, "cds.domain.enums"),
    (ResultStatus, "cds.domain.enums"),
)

COMPATIBILITY_EXPORTS = (
    ("Alert", Alert),
    ("Allergy", Allergy),
    ("Assumption", Assumption),
    ("CDSRecommendation", CDSRecommendation),
    ("CodeableConcept", CodeableConcept),
    ("Contraindication", Contraindication),
    ("DoseRecommendation", DoseRecommendation),
    ("Encounter", Encounter),
    ("EvidenceItem", EvidenceItem),
    ("LabResult", LabResult),
    ("MedicationOrder", MedicationOrder),
    ("Patient", Patient),
    ("Problem", Problem),
    ("Provenance", Provenance),
    ("RenalFunctionResult", RenalFunctionResult),
    ("RuleResult", RuleResult),
    ("TimeRange", TimeRange),
    ("ValueWithUnit", ValueWithUnit),
    ("VitalSign", VitalSign),
    ("WarningNote", WarningNote),
)

OUTPUT_FIELDS = (
    (
        RenalFunctionResult,
        (
            "result_id",
            "patient_id",
            "encounter_id",
            "method",
            "value",
            "normalized_to_bsa",
            "evaluation_date",
            "serum_creatinine_result_id",
            "serum_creatinine",
            "serum_creatinine_collected_at",
            "age_years",
            "sex",
            "weight_used",
            "weight_type_used",
            "measured_period",
            "calculated_at",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
    (
        Contraindication,
        (
            "code",
            "summary",
            "applies",
            "rationale",
            "severity",
            "related_problem",
            "related_medication",
            "related_lab",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
    (
        DoseRecommendation,
        (
            "medication",
            "recommended_dose",
            "recommended_route",
            "frequency_interval",
            "infusion_duration",
            "max_single_dose",
            "max_daily_dose",
            "regimen_variant",
            "rationale",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
    (
        CDSRecommendation,
        (
            "recommendation_id",
            "patient_id",
            "encounter_id",
            "title",
            "action",
            "strength",
            "summary",
            "rationale",
            "renal_function_result",
            "dose_recommendation",
            "contraindications",
            "suggested_monitoring",
            "linked_order_id",
            "linked_rule_id",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
    (
        Alert,
        (
            "alert_id",
            "patient_id",
            "encounter_id",
            "category",
            "severity",
            "title",
            "message",
            "interruptive",
            "recommendation",
            "linked_order_id",
            "linked_rule_id",
            "deduplication_key",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
    (
        RuleResult,
        (
            "rule_id",
            "patient_id",
            "encounter_id",
            "status",
            "applied",
            "passed",
            "summary",
            "renal_function_result",
            "recommendations",
            "alerts",
            "supporting_data",
            "evaluated_at",
            "assumptions",
            "warnings",
            "evidence",
            "provenance",
        ),
    ),
)

ENUM_WIRE_VALUES: tuple[tuple[type[StrEnum], dict[str, str]], ...] = (
    (
        Sex,
        {
            "MALE": "male",
            "FEMALE": "female",
            "OTHER": "other",
            "UNKNOWN": "unknown",
        },
    ),
    (
        ResultStatus,
        {
            "SUCCESS": "success",
            "SUCCESS_WITH_WARNINGS": "success_with_warnings",
            "INCOMPLETE": "incomplete",
            "NOT_APPLICABLE": "not_applicable",
            "FAILED": "failed",
        },
    ),
    (
        RenalMethod,
        {
            "COCKCROFT_GAULT": "cockcroft_gault",
            "CKD_EPI": "ckd_epi",
            "MDRD": "mdrd",
            "MEASURED_CRCL": "measured_crcl",
            "UNKNOWN": "unknown",
        },
    ),
    (
        Severity,
        {
            "LOW": "low",
            "MODERATE": "moderate",
            "HIGH": "high",
            "CRITICAL": "critical",
            "UNKNOWN": "unknown",
        },
    ),
    (
        WeightType,
        {
            "ACTUAL": "actual",
            "IDEAL": "ideal",
            "ADJUSTED": "adjusted",
            "OTHER": "other",
            "UNKNOWN": "unknown",
        },
    ),
)


@pytest.mark.parametrize(("public_object", "module_name"), FOCUSED_PUBLIC_OBJECTS)
def test_focused_modules_expose_representative_public_objects(
    public_object: object,
    module_name: str,
) -> None:
    assert public_object.__module__ == module_name


def test_models_compatibility_exports_match_focused_objects() -> None:
    assert compatibility_models.__all__ == [name for name, _ in COMPATIBILITY_EXPORTS]

    for name, focused_object in COMPATIBILITY_EXPORTS:
        assert getattr(compatibility_models, name) is focused_object


@pytest.mark.parametrize(("model_type", "expected_names"), OUTPUT_FIELDS)
def test_standard_output_field_names_and_order_are_stable(
    model_type: type[Any],
    expected_names: tuple[str, ...],
) -> None:
    assert tuple(model_field.name for model_field in fields(model_type)) == expected_names


@pytest.mark.parametrize(("enum_type", "expected_mapping"), ENUM_WIRE_VALUES)
def test_enum_member_names_and_wire_values_are_stable(
    enum_type: type[StrEnum],
    expected_mapping: dict[str, str],
) -> None:
    assert {member.name: member.value for member in enum_type} == expected_mapping


@pytest.mark.parametrize(
    ("value", "expected"),
    (
        (Decimal("1.20"), "1.20"),
        (Decimal("0"), "0"),
        (Decimal("1234567890.00000100"), "1234567890.00000100"),
    ),
)
def test_decimal_values_preserve_precision_and_scale(
    value: Decimal,
    expected: str,
) -> None:
    assert to_jsonable(value) == expected


def test_timezone_aware_datetime_is_normalized_to_utc_with_z_suffix() -> None:
    source_time = datetime(
        2026,
        7,
        21,
        17,
        30,
        45,
        120000,
        tzinfo=timezone(timedelta(hours=-4)),
    )

    assert to_jsonable(source_time) == "2026-07-21T21:30:45.120000Z"


def test_nested_domain_objects_use_declared_fields_and_enum_wire_values() -> None:
    result = RuleResult(
        rule_id="synthetic-rule-contract",
        patient_id="synthetic-patient-contract",
        encounter_id="synthetic-encounter-contract",
        status=ResultStatus.SUCCESS_WITH_WARNINGS,
        applied=True,
        passed=False,
        summary=(
            "Synthetic non-production contract fixture; not for direct clinical use."
        ),
        renal_function_result=RenalFunctionResult(
            result_id="synthetic-renal-contract",
            patient_id="synthetic-patient-contract",
            encounter_id="synthetic-encounter-contract",
            method=RenalMethod.COCKCROFT_GAULT,
            value=ValueWithUnit(value=Decimal("31.20"), unit="mL/min"),
            normalized_to_bsa=False,
            sex=Sex.FEMALE,
            weight_type_used=WeightType.ACTUAL,
        ),
        supporting_data={
            "synthetic_data": True,
            "clinical_guidance_reviewed": False,
        },
    )

    serialized = to_jsonable(result)

    assert tuple(serialized) == tuple(field.name for field in fields(RuleResult))
    assert serialized["status"] == "success_with_warnings"
    assert serialized["renal_function_result"]["method"] == "cockcroft_gault"
    assert serialized["renal_function_result"]["sex"] == "female"
    assert serialized["renal_function_result"]["weight_type_used"] == "actual"
    assert serialized["renal_function_result"]["value"] == {
        "value": "31.20",
        "unit": "mL/min",
    }
    assert serialized["supporting_data"]["synthetic_data"] is True
    assert "not for direct clinical use" in serialized["summary"]


def test_missing_false_and_zero_values_remain_distinct() -> None:
    serialized = to_jsonable(
        RuleResult(
            rule_id="synthetic-rule-distinct-values",
            applied=False,
            passed=None,
            supporting_data={"numeric_zero": 0},
        )
    )

    assert serialized["passed"] is None
    assert serialized["applied"] is False
    assert serialized["supporting_data"]["numeric_zero"] == 0
    assert type(serialized["supporting_data"]["numeric_zero"]) is int


def test_deterministic_json_is_independent_of_mapping_insertion_order() -> None:
    first = {"z": Decimal("2.00"), "a": {"beta": False, "alpha": None}}
    second = {"a": {"alpha": None, "beta": False}, "z": Decimal("2.00")}

    assert dumps_json(first) == dumps_json(second)
    assert dumps_json(first) == (
        '{"a":{"alpha":null,"beta":false},"z":"2.00"}'
    )


@pytest.mark.parametrize(
    ("value", "exception_type", "message"),
    (
        (
            datetime(2026, 7, 21, 12, 15),
            ValueError,
            "timezone-aware",
        ),
        ({1: "unsupported"}, TypeError, "keys must be strings"),
        ({"unsupported"}, TypeError, "Unsupported JSON serialization type: set"),
    ),
)
def test_unsupported_inputs_fail_explicitly(
    value: object,
    exception_type: type[Exception],
    message: str,
) -> None:
    with pytest.raises(exception_type, match=message):
        to_jsonable(value)
