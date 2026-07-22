"""Pure renal-function calculation helpers."""

from datetime import date

from cds.domain.exceptions import CalculationError

__all__ = ["derive_age_years"]


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
