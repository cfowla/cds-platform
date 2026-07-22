"""Focused tests for exact renal-band boundary predicates."""

from __future__ import annotations

from decimal import Decimal

import pytest

from cds.repositories.renal_content import RenalContentEndpoint
from cds.rules.predicates import renal_band_matches


Endpoint = RenalContentEndpoint
BANDS = {
    "below_11": (
        Endpoint(value=Decimal("0"), inclusive=False),
        Endpoint(value=Decimal("11"), inclusive=False),
    ),
    "crcl_11_to_below_30": (
        Endpoint(value=Decimal("11"), inclusive=True),
        Endpoint(value=Decimal("30"), inclusive=False),
    ),
    "crcl_30_to_60": (
        Endpoint(value=Decimal("30"), inclusive=True),
        Endpoint(value=Decimal("60"), inclusive=True),
    ),
    "above_60": (
        Endpoint(value=Decimal("60"), inclusive=False),
        None,
    ),
}


def _matching_band_ids(renal_value: Decimal) -> list[str]:
    return [
        band_id
        for band_id, (lower, upper) in BANDS.items()
        if renal_band_matches(renal_value, lower=lower, upper=upper)
    ]


@pytest.mark.parametrize(
    ("renal_value", "expected_band_id"),
    [
        (Decimal("0.000000000000000001"), "below_11"),
        (Decimal("10.999999999999999999"), "below_11"),
        (Decimal("11"), "crcl_11_to_below_30"),
        (Decimal("11.000000000000000001"), "crcl_11_to_below_30"),
        (Decimal("29.999999999999999999"), "crcl_11_to_below_30"),
        (Decimal("30"), "crcl_30_to_60"),
        (Decimal("30.000000000000000001"), "crcl_30_to_60"),
        (Decimal("59.999999999999999999"), "crcl_30_to_60"),
        (Decimal("60"), "crcl_30_to_60"),
        (Decimal("60.000000000000000001"), "above_60"),
    ],
)
def test_day_45_partition_matches_exactly_one_band_at_boundaries(
    renal_value: Decimal,
    expected_band_id: str,
) -> None:
    assert _matching_band_ids(renal_value) == [expected_band_id]


@pytest.mark.parametrize("renal_value", [Decimal("-1"), Decimal("0")])
def test_values_outside_the_declared_renal_domain_match_no_band(
    renal_value: Decimal,
) -> None:
    assert _matching_band_ids(renal_value) == []


def test_none_endpoint_is_unbounded_in_its_direction() -> None:
    upper = Endpoint(value=Decimal("11"), inclusive=False)
    lower = Endpoint(value=Decimal("60"), inclusive=False)

    assert renal_band_matches(Decimal("-999"), lower=None, upper=upper)
    assert renal_band_matches(Decimal("999"), lower=lower, upper=None)


def test_predicate_uses_the_supplied_decimal_without_rounding_or_quantization() -> None:
    lower = Endpoint(value=Decimal("30"), inclusive=True)
    upper = Endpoint(value=Decimal("60"), inclusive=True)

    assert not renal_band_matches(
        Decimal("29.9999999999999999999999999999"),
        lower=lower,
        upper=upper,
    )
    assert not renal_band_matches(
        Decimal("60.0000000000000000000000000001"),
        lower=lower,
        upper=upper,
    )
