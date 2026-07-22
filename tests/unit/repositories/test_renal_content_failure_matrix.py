"""Day 42 failure matrix across renal content validation and repositories."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Callable

import pytest
import yaml

from cds.domain.exceptions import ContentNotFound
from cds.repositories.renal_content import (
    InMemoryRenalDoseContentRepository,
    RenalDoseContentKey,
    RenalDoseContentRepository,
)
from cds.repositories.renal_content_schema import (
    ContentSchemaError,
    load_renal_dose_content_yaml,
    validate_renal_dose_content,
)
from cds.repositories.yaml_renal_content import YamlRenalDoseContentRepository

_FIXTURE_PATH = (
    Path(__file__).parents[3]
    / "src"
    / "cds"
    / "content"
    / "renal"
    / "cefepime_synthetic_fixture.yaml"
)
_EXPECTED_KEY = RenalDoseContentKey(
    medication_id="cefepime",
    regimen_id="synthetic_fixture_iv_regimen",
    content_version="0.1.0-draft",
)
Mutation = Callable[[dict[str, Any]], None]


def _valid_document() -> dict[str, Any]:
    return load_renal_dose_content_yaml(_FIXTURE_PATH.read_text(encoding="utf-8"))


def _missing_required_key(document: dict[str, Any]) -> None:
    del document["sources"]


def _invalid_unit(document: dict[str, Any]) -> None:
    document["regimen"]["base_dose"]["unit"] = "mgs"


def _gap(document: dict[str, Any]) -> None:
    document["renal_bands"][1]["lower"]["value"] = "51"


def _overlap(document: dict[str, Any]) -> None:
    document["renal_bands"][1]["lower"]["value"] = "49"


def _reviewed_version_mismatch(document: dict[str, Any]) -> None:
    document["review"].update(
        {
            "status": "reviewed",
            "reviewed_content_version": "different-version",
            "reviewer": "Synthetic reviewer",
            "reviewer_role": "Synthetic clinical content reviewer",
            "reviewed_on": "2026-07-22",
        }
    )


_SCHEMA_FAILURES: tuple[tuple[str, Mutation, str], ...] = (
    ("missing-key", _missing_required_key, "missing required key"),
    ("invalid-unit", _invalid_unit, "unsupported dose unit"),
    ("gap", _gap, "creates a gap"),
    ("overlap", _overlap, "overlaps or is unsorted"),
    ("reviewed-version-mismatch", _reviewed_version_mismatch, "document content_version"),
)


@pytest.mark.parametrize(
    ("_case", "mutation", "message"),
    _SCHEMA_FAILURES,
    ids=[case[0] for case in _SCHEMA_FAILURES],
)
def test_schema_failure_matrix(
    _case: str,
    mutation: Mutation,
    message: str,
) -> None:
    document = _valid_document()
    mutation(document)

    with pytest.raises(ContentSchemaError, match=message):
        validate_renal_dose_content(document)


@pytest.mark.parametrize(
    ("yaml_text", "message"),
    [
        ('schema_version: "1"\nregimen: [\n', "invalid YAML"),
        (
            _FIXTURE_PATH.read_text(encoding="utf-8").replace(
                'schema_version: "1"',
                'schema_version: "1"\nschema_version: "1"',
                1,
            ),
            "duplicate YAML mapping key",
        ),
    ],
    ids=["malformed-yaml", "duplicate-mapping-key"],
)
def test_yaml_loader_rejects_malformed_or_duplicate_key_content(
    yaml_text: str,
    message: str,
) -> None:
    with pytest.raises(ContentSchemaError, match=message):
        load_renal_dose_content_yaml(yaml_text)


@pytest.mark.parametrize(
    ("_case", "mutation", "message"),
    _SCHEMA_FAILURES,
    ids=[case[0] for case in _SCHEMA_FAILURES],
)
def test_yaml_repository_propagates_schema_failures(
    tmp_path: Path,
    _case: str,
    mutation: Mutation,
    message: str,
) -> None:
    document = deepcopy(_valid_document())
    mutation(document)
    invalid_path = tmp_path / f"{_case}.yaml"
    invalid_path.write_text(yaml.safe_dump(document, sort_keys=False), encoding="utf-8")

    with pytest.raises(ContentSchemaError, match=message):
        YamlRenalDoseContentRepository([invalid_path])


def _repository_factories() -> tuple[
    tuple[str, Callable[[], RenalDoseContentRepository]],
    ...,
]:
    typed_content = YamlRenalDoseContentRepository([_FIXTURE_PATH]).get(_EXPECTED_KEY)
    return (
        (
            "in-memory",
            lambda: InMemoryRenalDoseContentRepository([typed_content]),
        ),
        (
            "yaml",
            lambda: YamlRenalDoseContentRepository([_FIXTURE_PATH]),
        ),
    )


@pytest.mark.parametrize(
    "key",
    [
        RenalDoseContentKey(
            medication_id="cefepime",
            regimen_id="unsupported_regimen",
            content_version="0.1.0-draft",
        ),
        RenalDoseContentKey(
            medication_id="cefepime",
            regimen_id="synthetic_fixture_iv_regimen",
            content_version="different-version",
        ),
    ],
    ids=["unsupported-regimen", "content-version-mismatch"],
)
@pytest.mark.parametrize(
    ("_repository_name", "repository_factory"),
    _repository_factories(),
    ids=[item[0] for item in _repository_factories()],
)
def test_repositories_fail_closed_on_absent_exact_keys(
    _repository_name: str,
    repository_factory: Callable[[], RenalDoseContentRepository],
    key: RenalDoseContentKey,
) -> None:
    repository = repository_factory()

    with pytest.raises(ContentNotFound, match="exact key"):
        repository.get(key)


def test_yaml_repository_reports_a_missing_supplied_file(tmp_path: Path) -> None:
    with pytest.raises(ContentNotFound, match="content file not found"):
        YamlRenalDoseContentRepository([tmp_path / "missing.yaml"])


def test_both_repositories_reject_duplicate_exact_keys(tmp_path: Path) -> None:
    typed_content = YamlRenalDoseContentRepository([_FIXTURE_PATH]).get(_EXPECTED_KEY)
    with pytest.raises(ValueError, match="duplicate renal-dose content key"):
        InMemoryRenalDoseContentRepository([typed_content, typed_content])

    fixture_text = _FIXTURE_PATH.read_text(encoding="utf-8")
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    first.write_text(fixture_text, encoding="utf-8")
    second.write_text(fixture_text, encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate renal-dose content key"):
        YamlRenalDoseContentRepository([first, second])


def test_unreviewed_content_remains_explicit_without_repository_eligibility_filtering() -> None:
    yaml_content = YamlRenalDoseContentRepository([_FIXTURE_PATH]).get(_EXPECTED_KEY)
    in_memory_content = InMemoryRenalDoseContentRepository([yaml_content]).get(_EXPECTED_KEY)

    assert yaml_content.review.status == "draft"
    assert in_memory_content.review.status == "draft"
    assert in_memory_content is yaml_content
