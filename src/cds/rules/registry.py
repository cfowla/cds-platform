"""Deterministic exact-identifier registry for renal-dose rule implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

if TYPE_CHECKING:
    from cds.rules.interface import RenalDoseRule

__all__ = ["RenalDoseRuleRegistration", "RenalDoseRuleRegistry"]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseRuleRegistration:
    """Bind one stable medication identifier and rule identifier to one implementation."""

    medication_id: str
    rule_id: str
    rule: RenalDoseRule


class RenalDoseRuleRegistry:
    """Store exact renal-dose rule registrations without normalization or fallback.

    Construction copies the supplied iterable into private storage. A rule identifier is globally
    unique, while one medication may have multiple distinct rules. Eligible registrations are
    returned in rule-identifier order so behavior does not depend on registration order.
    """

    def __init__(
        self,
        registrations: Iterable[RenalDoseRuleRegistration] = (),
    ) -> None:
        rules_by_key: dict[tuple[str, str], RenalDoseRule] = {}
        rules_by_rule_id: dict[str, RenalDoseRule] = {}
        registrations_by_medication: dict[str, list[RenalDoseRuleRegistration]] = {}

        for registration in registrations:
            key = (registration.medication_id, registration.rule_id)
            if key in rules_by_key:
                raise ValueError(f"duplicate renal-dose rule registration {key!r}")
            if registration.rule_id in rules_by_rule_id:
                raise ValueError(
                    f"duplicate renal-dose rule identifier {registration.rule_id!r}"
                )

            rules_by_key[key] = registration.rule
            rules_by_rule_id[registration.rule_id] = registration.rule
            registrations_by_medication.setdefault(registration.medication_id, []).append(
                registration
            )

        self._rules_by_key = rules_by_key
        self._rules_by_rule_id = rules_by_rule_id
        self._registrations_by_medication = {
            medication_id: tuple(sorted(items, key=lambda item: item.rule_id))
            for medication_id, items in registrations_by_medication.items()
        }

    def get(
        self,
        *,
        medication_id: str,
        rule_id: str,
    ) -> RenalDoseRule | None:
        """Return the exact registered implementation or ``None`` without fallback."""

        return self._rules_by_key.get((medication_id, rule_id))

    def get_by_rule_id(self, rule_id: str, /) -> RenalDoseRule | None:
        """Return the implementation for one exact globally unique rule identifier."""

        return self._rules_by_rule_id.get(rule_id)

    def registrations_for_medication(
        self,
        medication_id: str,
        /,
    ) -> tuple[RenalDoseRuleRegistration, ...]:
        """Return exact eligible registrations in deterministic rule-identifier order."""

        return self._registrations_by_medication.get(medication_id, ())
