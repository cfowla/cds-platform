"""Focused contract tests for the three Day 51 draft piperacillin–tazobactam documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml


_CONTENT_DIRECTORY = Path(__file__).parents[3] / "src" / "cds" / "content" / "renal"
_CONTENT_VERSION = "1.0.0-draft"
_STANDARD_SOURCE_ID = "fda_dailymed_piperacillin_tazobactam_wgcc_spl_v14"
_EXTENDED_SOURCE_ID = (
    "patel_2010_piperacillin_tazobactam_extended_infusion_renal_adjustment"
)
_TOP_LEVEL_KEYS = {
    "schema_version",
    "content_id",
    "content_version",
    "rule_id",
    "medication",
    "regimen",
    "supported_context",
    "renal_domain",
    "renal_bands",
    "sources",
    "review",
    "limitations",
}

_EXPECTED: dict[str, dict[str, Any]] = {
    "piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes.yaml": {
        "regimen_id": "standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes",
        "rule_id": (
            "piperacillin_tazobactam_standard_infusion_iv_3_375_g_every_6_hours_renal_rule"
        ),
        "base": ("3.375", "6", "30"),
        "formulation_id": "powder_for_solution",
        "indication_ids": [
            "adult_intra_abdominal_infection",
            "adult_skin_and_skin_structure_infection",
            "adult_female_pelvic_infection",
            "adult_moderate_community_acquired_pneumonia",
        ],
        "matrix": [
            ("below_20", "2.25", "8", "adjust_dose"),
            ("crcl_20_to_40", "2.25", "6", "adjust_dose"),
            ("above_40", "3.375", "6", "continue"),
        ],
        "lower": [
            {"value": "0", "inclusive": False},
            {"value": "20", "inclusive": True},
            {"value": "40", "inclusive": False},
        ],
        "upper": [
            {"value": "20", "inclusive": False},
            {"value": "40", "inclusive": True},
            None,
        ],
        "document_source_ids": [_STANDARD_SOURCE_ID],
        "band_source_ids": [_STANDARD_SOURCE_ID],
    },
    "piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes.yaml": {
        "regimen_id": "standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes",
        "rule_id": (
            "piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_renal_rule"
        ),
        "base": ("4.5", "6", "30"),
        "formulation_id": "powder_for_solution",
        "indication_ids": [
            "adult_nosocomial_pneumonia_initial_presumptive_with_aminoglycoside_context",
        ],
        "matrix": [
            ("below_20", "2.25", "6", "adjust_dose"),
            ("crcl_20_to_40", "3.375", "6", "adjust_dose"),
            ("above_40", "4.5", "6", "continue"),
        ],
        "lower": [
            {"value": "0", "inclusive": False},
            {"value": "20", "inclusive": True},
            {"value": "40", "inclusive": False},
        ],
        "upper": [
            {"value": "20", "inclusive": False},
            {"value": "40", "inclusive": True},
            None,
        ],
        "document_source_ids": [_STANDARD_SOURCE_ID],
        "band_source_ids": [_STANDARD_SOURCE_ID],
    },
    "piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes.yaml": {
        "regimen_id": "extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes",
        "rule_id": (
            "piperacillin_tazobactam_extended_infusion_iv_3_375_g_every_8_hours_renal_rule"
        ),
        "base": ("3.375", "8", "240"),
        "formulation_id": None,
        "indication_ids": ["hospitalized_serious_gram_negative_infection"],
        "matrix": [
            ("at_or_below_20", "3.375", "12", "adjust_dose"),
            ("above_20", "3.375", "8", "continue"),
        ],
        "lower": [
            {"value": "0", "inclusive": False},
            {"value": "20", "inclusive": False},
        ],
        "upper": [
            {"value": "20", "inclusive": True},
            None,
        ],
        "document_source_ids": [_EXTENDED_SOURCE_ID, _STANDARD_SOURCE_ID],
        "band_source_ids": [_EXTENDED_SOURCE_ID],
    },
}


def _load(filename: str) -> dict[str, Any]:
    path = _CONTENT_DIRECTORY / filename
    document = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(document, dict)
    return document


def _regimen_signature(document: dict[str, Any]) -> tuple[str, str, str, str, str, str]:
    regimen = document["regimen"]
    return (
        regimen["base_dose"]["value"],
        regimen["base_dose"]["unit"],
        regimen["frequency_interval"]["value"],
        regimen["frequency_interval"]["unit"],
        regimen["infusion_duration"]["value"],
        regimen["infusion_duration"]["unit"],
    )


def test_day_51_commits_only_the_three_selected_exact_documents() -> None:
    actual = {
        path.name
        for path in _CONTENT_DIRECTORY.glob("piperacillin_tazobactam_*.yaml")
    }

    assert actual == set(_EXPECTED)


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_51_documents_match_selected_exact_regimens(filename: str) -> None:
    expected = _EXPECTED[filename]
    document = _load(filename)
    regimen = document["regimen"]
    base_value, base_interval, infusion_duration = expected["base"]

    assert set(document) == _TOP_LEVEL_KEYS
    assert document["schema_version"] == "1"
    assert document["content_version"] == _CONTENT_VERSION
    assert document["content_id"] == (
        f"renal_dose_piperacillin_tazobactam_{expected['regimen_id']}"
    )
    assert document["rule_id"] == expected["rule_id"]
    assert document["medication"] == {
        "id": "piperacillin_tazobactam",
        "display": "Piperacillin–tazobactam",
    }

    assert regimen["id"] == expected["regimen_id"]
    assert regimen["indication_ids"] == expected["indication_ids"]
    assert regimen["route_id"] == "iv"
    assert regimen["formulation_id"] == expected["formulation_id"]
    assert regimen["base_dose"] == {"value": base_value, "unit": "g"}
    assert regimen["frequency_interval"] == {
        "value": base_interval,
        "unit": "hours",
    }
    assert regimen["infusion_duration"] == {
        "value": infusion_duration,
        "unit": "minutes",
    }


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_51_documents_preserve_complete_renal_matrices(filename: str) -> None:
    expected = _EXPECTED[filename]
    document = _load(filename)
    actual = [
        (
            band["id"],
            band["recommendation"]["dose"]["value"],
            band["recommendation"]["frequency_interval"]["value"],
            band["recommendation"]["action"],
        )
        for band in document["renal_bands"]
    ]

    assert actual == expected["matrix"]
    assert document["renal_domain"] == {
        "lower": {"value": "0", "inclusive": False},
        "upper": None,
    }
    assert [band["lower"] for band in document["renal_bands"]] == expected["lower"]
    assert [band["upper"] for band in document["renal_bands"]] == expected["upper"]
    assert all(
        band["recommendation"]["dose"]["unit"] == "g"
        for band in document["renal_bands"]
    )
    assert all(
        band["recommendation"]["infusion_duration"]
        == document["regimen"]["infusion_duration"]
        for band in document["renal_bands"]
    )


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_51_documents_remain_draft_and_traceable(filename: str) -> None:
    expected = _EXPECTED[filename]
    document = _load(filename)

    assert document["review"] == {
        "status": "draft",
        "reviewed_content_version": None,
        "reviewer": None,
        "reviewer_role": None,
        "reviewed_on": None,
        "notes": document["review"]["notes"],
    }
    assert "Independent review" in document["review"]["notes"]
    assert [source["id"] for source in document["sources"]] == expected[
        "document_source_ids"
    ]
    assert all(
        band["source_ids"] == expected["band_source_ids"]
        for band in document["renal_bands"]
    )
    assert all(
        len(band["recommendation"]["monitoring"]) == 4
        for band in document["renal_bands"]
    )
    assert any(
        "not for direct clinical use" in limitation
        for limitation in document["limitations"]
    )
    assert any(
        "Draft content is not eligible" in limitation
        for limitation in document["limitations"]
    )


@pytest.mark.parametrize(
    ("filename", "expected_source"),
    [
        (
            (
                "piperacillin_tazobactam_standard_infusion_iv_3_375_g_"
                "every_6_hours_over_30_minutes.yaml"
            ),
            {
                "id": _STANDARD_SOURCE_ID,
                "evidence_level": "guideline",
                "publication_date": "2026-06-24",
            },
        ),
        (
            "piperacillin_tazobactam_standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes.yaml",
            {
                "id": _STANDARD_SOURCE_ID,
                "evidence_level": "guideline",
                "publication_date": "2026-06-24",
            },
        ),
        (
            (
                "piperacillin_tazobactam_extended_infusion_iv_3_375_g_"
                "every_8_hours_over_240_minutes.yaml"
            ),
            {
                "id": _EXTENDED_SOURCE_ID,
                "evidence_level": "primary_literature",
                "publication_date": "2009-10-26",
            },
        ),
    ],
)
def test_day_51_documents_preserve_governing_source_provenance(
    filename: str,
    expected_source: dict[str, str],
) -> None:
    document = _load(filename)
    source = document["sources"][0]

    assert {key: source[key] for key in expected_source} == expected_source
    if source["id"] == _STANDARD_SOURCE_ID:
        assert "SPL version 14" in source["source_version"]
        assert "labeling revised 11/2025" in source["source_version"]
        assert "version 14 published 2026-07-03" in source["source_version"]
        assert source["url"].endswith(
            "setid=17a400ae-cbaa-4d07-95f4-c6917dfc0585&version=14"
        )
    else:
        assert "DOI 10.1128/AAC.00296-09" in source["source_version"]
        assert source["url"] == "https://doi.org/10.1128/AAC.00296-09"
        assert any(
            "DailyMed source is included only for product safety monitoring" in limitation
            for limitation in document["limitations"]
        )


@pytest.mark.parametrize(
    "unsupported_signature",
    [
        ("3.375", "g", "8", "hours", "30", "minutes"),
        ("3.375", "g", "12", "hours", "240", "minutes"),
        ("4.5", "g", "6", "hours", "240", "minutes"),
        ("4.5", "g", "8", "hours", "240", "minutes"),
    ],
)
def test_day_51_unsupported_variants_are_not_encoded(
    unsupported_signature: tuple[str, str, str, str, str, str],
) -> None:
    selected_signatures = {
        _regimen_signature(_load(filename))
        for filename in _EXPECTED
    }

    assert unsupported_signature not in selected_signatures