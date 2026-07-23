"""Focused contract tests for the Day 54 draft famotidine content document."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

_CONTENT_DIRECTORY = Path(__file__).parents[3] / "src" / "cds" / "content" / "renal"
_FILENAME = "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml"
_SOURCE_ID = "fda_dailymed_famotidine_sportpharm_spl_v1"
_TOP_LEVEL_KEYS = {
    "schema_version", "content_id", "content_version", "rule_id", "medication",
    "regimen", "supported_context", "renal_domain", "renal_bands", "sources",
    "review", "limitations",
}


def _load() -> dict[str, Any]:
    document = yaml.safe_load((_CONTENT_DIRECTORY / _FILENAME).read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def _signature(document: dict[str, Any]) -> tuple[str, str, str, str, Any]:
    regimen = document["regimen"]
    return (
        regimen["route_id"], regimen["formulation_id"],
        regimen["base_dose"]["value"], regimen["frequency_interval"]["value"],
        regimen["infusion_duration"],
    )


def test_day_54_commits_only_the_selected_famotidine_document() -> None:
    actual = {path.name for path in _CONTENT_DIRECTORY.glob("famotidine_*.yaml")}
    assert actual == {_FILENAME}


def test_day_54_document_matches_the_exact_selected_regimen() -> None:
    document = _load()
    assert set(document) == _TOP_LEVEL_KEYS
    assert document["schema_version"] == "1"
    assert document["content_version"] == "1.0.0-draft"
    assert document["content_id"] == "renal_dose_famotidine_oral_film_coated_tablet_20_mg_every_12_hours"
    assert document["rule_id"] == "famotidine_oral_film_coated_tablet_20_mg_every_12_hours_renal_rule"
    assert document["medication"] == {"id": "famotidine", "display": "Famotidine"}
    regimen = document["regimen"]
    assert regimen["id"] == "oral_film_coated_tablet_20_mg_every_12_hours"
    assert regimen["indication_ids"] == ["adult_symptomatic_nonerosive_gerd"]
    assert regimen["route_id"] == "po"
    assert regimen["formulation_id"] == "film_coated_tablet"
    assert regimen["base_dose"] == {"value": "20", "unit": "mg"}
    assert regimen["frequency_interval"] == {"value": "12", "unit": "hours"}
    assert regimen["infusion_duration"] is None


def test_day_54_document_preserves_the_complete_unrounded_renal_partition() -> None:
    document = _load()
    assert document["renal_domain"] == {"lower": {"value": "0", "inclusive": False}, "upper": None}
    assert [band["id"] for band in document["renal_bands"]] == [
        "below_30", "crcl_30_to_below_60", "at_or_above_60"
    ]
    assert [band["lower"] for band in document["renal_bands"]] == [
        {"value": "0", "inclusive": False},
        {"value": "30", "inclusive": True},
        {"value": "60", "inclusive": True},
    ]
    assert [band["upper"] for band in document["renal_bands"]] == [
        {"value": "30", "inclusive": False},
        {"value": "60", "inclusive": False},
        None,
    ]
    assert [
        (band["recommendation"]["dose"]["value"],
         band["recommendation"]["frequency_interval"]["value"],
         band["recommendation"]["action"])
        for band in document["renal_bands"]
    ] == [("20", "48", "adjust_dose"), ("20", "24", "adjust_dose"), ("20", "12", "continue")]
    assert all(band["recommendation"]["dose"]["unit"] == "mg" for band in document["renal_bands"])
    assert all(band["recommendation"]["frequency_interval"]["unit"] == "hours" for band in document["renal_bands"])
    assert all(band["recommendation"]["infusion_duration"] is None for band in document["renal_bands"])


def test_day_54_document_remains_draft_and_traceable() -> None:
    document = _load()
    assert document["review"] == {
        "status": "draft", "reviewed_content_version": None, "reviewer": None,
        "reviewer_role": None, "reviewed_on": None, "notes": document["review"]["notes"],
    }
    assert "Independent review" in document["review"]["notes"]
    assert all(band["source_ids"] == [_SOURCE_ID] for band in document["renal_bands"])
    assert all(len(band["recommendation"]["monitoring"]) == 3 for band in document["renal_bands"])
    assert any("not for direct clinical use" in item for item in document["limitations"])
    assert any("Draft content is not eligible" in item for item in document["limitations"])


def test_day_54_document_preserves_selected_source_and_version() -> None:
    source = _load()["sources"][0]
    assert source["id"] == _SOURCE_ID
    assert source["evidence_level"] == "guideline"
    assert source["publication_date"] == "2026-06-26"
    assert "SPL version 1" in source["source_version"]
    assert "labeling revised 06/2026" in source["source_version"]
    assert source["url"].endswith("setid=4421ceb7-a114-436c-871a-7bc5444f8154&version=1")
    assert any("repackaged FDA-approved label" in item for item in _load()["limitations"])


@pytest.mark.parametrize(
    "unsupported_signature",
    [
        ("po", "oral_suspension", "20", "12", None),
        ("iv", "solution_for_injection", "20", "12", None),
        ("po", "film_coated_tablet", "10", "24", None),
        ("po", "film_coated_tablet", "40", "24", None),
    ],
)
def test_day_54_unsupported_formulations_and_regimens_are_not_encoded(
    unsupported_signature: tuple[str, str, str, str, Any],
) -> None:
    assert _signature(_load()) != unsupported_signature


def test_day_54_scope_exclusions_are_explicit() -> None:
    text = " ".join(_load()["limitations"] + _load()["supported_context"]["limitations"]).lower()
    for required in ("oral suspension", "intravenous", "10 mg", "other indications", "unstable renal function", "dialysis"):
        assert required in text
