"""Focused tests for shared domain value objects."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit


def test_value_with_unit_defaults_do_not_invent_measurement_data() -> None:
    quantity = ValueWithUnit()

    assert quantity.value is None
    assert quantity.unit is None


def test_value_with_unit_retains_a_known_unit_for_a_missing_value() -> None:
    quantity = ValueWithUnit(unit="mg/dL")

    assert quantity.value is None
    assert quantity.unit == "mg/dL"


def test_value_with_unit_preserves_decimal_precision_and_unit_text() -> None:
    quantity = ValueWithUnit(value=Decimal("1.20"), unit="mg/dL")

    assert quantity.value == Decimal("1.20")
    assert quantity.unit == "mg/dL"


def test_codeable_concept_defaults_do_not_invent_text_or_codes() -> None:
    concept = CodeableConcept()

    assert concept.text is None
    assert concept.system is None
    assert concept.code is None


def test_codeable_concept_preserves_text_only_and_coded_input() -> None:
    text_only = CodeableConcept(text="Serum creatinine")
    coded = CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0")

    assert text_only.system is None
    assert text_only.code is None
    assert coded == CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0")


def test_time_range_defaults_are_open_and_unspecified() -> None:
    time_range = TimeRange()

    assert time_range.start is None
    assert time_range.end is None


@pytest.mark.parametrize(
    ("start", "end"),
    [
        (datetime(2026, 7, 21, 12, tzinfo=UTC), None),
        (None, datetime(2026, 7, 21, 12, tzinfo=UTC)),
        (
            datetime(2026, 7, 21, 12, tzinfo=UTC),
            datetime(2026, 7, 21, 12, tzinfo=UTC),
        ),
    ],
)
def test_time_range_preserves_open_and_equal_boundaries(
    start: datetime | None,
    end: datetime | None,
) -> None:
    time_range = TimeRange(start=start, end=end)

    assert time_range.start == start
    assert time_range.end == end
