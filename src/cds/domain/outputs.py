"""Passive renal, recommendation, alert, and rule-result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Literal, TypeAlias

from cds.domain.enums import RenalMethod, ResultStatus, Severity, Sex, WeightType
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote, WarningSeverity
from cds.domain.value_objects import CodeableConcept, ValueWithUnit

RecommendationAction: TypeAlias = Literal[
    "continue",
    "adjust_dose",
    "hold",
    "stop",
    "avoid",
    "monitor",
    "switch",
    "clarify",
    "none",
    "unknown",
]
RecommendationStrength: TypeAlias = Literal[
    "info",
    "suggest",
    "recommend",
    "strongly_recommend",
    "unknown",
]
AlertCategory: TypeAlias = Literal[
    "dosing",
    "contraindication",
    "interaction",
    "monitoring",
    "allergy",
    "duplication",
    "general",
    "unknown",
]
SupportingValue: TypeAlias = str | int | float | bool | None

__all__ = [
    "Alert",
    "AlertCategory",
    "CDSRecommendation",
    "Contraindication",
    "DoseRecommendation",
    "RecommendationAction",
    "RecommendationStrength",
    "RenalFunctionResult",
    "RuleResult",
    "SupportingValue",
]


@dataclass(slots=True, kw_only=True)
class RenalFunctionResult:
    """Carry a renal-function result and the exact input context used to produce it.

    The calculated or measured result, serum creatinine, selected weight, and measured period
    all retain explicit units through ``ValueWithUnit``. ``normalized_to_bsa=None`` means the
    normalization state was not supplied; it is not silently treated as ``False``. This model
    records results only—equations, weight selection, unit conversion, and sufficiency checks
    remain in services and validation.
    """

    result_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    method: RenalMethod = RenalMethod.UNKNOWN
    value: ValueWithUnit = field(default_factory=ValueWithUnit)
    normalized_to_bsa: bool | None = None
    evaluation_date: date | None = None
    serum_creatinine_result_id: str | None = None
    serum_creatinine: ValueWithUnit = field(default_factory=ValueWithUnit)
    serum_creatinine_collected_at: datetime | None = None
    age_years: int | None = None
    sex: Sex = Sex.UNKNOWN
    weight_used: ValueWithUnit = field(default_factory=ValueWithUnit)
    weight_type_used: WeightType = WeightType.UNKNOWN
    measured_period: ValueWithUnit = field(default_factory=ValueWithUnit)
    calculated_at: datetime | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Contraindication:
    """Carry a structured contraindication finding without deciding whether it applies.

    ``applies=None`` represents an unevaluated or indeterminate state and remains distinct
    from an explicit negative finding. Related clinical concepts are optional source links;
    matching, severity assignment, and clinical evaluation belong outside the model.
    """

    code: str | None = None
    summary: str | None = None
    applies: bool | None = None
    rationale: str | None = None
    severity: Severity = Severity.UNKNOWN
    related_problem: CodeableConcept | None = None
    related_medication: CodeableConcept | None = None
    related_lab: CodeableConcept | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class DoseRecommendation:
    """Carry a proposed regimen without calculating or validating the dose.

    Dose, interval, infusion duration, and maximum values retain explicit units through
    ``ValueWithUnit``. Missing quantities use ``None`` and do not imply zero. Dose selection,
    renal-rule matching, unit conversion, and regimen validation belong outside this model.
    """

    medication: CodeableConcept = field(default_factory=CodeableConcept)
    recommended_dose: ValueWithUnit = field(default_factory=ValueWithUnit)
    recommended_route: CodeableConcept = field(default_factory=CodeableConcept)
    frequency_interval: ValueWithUnit = field(default_factory=ValueWithUnit)
    infusion_duration: ValueWithUnit = field(default_factory=ValueWithUnit)
    max_single_dose: ValueWithUnit = field(default_factory=ValueWithUnit)
    max_daily_dose: ValueWithUnit = field(default_factory=ValueWithUnit)
    regimen_variant: str | None = None
    rationale: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class CDSRecommendation:
    """Carry a clinician-facing recommendation without selecting or enforcing an action.

    ``action`` and ``strength`` use explicit unknown defaults instead of deriving meaning from
    missing text. Renal and dosing outputs may be linked when available, while an incomplete
    recommendation remains representable. Rule evaluation, recommendation selection, and
    clinical-policy enforcement belong outside this passive model.
    """

    recommendation_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    title: str | None = None
    action: RecommendationAction = "unknown"
    strength: RecommendationStrength = "unknown"
    summary: str | None = None
    rationale: str | None = None
    renal_function_result: RenalFunctionResult | None = None
    dose_recommendation: DoseRecommendation | None = None
    contraindications: list[Contraindication] = field(default_factory=list)
    suggested_monitoring: list[str] = field(default_factory=list)
    linked_order_id: str | None = None
    linked_rule_id: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Alert:
    """Carry a presentable alert without deciding display or interruption policy.

    ``interruptive=None`` means presentation policy has not been assigned and remains distinct
    from an explicit non-interruptive alert. Category and severity use explicit unknown values;
    deduplication, suppression, routing, and user-interface behavior belong outside the model.
    """

    alert_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    category: AlertCategory = "unknown"
    severity: WarningSeverity = "unknown"
    title: str | None = None
    message: str | None = None
    interruptive: bool | None = None
    recommendation: CDSRecommendation | None = None
    linked_order_id: str | None = None
    linked_rule_id: str | None = None
    deduplication_key: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class RuleResult:
    """Carry the structured output of one rule evaluation without evaluating the rule.

    The safe default is ``ResultStatus.INCOMPLETE`` with ``applied`` and ``passed`` unset, so
    missing evaluation state is not collapsed into a negative result. Linked renal output,
    recommendations, alerts, and primitive supporting data preserve an audit trail. Rule
    execution, branching, orchestration, and alert policy remain outside this model.
    """

    rule_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    status: ResultStatus = ResultStatus.INCOMPLETE
    applied: bool | None = None
    passed: bool | None = None
    summary: str | None = None
    renal_function_result: RenalFunctionResult | None = None
    recommendations: list[CDSRecommendation] = field(default_factory=list)
    alerts: list[Alert] = field(default_factory=list)
    supporting_data: dict[str, SupportingValue] = field(default_factory=dict)
    evaluated_at: datetime | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)
