"""Tests for shared traceability support models."""

import json
from dataclasses import asdict
from datetime import UTC, datetime

import pytest

from cds.domain.models import Assumption, EvidenceItem, Provenance, WarningNote


@pytest.mark.parametrize(
    "model_type",
    [Provenance, EvidenceItem, Assumption, WarningNote],
)
def test_support_models_can_be_instantiated_independently(model_type: type[object]) -> None:
    """Every traceability object has a safe zero-argument constructor."""
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


@pytest.mark.parametrize(
    "support_object",
    [Provenance(), EvidenceItem(), Assumption(), WarningNote()],
)
def test_default_support_objects_have_json_safe_dicts(support_object: object) -> None:
    """Default instances convert to JSON-safe primitive dictionaries."""
    serialized = json.loads(json.dumps(asdict(support_object)))

    assert isinstance(serialized, dict)
