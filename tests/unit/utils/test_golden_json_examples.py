"""Golden examples for the standard renal-evaluation output contract."""

from __future__ import annotations

import json
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from cds.domain.enums import RenalMethod, ResultStatus, Severity, Sex, WeightType
from cds.domain.outputs import (
    CDSRecommendation,
    Contraindication,
    DoseRecommendation,
    RenalFunctionResult,
    RuleResult,
)
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.utils.serialization import dumps_json

GOLDEN_DIR = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "golden"
    / "renal_evaluation"
)
EXAMPLE_NAMES = ("complete", "incomplete", "unsupported", "warning_bearing")
NON_PRODUCTION_NOTICE = (
    "Synthetic non-production schema demonstration only; not for direct clinical use "
    "and not reviewed clinical guidance."
)
EVALUATED_AT = datetime(2026, 7, 20, 16, 30, tzinfo=UTC)
CAPTURED_AT = datetime(2026, 7, 20, 16, 0, tzinfo=UTC)
EVALUATION_DATE = date(2026, 7, 20)


def _provenance(source_identifier: str) -> Provenance:
    return Provenance(
        source_type="manual_entry",
        source_name="Synthetic golden-example fixture",
        source_identifier=source_identifier,
        captured_at=CAPTURED_AT,
        author="cds-platform test suite",
        version="day-20",
    )


def _evidence(source_identifier: str) -> EvidenceItem:
    return EvidenceItem(
        summary="Synthetic evidence metadata for serialization demonstration only.",
        level="unknown",
        source_document="Non-production schema fixture",
        source_version="day-20",
        provenance=_provenance(source_identifier),
    )


def _renal_result(
    *,
    suffix: str,
    value: Decimal | None,
    serum_creatinine: Decimal | None,
    age_years: int | None,
    sex: Sex,
    weight: Decimal | None,
    weight_type: WeightType,
    normalized_to_bsa: bool | None,
    warnings: list[WarningNote] | None = None,
) -> RenalFunctionResult:
    return RenalFunctionResult(
        result_id=f"synthetic-renal-{suffix}",
        patient_id=f"synthetic-patient-{suffix}",
        encounter_id=f"synthetic-encounter-{suffix}",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=value, unit="mL/min"),
        normalized_to_bsa=normalized_to_bsa,
        evaluation_date=EVALUATION_DATE,
        serum_creatinine_result_id=(
            f"synthetic-lab-{suffix}" if serum_creatinine is not None else None
        ),
        serum_creatinine=ValueWithUnit(
            value=serum_creatinine,
            unit="mg/dL" if serum_creatinine is not None else None,
        ),
        serum_creatinine_collected_at=(
            datetime(2026, 7, 20, 15, 45, tzinfo=UTC)
            if serum_creatinine is not None
            else None
        ),
        age_years=age_years,
        sex=sex,
        weight_used=ValueWithUnit(
            value=weight,
            unit="kg" if weight is not None else None,
        ),
        weight_type_used=weight_type,
        calculated_at=EVALUATED_AT if value is not None else None,
        warnings=warnings or [],
        evidence=[_evidence(f"synthetic-evidence-renal-{suffix}")],
        provenance=_provenance(f"synthetic-provenance-renal-{suffix}"),
    )


def _dose_recommendation(suffix: str, dose: Decimal) -> DoseRecommendation:
    return DoseRecommendation(
        medication=CodeableConcept(
            text=f"Synthetic medication {suffix.upper()}",
            system="urn:example:synthetic-medication",
            code=f"SYNTH-{suffix.upper()}",
        ),
        recommended_dose=ValueWithUnit(value=dose, unit="mg"),
        recommended_route=CodeableConcept(
            text="Synthetic oral route",
            system="urn:example:synthetic-route",
            code="SYNTH-PO",
        ),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="hours"),
        regimen_variant="illustrative-only",
        rationale=(
            "Illustrative dose-shaped value for schema serialization; "
            "not reviewed clinical guidance."
        ),
        evidence=[_evidence(f"synthetic-evidence-dose-{suffix}")],
        provenance=_provenance(f"synthetic-provenance-dose-{suffix}"),
    )


def _recommendation(
    *, suffix: str, renal_result: RenalFunctionResult, dose: Decimal
) -> CDSRecommendation:
    return CDSRecommendation(
        recommendation_id=f"synthetic-recommendation-{suffix}",
        patient_id=f"synthetic-patient-{suffix}",
        encounter_id=f"synthetic-encounter-{suffix}",
        title="Synthetic renal-evaluation schema recommendation",
        action="adjust_dose",
        strength="info",
        summary=NON_PRODUCTION_NOTICE,
        rationale=(
            "This object demonstrates the serialized recommendation shape only; "
            "it is not a clinical decision."
        ),
        renal_function_result=renal_result,
        dose_recommendation=_dose_recommendation(suffix, dose),
        contraindications=[
            Contraindication(
                code="synthetic-contraindication-check",
                summary="Synthetic contraindication check",
                applies=False,
                rationale="Explicit negative demonstration value.",
                severity=Severity.UNKNOWN,
                related_medication=CodeableConcept(
                    text=f"Synthetic medication {suffix.upper()}",
                    system="urn:example:synthetic-medication",
                    code=f"SYNTH-{suffix.upper()}",
                ),
                provenance=_provenance(
                    f"synthetic-provenance-contraindication-{suffix}"
                ),
            )
        ],
        suggested_monitoring=["Synthetic monitoring placeholder; not clinical guidance."],
        linked_order_id=f"synthetic-order-{suffix}",
        linked_rule_id=f"synthetic-rule-{suffix}",
        evidence=[_evidence(f"synthetic-evidence-recommendation-{suffix}")],
        provenance=_provenance(f"synthetic-provenance-recommendation-{suffix}"),
    )


def build_examples() -> dict[str, RuleResult]:
    complete_renal = _renal_result(
        suffix="complete",
        value=Decimal("48.20"),
        serum_creatinine=Decimal("1.30"),
        age_years=64,
        sex=Sex.FEMALE,
        weight=Decimal("70.00"),
        weight_type=WeightType.ACTUAL,
        normalized_to_bsa=False,
    )
    warning = WarningNote(
        code="synthetic-input-limitation",
        message=(
            "A synthetic input limitation is retained to demonstrate structured warnings; "
            "this is not clinical guidance."
        ),
        severity="warning",
        provenance=_provenance("synthetic-provenance-warning-bearing-warning"),
    )
    warning_renal = _renal_result(
        suffix="warning-bearing",
        value=Decimal("32.00"),
        serum_creatinine=Decimal("1.80"),
        age_years=71,
        sex=Sex.MALE,
        weight=Decimal("82.50"),
        weight_type=WeightType.ACTUAL,
        normalized_to_bsa=False,
        warnings=[warning],
    )
    incomplete_renal = _renal_result(
        suffix="incomplete",
        value=None,
        serum_creatinine=None,
        age_years=59,
        sex=Sex.UNKNOWN,
        weight=None,
        weight_type=WeightType.UNKNOWN,
        normalized_to_bsa=None,
    )

    return {
        "complete": RuleResult(
            rule_id="synthetic-rule-complete",
            patient_id="synthetic-patient-complete",
            encounter_id="synthetic-encounter-complete",
            status=ResultStatus.SUCCESS,
            applied=True,
            passed=True,
            summary=NON_PRODUCTION_NOTICE,
            renal_function_result=complete_renal,
            recommendations=[
                _recommendation(
                    suffix="complete",
                    renal_result=complete_renal,
                    dose=Decimal("250.00"),
                )
            ],
            supporting_data={
                "schema_purpose": "non-production demonstration",
                "synthetic_data": True,
                "clinical_guidance_reviewed": False,
                "missing_required_inputs": None,
            },
            evaluated_at=EVALUATED_AT,
            assumptions=[
                Assumption(
                    code="synthetic-inputs-accepted-for-demonstration",
                    description=(
                        "Typed synthetic inputs are accepted only to demonstrate serialization."
                    ),
                    applies=True,
                    provenance=_provenance(
                        "synthetic-provenance-complete-assumption"
                    ),
                )
            ],
            evidence=[_evidence("synthetic-evidence-complete")],
            provenance=_provenance("synthetic-provenance-complete"),
        ),
        "incomplete": RuleResult(
            rule_id="synthetic-rule-incomplete",
            patient_id="synthetic-patient-incomplete",
            encounter_id="synthetic-encounter-incomplete",
            status=ResultStatus.INCOMPLETE,
            applied=False,
            passed=None,
            summary=NON_PRODUCTION_NOTICE,
            renal_function_result=incomplete_renal,
            recommendations=[],
            supporting_data={
                "schema_purpose": "non-production demonstration",
                "synthetic_data": True,
                "required_inputs_complete": False,
                "calculated_clearance": None,
            },
            evaluated_at=EVALUATED_AT,
            warnings=[
                WarningNote(
                    code="synthetic-missing-required-inputs",
                    message=(
                        "Synthetic required inputs are missing; no dose recommendation is present."
                    ),
                    severity="warning",
                    provenance=_provenance(
                        "synthetic-provenance-incomplete-warning"
                    ),
                )
            ],
            evidence=[_evidence("synthetic-evidence-incomplete")],
            provenance=_provenance("synthetic-provenance-incomplete"),
        ),
        "unsupported": RuleResult(
            rule_id="synthetic-rule-unsupported",
            patient_id="synthetic-patient-unsupported",
            encounter_id="synthetic-encounter-unsupported",
            status=ResultStatus.NOT_APPLICABLE,
            applied=False,
            passed=None,
            summary=NON_PRODUCTION_NOTICE,
            renal_function_result=None,
            recommendations=[],
            supporting_data={
                "schema_purpose": "non-production demonstration",
                "synthetic_data": True,
                "scenario_supported": False,
                "unsupported_reason": "Synthetic unsupported scenario",
            },
            evaluated_at=EVALUATED_AT,
            warnings=[
                WarningNote(
                    code="synthetic-unsupported-scenario",
                    message=(
                        "Synthetic scenario is outside the demonstration's supported path; "
                        "no dose recommendation is present."
                    ),
                    severity="warning",
                    provenance=_provenance(
                        "synthetic-provenance-unsupported-warning"
                    ),
                )
            ],
            evidence=[_evidence("synthetic-evidence-unsupported")],
            provenance=_provenance("synthetic-provenance-unsupported"),
        ),
        "warning_bearing": RuleResult(
            rule_id="synthetic-rule-warning-bearing",
            patient_id="synthetic-patient-warning-bearing",
            encounter_id="synthetic-encounter-warning-bearing",
            status=ResultStatus.SUCCESS_WITH_WARNINGS,
            applied=True,
            passed=True,
            summary=NON_PRODUCTION_NOTICE,
            renal_function_result=warning_renal,
            recommendations=[
                _recommendation(
                    suffix="warning-bearing",
                    renal_result=warning_renal,
                    dose=Decimal("125.00"),
                )
            ],
            supporting_data={
                "schema_purpose": "non-production demonstration",
                "synthetic_data": True,
                "warning_count": 1,
                "clinical_guidance_reviewed": False,
            },
            evaluated_at=EVALUATED_AT,
            warnings=[warning],
            evidence=[_evidence("synthetic-evidence-warning-bearing")],
            provenance=_provenance("synthetic-provenance-warning-bearing"),
        ),
    }


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_golden_example_byte_matches_canonical_regeneration(
    example_name: str,
) -> None:
    generated = dumps_json(build_examples()[example_name]).encode("utf-8")
    committed = (GOLDEN_DIR / f"{example_name}.json").read_bytes()

    assert committed == generated


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_committed_golden_example_parses_successfully(example_name: str) -> None:
    payload = json.loads((GOLDEN_DIR / f"{example_name}.json").read_text())

    assert payload["rule_id"] == f"synthetic-rule-{example_name.replace('_', '-')}"


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_golden_example_regeneration_is_deterministic(example_name: str) -> None:
    first = dumps_json(build_examples()[example_name])
    second = dumps_json(build_examples()[example_name])

    assert first == second


def test_example_statuses_and_fail_closed_recommendations_are_distinct() -> None:
    payloads = {
        name: json.loads((GOLDEN_DIR / f"{name}.json").read_text())
        for name in EXAMPLE_NAMES
    }

    assert payloads["complete"]["status"] == "success"
    assert payloads["incomplete"]["status"] == "incomplete"
    assert payloads["unsupported"]["status"] == "not_applicable"
    assert payloads["warning_bearing"]["status"] == "success_with_warnings"
    assert payloads["incomplete"]["recommendations"] == []
    assert payloads["unsupported"]["recommendations"] == []
    assert payloads["incomplete"]["passed"] is None
    assert payloads["unsupported"]["passed"] is None
    assert payloads["complete"]["recommendations"][0]["contraindications"][0][
        "applies"
    ] is False


def test_missing_quantities_remain_null_and_decimals_are_strings() -> None:
    payloads = {
        name: json.loads((GOLDEN_DIR / f"{name}.json").read_text())
        for name in EXAMPLE_NAMES
    }

    assert payloads["incomplete"]["renal_function_result"]["value"]["value"] is None
    assert (
        payloads["incomplete"]["renal_function_result"]["serum_creatinine"][
            "value"
        ]
        is None
    )
    assert payloads["complete"]["renal_function_result"]["value"]["value"] == (
        "48.20"
    )
    assert payloads["complete"]["recommendations"][0]["dose_recommendation"][
        "recommended_dose"
    ]["value"] == "250.00"
    assert payloads["warning_bearing"]["renal_function_result"]["value"][
        "value"
    ] == "32.00"
    assert payloads["warning_bearing"]["warnings"][0]["code"] == (
        "synthetic-input-limitation"
    )


def test_examples_are_synthetic_and_disclaim_clinical_use() -> None:
    for name in EXAMPLE_NAMES:
        payload = json.loads((GOLDEN_DIR / f"{name}.json").read_text())
        serialized = dumps_json(payload).lower()

        assert payload["patient_id"].startswith("synthetic-patient-")
        assert payload["encounter_id"].startswith("synthetic-encounter-")
        assert payload["supporting_data"]["synthetic_data"] is True
        assert "synthetic non-production schema demonstration only" in serialized
        assert "not for direct clinical use" in serialized
        assert "not reviewed clinical guidance" in serialized
