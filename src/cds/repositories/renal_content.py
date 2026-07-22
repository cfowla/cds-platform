"""Typed renal-dose content and its exact-key repository boundary.

The objects in this module represent already validated, versioned clinical content. They perform no
file access, YAML parsing, schema validation, version selection, identifier normalization, or rule
matching. Repository implementations must retrieve content by the exact case-sensitive
``(medication_id, regimen_id, content_version)`` key and raise ``ContentNotFound`` when that exact
key is absent.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal, Protocol, TypeAlias, runtime_checkable

from cds.domain.exceptions import ContentNotFound

ContentReviewStatus: TypeAlias = Literal["draft", "reviewed", "retired"]
ContentBandOutcome: TypeAlias = Literal["recommendation", "no_recommendation"]
ContentEvidenceLevel: TypeAlias = Literal[
    "guideline",
    "primary_literature",
    "local_policy",
    "expert_opinion",
]
ContentRecommendationAction: TypeAlias = Literal[
    "continue",
    "adjust_dose",
    "hold",
    "stop",
    "avoid",
    "monitor",
    "switch",
    "clarify",
    "none",
]

__all__ = [
    "ContentBandOutcome",
    "ContentEvidenceLevel",
    "ContentRecommendationAction",
    "ContentReviewStatus",
    "ContentNotFound",
    "RenalContentEndpoint",
    "RenalContentInterval",
    "RenalDoseBandContent",
    "RenalDoseContent",
    "RenalDoseContentKey",
    "RenalDoseContentRepository",
    "RenalDoseMedicationContent",
    "RenalDoseRecommendationContent",
    "RenalDoseRegimenContent",
    "RenalDoseReviewContent",
    "RenalDoseSourceContent",
    "RenalDoseSupportedContext",
    "RenalDoseQuantity",
]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseContentKey:
    """Exact immutable lookup key for one renal-dose content document."""

    medication_id: str
    regimen_id: str
    content_version: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseQuantity:
    """One exact decimal quantity and its explicit case-sensitive unit."""

    value: Decimal
    unit: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalContentEndpoint:
    """One bounded renal interval endpoint."""

    value: Decimal
    inclusive: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalContentInterval:
    """A renal interval whose absent endpoint is unbounded in that direction."""

    lower: RenalContentEndpoint | None
    upper: RenalContentEndpoint | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseMedicationContent:
    """Exact medication identity carried by one content document."""

    id: str
    display: str


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseRegimenContent:
    """Exact regimen facts that must match before renal-band evaluation."""

    id: str
    display: str
    indication_ids: tuple[str, ...]
    route_id: str
    formulation_id: str | None
    base_dose: RenalDoseQuantity
    frequency_interval: RenalDoseQuantity
    infusion_duration: RenalDoseQuantity | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseSupportedContext:
    """Explicit population and renal-method constraints declared by the document."""

    minimum_age_years: int
    renal_method: str
    renal_unit: str
    renal_function_stable: bool
    renal_replacement_therapy: bool
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseRecommendationContent:
    """Structured recommendation payload stored in a recommendation-bearing renal band."""

    action: ContentRecommendationAction
    dose: RenalDoseQuantity | None
    route_id: str | None
    frequency_interval: RenalDoseQuantity | None
    infusion_duration: RenalDoseQuantity | None
    rationale: str
    monitoring: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseBandContent:
    """One ordered renal band and its explicitly represented outcome."""

    id: str
    lower: RenalContentEndpoint | None
    upper: RenalContentEndpoint | None
    outcome: ContentBandOutcome
    recommendation: RenalDoseRecommendationContent | None
    no_recommendation_reason: str | None
    source_ids: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseSourceContent:
    """One inspectable evidence source referenced by renal bands."""

    id: str
    evidence_level: ContentEvidenceLevel
    citation: str
    source_document: str
    source_version: str
    publication_date: date | None
    url: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseReviewContent:
    """Approval state and reviewer metadata without inferring eligibility."""

    status: ContentReviewStatus
    reviewed_content_version: str | None
    reviewer: str | None
    reviewer_role: str | None
    reviewed_on: date | None
    notes: str | None


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseContent:
    """One typed, validated renal-dose document for one exact key."""

    schema_version: str
    content_id: str
    content_version: str
    rule_id: str
    medication: RenalDoseMedicationContent
    regimen: RenalDoseRegimenContent
    supported_context: RenalDoseSupportedContext
    renal_domain: RenalContentInterval
    renal_bands: tuple[RenalDoseBandContent, ...]
    sources: tuple[RenalDoseSourceContent, ...]
    review: RenalDoseReviewContent
    limitations: tuple[str, ...]

    @property
    def key(self) -> RenalDoseContentKey:
        """Return the exact immutable repository key represented by this document."""

        return RenalDoseContentKey(
            medication_id=self.medication.id,
            regimen_id=self.regimen.id,
            content_version=self.content_version,
        )


@runtime_checkable
class RenalDoseContentRepository(Protocol):
    """Repository boundary for exact, explicitly versioned renal-dose content retrieval.

    Implementations must not normalize, alias, case-fold, trim, fuzzy-match, fall back to another
    regimen, or choose a version. Absence of the exact key is reported with ``ContentNotFound``.
    """

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        """Return content for ``key`` or raise ``ContentNotFound`` when it is absent."""

        ...
