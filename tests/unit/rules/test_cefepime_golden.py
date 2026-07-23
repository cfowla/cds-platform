"""Deterministic golden JSON cases for the synthetic cefepime rule contract."""

from __future__ import annotations

import json
from dataclasses import replace
from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest

from cds.domain.clinical import MedicationOrder
from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.domain.support import Provenance
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

GOLDEN_DIR = Path(__file__).resolve().parents[3] / "examples" / "golden" / "cefepime"
EXAMPLE_NAMES = (
    "normal",
    "impaired",
    "exact_boundary",
    "missing",
    "unsupported_regimen",
    "unstable_renal_function",
    "contraindication",
)
EVALUATED_AT = datetime(2026, 7, 22, 12, 0, tzinfo=UTC)
NON_PRODUCTION_NOTICE = (
    "Synthetic cefepime golden fixture only; not for direct clinical use or reviewed clinical "
    "guidance."
)


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
        rationale=NON_PRODUCTION_NOTICE,
        monitoring=("Synthetic monitoring placeholder; not clinical guidance.",),
    )


def _default_bands() -> tuple[RenalDoseBandContent, ...]:
    return (
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
            limitations=(),
        ),
        RenalDoseBandContent(
            id="normal_at_or_above_30",
            lower=RenalContentEndpoint(value=Decimal("30"), inclusive=True),
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
            limitations=(),
        ),
    )


def _content(
    *, bands: tuple[RenalDoseBandContent, ...] | None = None
) -> RenalDoseContent:
    return RenalDoseContent(
        schema_version="1",
        content_id="renal_dose_cefepime_synthetic_iv_2_g_q12h",
        content_version="1.0.0",
        rule_id="cefepime_synthetic_renal_rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Cefepime"),
        regimen=RenalDoseRegimenContent(
            id="synthetic_iv_2_g_q12h_over_30_minutes",
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
            limitations=(NON_PRODUCTION_NOTICE,),
        ),
        renal_domain=RenalContentInterval(
            lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
            upper=None,
        ),
        renal_bands=bands or _default_bands(),
        sources=(
            RenalDoseSourceContent(
                id="synthetic_source",
                evidence_level="expert_opinion",
                citation="Synthetic source with no clinical authority.",
                source_document="Synthetic cefepime golden fixture",
                source_version="1",
                publication_date=date(2026, 7, 22),
                url=None,
            ),
        ),
        review=RenalDoseReviewContent(
            status="reviewed",
            reviewed_content_version="1.0.0",
            reviewer="Synthetic Fixture Reviewer",
            reviewer_role="Software test fixture reviewer",
            reviewed_on=date(2026, 7, 22),
            notes=NON_PRODUCTION_NOTICE,
        ),
        limitations=(NON_PRODUCTION_NOTICE,),
    )


def _order() -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order-1",
        patient_id="synthetic-patient-1",
        encounter_id="synthetic-encounter-1",
        medication=CodeableConcept(code="cefepime", text="Cefepime"),
        dose=ValueWithUnit(value=Decimal("2"), unit="g"),
        route=CodeableConcept(code="iv"),
        frequency_interval=ValueWithUnit(value=Decimal("12"), unit="hours"),
        indication=CodeableConcept(code="synthetic_indication"),
        infusion_duration=ValueWithUnit(value=Decimal("30"), unit="minutes"),
    )


def _renal(value: str | None) -> RenalFunctionResult:
    return RenalFunctionResult(
        result_id="synthetic-renal-1",
        patient_id="synthetic-patient-1",
        encounter_id="synthetic-encounter-1",
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(
            value=Decimal(value) if value is not None else None,
            unit="mL/min",
        ),
        normalized_to_bsa=False,
        age_years=65,
        provenance=Provenance(
            source_type="manual_entry",
            source_name=NON_PRODUCTION_NOTICE,
            source_identifier="synthetic-cefepime-golden-renal",
            captured_at=EVALUATED_AT,
            author="cds-platform test suite",
            version="day-48",
        ),
    )


def _evaluate(
    *,
    renal: RenalFunctionResult,
    content: RenalDoseContent | None = None,
    regimen_id: str = "synthetic_iv_2_g_q12h_over_30_minutes",
    renal_function_stable: bool = True,
) -> RuleResult:
    return evaluate_cefepime_rule(
        order=_order(),
        renal_function=renal,
        regimen_id=regimen_id,
        formulation_id="powder_for_solution",
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=False,
        requested_content_version="1.0.0",
        content=content or _content(),
        evaluated_at=EVALUATED_AT,
    )


def build_examples() -> dict[str, RuleResult]:
    contraindication_band = RenalDoseBandContent(
        id="synthetic_contraindication_no_recommendation",
        lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
        upper=None,
        outcome="no_recommendation",
        recommendation=None,
        no_recommendation_reason=(
            "Synthetic contraindication fixture; no dose recommendation is permitted."
        ),
        source_ids=("synthetic_source",),
        limitations=(NON_PRODUCTION_NOTICE,),
    )

    return {
        "normal": _evaluate(renal=_renal("90")),
        "impaired": _evaluate(renal=_renal("29.999999999999999999")),
        "exact_boundary": _evaluate(renal=_renal("30")),
        "missing": _evaluate(renal=_renal(None)),
        "unsupported_regimen": _evaluate(
            renal=_renal("45"),
            regimen_id="unsupported_regimen",
        ),
        "unstable_renal_function": _evaluate(
            renal=_renal("45"),
            renal_function_stable=False,
        ),
        "contraindication": _evaluate(
            renal=_renal("10"),
            content=_content(bands=(contraindication_band,)),
        ),
    }


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_golden_example_byte_matches_canonical_regeneration(example_name: str) -> None:
    generated = dumps_json(build_examples()[example_name]).encode("utf-8")
    committed = (GOLDEN_DIR / f"{example_name}.json").read_bytes()

    assert committed == generated


@pytest.mark.parametrize("example_name", EXAMPLE_NAMES)
def test_golden_example_regeneration_is_deterministic(example_name: str) -> None:
    first = dumps_json(build_examples()[example_name])
    second = dumps_json(build_examples()[example_name])

    assert first == second


def test_golden_outcomes_cover_success_boundaries_and_fail_closed_paths() -> None:
    payloads = {
        name: json.loads((GOLDEN_DIR / f"{name}.json").read_text())
        for name in EXAMPLE_NAMES
    }

    assert payloads["normal"]["status"] == ResultStatus.SUCCESS.value
    assert payloads["normal"]["supporting_data"]["renal_band_id"] == (
        "normal_at_or_above_30"
    )
    assert payloads["impaired"]["status"] == ResultStatus.SUCCESS.value
    assert payloads["impaired"]["supporting_data"]["renal_band_id"] == (
        "impaired_below_30"
    )
    assert payloads["impaired"]["supporting_data"]["renal_value"] == (
        "29.999999999999999999"
    )
    assert payloads["exact_boundary"]["status"] == ResultStatus.SUCCESS.value
    assert payloads["exact_boundary"]["supporting_data"]["renal_value"] == "30"
    assert payloads["exact_boundary"]["supporting_data"]["renal_band_id"] == (
        "normal_at_or_above_30"
    )

    assert payloads["missing"]["status"] == ResultStatus.INCOMPLETE.value
    assert payloads["missing"]["supporting_data"]["outcome_category"] == "incomplete"
    assert payloads["missing"]["renal_function_result"]["value"]["value"] is None
    assert payloads["missing"]["recommendations"] == []

    assert payloads["unsupported_regimen"]["status"] == (
        ResultStatus.NOT_APPLICABLE.value
    )
    assert payloads["unsupported_regimen"]["supporting_data"]["outcome_category"] == (
        "unsupported"
    )
    assert payloads["unsupported_regimen"]["warnings"][0]["code"] == (
        "unsupported_cefepime_regimen"
    )
    assert payloads["unsupported_regimen"]["recommendations"] == []

    assert payloads["unstable_renal_function"]["status"] == (
        ResultStatus.NOT_APPLICABLE.value
    )
    assert payloads["unstable_renal_function"]["warnings"][0]["code"] == (
        "unsupported_unstable_renal_function"
    )
    assert payloads["unstable_renal_function"]["recommendations"] == []

    assert payloads["contraindication"]["status"] == ResultStatus.NOT_APPLICABLE.value
    assert payloads["contraindication"]["applied"] is True
    assert payloads["contraindication"]["passed"] is False
    assert payloads["contraindication"]["supporting_data"]["renal_band_id"] == (
        "synthetic_contraindication_no_recommendation"
    )
    assert payloads["contraindication"]["warnings"][0]["code"] == (
        "cefepime_no_recommendation_band"
    )
    assert payloads["contraindication"]["recommendations"] == []


def test_golden_recommendation_doses_preserve_exact_values_and_units() -> None:
    payloads = {
        name: json.loads((GOLDEN_DIR / f"{name}.json").read_text())
        for name in ("normal", "impaired", "exact_boundary")
    }

    normal_dose = payloads["normal"]["recommendations"][0]["dose_recommendation"][
        "recommended_dose"
    ]
    impaired_dose = payloads["impaired"]["recommendations"][0][
        "dose_recommendation"
    ]["recommended_dose"]
    boundary_dose = payloads["exact_boundary"]["recommendations"][0][
        "dose_recommendation"
    ]["recommended_dose"]

    assert normal_dose == {"unit": "g", "value": "2"}
    assert impaired_dose == {"unit": "mg", "value": "500"}
    assert boundary_dose == {"unit": "g", "value": "2"}


def test_golden_examples_are_synthetic_and_disclaim_clinical_use() -> None:
    for example_name in EXAMPLE_NAMES:
        payload = json.loads((GOLDEN_DIR / f"{example_name}.json").read_text())
        serialized = dumps_json(payload).lower()

        assert payload["patient_id"].startswith("synthetic-patient-")
        assert "not for direct clinical use" in serialized
        assert "synthetic" in serialized
