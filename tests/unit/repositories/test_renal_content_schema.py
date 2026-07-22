"""Focused tests for the closed version 1 renal-dose content schema."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import pytest

from cds.repositories.renal_content_schema import (
    ContentSchemaError,
    load_renal_dose_content_yaml,
    validate_renal_dose_content,
)


FIXTURE_PATH = (
    Path(__file__).parents[3]
    / "src"
    / "cds"
    / "content"
    / "renal"
    / "cefepime_synthetic_fixture.yaml"
)
Mutation = Callable[[dict[str, Any]], None]


def _valid_document() -> dict[str, Any]:
    return load_renal_dose_content_yaml(FIXTURE_PATH.read_text(encoding="utf-8"))


def _replace(path: tuple[str | int, ...], value: object) -> Mutation:
    def mutate(document: dict[str, Any]) -> None:
        target: Any = document
        for part in path[:-1]:
            target = target[part]
        target[path[-1]] = value

    return mutate


def _delete(path: tuple[str | int, ...]) -> Mutation:
    def mutate(document: dict[str, Any]) -> None:
        target: Any = document
        for part in path[:-1]:
            target = target[part]
        del target[path[-1]]

    return mutate


def _add_unknown(document: dict[str, Any]) -> None:
    document["unexpected"] = True


def _duplicate_band_id(document: dict[str, Any]) -> None:
    document["renal_bands"][1]["id"] = document["renal_bands"][0]["id"]


def _duplicate_source(document: dict[str, Any]) -> None:
    document["sources"].append(deepcopy(document["sources"][0]))


def _gap_bands(document: dict[str, Any]) -> None:
    document["renal_bands"][1]["lower"]["value"] = "51"


def _overlap_bands(document: dict[str, Any]) -> None:
    document["renal_bands"][1]["lower"]["value"] = "49"


def _both_include_shared_boundary(document: dict[str, Any]) -> None:
    document["renal_bands"][0]["upper"]["inclusive"] = True
    document["renal_bands"][1]["lower"]["inclusive"] = True


def _both_exclude_shared_boundary(document: dict[str, Any]) -> None:
    document["renal_bands"][0]["upper"]["inclusive"] = False
    document["renal_bands"][1]["lower"]["inclusive"] = False


def _reviewed_without_metadata(document: dict[str, Any]) -> None:
    document["review"]["status"] = "reviewed"


def _valid_reviewed_metadata(document: dict[str, Any]) -> None:
    document["review"].update(
        {
            "status": "reviewed",
            "reviewed_content_version": document["content_version"],
            "reviewer": "Synthetic reviewer",
            "reviewer_role": "Synthetic clinical content reviewer",
            "reviewed_on": "2026-07-22",
        }
    )


def test_day_37_fixture_passes_without_normalizing_values() -> None:
    document = _valid_document()

    assert document["schema_version"] == "1"
    assert document["regimen"]["base_dose"]["value"] == "1"
    assert document["renal_bands"][0]["upper"]["value"] == "50"
    assert document["review"]["status"] == "draft"


def test_yaml_loader_rejects_duplicate_mapping_keys() -> None:
    yaml_text = FIXTURE_PATH.read_text(encoding="utf-8").replace(
        'schema_version: "1"',
        'schema_version: "1"\nschema_version: "1"',
        1,
    )

    with pytest.raises(ContentSchemaError, match="duplicate YAML mapping key"):
        load_renal_dose_content_yaml(yaml_text)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_delete(("schema_version",)), "missing required key"),
        (_add_unknown, "unknown key"),
        (_replace(("medication",), []), "must be a mapping"),
        (_replace(("schema_version",), "2"), 'must be exactly "1"'),
        (_replace(("content_version",), ""), "must not be empty"),
        (_replace(("rule_id",), "Bad-Rule"), "must match"),
        (_replace(("medication", "id"), "vancomycin"), "not a supported"),
        (_replace(("content_id",), "renal_dose_wrong"), "must equal"),
        (_replace(("regimen", "display"), "<placeholder>"), "placeholder"),
        (_replace(("regimen", "indication_ids"), []), "at least 1"),
        (
            _replace(
                ("regimen", "indication_ids"),
                ["synthetic_fixture_indication", "synthetic_fixture_indication"],
            ),
            "duplicate identifier",
        ),
    ],
)
def test_rejects_closed_shape_identifier_and_required_field_errors(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_replace(("regimen", "base_dose", "value"), 1), "quoted decimal string"),
        (_replace(("regimen", "base_dose", "value"), "01"), "invalid decimal syntax"),
        (_replace(("regimen", "base_dose", "value"), "0"), "greater than zero"),
        (_replace(("regimen", "base_dose", "unit"), "mgs"), "unsupported dose unit"),
        (_replace(("regimen", "frequency_interval", "unit"), "hrs"), "unsupported time unit"),
        (_delete(("regimen", "base_dose", "unit")), "missing required key"),
        (_replace(("renal_domain", "lower", "value"), 0), "quoted decimal string"),
    ],
)
def test_rejects_invalid_clinical_decimal_and_unit_nodes(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_replace(("supported_context", "minimum_age_years"), "18"), "YAML integer 18"),
        (_replace(("supported_context", "minimum_age_years"), 17), "YAML integer 18"),
        (_replace(("supported_context", "renal_method"), "ckd_epi"), "cockcroft_gault"),
        (_replace(("supported_context", "renal_unit"), "mL/min/1.73m2"), "mL/min"),
        (_replace(("supported_context", "renal_function_stable"), False), "must be true"),
        (_replace(("supported_context", "renal_replacement_therapy"), True), "must be false"),
        (_replace(("supported_context", "limitations"), []), "at least 1"),
    ],
)
def test_rejects_content_that_broadens_the_supported_context(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_replace(("renal_bands",), []), "at least 1"),
        (_duplicate_band_id, "duplicate band identifier"),
        (_replace(("renal_bands", 0, "upper", "value"), "-1"), "lower boundary exceeds"),
        (_gap_bands, "creates a gap"),
        (_overlap_bands, "overlaps or is unsorted"),
        (_both_include_shared_boundary, "included by both"),
        (_both_exclude_shared_boundary, "excluded by both"),
        (_replace(("renal_bands", 0, "lower", "value"), "1"), "renal_domain.lower"),
        (
            _replace(("renal_bands", 1, "upper"), {"value": "100", "inclusive": True}),
            "renal_domain.upper",
        ),
    ],
)
def test_rejects_empty_unreachable_gapped_overlapping_or_out_of_domain_bands(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            _replace(("renal_bands", 0, "outcome"), "unknown"),
            "recommendation.*no_recommendation",
        ),
        (_replace(("renal_bands", 0, "recommendation"), None), "is required"),
        (
            _replace(("renal_bands", 0, "no_recommendation_reason"), "contradiction"),
            "must be null",
        ),
        (_replace(("renal_bands", 0, "recommendation", "action"), "unknown"), "implemented"),
        (_replace(("renal_bands", 0, "recommendation", "dose"), None), "must be a mapping"),
        (_replace(("renal_bands", 0, "recommendation", "route_id"), "po"), "match regimen"),
        (
            _replace(("renal_bands", 0, "recommendation", "frequency_interval", "unit"), "minutes"),
            "exact regimen interval unit",
        ),
    ],
)
def test_rejects_outcome_and_recommendation_contradictions(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


def test_accepts_explicit_no_recommendation_band() -> None:
    document = _valid_document()
    band = document["renal_bands"][0]
    band["outcome"] = "no_recommendation"
    band["recommendation"] = None
    band["no_recommendation_reason"] = "Synthetic fail-closed branch for testing only."

    validated = validate_renal_dose_content(document)

    assert validated["renal_bands"][0]["recommendation"] is None


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_replace(("renal_bands", 0, "source_ids", 0), "missing_source"), "unresolved source_ids"),
        (_duplicate_source, "duplicate source identifier"),
        (_replace(("sources", 0, "evidence_level"), "unknown"), "supported evidence level"),
        (_replace(("sources", 0, "citation"), ""), "must not be empty"),
        (_replace(("sources", 0, "publication_date"), "2026-02-30"), "valid calendar date"),
        (_replace(("sources", 0, "url"), "http://example.com/source"), "absolute HTTPS URL"),
    ],
)
def test_rejects_unresolved_or_invalid_source_metadata(
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


def test_accepts_complete_reviewed_metadata_for_the_same_content_version() -> None:
    document = _valid_document()
    _valid_reviewed_metadata(document)

    validated = validate_renal_dose_content(document)

    assert validated["review"]["status"] == "reviewed"
    assert validated["review"]["reviewed_content_version"] == validated["content_version"]


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (_reviewed_without_metadata, "must be a string"),
        (_replace(("review", "reviewer"), "Synthetic reviewer"), "draft content must have null"),
        (_replace(("review", "status"), "approved"), "draft, reviewed, or retired"),
    ],
)
def test_rejects_invalid_review_state_metadata(mutation: Mutation, message: str) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


def test_rejects_reviewed_version_mismatch() -> None:
    document = _valid_document()
    _valid_reviewed_metadata(document)
    document["review"]["reviewed_content_version"] = "different-version"

    with pytest.raises(ContentSchemaError, match="document content_version"):
        validate_renal_dose_content(document)
