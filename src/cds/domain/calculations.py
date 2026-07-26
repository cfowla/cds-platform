"""Passive, feature-neutral calculation result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Mapping, TypeAlias

from cds.domain.support import Assumption, Provenance, WarningNote

SerializableValue: TypeAlias = str | int | float | bool | Decimal | None

__all__ = ["CalculationResult", "SerializableValue"]


@dataclass(frozen=True, slots=True, kw_only=True)
class CalculationResult:
    """Carry one reproducible calculation without performing the calculation.

    Missing numeric output remains ``None`` rather than zero. Inputs are copied by callers into a
    stable, string-keyed mapping suitable for audit and serialization. Clinical calculations,
    validation, unit conversion, and provenance assignment remain outside this passive model.
    """

    calculation_id: str
    method: str
    implementation_version: str
    value: Decimal | None
    unit: str
    inputs: Mapping[str, SerializableValue] = field(default_factory=dict)
    assumptions: tuple[Assumption, ...] = ()
    warnings: tuple[WarningNote, ...] = ()
    provenance: Provenance = field(default_factory=Provenance)
