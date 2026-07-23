"""Focused tests for the minimal renal-dose rule contract."""

from inspect import Parameter, signature
from typing import get_type_hints

from cds.app.context import RenalDoseEvaluationContext
from cds.domain.outputs import RuleResult
from cds.repositories.renal_content import RenalDoseContent
from cds.rules.interface import RenalDoseRule


class _SyntheticRule:
    def evaluate(
        self,
        context: RenalDoseEvaluationContext,
        content: RenalDoseContent,
        /,
    ) -> RuleResult:
        return RuleResult(rule_id="synthetic-rule", patient_id=context.patient.patient_id)


def test_rule_contract_exposes_only_the_minimal_evaluate_method() -> None:
    public_names = {
        name
        for name in vars(RenalDoseRule)
        if not name.startswith("_")
    }

    assert public_names == {"evaluate"}


def test_evaluate_signature_uses_context_content_and_structured_result() -> None:
    evaluate_signature = signature(RenalDoseRule.evaluate)
    parameters = list(evaluate_signature.parameters.values())
    type_hints = get_type_hints(RenalDoseRule.evaluate)

    assert [parameter.name for parameter in parameters] == ["self", "context", "content"]
    assert parameters[1].kind is Parameter.POSITIONAL_ONLY
    assert parameters[2].kind is Parameter.POSITIONAL_ONLY
    assert type_hints["context"] is RenalDoseEvaluationContext
    assert type_hints["content"] is RenalDoseContent
    assert type_hints["return"] is RuleResult


def test_structurally_compatible_rule_satisfies_runtime_contract() -> None:
    assert isinstance(_SyntheticRule(), RenalDoseRule)
