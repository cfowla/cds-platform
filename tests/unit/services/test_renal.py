"""Tests for renal-function calculation services."""

from datetime import date

import pytest

from cds.domain.exceptions import CalculationError
from cds.services.renal import derive_age_years


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


@pytest.mark.skip(reason="Placeholder: Cockcroft-Gault calculator is not implemented yet")
def test_cockcroft_gault_calculator() -> None:
    """Reserve the first renal-calculator behavior test."""
