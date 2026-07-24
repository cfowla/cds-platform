"""Day 75 property and safety-invariant coverage for renal-dose evaluation.

Prototype only. Synthetic data and test-only reviewed copies of draft content do not
constitute clinical review or authorize patient-care use.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from typing import Callable

import pytest

from cds.app.renal_dose import RenalDoseUseCase
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.outputs import RuleResult
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.repositories.renal_content import (
    InMemoryRenalDoseContentRepository,
    RenalDoseContent,
    RenalDoseContentKey,
)
from cds.repositories.yaml_renal_content import YamlRenalDoseContentRepository
from cds.rules.cefepime import evaluate_cefepime_rule
from cds.rules.engine import RenalDoseRuleEngine
from cds.rules.famotidine import evaluate_famotidine_rule
from cds.rules.piperacillin_tazobactam import evaluate_piperacillin_tazobactam_rule
from cds.rules.predicates import renal_band_matches
from cds.rules.registry import RenalDoseRuleRegistration, RenalDoseRuleRegistry

AT = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)
COLLECTED = AT - timedelta(hours=2)
MED_SYSTEM = "cds-medication-id"
ROUTE_SYSTEM = "cds-route-id"
INDICATION_SYSTEM = "cds-indication-id"
DELTA = Decimal("0.0001")
CONTENT_DIR = Path(__file__).parents[2] / "src/cds/content/renal"


@dataclass(frozen=True, slots=True)
class ContentCase:
    key: str
    medication: str
    regimen: str
    filename: str
    full_flow: bool = True


CONTENT_CASES = (
    ContentCase(
        "CEF-500-Q12",
        "cefepime",
        "iv_500_mg_every_12_hours_over_30_minutes",
        "cefepime_iv_500_mg_every_12_hours_over_30_minutes.yaml",
        full_flow=False,
    ),
    ContentCase(
        "CEF-1G-Q12",
        "cefepime",
        "iv_1_g_every_12_hours_over_30_minutes",
        "cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml",
        full_flow=False,
    ),
    ContentCase(
        "CEF-2G-Q12",
        "cefepime",
        "iv_2_g_every_12_hours_over_30_minutes",
        "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml",
    ),
    ContentCase(
        "CEF-2G-Q8",
        "cefepime",
        "iv_2_g_every_8_hours_over_30_minutes",
        "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml",
    ),
    ContentCase(
        "PTZ-STD-3375",
        "piperacillin_tazobactam",
        "standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes",
        "piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes.yaml",
    ),
    ContentCase(
        "PTZ-STD-4500",
        "piperacillin_tazobactam",
        "standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes",
        "piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes.yaml",
    ),
    ContentCase(
        "PTZ-EI-3375",
        "piperacillin_tazobactam",
        "extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes",
        "piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes.yaml",
    ),
    ContentCase(
        "FAM-PO-20",
        "famotidine",
        "oral_film_coated_tablet_20_mg_every_12_hours",
        "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml",
    ),
)
FULL_FLOW_CASES = tuple(case for case in CONTENT_CASES if case.full_flow)
BY_KEY = {case.key: case for case in CONTENT_CASES}


def _draft(case: ContentCase) -> RenalDoseContent:
    key = RenalDoseContentKey(
        medication_id=case.medication,
        regimen_id=case.regimen,
        content_version="1.0.0-draft",
    )
    return YamlRenalDoseContentRepository([CONTENT_DIR / case.filename]).get(key)


def _reviewed(case: ContentCase) -> RenalDoseContent:
    draft = _draft(case)
    version = f"{draft.content_version}-day-75-test-reviewed"
    return replace(
        draft,
        content_version=version,
        review=replace(
            draft.review,
            status="reviewed",
            reviewed_content_version=version,
            reviewer="Synthetic Day 75 software-fixture reviewer",
            reviewer_role="Software invariant-test fixture reviewer",
            reviewed_on=AT.date(),
            notes="Test-only software eligibility override; not clinical review.",
        ),
    )


def _probe_values(content: RenalDoseContent) -> tuple[Decimal, ...]:
    endpoints = {
        endpoint.value
        for band in content.renal_bands
        for endpoint in (band.lower, band.upper)
        if endpoint is not None
    }
    for endpoint in (content.renal_domain.lower, content.renal_domain.upper):
        if endpoint is not None:
            endpoints.add(endpoint.value)

    ordered = sorted(endpoints)
    probes: set[Decimal] = set()
    for value in ordered:
        probes.update((value - DELTA, value, value + DELTA))
    for lower, upper in zip(ordered, ordered[1:], strict=False):
        probes.add((lower + upper) / Decimal("2"))
    if ordered:
        probes.add(ordered[-1] + Decimal("1"))

    return tuple(
        value
        for value in sorted(probes)
        if renal_band_matches(
            value,
            lower=content.renal_domain.lower,
            upper=content.renal_domain.upper,
        )
    )


def _matching_band_ids(content: RenalDoseContent, value: Decimal) -> tuple[str, ...]:
    return tuple(
        band.id
        for band in content.renal_bands
        if renal_band_matches(value, lower=band.lower, upper=band.upper)
    )


def _representative_value(content: RenalDoseContent, band_id: str) -> Decimal:
    band = next(candidate for candidate in content.renal_bands if candidate.id == band_id)
    if band.lower is not None and band.upper is not None:
        value = (band.lower.value + band.upper.value) / Decimal("2")
    elif band.upper is not None:
        value = band.upper.value - DELTA
    elif band.lower is not None:
        value = band.lower.value + DELTA
    else:
        value = Decimal("1")
    assert renal_band_matches(value, lower=band.lower, upper=band.upper)
    return value


class ProductionRule:
    def __init__(self, evaluator: Callable[..., RuleResult]) -> None:
        self.evaluator = evaluator

    def evaluate(self, context, renal, content, /) -> RuleResult:
        return self.evaluator(
            order=context.medication_order,
            renal_function=renal,
            regimen_id=context.regimen_id,
            formulation_id=context.formulation_id,
            renal_function_stable=context.renal_function_stable,
            renal_replacement_therapy=context.renal_replacement_therapy,
            requested_content_version=context.requested_content_version,
            content=content,
            evaluated_at=context.evaluated_at,
        )


def _use_case(content: RenalDoseContent) -> RenalDoseUseCase:
    evaluators = {
        "cefepime": evaluate_cefepime_rule,
        "piperacillin_tazobactam": evaluate_piperacillin_tazobactam_rule,
        "famotidine": evaluate_famotidine_rule,
    }
    registration = RenalDoseRuleRegistration(
        medication_id=content.medication.id,
        rule_id=content.rule_id,
        rule=ProductionRule(evaluators[content.medication.id]),
    )
    engine = RenalDoseRuleEngine(RenalDoseRuleRegistry((registration,)))
    repository = InMemoryRenalDoseContentRepository((content,))
    return RenalDoseUseCase(
        content_repository=repository,
        rule_engine=engine,
        medication_identifier_system=MED_SYSTEM,
    )


def _patient(target: Decimal = Decimal("50")) -> Patient:
    # Age 80 and SCr 4 make Cockcroft-Gault equal weight / 4.8 exactly.
    return Patient(
        patient_id="synthetic-day-75-patient",
        birth_date=date(1946, 7, 24),
        sex=Sex.MALE,
        actual_body_weight=ValueWithUnit(value=target * Decimal("4.8"), unit="kg"),
    )


def _lab() -> LabResult:
    return LabResult(
        result_id="synthetic-day-75-lab",
        patient_id="synthetic-day-75-patient",
        encounter_id="synthetic-day-75-encounter",
        test=CodeableConcept(system="LOINC", code="2160-0"),
        value=ValueWithUnit(value=Decimal("4"), unit="mg/dL"),
        collected_at=COLLECTED,
        resulted_at=COLLECTED,
        status="final",
    )


def _order(content: RenalDoseContent) -> MedicationOrder:
    regimen = content.regimen
    infusion = regimen.infusion_duration
    return MedicationOrder(
        order_id="synthetic-day-75-order",
        patient_id="synthetic-day-75-patient",
        encounter_id="synthetic-day-75-encounter",
        medication=CodeableConcept(system=MED_SYSTEM, code=content.medication.id),
        dose=ValueWithUnit(value=regimen.base_dose.value, unit=regimen.base_dose.unit),
        route=CodeableConcept(system=ROUTE_SYSTEM, code=regimen.route_id),
        frequency_interval=ValueWithUnit(
            value=regimen.frequency_interval.value,
            unit=regimen.frequency_interval.unit,
        ),
        indication=CodeableConcept(
            system=INDICATION_SYSTEM,
            code=regimen.indication_ids[0],
        ),
        infusion_duration=(
            ValueWithUnit(value=infusion.value, unit=infusion.unit)
            if infusion
            else ValueWithUnit()
        ),
    )


def _evaluate(
    content: RenalDoseContent,
    *,
    target: Decimal = Decimal("50"),
    patient: Patient | None = None,
    lab: LabResult | None = None,
    order: MedicationOrder | None = None,
):
    return _use_case(content).evaluate(
        patient=patient or _patient(target),
        serum_creatinine_result=lab or _lab(),
        medication_order=order or _order(content),
        weight_type=WeightType.ACTUAL,
        regimen_id=content.regimen.id,
        formulation_id=content.regimen.formulation_id,
        renal_function_stable=True,
        renal_replacement_therapy=False,
        pregnant_or_lactating=False,
        requested_content_version=content.content_version,
        evaluation_date=AT.date(),
        evaluated_at=AT,
    )


@pytest.mark.parametrize("case", [pytest.param(case, id=case.key) for case in CONTENT_CASES])
def test_each_in_domain_probe_matches_exactly_one_renal_band(case) -> None:
    content = _draft(case)
    probes = _probe_values(content)

    assert probes
    for value in probes:
        matches = _matching_band_ids(content, value)
        assert len(matches) == 1, f"{case.key} value {value} matched {matches}"


@pytest.mark.parametrize("case", [pytest.param(case, id=case.key) for case in CONTENT_CASES])
def test_no_in_domain_probe_matches_overlapping_renal_bands(case) -> None:
    content = _draft(case)

    for value in _probe_values(content):
        matches = _matching_band_ids(content, value)
        assert len(matches) <= 1, f"{case.key} value {value} overlapped {matches}"


@pytest.mark.parametrize("kind", ("birth_date", "weight", "serum_creatinine"))
def test_critical_validation_failure_never_produces_a_recommendation(kind) -> None:
    content = _reviewed(BY_KEY["CEF-2G-Q8"])
    patient = _patient()
    lab = _lab()
    if kind == "birth_date":
        patient = replace(patient, birth_date=None)
    elif kind == "weight":
        patient = replace(patient, actual_body_weight=ValueWithUnit(unit="kg"))
    else:
        lab = replace(lab, value=ValueWithUnit(unit="mg/dL"))

    result = _evaluate(content, patient=patient, lab=lab)

    assert result.validation.is_valid is False
    assert any(issue.severity == "error" for issue in result.validation.issues)
    assert result.rule_result.renal_function_result is None
    assert result.rule_result.status is not ResultStatus.SUCCESS
    assert result.rule_result.recommendations == []


def _assert_content_provenance(value, content: RenalDoseContent) -> None:
    provenance = value.provenance
    assert provenance.source_type == "rule_content"
    assert provenance.source_name == "renal_dose_content"
    assert provenance.source_identifier == content.content_id
    assert provenance.captured_at == AT
    assert provenance.version == content.content_version


@pytest.mark.parametrize("case", [pytest.param(case, id=case.key) for case in FULL_FLOW_CASES])
def test_every_successful_recommendation_has_required_evidence_and_provenance(case) -> None:
    content = _reviewed(case)

    for band in content.renal_bands:
        target = _representative_value(content, band.id)
        result = _evaluate(content, target=target)

        assert result.rule_result.status is ResultStatus.SUCCESS
        assert len(result.rule_result.recommendations) == 1
        recommendation = result.rule_result.recommendations[0]
        dose = recommendation.dose_recommendation
        assert dose is not None

        for traceable in (result.rule_result, recommendation, dose):
            assert traceable.evidence
            _assert_content_provenance(traceable, content)

        for evidence in recommendation.evidence:
            assert evidence.summary
            assert evidence.level != "unknown"
            assert evidence.citation
            assert evidence.source_document
            assert evidence.source_version
            assert evidence.provenance.source_type == "rule_content"
            assert evidence.provenance.source_name == "renal_dose_content_source"
            assert evidence.provenance.source_identifier
            assert evidence.provenance.version == content.content_version
