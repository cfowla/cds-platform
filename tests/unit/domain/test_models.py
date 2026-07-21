"""Tests for shared traceability and value objects."""

import json
from dataclasses import asdict
from datetime import UTC, datetime
from decimal import Decimal

import pytest

from cds.domain.models import (
    Assumption,
    CodeableConcept,
    EvidenceItem,
    Provenance,
    TimeRange,
    ValueWithUnit,
    WarningNote,
)


@pytest.mark.parametrize(
    "model_type",
    [
        Provenance,
        EvidenceItem,
        Assumption,
        WarningNote,
        ValueWithUnit,
        CodeableConcept,
        TimeRange,
    ],
)
def test_shared_models_can_be_instantiated_independently(model_type: type[object]) -> None:
    """Every shared domain object has a safe zero-argument constructor."""
    assert isinstance(model_type(), model_type)


def test_provenance_defaults_do_not_claim_a_source() -> None:
    """Missing provenance remains explicit without inventing identifying details."""
    provenance = Provenance()

    assert provenance.source_type == "unknown"
    assert provenance.source_name is None
    assert provenance.source_identifier is None
    assert provenance.captured_at is None
    assert provenance.author is None
    assert provenance.version is None


def test_evidence_defaults_do_not_claim_support() -> None:
    """An empty evidence object does not imply a citation or evidence level."""
    evidence = EvidenceItem()

    assert evidence.summary is None
    assert evidence.level == "unknown"
    assert evidence.citation is None
    assert evidence.url is None
    assert evidence.source_document is None
    assert evidence.source_version is None
    assert evidence.provenance == Provenance()


def test_assumption_defaults_do_not_silently_apply() -> None:
    """An unspecified assumption remains unevaluated rather than true or false."""
    assumption = Assumption()

    assert assumption.code is None
    assert assumption.description is None
    assert assumption.applies is None
    assert assumption.provenance == Provenance()


def test_warning_defaults_do_not_invent_a_message_or_severity() -> None:
    """An unspecified warning uses an explicit unknown severity and missing text."""
    warning = WarningNote()

    assert warning.code is None
    assert warning.message is None
    assert warning.severity == "unknown"
    assert warning.provenance == Provenance()


@pytest.mark.parametrize("model_type", [EvidenceItem, Assumption, WarningNote])
def test_nested_provenance_is_not_shared(model_type: type[object]) -> None:
    """Each support object receives its own provenance instance."""
    first = model_type()
    second = model_type()

    first.provenance.source_name = "changed"

    assert second.provenance.source_name is None


def test_support_models_accept_explicit_traceability_values() -> None:
    """Traceability objects preserve supplied evidence and source details."""
    captured_at = datetime(2026, 7, 21, 18, 30, tzinfo=UTC)
    provenance = Provenance(
        source_type="rule_content",
        source_name="renal-rules",
        source_identifier="cefepime-standard",
        captured_at=captured_at,
        author="clinical-reviewer",
        version="1.0.0",
    )
    evidence = EvidenceItem(
        summary="Reviewed renal-adjustment content.",
        level="guideline",
        citation="Synthetic citation for testing.",
        source_document="renal-content",
        source_version="2026-07-21",
        provenance=provenance,
    )
    assumption = Assumption(
        code="stable_serum_creatinine",
        description="The synthetic scenario declares renal function stable.",
        applies=True,
        provenance=provenance,
    )
    warning = WarningNote(
        code="prototype_only",
        message="Not for direct clinical use.",
        severity="high",
        provenance=provenance,
    )

    assert evidence.provenance is provenance
    assert assumption.applies is True
    assert warning.severity == "high"
    assert provenance.captured_at == captured_at


def test_value_with_unit_defaults_do_not_invent_measurement_data() -> None:
    """Missing quantitative data is represented by None, not zero."""
    quantity = ValueWithUnit()

    assert quantity.value is None
    assert quantity.unit is None


def test_value_with_unit_can_retain_a_known_unit_for_a_missing_value() -> None:
    """An expected unit may remain explicit when the observation is absent."""
    quantity = ValueWithUnit(unit="mg/dL")

    assert quantity.value is None
    assert quantity.unit == "mg/dL"


def test_value_with_unit_preserves_decimal_precision_and_unit_text() -> None:
    """The value object stores supplied decimal precision without conversion."""
    quantity = ValueWithUnit(value=Decimal("1.20"), unit="mg/dL")

    assert quantity.value == Decimal("1.20")
    assert quantity.unit == "mg/dL"


def test_codeable_concept_defaults_do_not_invent_text_or_codes() -> None:
    """A missing concept remains entirely unspecified."""
    concept = CodeableConcept()

    assert concept.text is None
    assert concept.system is None
    assert concept.code is None


def test_codeable_concept_preserves_text_only_and_coded_input() -> None:
    """Free text and normalized coding can be represented without lookup logic."""
    text_only = CodeableConcept(text="Serum creatinine")
    coded = CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0")

    assert text_only.system is None
    assert text_only.code is None
    assert coded == CodeableConcept(text="Serum creatinine", system="LOINC", code="2160-0")


def test_time_range_defaults_are_open_and_unspecified() -> None:
    """Missing temporal boundaries are explicit rather than fabricated."""
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
    """The passive value object preserves supplied endpoints without chronology logic."""
    time_range = TimeRange(start=start, end=end)

    assert time_range.start == start
    assert time_range.end == end


@pytest.mark.parametrize(
    "shared_object",
    [
        Provenance(),
        EvidenceItem(),
        Assumption(),
        WarningNote(),
        ValueWithUnit(),
        CodeableConcept(),
        TimeRange(),
    ],
)
def test_default_shared_objects_have_json_safe_dicts(shared_object: object) -> None:
    """Default instances convert to JSON-safe primitive dictionaries."""
    serialized = json.loads(json.dumps(asdict(shared_object)))

    assert isinstance(serialized, dict)
