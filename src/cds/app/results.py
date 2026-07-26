"""Canonical application-owned evaluation result contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from cds.domain.calculations import CalculationResult
from cds.domain.enums import ResultStatus
from cds.domain.failures import FailureDetail
from cds.domain.outputs import Alert, CDSRecommendation
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.validation.models import ValidationResult

__all__ = ["EvaluationResult"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationResult:
    """Carry one feature-neutral application evaluation outcome.

    The safe default collections are empty. Non-success states therefore cannot accidentally contain
    recommendations unless the orchestrating use case explicitly supplies them. Internal exception
    messages and traceback data are outside this contract and must not be attached to ``failure``.
    """

    evaluation_id: str
    feature_id: str
    status: ResultStatus
    validation: ValidationResult
    recommendations: tuple[CDSRecommendation, ...] = ()
    alerts: tuple[Alert, ...] = ()
    calculations: tuple[CalculationResult, ...] = ()
    assumptions: tuple[Assumption, ...] = ()
    warnings: tuple[WarningNote, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
    evaluated_at: datetime
    failure: FailureDetail | None = None
    evaluated_rule_ids: tuple[str, ...] = ()
