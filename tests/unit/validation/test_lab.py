"""Focused tests for pure structural serum-creatinine validation."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone, tzinfo
from decimal import Decimal

import pytest

from cds.domain.clinical import LabResult
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.validation.lab import validate_serum_creatinine_structure


UTC_EVALUATION = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
UTC_COLLECTION = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
UTC_RESULT = datetime(2026, 7, 22, 10, 30, tzinfo=timezone.utc)


def _lab(
    *,
    value: object = Decimal("1.2"),
    unit: object = "mg/dL",
    status: object = "final",
    collected_at: object = UTC_COLLECTION,
    resulted_at: object = UTC_RESULT,
) -> LabResult:
    return LabResult(
        result_id="synthetic-lab-001",
        patient_id="synthetic-patient-001",
        test=CodeableConcept(text="Synthetic serum creatinine"),
        value=ValueWithUnit(value=value, unit=unit),  # type: ignore[arg-type]
        collected_at=collected_at,  # type: ignore[arg-type]
        resulted_at=resulted_at,  # type: ignore[arg-type]
        status=status,  # type: ignore[arg-type]
    )


def _codes(result: object) -> list[str | None]:
    return [issue.code for issue in result.issues]


class _UnavailableOffset(tzinfo):
    def utcoffset(self, dt: datetime | None) -> None:
        return None

    def dst(self, dt: datetime | None) -> None:
        return None


def test_valid_final_serum_creatinine() -> None:
    result = validate_serum_creatinine_structure(
        _lab(status="final"),
        evaluation_at=UTC_EVALUATION,
    )
    assert result.is_valid is True
    assert result.issues == []


def test_valid_corrected_serum_creatinine() -> None:
    result = validate_serum_creatinine_structure(
        _lab(status="corrected"),
        evaluation_at=UTC_EVALUATION,
    )
    assert result.is_valid is True
    assert result.issues == []


def test_validation_result_issue_collections_are_independent() -> None:
    first = validate_serum_creatinine_structure(
        _lab(value=Decimal("0")), evaluation_at=UTC_EVALUATION
    )
    second = validate_serum_creatinine_structure(_lab(), evaluation_at=UTC_EVALUATION)
    first.issues.clear()
    assert second.issues == []
    assert second.is_valid is True


def test_missing_numeric_value_remains_distinct_from_measured_zero() -> None:
    missing_lab = _lab(value=None)
    zero_lab = _lab(value=Decimal("0"))

    missing = validate_serum_creatinine_structure(
        missing_lab, evaluation_at=UTC_EVALUATION
    )
    zero = validate_serum_creatinine_structure(zero_lab, evaluation_at=UTC_EVALUATION)

    assert _codes(missing) == ["missing_serum_creatinine_value"]
    assert _codes(zero) == ["invalid_serum_creatinine_value"]
    assert missing_lab.value.value is None
    assert zero_lab.value.value == Decimal("0")


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-0.1")])
def test_zero_and_negative_values_are_rejected(value: Decimal) -> None:
    result = validate_serum_creatinine_structure(
        _lab(value=value), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["invalid_serum_creatinine_value"]
    assert result.issues[0].field_path == "value.value"


@pytest.mark.parametrize(
    "value",
    [Decimal("NaN"), Decimal("sNaN"), Decimal("Infinity"), Decimal("-Infinity")],
)
def test_each_nonfinite_decimal_is_rejected_without_crashing(value: Decimal) -> None:
    result = validate_serum_creatinine_structure(
        _lab(value=value), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["invalid_serum_creatinine_value"]


def test_non_decimal_numeric_value_is_rejected_without_crashing() -> None:
    result = validate_serum_creatinine_structure(
        _lab(value=1.2), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["invalid_serum_creatinine_value"]


@pytest.mark.parametrize("unit", [None, "", " ", "\t\n"])
def test_missing_and_whitespace_only_units_are_rejected(unit: object) -> None:
    result = validate_serum_creatinine_structure(
        _lab(unit=unit), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["missing_serum_creatinine_unit"]
    assert result.issues[0].field_path == "value.unit"


def test_exact_mg_per_dl_unit_is_accepted() -> None:
    result = validate_serum_creatinine_structure(
        _lab(unit="mg/dL"), evaluation_at=UTC_EVALUATION
    )
    assert result.is_valid is True


@pytest.mark.parametrize("unit", ["mg/L", "mmol/L", "µmol/L", "MG/DL", " mg/dL "])
def test_unsupported_or_ambiguous_units_are_rejected_without_conversion(unit: str) -> None:
    lab = _lab(unit=unit)
    result = validate_serum_creatinine_structure(lab, evaluation_at=UTC_EVALUATION)
    assert _codes(result) == ["unsupported_serum_creatinine_unit"]
    assert lab.value.unit == unit
    assert lab.value.value == Decimal("1.2")


@pytest.mark.parametrize("status", [None, "", " ", "\t\n"])
def test_missing_and_blank_statuses_are_rejected(status: object) -> None:
    result = validate_serum_creatinine_structure(
        _lab(status=status), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["missing_lab_status"]
    assert result.issues[0].field_path == "status"


@pytest.mark.parametrize(
    "status",
    [
        "preliminary",
        "cancelled",
        "entered-in-error",
        "unknown",
        "FINAL",
        " final",
        "final ",
    ],
)
def test_unsupported_statuses_are_rejected_exactly(status: str) -> None:
    result = validate_serum_creatinine_structure(
        _lab(status=status), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["unsupported_lab_status"]


def test_collection_time_is_required() -> None:
    result = validate_serum_creatinine_structure(
        _lab(collected_at=None), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["missing_collection_time"]
    assert result.issues[0].field_path == "collected_at"


def test_missing_collection_time_does_not_emit_timezone_issue() -> None:
    result = validate_serum_creatinine_structure(
        _lab(collected_at=None), evaluation_at=UTC_EVALUATION
    )
    assert _codes(result) == ["missing_collection_time"]


def test_naive_collection_time_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(collected_at=datetime(2026, 7, 22, 10, 0)),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["collection_timezone_required"]


def test_collection_time_with_unavailable_utc_offset_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(
            collected_at=datetime(2026, 7, 22, 10, 0, tzinfo=_UnavailableOffset())
        ),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["collection_timezone_required"]


def test_collection_after_evaluation_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(
            collected_at=datetime(2026, 7, 22, 12, 1, tzinfo=timezone.utc),
            resulted_at=None,
        ),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["collection_after_evaluation"]


def test_missing_result_time_is_optional() -> None:
    result = validate_serum_creatinine_structure(
        _lab(resulted_at=None), evaluation_at=UTC_EVALUATION
    )
    assert result.is_valid is True
    assert result.issues == []


def test_naive_result_time_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(resulted_at=datetime(2026, 7, 22, 10, 30)),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["result_timezone_required"]


def test_result_time_with_unavailable_utc_offset_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(resulted_at=datetime(2026, 7, 22, 10, 30, tzinfo=_UnavailableOffset())),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["result_timezone_required"]


def test_result_before_collection_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(resulted_at=datetime(2026, 7, 22, 9, 59, tzinfo=timezone.utc)),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["result_before_collection"]


def test_result_after_evaluation_is_rejected() -> None:
    result = validate_serum_creatinine_structure(
        _lab(resulted_at=datetime(2026, 7, 22, 12, 1, tzinfo=timezone.utc)),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == ["result_after_evaluation"]


def test_equivalent_instants_with_different_offsets_are_valid() -> None:
    collection = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
    result_time = datetime(
        2026, 7, 22, 6, 0, tzinfo=timezone(timedelta(hours=-4))
    )
    evaluation = datetime(
        2026, 7, 22, 8, 0, tzinfo=timezone(timedelta(hours=-4))
    )
    result = validate_serum_creatinine_structure(
        _lab(collected_at=collection, resulted_at=result_time),
        evaluation_at=evaluation,
    )
    assert result.is_valid is True
    assert result.issues == []


@pytest.mark.parametrize(
    "evaluation_at",
    [
        datetime(2026, 7, 22, 12, 0),
        datetime(2026, 7, 22, 12, 0, tzinfo=_UnavailableOffset()),
    ],
)
def test_invalid_evaluation_time_does_not_fabricate_evaluation_chronology(
    evaluation_at: datetime,
) -> None:
    result = validate_serum_creatinine_structure(
        _lab(
            collected_at=datetime(2026, 7, 23, 10, 0, tzinfo=timezone.utc),
            resulted_at=datetime(2026, 7, 23, 10, 30, tzinfo=timezone.utc),
        ),
        evaluation_at=evaluation_at,
    )
    assert _codes(result) == ["evaluation_timezone_required"]


def test_invalid_evaluation_still_allows_independent_result_collection_check() -> None:
    result = validate_serum_creatinine_structure(
        _lab(
            collected_at=datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc),
            resulted_at=datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
        ),
        evaluation_at=datetime(2026, 7, 22, 12, 0),
    )
    assert _codes(result) == [
        "evaluation_timezone_required",
        "result_before_collection",
    ]


def test_multiple_findings_follow_required_deterministic_order() -> None:
    result = validate_serum_creatinine_structure(
        _lab(
            value=Decimal("0"),
            unit="mg/L",
            status="preliminary",
            collected_at=datetime(2026, 7, 22, 14, 0, tzinfo=timezone.utc),
            resulted_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
        ),
        evaluation_at=UTC_EVALUATION,
    )
    assert _codes(result) == [
        "invalid_serum_creatinine_value",
        "unsupported_serum_creatinine_unit",
        "unsupported_lab_status",
        "collection_after_evaluation",
        "result_before_collection",
        "result_after_evaluation",
    ]
    assert all(issue.severity == "error" for issue in result.issues)
    assert all(issue.field_path for issue in result.issues)
    assert all(issue.message and issue.message.strip() for issue in result.issues)
    assert result.is_valid is False


def test_evaluation_issue_precedes_other_structural_findings() -> None:
    result = validate_serum_creatinine_structure(
        _lab(value=None, unit=" ", status=None, collected_at=None, resulted_at=None),
        evaluation_at=datetime(2026, 7, 22, 12, 0),
    )
    assert _codes(result) == [
        "evaluation_timezone_required",
        "missing_serum_creatinine_value",
        "missing_serum_creatinine_unit",
        "missing_lab_status",
        "missing_collection_time",
    ]


def test_validation_does_not_mutate_lab_or_traceability_structures() -> None:
    lab = _lab()
    lab.assumptions.append(
        Assumption(code="synthetic_fixture", description="Synthetic test data.")
    )
    lab.warnings.append(WarningNote(code="synthetic_warning", message="Synthetic."))
    lab.evidence.append(EvidenceItem(summary="Synthetic evidence."))
    lab.provenance = Provenance(
        source_type="manual_entry", source_identifier="synthetic-source-001"
    )
    before = deepcopy(lab)

    result = validate_serum_creatinine_structure(lab, evaluation_at=UTC_EVALUATION)

    assert result.is_valid is True
    assert lab == before
    assert lab.assumptions is not result.issues
    assert lab.warnings is not result.issues
    assert lab.evidence is not result.issues


def test_validator_adds_no_renal_calculation_or_derived_clinical_attributes() -> None:
    lab = _lab()
    result = validate_serum_creatinine_structure(lab, evaluation_at=UTC_EVALUATION)
    assert result.is_valid is True
    for derived_name in (
        "creatinine_clearance",
        "crcl",
        "renal_function",
        "renal_stability",
        "normalized_value",
        "converted_value",
        "age_years",
    ):
        assert not hasattr(lab, derived_name)
        assert not hasattr(result, derived_name)
