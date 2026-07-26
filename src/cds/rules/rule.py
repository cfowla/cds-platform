"""Feature-neutral rule contracts and outcomes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Protocol, runtime_checkable

from cds.domain.outputs import Alert, CDSRecommendation
from cds.domain.support import EvidenceItem, WarningNote

__all__ = ["EvaluationContext", "Rule", "RuleOutcome"]


@dataclass(frozen=True, slots=True, kw_only=True)
class EvaluationContext:
    """Carry validated feature facts into pure rule evaluation.

    Values must already be typed and validated by the application layer. The generic contract does
    not normalize identifiers, load content, calculate clinical values, or perform I/O.
    """

    feature_id: str
    values: Mapping[str, Any]


@dataclass(frozen=True, slots=True, kw_only=True)
class RuleOutcome:
    """Carry one deterministic rule outcome without applying presentation or orchestration policy."""

    matched: bool
    recommendations: tuple[CDSRecommendation, ...] = ()
    alerts: tuple[Alert, ...] = ()
    evidence: tuple[EvidenceItem, ...] = ()
    warnings: tuple[WarningNote, ...] = ()


@runtime_checkable
class Rule(Protocol):
    """Evaluate one validated context without I/O, loading, normalization, or hidden state."""

    rule_id: str
    feature_id: str
    priority: int

    def evaluate(self, context: EvaluationContext, /) -> RuleOutcome:
        """Return one structured outcome for the supplied validated context."""
        ...
