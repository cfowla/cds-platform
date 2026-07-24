"""Typed validated facts for one renal-dose rule evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import WeightType
from cds.domain.value_objects import ValueWithUnit

__all__ = ["RenalDoseEvaluationContext"]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseEvaluationContext:
    """Carry validated facts required by renal calculation and exact rule evaluation.

    Callers construct this object only after structural and task-sufficiency
    validation succeeds. The context deliberately performs no validation,
    normalization, inference, content loading, calculation, rule matching, I/O,
    or mutation. Domain objects and exact identifiers are preserved as supplied
    so application orchestration can pass them to the existing pure calculator,
    repository boundary, and rule evaluators.
    """

    patient: Patient
    serum_creatinine_result: LabResult
    supplied_weight: ValueWithUnit
    weight_type: WeightType
    medication_order: MedicationOrder
    regimen_id: str
    formulation_id: str | None
    renal_function_stable: bool
    renal_replacement_therapy: bool
    requested_content_version: str
    evaluation_date: date
    evaluated_at: datetime
