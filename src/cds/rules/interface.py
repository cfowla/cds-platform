"""Minimal typed contract for renal-dose rule evaluation."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.outputs import RuleResult
from cds.repositories.renal_content import RenalDoseContent

__all__ = ["RenalDoseRule"]


@runtime_checkable
class RenalDoseRule(Protocol):
    """Evaluate validated renal-dose facts against one supplied content document.

    Implementations must remain pure and deterministic. The caller is responsible
    for validation and exact content selection before invoking this contract. A rule
    returns a structured ``RuleResult`` and does not load content, calculate renal
    function, normalize identifiers, perform I/O, or mutate the supplied objects.
    """

    def evaluate(
        self,
        context: RenalDoseEvaluationContext,
        content: RenalDoseContent,
        /,
    ) -> RuleResult:
        """Return one structured result for the supplied validated context and content."""
        ...
