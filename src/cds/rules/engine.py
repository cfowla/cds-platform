"""Deterministic orchestration for exact renal-dose rule evaluation."""

from __future__ import annotations

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.enums import ResultStatus
from cds.domain.outputs import RuleResult
from cds.repositories.renal_content import RenalDoseContent
from cds.rules.registry import RenalDoseRuleRegistry

__all__ = ["RenalDoseRuleEngine"]

_OUTCOME_CATEGORY_KEY = "outcome_category"
_OUTCOME_UNMATCHED = "unmatched"
_OUTCOME_UNSUPPORTED = "unsupported"


class RenalDoseRuleEngine:
    """Evaluate the exact registered rule for validated context and supplied typed content.

    The application layer remains responsible for validation, content loading, and renal
    calculation before calling the engine. Selection is exact and case-sensitive: the medication
    identifier comes from the validated order, and the content document's rule identifier must
    match one registration eligible for that medication. The engine performs no normalization,
    fallback, content selection, calculation, logging, or I/O.
    """

    def __init__(self, registry: RenalDoseRuleRegistry) -> None:
        self._registry = registry

    def evaluate(
        self,
        context: RenalDoseEvaluationContext,
        content: RenalDoseContent,
        /,
    ) -> RuleResult:
        """Return one exact rule result or an explicit fail-closed non-match outcome."""

        medication_id = context.medication_order.medication.code
        registrations = (
            self._registry.registrations_for_medication(medication_id)
            if medication_id is not None
            else ()
        )

        if not registrations:
            return _nonmatch_result(
                context=context,
                content=content,
                medication_id=medication_id,
                outcome_category=_OUTCOME_UNSUPPORTED,
                summary="No registered renal-dose rule supports the exact medication identifier.",
                eligible_rule_count=0,
            )

        for registration in registrations:
            if registration.rule_id == content.rule_id:
                return registration.rule.evaluate(context, content)

        return _nonmatch_result(
            context=context,
            content=content,
            medication_id=medication_id,
            outcome_category=_OUTCOME_UNMATCHED,
            summary=(
                "No eligible renal-dose rule registration matches the supplied content rule "
                "identifier."
            ),
            eligible_rule_count=len(registrations),
        )


def _nonmatch_result(
    *,
    context: RenalDoseEvaluationContext,
    content: RenalDoseContent,
    medication_id: str | None,
    outcome_category: str,
    summary: str,
    eligible_rule_count: int,
) -> RuleResult:
    order = context.medication_order
    return RuleResult(
        rule_id=content.rule_id,
        patient_id=order.patient_id or context.patient.patient_id,
        encounter_id=order.encounter_id,
        status=ResultStatus.NOT_APPLICABLE,
        applied=False,
        passed=None,
        summary=summary,
        evaluated_at=context.evaluated_at,
        supporting_data={
            _OUTCOME_CATEGORY_KEY: outcome_category,
            "medication_id": medication_id,
            "regimen_id": context.regimen_id,
            "requested_content_version": context.requested_content_version,
            "content_version": content.content_version,
            "content_rule_id": content.rule_id,
            "eligible_rule_count": eligible_rule_count,
        },
    )
