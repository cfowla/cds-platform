"""Focused tests for traceability support objects."""

from datetime import UTC, datetime

from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote


def test_provenance_defaults_do_not_claim_a_source() -> None:
    provenance = Provenance()

    assert provenance.source_type == "unknown"
    assert provenance.source_name is None
    assert provenance.source_identifier is None
    assert provenance.captured_at is None
    assert provenance.author is None
    assert provenance.version is None


def test_evidence_defaults_do_not_claim_support() -> None:
    evidence = EvidenceItem()

    assert evidence.summary is None
    assert evidence.level == "unknown"
    assert evidence.citation is None
    assert evidence.url is None
    assert evidence.source_document is None
    assert evidence.source_version is None
    assert evidence.provenance == Provenance()


def test_assumption_defaults_remain_unevaluated() -> None:
    assumption = Assumption()

    assert assumption.code is None
    assert assumption.description is None
    assert assumption.applies is None
    assert assumption.provenance == Provenance()


def test_warning_defaults_do_not_invent_a_message_or_severity() -> None:
    warning = WarningNote()

    assert warning.code is None
    assert warning.message is None
    assert warning.severity == "unknown"
    assert warning.provenance == Provenance()


def test_support_objects_preserve_explicit_traceability_values() -> None:
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
