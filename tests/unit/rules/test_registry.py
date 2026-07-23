"""Focused tests for the deterministic renal-dose rule registry."""

import pytest

from cds.rules.registry import RenalDoseRuleRegistration, RenalDoseRuleRegistry


class _SyntheticRule:
    def __init__(self, name: str) -> None:
        self.name = name

    def evaluate(self, context: object, content: object, /) -> object:
        return (context, content)


def _registration(
    *,
    medication_id: str,
    rule_id: str,
    rule: _SyntheticRule | None = None,
) -> RenalDoseRuleRegistration:
    return RenalDoseRuleRegistration(
        medication_id=medication_id,
        rule_id=rule_id,
        rule=rule or _SyntheticRule(rule_id),
    )


def test_registry_resolves_only_the_exact_medication_and_rule_identifiers() -> None:
    rule = _SyntheticRule("cefepime")
    registry = RenalDoseRuleRegistry(
        [_registration(medication_id="cefepime", rule_id="cefepime_renal_v1", rule=rule)]
    )

    assert registry.get(medication_id="cefepime", rule_id="cefepime_renal_v1") is rule
    assert registry.get_by_rule_id("cefepime_renal_v1") is rule
    assert registry.get(medication_id="CEFEPIME", rule_id="cefepime_renal_v1") is None
    assert registry.get(medication_id="cefepime ", rule_id="cefepime_renal_v1") is None
    assert registry.get(medication_id="cefepime", rule_id="CEFEPIME_RENAL_V1") is None
    assert registry.get_by_rule_id("cefepime_renal_v1 ") is None


def test_medication_registrations_are_sorted_by_rule_id_not_input_order() -> None:
    later = _registration(medication_id="cefepime", rule_id="rule-z")
    earlier = _registration(medication_id="cefepime", rule_id="rule-a")
    other = _registration(medication_id="famotidine", rule_id="rule-m")

    registry = RenalDoseRuleRegistry([later, other, earlier])

    assert registry.registrations_for_medication("cefepime") == (earlier, later)
    assert registry.registrations_for_medication("famotidine") == (other,)
    assert registry.registrations_for_medication("unknown") == ()


def test_registry_allows_distinct_rule_ids_for_one_medication() -> None:
    first = _registration(medication_id="cefepime", rule_id="rule-a")
    second = _registration(medication_id="cefepime", rule_id="rule-b")

    registry = RenalDoseRuleRegistry([first, second])

    assert registry.get(medication_id="cefepime", rule_id="rule-a") is first.rule
    assert registry.get(medication_id="cefepime", rule_id="rule-b") is second.rule


def test_registry_rejects_duplicate_exact_registration() -> None:
    first = _registration(medication_id="cefepime", rule_id="rule-a")
    duplicate = _registration(medication_id="cefepime", rule_id="rule-a")

    with pytest.raises(ValueError, match="duplicate renal-dose rule registration"):
        RenalDoseRuleRegistry([first, duplicate])


def test_registry_rejects_reused_rule_id_for_another_medication() -> None:
    first = _registration(medication_id="cefepime", rule_id="shared-rule")
    duplicate_rule_id = _registration(
        medication_id="famotidine",
        rule_id="shared-rule",
    )

    with pytest.raises(ValueError, match="duplicate renal-dose rule identifier"):
        RenalDoseRuleRegistry([first, duplicate_rule_id])
