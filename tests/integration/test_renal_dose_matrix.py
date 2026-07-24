"""Day 72 full-flow renal-dose integration matrix.

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

import cds.app.renal_dose as renal_dose_module
from cds.app.renal_dose import RenalDoseUseCase
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.exceptions import CalculationError, ContentNotFound, ValidationError
from cds.domain.outputs import RenalFunctionResult, RuleResult
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
from cds.rules.registry import RenalDoseRuleRegistration, RenalDoseRuleRegistry
from cds.services.renal import calculate_cockcroft_gault
from cds.utils.serialization import to_jsonable

AT = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)
COLLECTED = AT - timedelta(hours=2)
MED_SYSTEM = "cds-medication-id"
DELTA = Decimal("0.0001")
CONTENT_DIR = Path(__file__).parents[2] / "src/cds/content/renal"


@dataclass(frozen=True, slots=True)
class Regimen:
    key: str
    medication: str
    regimen: str
    filename: str
    boundaries: tuple[tuple[str, str, str, str], ...]


REGIMENS = (
    Regimen(
        "CEF-Q8",
        "cefepime",
        "iv_2_g_every_8_hours_over_30_minutes",
        "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml",
        (
            ("11", "below_11", "crcl_11_to_below_30", "crcl_11_to_below_30"),
            ("30", "crcl_11_to_below_30", "crcl_30_to_60", "crcl_30_to_60"),
            ("60", "crcl_30_to_60", "crcl_30_to_60", "above_60"),
        ),
    ),
    Regimen(
        "CEF-Q12",
        "cefepime",
        "iv_2_g_every_12_hours_over_30_minutes",
        "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml",
        (
            ("11", "below_11", "crcl_11_to_below_30", "crcl_11_to_below_30"),
            ("30", "crcl_11_to_below_30", "crcl_30_to_60", "crcl_30_to_60"),
            ("60", "crcl_30_to_60", "crcl_30_to_60", "above_60"),
        ),
    ),
    Regimen(
        "PTZ-STD-3375",
        "piperacillin_tazobactam",
        "standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes",
        "piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes.yaml",
        (
            ("20", "below_20", "crcl_20_to_40", "crcl_20_to_40"),
            ("40", "crcl_20_to_40", "crcl_20_to_40", "above_40"),
        ),
    ),
    Regimen(
        "PTZ-STD-4500",
        "piperacillin_tazobactam",
        "standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes",
        "piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes.yaml",
        (
            ("20", "below_20", "crcl_20_to_40", "crcl_20_to_40"),
            ("40", "crcl_20_to_40", "crcl_20_to_40", "above_40"),
        ),
    ),
    Regimen(
        "PTZ-EI-3375",
        "piperacillin_tazobactam",
        "extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes",
        "piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes.yaml",
        (("20", "at_or_below_20", "at_or_below_20", "above_20"),),
    ),
    Regimen(
        "FAM-PO-20",
        "famotidine",
        "oral_film_coated_tablet_20_mg_every_12_hours",
        "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml",
        (
            ("30", "below_30", "crcl_30_to_below_60", "crcl_30_to_below_60"),
            ("60", "crcl_30_to_below_60", "at_or_above_60", "at_or_above_60"),
        ),
    ),
)
BY_KEY = {case.key: case for case in REGIMENS}


def _boundary_cases():
    params = []
    for case in REGIMENS:
        for raw, below, at, above in case.boundaries:
            threshold = Decimal(raw)
            family = f"BND-{case.key}-{raw}"
            params += [
                pytest.param(case, threshold - DELTA, below, id=f"{family}-below"),
                pytest.param(case, threshold, at, id=f"{family}-at"),
                pytest.param(case, threshold + DELTA, above, id=f"{family}-above"),
            ]
    return params


def _draft(case: Regimen) -> RenalDoseContent:
    key = RenalDoseContentKey(
        medication_id=case.medication,
        regimen_id=case.regimen,
        content_version="1.0.0-draft",
    )
    return YamlRenalDoseContentRepository([CONTENT_DIR / case.filename]).get(key)


def _reviewed(case: Regimen) -> RenalDoseContent:
    draft = _draft(case)
    version = f"{draft.content_version}-day-72-test-reviewed"
    return replace(
        draft,
        content_version=version,
        review=replace(
            draft.review,
            status="reviewed",
            reviewed_content_version=version,
            reviewer="Synthetic Day 72 software-fixture reviewer",
            reviewer_role="Software integration-test fixture reviewer",
            reviewed_on=AT.date(),
            notes="Test-only software eligibility override; not clinical review.",
        ),
    )


class Repository:
    def __init__(self, contents: tuple[RenalDoseContent, ...]) -> None:
        self.inner = InMemoryRenalDoseContentRepository(contents)
        self.keys: list[RenalDoseContentKey] = []
        self.error: Exception | None = None
        self.override: RenalDoseContent | None = None

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        self.keys.append(key)
        if self.error:
            raise self.error
        return self.override or self.inner.get(key)


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


class Engine:
    def __init__(self, inner: RenalDoseRuleEngine) -> None:
        self.inner = inner
        self.calls: list[tuple[object, RenalFunctionResult, RenalDoseContent]] = []
        self.error: Exception | None = None

    def evaluate(self, context, renal, content, /) -> RuleResult:
        self.calls.append((context, renal, content))
        if self.error:
            raise self.error
        return self.inner.evaluate(context, renal, content)


def _runtime():
    contents = {case.key: _reviewed(case) for case in REGIMENS}
    evaluators = {
        "cefepime": evaluate_cefepime_rule,
        "piperacillin_tazobactam": evaluate_piperacillin_tazobactam_rule,
        "famotidine": evaluate_famotidine_rule,
    }
    registrations = (
        RenalDoseRuleRegistration(
            medication_id=content.medication.id,
            rule_id=content.rule_id,
            rule=ProductionRule(evaluators[content.medication.id]),
        )
        for content in contents.values()
    )
    return (
        contents,
        Repository(tuple(contents.values())),
        Engine(RenalDoseRuleEngine(RenalDoseRuleRegistry(registrations))),
    )


def _patient(target: Decimal = Decimal("50")) -> Patient:
    # Age 80 and SCr 4 make Cockcroft-Gault equal weight / 4.8 exactly.
    return Patient(
        patient_id="synthetic-day-72-patient",
        birth_date=date(1946, 7, 24),
        sex=Sex.MALE,
        actual_body_weight=ValueWithUnit(value=target * Decimal("4.8"), unit="kg"),
    )


def _lab() -> LabResult:
    return LabResult(
        result_id="synthetic-day-72-lab",
        patient_id="synthetic-day-72-patient",
        encounter_id="synthetic-day-72-encounter",
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
        order_id="synthetic-day-72-order",
        patient_id="synthetic-day-72-patient",
        encounter_id="synthetic-day-72-encounter",
        medication=CodeableConcept(system=MED_SYSTEM, code=content.medication.id),
        dose=ValueWithUnit(value=regimen.base_dose.value, unit=regimen.base_dose.unit),
        route=CodeableConcept(code=regimen.route_id),
        frequency_interval=ValueWithUnit(
            value=regimen.frequency_interval.value,
            unit=regimen.frequency_interval.unit,
        ),
        indication=CodeableConcept(code=regimen.indication_ids[0]),
        infusion_duration=(
            ValueWithUnit(value=infusion.value, unit=infusion.unit)
            if infusion
            else ValueWithUnit()
        ),
    )


def _run(case: Regimen, target: Decimal = Decimal("50"), **changes):
    contents, default_repo, default_engine = _runtime()
    content = contents[case.key]
    repo = changes.pop("repo", default_repo)
    engine = changes.pop("engine", default_engine)
    args = {
        "patient": changes.pop("patient", _patient(target)),
        "serum_creatinine_result": changes.pop("lab", _lab()),
        "medication_order": changes.pop("order", _order(content)),
        "weight_type": WeightType.ACTUAL,
        "regimen_id": content.regimen.id,
        "formulation_id": content.regimen.formulation_id,
        "renal_function_stable": True,
        "renal_replacement_therapy": False,
        "pregnant_or_lactating": False,
        "requested_content_version": content.content_version,
        "evaluation_date": AT.date(),
        "evaluated_at": AT,
    }
    args.update(changes)
    result = RenalDoseUseCase(
        content_repository=repo,
        rule_engine=engine,
        medication_identifier_system=MED_SYSTEM,
    ).evaluate(**args)
    return result, content, repo, engine


def _no_recommendation(result) -> None:
    assert result.rule_result.recommendations == []
    assert result.rule_result.status is not ResultStatus.SUCCESS


@pytest.mark.parametrize("case,target,band_id", _boundary_cases())
def test_full_flow_boundaries(case, target, band_id, monkeypatch) -> None:
    calculations = []

    def calculate(**kwargs):
        calculations.append(kwargs)
        return calculate_cockcroft_gault(**kwargs)

    monkeypatch.setattr(renal_dose_module, "calculate_cockcroft_gault", calculate)
    result, content, repo, engine = _run(case, target)

    assert result.validation.is_valid is True
    assert repo.keys == [content.key]
    assert len(calculations) == len(engine.calls) == 1
    renal = result.rule_result.renal_function_result
    assert renal and renal.value == ValueWithUnit(value=target, unit="mL/min")
    assert result.rule_result.status is ResultStatus.SUCCESS
    assert result.rule_result.rule_id == content.rule_id
    assert result.rule_result.evaluated_at == AT
    assert result.rule_result.supporting_data["content_version"] == content.content_version
    assert result.rule_result.supporting_data["renal_band_id"] == band_id
    assert result.rule_result.supporting_data["renal_value"] == str(target)
    assert len(result.rule_result.recommendations) == 1
    recommendation = result.rule_result.recommendations[0]
    expected = next(b for b in content.renal_bands if b.id == band_id).recommendation
    dose = recommendation.dose_recommendation
    assert expected and dose
    assert recommendation.action == expected.action
    assert dose.recommended_dose == ValueWithUnit(
        value=expected.dose.value,
        unit=expected.dose.unit,
    )
    assert dose.recommended_route.code == expected.route_id
    assert dose.frequency_interval.value == expected.frequency_interval.value
    assert dose.frequency_interval.unit == expected.frequency_interval.unit
    expected_infusion = expected.infusion_duration
    assert dose.infusion_duration == (
        ValueWithUnit(value=expected_infusion.value, unit=expected_infusion.unit)
        if expected_infusion
        else ValueWithUnit()
    )
    assert recommendation.linked_order_id == "synthetic-day-72-order"
    assert recommendation.linked_rule_id == content.rule_id
    assert recommendation.evidence and recommendation.provenance.source_identifier
    payload = to_jsonable(result.rule_result)
    assert payload["renal_function_result"]["value"]["value"] == str(target)
    assert payload["evaluated_at"] == "2026-07-24T12:00:00Z"


@pytest.mark.parametrize("case", [pytest.param(c, id=c.key) for c in REGIMENS])
def test_all_six_exact_regimens_complete(case) -> None:
    result, content, repo, engine = _run(case)
    assert result.validation.is_valid is True
    assert repo.keys == [content.key]
    assert len(engine.calls) == 1
    assert result.rule_result.status is ResultStatus.SUCCESS
    assert result.rule_result.applied is result.rule_result.passed is True
    assert len(result.rule_result.recommendations) == 1


INITIAL_CASES = (
    pytest.param("patient_id", "missing_patient_identifier", id="DATA-PATIENT-ID"),
    pytest.param("order_patient", "order_patient_mismatch", id="DATA-PATIENT-MISMATCH"),
    pytest.param("lab_patient", "lab_patient_mismatch", id="DATA-LAB-PATIENT-MISMATCH"),
    pytest.param("encounter", "encounter_mismatch", id="DATA-ENCOUNTER-MISMATCH"),
    pytest.param("birth", "missing_age_source", id="DATA-BIRTH-DATE"),
    pytest.param("sex", "unsupported_sex_for_cockcroft_gault", id="DATA-SEX"),
    pytest.param("weight", "missing_weight_value", id="DATA-WEIGHT-VALUE"),
    pytest.param("weight_unit", "unsupported_weight_unit", id="DATA-WEIGHT-UNIT"),
    pytest.param("scr", "missing_serum_creatinine_value", id="DATA-SCR-VALUE"),
    pytest.param("scr_unit", "unsupported_serum_creatinine_unit", id="DATA-SCR-UNIT"),
    pytest.param("status", "unsupported_lab_status", id="DATA-SCR-STATUS"),
    pytest.param("time", "missing_collection_time", id="DATA-SCR-TIME"),
    pytest.param("medication", "missing_medication_code", id="DATA-MEDICATION-CODE"),
)


def _initial_mutation(kind, patient, lab, order):
    if kind == "patient_id":
        patient = replace(patient, patient_id=None)
    elif kind == "order_patient":
        order = replace(order, patient_id="other")
    elif kind == "lab_patient":
        lab = replace(lab, patient_id="other")
    elif kind == "encounter":
        order = replace(order, encounter_id="other")
    elif kind == "birth":
        patient = replace(patient, birth_date=None)
    elif kind == "sex":
        patient = replace(patient, sex=Sex.UNKNOWN)
    elif kind == "weight":
        patient = replace(patient, actual_body_weight=ValueWithUnit(unit="kg"))
    elif kind == "weight_unit":
        patient = replace(
            patient,
            actual_body_weight=replace(patient.actual_body_weight, unit="lb"),
        )
    elif kind == "scr":
        lab = replace(lab, value=ValueWithUnit(unit="mg/dL"))
    elif kind == "scr_unit":
        lab = replace(lab, value=replace(lab.value, unit="umol/L"))
    elif kind == "status":
        lab = replace(lab, status="preliminary")
    elif kind == "time":
        lab = replace(lab, collected_at=None)
    else:
        order = replace(order, medication=replace(order.medication, code=None))
    return patient, lab, order


@pytest.mark.parametrize("kind,code", INITIAL_CASES)
def test_initial_validation_stops_before_repository(kind, code, monkeypatch) -> None:
    case = BY_KEY["CEF-Q8"]
    contents, repo, engine = _runtime()
    patient, lab, order = _initial_mutation(
        kind,
        _patient(),
        _lab(),
        _order(contents[case.key]),
    )
    calculations = []
    monkeypatch.setattr(
        renal_dose_module,
        "calculate_cockcroft_gault",
        lambda **kwargs: calculations.append(kwargs),
    )
    result, _, _, _ = _run(
        case,
        patient=patient,
        lab=lab,
        order=order,
        repo=repo,
        engine=engine,
    )
    assert result.validation.is_valid is False
    assert code in {issue.code for issue in result.validation.issues}
    _no_recommendation(result)
    assert repo.keys == calculations == engine.calls == []


@pytest.mark.parametrize(
    "field,value,code",
    (
        pytest.param(
            "renal_function_stable",
            None,
            "missing_renal_stability_status",
            id="DATA-RENAL-STABILITY",
        ),
        pytest.param(
            "renal_replacement_therapy",
            None,
            "missing_renal_replacement_therapy_status",
            id="DATA-RRT",
        ),
        pytest.param(
            "pregnant_or_lactating",
            None,
            "missing_pregnancy_or_lactation_status",
            id="DATA-PREGNANCY",
        ),
        pytest.param("regimen_id", None, "missing_regimen_identifier", id="DATA-REGIMEN-ID"),
        pytest.param(
            "requested_content_version",
            None,
            "missing_content_version",
            id="DATA-CONTENT-VERSION",
        ),
    ),
)
def test_other_initial_stop_cases(field, value, code) -> None:
    result, _, repo, engine = _run(BY_KEY["CEF-Q8"], **{field: value})
    assert result.validation.is_valid is False
    assert code in {issue.code for issue in result.validation.issues}
    _no_recommendation(result)
    assert repo.keys == engine.calls == []


@pytest.mark.xfail(
    strict=True,
    reason="Known gap: supplied actual weight can be declared as another weight type.",
)
def test_declared_weight_type_conflict_fails_closed() -> None:
    result, _, _, _ = _run(BY_KEY["CEF-Q8"], weight_type=WeightType.IDEAL)
    _no_recommendation(result)


@pytest.mark.parametrize(
    "field",
    (
        pytest.param("dose", id="DATA-DOSE"),
        pytest.param("route", id="DATA-ROUTE"),
        pytest.param("frequency", id="DATA-FREQUENCY"),
        pytest.param("indication", id="DATA-INDICATION"),
        pytest.param("formulation", id="DATA-FORMULATION"),
        pytest.param("infusion", id="DATA-INFUSION"),
    ),
)
def test_content_specific_missing_facts_stop_after_lookup(field) -> None:
    case = BY_KEY["CEF-Q8"]
    contents, repo, engine = _runtime()
    content = contents[case.key]
    order = _order(content)
    changes = {}
    if field in {"dose", "frequency", "infusion"}:
        name = "frequency_interval" if field == "frequency" else f"{field}_duration"
        if field == "dose":
            name = "dose"
        order = replace(order, **{name: ValueWithUnit(unit=getattr(order, name).unit)})
    elif field in {"route", "indication"}:
        order = replace(order, **{field: CodeableConcept()})
    else:
        changes["formulation_id"] = None
    result, _, _, _ = _run(case, order=order, repo=repo, engine=engine, **changes)
    assert result.validation.is_valid is False
    assert repo.keys == [content.key]
    assert result.rule_result.renal_function_result is None
    _no_recommendation(result)
    assert engine.calls == []


UNSUPPORTED = (
    pytest.param("CEF-Q8", "medication", id="UNSUP-MEDICATION"),
    pytest.param("CEF-Q8", "case", id="UNSUP-CASE"),
    pytest.param("CEF-Q8", "regimen", id="UNSUP-REGIMEN"),
    pytest.param("CEF-Q8", "version", id="UNSUP-VERSION"),
    pytest.param("CEF-Q8", "route", id="UNSUP-ROUTE"),
    pytest.param("CEF-Q8", "formulation", id="UNSUP-FORMULATION"),
    pytest.param("CEF-Q8", "dose", id="UNSUP-DOSE"),
    pytest.param("CEF-Q8", "frequency", id="UNSUP-FREQUENCY"),
    pytest.param("CEF-Q8", "infusion", id="UNSUP-INFUSION"),
    pytest.param("CEF-Q8", "indication", id="UNSUP-INDICATION"),
    pytest.param("CEF-Q8", "pediatric", id="UNSUP-PEDIATRIC"),
    pytest.param(
        "FAM-PO-20",
        "fam_weight",
        id="UNSUP-FAM-WEIGHT",
        marks=pytest.mark.xfail(
            strict=True,
            reason="Known gap: famotidine adult-weight floor is not enforced.",
        ),
    ),
    pytest.param("CEF-Q8", "rrt", id="UNSUP-RRT"),
    pytest.param("CEF-Q8", "unstable", id="UNSUP-UNSTABLE"),
)


def _unsupported_mutation(kind, case, content, patient, order):
    changes = {}
    if kind == "medication":
        order = replace(order, medication=replace(order.medication, code="unknown"))
    elif kind == "case":
        order = replace(order, medication=replace(order.medication, code=case.medication.upper()))
    elif kind == "regimen":
        changes["regimen_id"] = f"{case.regimen}_unknown"
    elif kind == "version":
        changes["requested_content_version"] = "missing-version"
    elif kind == "route":
        order = replace(order, route=replace(order.route, code="wrong-route"))
    elif kind == "formulation":
        changes["formulation_id"] = "wrong-formulation"
    elif kind == "dose":
        order = replace(order, dose=replace(order.dose, value=order.dose.value + 1))
    elif kind == "frequency":
        order = replace(
            order,
            frequency_interval=replace(order.frequency_interval, value=Decimal("999")),
        )
    elif kind == "infusion":
        order = replace(
            order,
            infusion_duration=replace(order.infusion_duration, value=Decimal("999")),
        )
    elif kind == "indication":
        order = replace(order, indication=replace(order.indication, code="wrong-indication"))
    elif kind == "pediatric":
        patient = replace(patient, birth_date=date(2016, 7, 24))
    elif kind == "fam_weight":
        patient = replace(
            patient,
            actual_body_weight=ValueWithUnit(value=Decimal("39.999"), unit="kg"),
        )
    elif kind == "rrt":
        changes["renal_replacement_therapy"] = True
    else:
        changes["renal_function_stable"] = False
    return patient, order, changes


@pytest.mark.parametrize("case_key,kind", UNSUPPORTED)
def test_exact_unsupported_contexts_fail_closed(case_key, kind) -> None:
    case = BY_KEY[case_key]
    contents, repo, engine = _runtime()
    content = contents[case.key]
    patient, order, changes = _unsupported_mutation(
        kind,
        case,
        content,
        _patient(),
        _order(content),
    )
    result, _, _, _ = _run(
        case,
        patient=patient,
        order=order,
        repo=repo,
        engine=engine,
        **changes,
    )
    _no_recommendation(result)


FAILURES = (
    pytest.param(
        "validation",
        "validation_boundary_failure",
        "initial_validation",
        id="FAIL-VALIDATION-TYPED",
    ),
    pytest.param("missing", "content_not_found", "content_repository", id="FAIL-CONTENT-MISSING"),
    pytest.param(
        "repository",
        "unexpected_content_repository_failure",
        "content_repository",
        id="FAIL-CONTENT-UNEXPECTED",
    ),
    pytest.param(
        "context",
        "unexpected_application_failure",
        "context_assembly",
        id="FAIL-CONTEXT",
    ),
    pytest.param(
        "calculation",
        "calculation_failure",
        "renal_calculation",
        id="FAIL-CALC-TYPED",
    ),
    pytest.param(
        "calculation_unexpected",
        "unexpected_calculation_failure",
        "renal_calculation",
        id="FAIL-CALC-UNEXPECTED",
    ),
    pytest.param("rule", "unexpected_rule_failure", "rule_evaluation", id="FAIL-RULE"),
)


@pytest.mark.parametrize("failure,code,stage", FAILURES)
def test_failures_are_structured_and_sanitized(failure, code, stage, monkeypatch) -> None:
    case = BY_KEY["CEF-Q8"]
    _, repo, engine = _runtime()
    secret = "synthetic payload must not escape"
    throwing = lambda error: lambda **kwargs: (_ for _ in ()).throw(error)
    if failure == "validation":
        monkeypatch.setattr(
            renal_dose_module,
            "validate_patient_structure",
            lambda *args, **kwargs: (_ for _ in ()).throw(ValidationError(secret)),
        )
    elif failure == "missing":
        repo.error = ContentNotFound(secret)
    elif failure == "repository":
        repo.error = RuntimeError(secret)
    elif failure == "context":
        monkeypatch.setattr(
            renal_dose_module,
            "RenalDoseEvaluationContext",
            throwing(RuntimeError(secret)),
        )
    elif failure == "calculation":
        monkeypatch.setattr(
            renal_dose_module,
            "calculate_cockcroft_gault",
            throwing(CalculationError(secret)),
        )
    elif failure == "calculation_unexpected":
        monkeypatch.setattr(
            renal_dose_module,
            "calculate_cockcroft_gault",
            throwing(RuntimeError(secret)),
        )
    else:
        engine.error = RuntimeError(secret)
    result, _, _, _ = _run(case, repo=repo, engine=engine)
    assert result.rule_result.status is ResultStatus.FAILED
    assert result.rule_result.supporting_data["failure_code"] == code
    assert result.rule_result.supporting_data["failure_stage"] == stage
    _no_recommendation(result)
    assert secret not in repr(result)
    if failure == "rule":
        assert result.rule_result.renal_function_result is not None


def test_draft_content_remains_ineligible() -> None:
    case = BY_KEY["CEF-Q8"]
    _, repo, engine = _runtime()
    repo.override = _draft(case)
    result, _, _, _ = _run(
        case,
        repo=repo,
        engine=engine,
        requested_content_version="1.0.0-draft",
    )
    assert result.rule_result.status is ResultStatus.INCOMPLETE
    _no_recommendation(result)


@pytest.mark.parametrize("mode", ("empty", "mismatched"))
def test_absent_exact_rule_selection_fails_closed(mode) -> None:
    case = BY_KEY["CEF-Q8"]
    contents, repo, _ = _runtime()
    content = contents[case.key]
    registrations = ()
    if mode == "mismatched":
        registrations = (
            RenalDoseRuleRegistration(
                medication_id=content.medication.id,
                rule_id="different-rule-id",
                rule=ProductionRule(evaluate_cefepime_rule),
            ),
        )
    engine = Engine(RenalDoseRuleEngine(RenalDoseRuleRegistry(registrations)))
    result, _, _, _ = _run(case, repo=repo, engine=engine)
    assert result.rule_result.status is ResultStatus.NOT_APPLICABLE
    _no_recommendation(result)
