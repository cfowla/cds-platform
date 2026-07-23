"""Deterministic golden cases for the exact-context cefepime renal-dose rule."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

from cds.domain.clinical import MedicationOrder
from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    RenalContentEndpoint,
    RenalContentInterval,
    RenalDoseBandContent,
    RenalDoseContent,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRecommendationContent,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSourceContent,
    RenalDoseSupportedContext,
)
from cds.rules.cefepime import evaluate_cefepime_rule
from cds.utils.serialization import dumps_json

GOLDEN_PATH = (
    Path(__file__).resolve().parents[3]
    / "examples"
    / "golden"
    / "cefepime_rule"
    / "cases.json"
)
CASE_NAMES = (
    "normal",
    "impaired",
    "exact_boundary",
    "missing",
    "unsupported_regimen",
    "unstable_renal_function",
    "contraindication",
)
EVALUATED_AT = datetime(2026, 7, 22, 16, 0, tzinfo=UTC)
CONTENT_VERSION = "synthetic-day-48"
REGIMEN_ID = "synthetic_iv_2_g_q12h_over_30_minutes"
NON_PRODUCTION_TEXT = "Synthetic software fixture only; not clinical guidance."


def _quantity(value: str, unit: str) -> RenalDoseQuantity:
    return RenalDoseQuantity(value=Decimal(value), unit=unit)


def _recommendation(
    *, action: str, dose_value: str, dose_unit: str, frequency_value: str
) -> RenalDoseRecommendationContent:
    return RenalDoseRecommendationContent(
        action=action,  # type: ignore[arg-type]
        dose=_quantity(dose_value, dose_unit),
        route_id="iv",
        frequency_interval=_quantity(frequency_value, "hours"),
        infusion_duration=_quantity("30", "minutes"),
        rationale=NON_PRODUCTION_TEXT,
        monitoring=("Synthetic monitoring text; not clinical guidance.",),
    )


def _content() -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="renal_dose_cefepime_synthetic_day_48",
        content_version=CONTENT_VERSION,
        rule_id="cefepime_synthetic_day_48_rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Cefepime"),
        regimen=RenalDoseRegimenContent(
            id=REGIMEN_ID,
            display="Synthetic cefepime regimen — not clinical guidance",
            indication_ids=("synthetic_indication",),
            route_id="iv",
            formulation_id="powder_for_solution",
            base_dose=_quantity("2", "g"),
            frequency_interval=_quantity("12", "hours"),
            infusion_duration=_quantity("30", "minutes"),
        ),
        supported_context=RenalDoseSupportedContext(
            minimum_age_years=18,
            renal_method="cockcroft_gault",
            renal_unit="mL/min",
            renal_function_stable=True,
            renal_replacement_therapy=False,
            limitations=(NON_PRODUCTION_TEXT,),
        ),
        renal_domain=RenalContentInterval(
            lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
            upper=None,
        ),
        renal_bands=(
            RenalDoseBandContent(
                id="impaired_below_30",
                lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
                upper=RenalContentEndpoint(value=Decimal("30"), inclusive=False),
                outcome="recommendation",
                recommendation=_recommendation(
                    action="adjust_dose",
                    dose_value="500",
                    dose_unit="mg",
                    frequency_value="24",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(NON_PRODUCTION_TEXT,),
            ),
            RenalDoseBandContent(
                id="impaired_30_to_60",
                lower=RenalContentEndpoint(value=Decimal("30"), inclusive=True),
                upper=RenalContentEndpoint(value=Decimal("60"), inclusive=True),
                outcome="recommendation",
                recommendation=_recommendation(
                    action="adjust_dose",
                    dose_value="1",
                    dose_unit="g",
                    frequency_value="24",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(NON_PRODUCTION_TEXT,),
            ),
            RenalDoseBandContent(
                id="normal_above_60",
                lower=RenalContentEndpoint(value=Decimal("60"), inclusive=False),
                upper=None,
                outcome="recommendation",
                recommendation=_recommendation(
                    action="continue",
                    dose_value="2",
                    dose_unit="g",
                    frequency_value="12",
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_source",),
                limitations=(NON_PRODUCTION_TEXT,),
            ),
        ),
        sources=(
            RenalDoseSourceContent(
                id="synthetic_source",
                evidence_level="expert_opinion",
                citation="Synthetic source with no clinical authority.",
                source_document="Synthetic Day 48 fixture specification",
                source_version="1",
                publication_date=date(2026, 7, 22),
                url=None,
            ),
        ),
        review=RenalDoseReviewContent(
            status="reviewed",
            reviewed_content_version=CONTENT_VERSION,
            reviewer="Synthetic Reviewer",
            reviewer_role="Software test fixture reviewer",
            reviewed_on=date(2026, 7, 22),
            notes=NON_PRODUCTION_TEXT,
        ),
        limitations=("Prototype only — not for direct clinical use.",),
    )


def _contraindication_content() -> RenalDoseContent:
    band = RenalDoseBandContent(
        id="synthetic_contraindication",
        lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
        upper=None,
        outcome="no_recommendation",
        recommendation=None,
        no_recommendation_reason=(
            "Synthetic contraindication fixture; no dose recommendation."
        ),
        source_ids=("synthetic_source",),
        limitations=(NON_PRODUCTION_TEXT,),
    )
    return replace(_content(), renal_bands=(band,))


def _order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order-day-48",
        patient_id="synthetic-patient-day-48",
        encounter_id="synthetic-encounter-day-48",
        medication=CodeableConcept(code="cefepime", text="Cefepime"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="hours"),
        indication=CodeableConcept(code="synthetic_indication"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="minutes"),
    )


def _renal(case_name: str, value: str | None) -> RenalFunctionResult:
    return RenalFunctionResult(
        result_id=f"synthetic-renal-{case_name.replace('_', '-')}",
        patient_id="synthetic-patient-day-48",
        encounter_id="synthetic-encounter-day-48",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(
            value=Decimal(value) if value is not None else None,
            unit="mL/min",
        ),
        normalized_to_bsa=False,
        evaluation_date=date(2026, 7, 22),
        age_years=65,
        calculated_at=EVALUATED_AT if value is not None else None,
    )


def _evaluate(
    *,
    case_name: str,
    renal_value: str | None,
    content: RenalDoseContent | None = None,
    regimen_id: str | None = REGIMEN_ID,
    renal_function_stable: bool | None = True,
) -> RuleResult:
    return evaluate_cefepime_rule(
        order=_order(),
        renal_function=_renal(case_name, renal_value),
        regimen_id=regimen_id,
        formulation_id="powder_for_solution",
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=False,
        requested_content_version=CONTENT_VERSION,
        content=content or _content(),
        evaluated_at=EVALUATED_AT,
    )


def build_cases() -> dict[str, RuleResult]:
    return {
        "normal": _evaluate(case_name="normal", renal_value="75"),
        "impaired": _evaluate(case_name="impaired", renal_value="15"),
        "exact_boundary": _evaluate(
            case_name="exact_boundary",
            renal_value="30",
        ),
        "missing": _evaluate(case_name="missing", renal_value=None),
        "unsupported_regimen": _evaluate(
            case_name="unsupported_regimen",
            renal_value="45",
            regimen_id="synthetic_unsupported_regimen",
        ),
        "unstable_renal_function": _evaluate(
            case_name="unstable_renal_function",
            renal_value="45",
            renal_function_stable=False,
        ),
        "contraindication": _evaluate(
            case_name="contraindication",
            renal_value="15",
            content=_contraindication_content(),
        ),
    }


def test_cefepime_golden_cases_byte_match_canonical_regeneration() -> None:
    generated = dumps_json(build_cases()).encode("utf-8")

    assert GOLDEN_PATH.read_bytes() == generated


def test_cefepime_golden_case_regeneration_is_deterministic() -> None:
    assert dumps_json(build_cases()) == dumps_json(build_cases())


def test_cefepime_golden_cases_cover_required_outcomes() -> None:
    payloads = json.loads(GOLDEN_PATH.read_text())

    assert tuple(sorted(payloads)) == tuple(sorted(CASE_NAMES))
    assert payloads["normal"]["supporting_data"]["renal_band_id"] == "normal_above_60"
    assert payloads["impaired"]["supporting_data"]["renal_band_id"] == "impaired_below_30"
    assert (
        payloads["exact_boundary"]["supporting_data"]["renal_band_id"]
        == "impaired_30_to_60"
    )
    assert payloads["exact_boundary"]["supporting_data"]["renal_value"] == "30"
    assert payloads["missing"]["status"] == ResultStatus.INCOMPLETE
    assert payloads["missing"]["renal_function_result"]["value"]["value"] is None
    assert payloads["missing"]["recommendations"] == []
    assert payloads["unsupported_regimen"]["status"] == ResultStatus.NOT_APPLICABLE
    assert payloads["unsupported_regimen"]["warnings"][0]["code"] == (
        "unsupported_cefepime_regimen"
    )
    assert payloads["unstable_renal_function"]["warnings"][0]["code"] == (
        "unsupported_unstable_renal_function"
    )
    assert payloads["contraindication"]["applied"] is True
    assert payloads["contraindication"]["passed"] is False
    assert payloads["contraindication"]["recommendations"] == []
    assert payloads["contraindication"]["warnings"][0]["code"] == (
        "cefepime_no_recommendation_band"
    )


def test_cefepime_golden_cases_are_synthetic_and_fail_closed() -> None:
    payloads = json.loads(GOLDEN_PATH.read_text())

    for name, payload in payloads.items():
        assert name in CASE_NAMES
        assert payload["patient_id"].startswith("synthetic-patient-")
        assert payload["rule_id"] == "cefepime_synthetic_day_48_rule"
        assert payload["supporting_data"]["content_version"] == CONTENT_VERSION

    for name in (
        "missing",
        "unsupported_regimen",
        "unstable_renal_function",
        "contraindication",
    ):
        assert payloads[name]["recommendations"] == []
