"""Tests for renal-function calculation services."""

from datetime import date
from decimal import Decimal

import pytest

from cds.domain.enums import WeightType
from cds.domain.exceptions import CalculationError
from cds.domain.value_objects import ValueWithUnit
from cds.services.renal import derive_age_years, require_supplied_weight


def test_evaluation_before_birthday_returns_prior_completed_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 23),
        evaluation_date=date(2026, 7, 22),
    ) == 45


def test_evaluation_on_birthday_increments_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 22),
        evaluation_date=date(2026, 7, 22),
    ) == 46


def test_evaluation_after_birthday_retains_incremented_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 21),
        evaluation_date=date(2026, 7, 22),
    ) == 46


def test_february_29_birth_does_not_increment_on_february_28_non_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2023, 2, 28),
    ) == 18


def test_february_29_birth_increments_on_march_1_non_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2023, 3, 1),
    ) == 19


def test_february_29_birth_increments_on_february_29_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2024, 2, 29),
    ) == 20


def test_birth_date_equal_to_evaluation_date_returns_zero() -> None:
    same_date = date(2026, 7, 22)

    assert derive_age_years(birth_date=same_date, evaluation_date=same_date) == 0


def test_birth_date_after_evaluation_date_raises_calculation_error() -> None:
    with pytest.raises(CalculationError):
        derive_age_years(
            birth_date=date(2026, 7, 23),
            evaluation_date=date(2026, 7, 22),
        )


def test_identical_explicit_inputs_produce_identical_ages() -> None:
    birth_date = date(1980, 7, 23)
    evaluation_date = date(2026, 7, 22)

    first = derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)
    second = derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)

    assert first == second == 45
    assert isinstance(first, int)


def test_caller_supplied_date_objects_remain_unchanged() -> None:
    birth_date = date(1980, 7, 23)
    evaluation_date = date(2026, 7, 22)
    original_birth_date = date(1980, 7, 23)
    original_evaluation_date = date(2026, 7, 22)

    derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)

    assert birth_date == original_birth_date
    assert evaluation_date == original_evaluation_date


@pytest.mark.parametrize(
    ("supplied_value", "weight_type"),
    [
        (Decimal("72.40"), WeightType.ACTUAL),
        (Decimal("61.25"), WeightType.IDEAL),
        (Decimal("66.875"), WeightType.ADJUSTED),
        (Decimal("54.321"), WeightType.OTHER),
    ],
)
def test_supported_supplied_weight_is_preserved_without_derivation(
    supplied_value: Decimal,
    weight_type: WeightType,
) -> None:
    weight = ValueWithUnit(value=supplied_value, unit="kg")
    original_value_tuple = supplied_value.as_tuple()

    returned_weight, returned_type = require_supplied_weight(
        weight=weight,
        weight_type=weight_type,
    )

    assert returned_weight is not weight
    assert returned_weight.value is supplied_value
    assert returned_weight.value.as_tuple() == original_value_tuple
    assert returned_weight.unit == "kg"
    assert returned_type is weight_type
    assert weight.value is supplied_value
    assert weight.value.as_tuple() == original_value_tuple
    assert weight.unit == "kg"


def test_repeated_calls_return_equivalent_independently_allocated_weights() -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit="kg")

    first = require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)
    second = require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)

    assert first == second
    assert first[0] is not second[0]
    assert first[0] is not weight
    assert second[0] is not weight


@pytest.mark.parametrize("value", [None, 72.4])
def test_missing_or_non_decimal_weight_value_raises_calculation_error(
    value: object,
) -> None:
    weight = ValueWithUnit(value=value, unit="kg")  # type: ignore[arg-type]

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-0.01")])
def test_non_positive_weight_value_raises_calculation_error(value: Decimal) -> None:
    weight = ValueWithUnit(value=value, unit="kg")

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("unit", [None, "", "KG", " kg", "kg ", " kg ", "lb"])
def test_non_exact_kilogram_unit_raises_calculation_error(unit: str | None) -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit=unit)

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("weight_type", [WeightType.UNKNOWN, None, "actual"])
def test_unknown_missing_or_raw_string_weight_type_raises_calculation_error(
    weight_type: object,
) -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit="kg")

    with pytest.raises(CalculationError):
        require_supplied_weight(  # type: ignore[arg-type]
            weight=weight,
            weight_type=weight_type,
        )


@pytest.mark.skip(reason="Placeholder: Cockcroft-Gault calculator is not implemented yet")
def test_cockcroft_gault_calculator() -> None:
    """Reserve the first renal-calculator behavior test."""
