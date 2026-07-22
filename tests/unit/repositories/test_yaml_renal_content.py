"""Focused tests for the YAML-backed renal-dose content repository."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from cds.domain.exceptions import ContentNotFound
from cds.repositories.renal_content import (
    RenalDoseContentKey,
    RenalDoseContentRepository,
)
from cds.repositories.renal_content_schema import ContentSchemaError
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


def test_yaml_repository_satisfies_repository_protocol() -> None:
    repository = YamlRenalDoseContentRepository([_FIXTURE_PATH])

    assert isinstance(repository, RenalDoseContentRepository)


def test_yaml_repository_loads_validated_fixture_into_typed_content() -> None:
    repository = YamlRenalDoseContentRepository([_FIXTURE_PATH])

    content = repository.get(_EXPECTED_KEY)

    assert content.key == _EXPECTED_KEY
    assert content.regimen.base_dose.value == Decimal("1")
    assert content.regimen.indication_ids == ("synthetic_fixture_indication",)
    assert content.renal_domain.lower is not None
    assert content.renal_domain.lower.value == Decimal("0")
    assert content.renal_bands[0].upper is not None
    assert content.renal_bands[0].upper.value == Decimal("50")
    assert content.renal_bands[0].recommendation is not None
    assert content.renal_bands[0].recommendation.frequency_interval is not None
    assert content.renal_bands[0].recommendation.frequency_interval.value == Decimal("2")
    assert content.review.status == "draft"


def test_yaml_repository_converts_validated_date_strings(tmp_path: Path) -> None:
    dated_path = tmp_path / "dated.yaml"
    dated_path.write_text(
        _FIXTURE_PATH.read_text(encoding="utf-8").replace(
            "publication_date: null",
            'publication_date: "2026-07-22"',
        ),
        encoding="utf-8",
    )

    content = YamlRenalDoseContentRepository([dated_path]).get(_EXPECTED_KEY)

    assert content.sources[0].publication_date == date(2026, 7, 22)


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
            content_version="1.0.0",
        ),
    ],
)
def test_yaml_repository_requires_the_exact_explicit_key(key: RenalDoseContentKey) -> None:
    repository = YamlRenalDoseContentRepository([_FIXTURE_PATH])

    with pytest.raises(ContentNotFound, match="exact key"):
        repository.get(key)


def test_yaml_repository_rejects_duplicate_exact_keys(tmp_path: Path) -> None:
    first = tmp_path / "first.yaml"
    second = tmp_path / "second.yaml"
    fixture_text = _FIXTURE_PATH.read_text(encoding="utf-8")
    first.write_text(fixture_text, encoding="utf-8")
    second.write_text(fixture_text, encoding="utf-8")

    with pytest.raises(ValueError, match="duplicate renal-dose content key"):
        YamlRenalDoseContentRepository([first, second])


def test_yaml_repository_fails_closed_on_invalid_content(tmp_path: Path) -> None:
    invalid_path = tmp_path / "invalid.yaml"
    invalid_path.write_text('schema_version: "1"\n', encoding="utf-8")

    with pytest.raises(ContentSchemaError, match="missing required key"):
        YamlRenalDoseContentRepository([invalid_path])


def test_yaml_repository_reports_a_missing_supplied_file(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.yaml"

    with pytest.raises(ContentNotFound, match="content file not found"):
        YamlRenalDoseContentRepository([missing_path])


def test_yaml_repository_reads_files_only_during_construction(tmp_path: Path) -> None:
    copied_path = tmp_path / "fixture.yaml"
    copied_path.write_text(_FIXTURE_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    repository = YamlRenalDoseContentRepository([copied_path])
    copied_path.unlink()

    assert repository.get(_EXPECTED_KEY).key == _EXPECTED_KEY


def test_yaml_repository_copies_a_one_shot_path_iterable() -> None:
    repository = YamlRenalDoseContentRepository(path for path in [_FIXTURE_PATH])

    assert repository.get(_EXPECTED_KEY).key == _EXPECTED_KEY
