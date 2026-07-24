"""Map one renal-dose use-case result to the canonical JSON response shape."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, cast

from cds.utils.serialization import JsonValue, dumps_json, to_jsonable

if TYPE_CHECKING:
    from cds.app.renal_dose import RenalDoseUseCaseResult

__all__ = ["dumps_renal_dose_response", "map_renal_dose_response"]


class _RenalDoseUseCaseResultLike(Protocol):
    validation: object
    rule_result: object


def map_renal_dose_response(
    result: RenalDoseUseCaseResult,
) -> dict[str, JsonValue]:
    """Return a stable JSON-compatible response for one renal-dose evaluation.

    The mapper fixes the external top-level keys as ``validation`` and ``rule_result`` while the
    canonical serializer handles nested dataclasses, enums, dates, timezone-aware datetimes,
    ``Decimal`` values, warnings, evidence, provenance, rule identifiers, and content versions.
    It performs no clinical validation, calculation, content access, rule matching, recommendation
    selection, normalization, or rounding.
    """

    if not hasattr(result, "validation") or not hasattr(result, "rule_result"):
        raise TypeError("result must be a RenalDoseUseCaseResult")

    typed_result = cast(_RenalDoseUseCaseResultLike, result)
    validation = to_jsonable(typed_result.validation)
    rule_result = to_jsonable(typed_result.rule_result)
    if not isinstance(validation, dict) or not isinstance(rule_result, dict):
        raise TypeError("Renal-dose validation and rule result must serialize as JSON objects")

    return {
        "validation": validation,
        "rule_result": rule_result,
    }


def dumps_renal_dose_response(result: RenalDoseUseCaseResult) -> str:
    """Return deterministic compact JSON text for one mapped renal-dose response."""

    return dumps_json(map_renal_dose_response(result))
