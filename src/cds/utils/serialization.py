"""Canonical JSON-compatible serialization for CDS boundary objects.

The domain layer remains passive. This module converts supported boundary values as follows:

- dataclasses become dictionaries using declared field names;
- string enums become their stable wire values;
- ``date`` values use ISO 8601 calendar dates;
- timezone-aware ``datetime`` values are normalized to UTC with a ``Z`` suffix;
- ``Decimal`` values become strings so precision and scale are not lost;
- tuples become JSON arrays, while dictionaries require string keys.

Naive datetimes and unsupported values fail explicitly rather than being guessed or coerced.
"""

from __future__ import annotations

import json
from dataclasses import fields, is_dataclass
from datetime import UTC, date, datetime
from decimal import Decimal
from enum import Enum
from typing import TypeAlias

JsonPrimitive: TypeAlias = str | int | float | bool | None
JsonValue: TypeAlias = JsonPrimitive | list["JsonValue"] | dict[str, "JsonValue"]

__all__ = ["JsonValue", "dumps_json", "to_jsonable"]


def to_jsonable(value: object) -> JsonValue:
    """Convert one supported value into a JSON-compatible primitive tree."""
    if isinstance(value, Enum):
        return to_jsonable(value.value)

    if value is None or isinstance(value, (str, int, float, bool)):
        return value

    if isinstance(value, Decimal):
        return str(value)

    if isinstance(value, datetime):
        return _serialize_datetime(value)

    if isinstance(value, date):
        return value.isoformat()

    if is_dataclass(value) and not isinstance(value, type):
        return {
            model_field.name: to_jsonable(getattr(value, model_field.name))
            for model_field in fields(value)
        }

    if isinstance(value, dict):
        serialized: dict[str, JsonValue] = {}
        for key, item in value.items():
            if not isinstance(key, str):
                raise TypeError(
                    "JSON object keys must be strings; "
                    f"received {type(key).__name__}"
                )
            serialized[key] = to_jsonable(item)
        return serialized

    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]

    raise TypeError(f"Unsupported JSON serialization type: {type(value).__name__}")


def dumps_json(value: object) -> str:
    """Return deterministic, compact JSON text for a supported value."""
    return json.dumps(
        to_jsonable(value),
        allow_nan=False,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    )


def _serialize_datetime(value: datetime) -> str:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError("datetime values must be timezone-aware")

    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
