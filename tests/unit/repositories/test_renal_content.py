"""Focused contract tests for typed renal content and its repository interface."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import inspect

import pytest

from cds.domain.exceptions import ContentNotFound
from cds.repositories.renal_content import (
    ContentReviewStatus,
    RenalContentEndpoint,
    RenalContentInterval,
    RenalDoseBandContent,
    RenalDoseContent,
    RenalDoseContentKey,
    RenalDoseContentRepository,
    RenalDoseMedicationContent,
    RenalDoseQuantity,
    RenalDoseRecommendationContent,
    RenalDoseRegimenContent,
    RenalDoseReviewContent,
    RenalDoseSourceContent,
    RenalDoseSupportedContext,
)


def _content(*, review_status: ContentReviewStatus = "draft") -> RenalDoseContent:
    version = "0.1.0-draft"
    review = RenalDoseReviewContent(
        status=review_status,
        reviewed_content_version=None,
        reviewer=None,
        reviewer_role=None,
        reviewed_on=None,
        notes="Synthetic fixture only; not clinical guidance.",
    )
    return RenalDoseContent(
        schema_version="1",
        content_id="renal_dose_cefepime_synthetic_fixture_iv_regimen",
        content_version=version,
        rule_id="cefepime_synthetic_fixture_rule",
        medication=RenalDoseMedicationContent(id="cefepime", display="Cefepime"),
        regimen=RenalDoseRegimenContent(
            id="synthetic_fixture_iv_regimen",
            display="Synthetic fixture IV regimen — not clinical guidance",
            indication_ids=("synthetic_fixture_indication",),
            route_id="iv",
            formulation_id="injectable",
            base_dose=RenalDoseQuantity(value=Decimal("1"), unit="mg"),
            frequency_interval=RenalDoseQuantity(value=Decimal("1"), unit="hours"),
            infusion_duration=RenalDoseQuantity(value=Decimal("1"), unit="minutes"),
        ),
        supported_context=RenalDoseSupportedContext(
            minimum_age_years=18,
            renal_method="cockcroft_gault",
            renal_unit="mL/min",
            renal_function_stable=True,
            renal_replacement_therapy=False,
            limitations=("Synthetic software fixture only.",),
        ),
        renal_domain=RenalContentInterval(
            lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
            upper=None,
        ),
        renal_bands=(
            RenalDoseBandContent(
                id="synthetic_fixture_band",
                lower=RenalContentEndpoint(value=Decimal("0"), inclusive=False),
                upper=None,
                outcome="recommendation",
                recommendation=RenalDoseRecommendationContent(
                    action="continue",
                    dose=RenalDoseQuantity(value=Decimal("1"), unit="mg"),
                    route_id="iv",
                    frequency_interval=RenalDoseQuantity(value=Decimal("1"), unit="hours"),
                    infusion_duration=RenalDoseQuantity(value=Decimal("1"), unit="minutes"),
                    rationale="Synthetic branch for repository contract testing only.",
                    monitoring=("Synthetic monitoring text.",),
                ),
                no_recommendation_reason=None,
                source_ids=("synthetic_fixture_source",),
                limitations=(),
            ),
        ),
        sources=(
            RenalDoseSourceContent(
                id="synthetic_fixture_source",
                evidence_level="expert_opinion",
                citation="Synthetic source with no clinical authority.",
                source_document="Synthetic fixture specification",
                source_version="1",
                publication_date=date(2026, 7, 22),
                url=None,
            ),
        ),
        review=review,
        limitations=("Prototype only — not for direct clinical use.",),
    )


class _ExactRepository:
    def __init__(self, content: RenalDoseContent) -> None:
        self._content = content

    def get(self, key: RenalDoseContentKey) -> RenalDoseContent:
        if key != self._content.key:
            raise ContentNotFound(f"renal-dose content not found for exact key {key!r}")
        return self._content


def test_typed_content_preserves_exact_decimal_units_version_and_review_state() -> None:
    content = _content()

    assert content.regimen.base_dose.value == Decimal("1")
    assert content.regimen.base_dose.unit == "mg"
    assert content.content_version == "0.1.0-draft"
    assert content.review.status == "draft"
    assert content.renal_domain.upper is None
    assert content.regimen.indication_ids == ("synthetic_fixture_indication",)


def test_content_key_is_exact_and_derived_without_normalization() -> None:
    content = _content()

    assert content.key == RenalDoseContentKey(
        medication_id="cefepime",
        regimen_id="synthetic_fixture_iv_regimen",
        content_version="0.1.0-draft",
    )
    assert content.key != RenalDoseContentKey(
        medication_id="Cefepime",
        regimen_id="synthetic_fixture_iv_regimen",
        content_version="0.1.0-draft",
    )
    assert content.key != RenalDoseContentKey(
        medication_id="cefepime",
        regimen_id="synthetic_fixture_iv_regimen ",
        content_version="0.1.0-draft",
    )


def test_repository_contract_requires_an_explicit_versioned_key() -> None:
    signature = inspect.signature(RenalDoseContentRepository.get)

    assert tuple(signature.parameters) == ("self", "key")
    assert signature.parameters["key"].default is inspect.Parameter.empty


def test_structural_implementation_satisfies_repository_protocol() -> None:
    repository = _ExactRepository(_content())

    assert isinstance(repository, RenalDoseContentRepository)


def test_repository_returns_only_the_exact_requested_document() -> None:
    content = _content()
    repository: RenalDoseContentRepository = _ExactRepository(content)

    assert repository.get(content.key) is content


@pytest.mark.parametrize(
    "key",
    [
        RenalDoseContentKey(
            medication_id="Cefepime",
            regimen_id="synthetic_fixture_iv_regimen",
            content_version="0.1.0-draft",
        ),
        RenalDoseContentKey(
            medication_id="cefepime",
            regimen_id="synthetic_fixture_iv_regimen ",
            content_version="0.1.0-draft",
        ),
        RenalDoseContentKey(
            medication_id="cefepime",
            regimen_id="synthetic_fixture_iv_regimen",
            content_version="0.1.0",
        ),
    ],
)
def test_absent_exact_key_raises_content_not_found_without_fallback(
    key: RenalDoseContentKey,
) -> None:
    repository = _ExactRepository(_content())

    with pytest.raises(ContentNotFound):
        repository.get(key)


def test_review_state_is_represented_without_automatic_version_selection_or_eligibility() -> None:
    draft = _content(review_status="draft")
    retired = _content(review_status="retired")

    assert draft.review.status == "draft"
    assert retired.review.status == "retired"
    assert draft.key == retired.key
