"""Tests for canonical CDS JSON-compatible serialization."""

from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest

from cds.domain.enums import RenalMethod, ResultStatus
from cds.domain.models import RenalFunctionResult, RuleResult, ValueWithUnit
from cds.utils.serialization import dumps_json, to_jsonable


def test_nested_domain_result_uses_canonical_wire_values() -> None:
    evaluated_at = datetime(
        2026,
        7,
        21,
        17,
        30,
        tzinfo=timezone(timedelta(hours=-4)),
    )
    result = RuleResult(
        rule_id="renal-dose-cefepime",
        status=ResultStatus.SUCCESS_WITH_WARNINGS,
        applied=True,
        passed=False,
        evaluated_at=evaluated_at,
        renal_function_result=RenalFunctionResult(
            method=RenalMethod.COCKCROFT_GAULT,
            evaluation_date=date(2026, 7, 21),
            value=ValueWithUnit(value=Decimal("31.20"), unit="mL/min"),
        ),
    )

    serialized = to_jsonable(result)

    assert serialized["status"] == "success_with_warnings"
    assert serialized["applied"] is True
    assert serialized["passed"] is False
    assert serialized["evaluated_at"] == "2026-07-21T21:30:00Z"
    assert serialized["renal_function_result"]["method"] == "cockcroft_gault"
    assert serialized["renal_function_result"]["evaluation_date"] == "2026-07-21"
    assert serialized["renal_function_result"]["value"] == {
        "value": "31.20",
        "unit": "mL/min",
    }


def test_decimal_serialization_preserves_precision_and_scale() -> None:
    assert to_jsonable(Decimal("1.20")) == "1.20"
    assert to_jsonable(Decimal("0")) == "0"
    assert to_jsonable(Decimal("0.000001")) == "0.000001"


def test_datetime_is_normalized_to_utc() -> None:
    source_time = datetime(
        2026,
        7,
        21,
        8,
        15,
        tzinfo=timezone(timedelta(hours=-4)),
    )

    assert to_jsonable(source_time) == "2026-07-21T12:15:00Z"
    assert to_jsonable(datetime(2026, 7, 21, 12, 15, tzinfo=UTC)) == (
        "2026-07-21T12:15:00Z"
    )


def test_naive_datetime_fails_instead_of_assuming_a_timezone() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        to_jsonable(datetime(2026, 7, 21, 12, 15))


def test_collections_preserve_missing_and_false_values() -> None:
    serialized = to_jsonable(
        {
            "values": (None, False, 0, "unknown"),
            "nested": [ResultStatus.INCOMPLETE],
        }
    )

    assert serialized == {
        "values": [None, False, 0, "unknown"],
        "nested": ["incomplete"],
    }


def test_non_string_mapping_keys_fail_explicitly() -> None:
    with pytest.raises(TypeError, match="keys must be strings"):
        to_jsonable({1: "unsupported"})


def test_unsupported_values_fail_explicitly() -> None:
    with pytest.raises(TypeError, match="Unsupported JSON serialization type: set"):
        to_jsonable({"unsupported"})


def test_dumps_json_is_compact_and_deterministic() -> None:
    value = {"b": "text", "a": Decimal("1.20")}

    assert dumps_json(value) == '{"a":"1.20","b":"text"}'
    assert dumps_json(value) == dumps_json({"a": Decimal("1.20"), "b": "text"})


def test_serialization_behavior_remains_outside_domain_models() -> None:
    assert not hasattr(RuleResult, "to_json")
    assert not hasattr(RuleResult, "to_jsonable")
