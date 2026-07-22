"""Focused contract tests for typed renal content and repository implementations."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
import inspect

import pytest

from cds.domain.exceptions import ContentNotFound
from cds.repositories.renal_content import (
    ContentReviewStatus,
    InMemoryRenalDoseContentRepository,
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


def _content(
    *,
    medication_id: str = "cefepime",
    regimen_id: str = "synthetic_fixture_iv_regimen",
    content_version: str = "0.1.0-draft",
    review_status: ContentReviewStatus = "draft",
) -> RenalDoseContent:
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
        content_id=f"renal_dose_{medication_id}_{regimen_id}",
        content_version=content_version,
        rule_id=f"{medication_id}_synthetic_fixture_rule",
        medication=RenalDoseMedicationContent(id=medication_id, display="Synthetic medication"),
        regimen=RenalDoseRegimenContent(
            id=regimen_id,
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


def test_in_memory_repository_satisfies_repository_protocol() -> None:
    repository = InMemoryRenalDoseContentRepository([_content()])

    assert isinstance(repository, RenalDoseContentRepository)


def test_in_memory_repository_returns_only_the_exact_requested_document() -> None:
    content = _content()
    repository: RenalDoseContentRepository = InMemoryRenalDoseContentRepository([content])

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
    repository = InMemoryRenalDoseContentRepository([_content()])

    with pytest.raises(ContentNotFound, match="exact key"):
        repository.get(key)


def test_empty_in_memory_repository_raises_content_not_found() -> None:
    key = _content().key
    repository = InMemoryRenalDoseContentRepository()

    with pytest.raises(ContentNotFound, match="exact key"):
        repository.get(key)


def test_in_memory_repository_rejects_duplicate_exact_keys() -> None:
    first = _content(review_status="draft")
    duplicate = _content(review_status="retired")

    with pytest.raises(ValueError, match="duplicate renal-dose content key"):
        InMemoryRenalDoseContentRepository([first, duplicate])


def test_in_memory_repository_stores_multiple_explicit_versions_without_selecting_one() -> None:
    draft = _content(content_version="0.1.0-draft")
    reviewed = _content(content_version="1.0.0", review_status="reviewed")
    repository = InMemoryRenalDoseContentRepository([draft, reviewed])

    assert repository.get(draft.key) is draft
    assert repository.get(reviewed.key) is reviewed


def test_in_memory_repository_copies_a_one_shot_input_iterable() -> None:
    content = _content()
    repository = InMemoryRenalDoseContentRepository(item for item in [content])

    assert repository.get(content.key) is content


def test_review_state_is_represented_without_automatic_version_selection_or_eligibility() -> None:
    draft = _content(review_status="draft")
    retired = _content(review_status="retired")

    assert draft.review.status == "draft"
    assert retired.review.status == "retired"
    assert draft.key == retired.key
