"""Pure exact-context cefepime renal-dose rule evaluation."""

from __future__ import annotations

from datetime import datetime

from cds.domain.clinical import MedicationOrder
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.repositories.renal_content import RenalDoseContent
from cds.rules.exact_renal_dose import (
    ExactRenalDoseRuleConfig,
    evaluate_exact_renal_dose_rule,
)

CEFEPIME_MEDICATION_ID = "cefepime"
CEFEPIME_RULE_IMPLEMENTATION_VERSION = "1.1.0"

_CONFIG = ExactRenalDoseRuleConfig(
    medication_id=CEFEPIME_MEDICATION_ID,
    medication_display="Cefepime",
    implementation_version=CEFEPIME_RULE_IMPLEMENTATION_VERSION,
    warning_code_prefix="cefepime",
    recommendation_title="Cefepime renal-dose recommendation",
    provenance_source_name="cefepime_rule",
)

__all__ = [
    "CEFEPIME_MEDICATION_ID",
    "CEFEPIME_RULE_IMPLEMENTATION_VERSION",
    "evaluate_cefepime_rule",
]


def evaluate_cefepime_rule(
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
    """Evaluate one exact cefepime regimen against one reviewed content document.

    Inputs are expected to have completed structural and task-sufficiency validation. The shared
    matcher still fails closed for absent or nonexact facts and never loads content, selects a
    version, normalizes identifiers, converts quantities, infers clinical context, or extrapolates.
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
