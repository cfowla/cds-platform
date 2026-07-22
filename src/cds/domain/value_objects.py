"""Passive shared value objects used by CDS domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

__all__ = ["CodeableConcept", "TimeRange", "ValueWithUnit"]


@dataclass(slots=True, kw_only=True)
class ValueWithUnit:
    """Carry a quantitative value with its explicitly declared unit.

    Missing data uses ``None`` rather than zero or an empty string. A known unit may be
    retained when the numeric value is absent. Units are case-sensitive source values;
    normalization, compatibility checks, and conversion belong outside the domain model.
    """

    value: Decimal | None = None
    unit: str | None = None


@dataclass(slots=True, kw_only=True)
class CodeableConcept:
    """Carry source text with optional terminology-system coding.

    Missing text, system, or code uses ``None``; no field is inferred from another. The
    model preserves supplied coding only—lookup, validation, and normalization belong at
    mapper or validation boundaries.
    """

    text: str | None = None
    system: str | None = None
    code: str | None = None


@dataclass(slots=True, kw_only=True)
class TimeRange:
    """Represent optional start and end boundaries for a clinical interval.

    A missing boundary uses ``None`` and may mean unknown or open-ended according to the
    enclosing domain object. Datetimes should be timezone-aware at system boundaries;
    chronology and timezone validation remain responsibilities of the validation layer.
    """

    start: datetime | None = None
    end: datetime | None = None
