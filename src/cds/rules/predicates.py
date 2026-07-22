"""Pure predicates for explicit clinical-content matching."""

from __future__ import annotations

from decimal import Decimal

from cds.repositories.renal_content import RenalContentEndpoint

__all__ = ["renal_band_matches"]


def renal_band_matches(
    renal_value: Decimal,
    *,
    lower: RenalContentEndpoint | None,
    upper: RenalContentEndpoint | None,
) -> bool:
    """Return whether an unrounded renal value lies within the explicit band endpoints.

    ``None`` represents an unbounded endpoint. Inputs are expected to have passed structural and
    task-sufficiency validation before this predicate is called. The supplied ``Decimal`` is compared
    directly without rounding, quantization, interpolation, extrapolation, or unit conversion.
    """

    lower_satisfied = lower is None or renal_value > lower.value or (
        lower.inclusive and renal_value == lower.value
    )
    upper_satisfied = upper is None or renal_value < upper.value or (
        upper.inclusive and renal_value == upper.value
    )
    return lower_satisfied and upper_satisfied
