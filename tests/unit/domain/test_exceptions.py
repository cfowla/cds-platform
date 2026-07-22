"""Focused tests for passive typed domain exceptions."""

import pytest

from cds.domain.exceptions import CalculationError, ContentNotFound, ValidationError


EXCEPTION_TYPES = (ValidationError, ContentNotFound, CalculationError)


@pytest.mark.parametrize("exception_type", EXCEPTION_TYPES)
def test_exception_preserves_standard_behavior_and_can_be_caught_exactly(
    exception_type: type[Exception],
) -> None:
    message = "unexpected internal failure"

    with pytest.raises(exception_type) as captured:
        raise exception_type(message)

    assert type(captured.value) is exception_type
    assert isinstance(captured.value, Exception)
    assert str(captured.value) == message
    assert captured.value.args == (message,)


def test_exception_types_are_distinct_from_each_other() -> None:
    for exception_type in EXCEPTION_TYPES:
        other_types = tuple(
            candidate for candidate in EXCEPTION_TYPES if candidate is not exception_type
        )
        assert not any(issubclass(exception_type, other_type) for other_type in other_types)
