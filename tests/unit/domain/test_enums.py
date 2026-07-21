"""Tests for stable CDS domain enum values and serialization."""

import json
from enum import StrEnum

import pytest

from cds.domain.enums import RenalMethod, ResultStatus, Sex, WeightType


@pytest.mark.parametrize(
    ("enum_type", "expected"),
    [
        (
            Sex,
            {
                "MALE": "male",
                "FEMALE": "female",
                "OTHER": "other",
                "UNKNOWN": "unknown",
            },
        ),
        (
            ResultStatus,
            {
                "SUCCESS": "success",
                "SUCCESS_WITH_WARNINGS": "success_with_warnings",
                "INCOMPLETE": "incomplete",
                "NOT_APPLICABLE": "not_applicable",
                "FAILED": "failed",
            },
        ),
        (
            RenalMethod,
            {
                "COCKCROFT_GAULT": "cockcroft_gault",
                "CKD_EPI": "ckd_epi",
                "MDRD": "mdrd",
                "MEASURED_CRCL": "measured_crcl",
                "UNKNOWN": "unknown",
            },
        ),
        (
            WeightType,
            {
                "ACTUAL": "actual",
                "IDEAL": "ideal",
                "ADJUSTED": "adjusted",
                "OTHER": "other",
                "UNKNOWN": "unknown",
            },
        ),
    ],
)
def test_enum_values_are_stable(enum_type: type[StrEnum], expected: dict[str, str]) -> None:
    """Enum names and wire values remain explicit and reviewable."""
    assert {member.name: member.value for member in enum_type} == expected


@pytest.mark.parametrize("enum_type", [Sex, ResultStatus, RenalMethod, WeightType])
def test_enum_members_serialize_as_strings(enum_type: type[StrEnum]) -> None:
    """Domain enums serialize directly to their declared string values."""
    for member in enum_type:
        assert str(member) == member.value
        assert json.loads(json.dumps(member)) == member.value


@pytest.mark.parametrize("enum_type", [Sex, RenalMethod, WeightType])
def test_unknown_states_are_explicit(enum_type: type[StrEnum]) -> None:
    """Uncertain categorical input uses a named, non-blank value."""
    assert enum_type.UNKNOWN.value == "unknown"


@pytest.mark.parametrize("enum_type", [Sex, ResultStatus, RenalMethod, WeightType])
def test_no_enum_value_is_blank(enum_type: type[StrEnum]) -> None:
    """No category, including an unknown state, is encoded as an empty string."""
    assert all(member.value.strip() for member in enum_type)
