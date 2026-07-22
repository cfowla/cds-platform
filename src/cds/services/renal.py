"""Pure renal-function calculation helpers."""

from datetime import date
from decimal import Decimal

from cds.domain.enums import WeightType
from cds.domain.exceptions import CalculationError
from cds.domain.value_objects import ValueWithUnit

__all__ = ["derive_age_years", "require_supplied_weight"]


def derive_age_years(*, birth_date: date, evaluation_date: date) -> int:
    """Return completed calendar years at an explicit evaluation date.

    For a February 29 birth, age advances on February 29 in leap years and
    on March 1 in non-leap years. Callers must complete structural and
    sufficiency validation before invoking this service.

    Raises:
        CalculationError: If the birth date is after the evaluation date,
            indicating a breach of the validated-service boundary.
    """

    if birth_date > evaluation_date:
        raise CalculationError("Birth date cannot be after the evaluation date.")

    years = evaluation_date.year - birth_date.year
    birthday_not_reached = (evaluation_date.month, evaluation_date.day) < (
        birth_date.month,
        birth_date.day,
    )
    return years - int(birthday_not_reached)


def require_supplied_weight(
    *,
    weight: ValueWithUnit,
    weight_type: WeightType,
) -> tuple[ValueWithUnit, WeightType]:
    """Return an independently allocated copy of a validated supplied weight.

    Callers must complete structural and task-sufficiency validation before
    invoking this helper. It preserves the exact supplied Decimal, kilogram
    unit, and explicit supported weight type without derivation or conversion.

    Raises:
        CalculationError: If the validated-service contract is breached.
    """

    if not isinstance(weight, ValueWithUnit):
        raise CalculationError("Supplied weight must be a ValueWithUnit.")
    if weight.value is None:
        raise CalculationError("Supplied weight requires a numeric value.")
    if not isinstance(weight.value, Decimal):
        raise CalculationError("Supplied weight value must be a Decimal.")
    if weight.value <= Decimal("0"):
        raise CalculationError("Supplied weight value must be greater than zero.")
    if weight.unit != "kg":
        raise CalculationError('Supplied weight unit must be exactly "kg".')
    if not isinstance(weight_type, WeightType) or weight_type not in {
        WeightType.ACTUAL,
        WeightType.IDEAL,
        WeightType.ADJUSTED,
        WeightType.OTHER,
    }:
        raise CalculationError("Supplied weight type must be explicit and supported.")

    return ValueWithUnit(value=weight.value, unit=weight.unit), weight_type
