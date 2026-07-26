"""Pure exact-context famotidine renal-dose rule evaluation."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from cds.domain.clinical import MedicationOrder
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.repositories.renal_content import RenalDoseContent, RenalDoseQuantity
from cds.rules.exact_renal_dose import (
    ExactRenalDoseRuleConfig,
    evaluate_exact_renal_dose_rule,
)

FAMOTIDINE_MEDICATION_ID = "famotidine"
FAMOTIDINE_RULE_IMPLEMENTATION_VERSION = "1.1.0"

_CONFIG = ExactRenalDoseRuleConfig(
    medication_id=FAMOTIDINE_MEDICATION_ID,
    medication_display="Famotidine",
    implementation_version=FAMOTIDINE_RULE_IMPLEMENTATION_VERSION,
    warning_code_prefix="famotidine",
    recommendation_title="Famotidine renal-dose recommendation",
    provenance_source_name="famotidine_rule",
    minimum_weight=RenalDoseQuantity(value=Decimal("40"), unit="kg"),
)

__all__ = [
    "FAMOTIDINE_MEDICATION_ID",
    "FAMOTIDINE_RULE_IMPLEMENTATION_VERSION",
    "evaluate_famotidine_rule",
]


def evaluate_famotidine_rule(
    *,
    order: MedicationOrder,
    renal_function: RenalFunctionResult,
    regimen_id: str | None,
    formulation_id: str | None,
    renal_function_stable: bool | None,
    renal_replacement_therapy: bool | None,
    requested_content_version: str | None,
    content: RenalDoseContent,
    evaluated_at: datetime,
) -> RuleResult:
    """Evaluate one exact famotidine regimen against one reviewed content document.

    Inputs are expected to have completed structural and task-sufficiency validation. The shared
    matcher still fails closed for absent or nonexact facts and never loads content, selects a
    version, normalizes identifiers, converts quantities, infers formulation, or extrapolates.
    """

    return evaluate_exact_renal_dose_rule(
        order=order,
        renal_function=renal_function,
        regimen_id=regimen_id,
        formulation_id=formulation_id,
        renal_function_stable=renal_function_stable,
        renal_replacement_therapy=renal_replacement_therapy,
        requested_content_version=requested_content_version,
        content=content,
        evaluated_at=evaluated_at,
        config=_CONFIG,
    )
