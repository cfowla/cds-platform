"""Shared traceability support models for the CDS domain layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, TypeAlias

ProvenanceSourceType: TypeAlias = Literal[
    "ehr",
    "manual_entry",
    "interface",
    "calculated",
    "rule_content",
    "external_api",
    "unknown",
]
EvidenceLevel: TypeAlias = Literal[
    "guideline",
    "primary_literature",
    "local_policy",
    "expert_opinion",
    "computed",
    "unknown",
]
WarningSeverity: TypeAlias = Literal["info", "warning", "high", "critical", "unknown"]

__all__ = ["Assumption", "EvidenceItem", "Provenance", "WarningNote"]


@dataclass(slots=True, kw_only=True)
class Provenance:
    """Describe where a domain value or decision originated."""

    source_type: ProvenanceSourceType = "unknown"
    source_name: str | None = None
    source_identifier: str | None = None
    captured_at: datetime | None = None
    author: str | None = None
    version: str | None = None


@dataclass(slots=True, kw_only=True)
class EvidenceItem:
    """Reference evidence supporting a calculation, rule, or recommendation."""

    summary: str | None = None
    level: EvidenceLevel = "unknown"
    citation: str | None = None
    url: str | None = None
    source_document: str | None = None
    source_version: str | None = None
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Assumption:
    """Record an explicit assumption introduced during evaluation."""

    code: str | None = None
    description: str | None = None
    applies: bool | None = None
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class WarningNote:
    """Record a non-fatal limitation, uncertainty, or validation concern."""

    code: str | None = None
    message: str | None = None
    severity: WarningSeverity = "unknown"
    provenance: Provenance = field(default_factory=Provenance)
