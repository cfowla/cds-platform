"""Focused contract tests for the four Day 44 draft cefepime content documents."""

from __future__ import annotations

from pathlib import Path

import pytest

from cds.repositories.renal_content_schema import load_renal_dose_content_yaml


_CONTENT_DIRECTORY = (
    Path(__file__).parents[3] / "src" / "cds" / "content" / "renal"
)
_SOURCE_ID = "fda_dailymed_cefepime_for_injection_wgcc_spl_v17"
_CONTENT_VERSION = "1.0.0-draft"

_EXPECTED = {
    "cefepime_iv_500_mg_every_12_hours_over_30_minutes.yaml": {
        "regimen_id": "iv_500_mg_every_12_hours_over_30_minutes",
        "rule_id": "cefepime_iv_500_mg_every_12_hours_renal_rule",
        "base": ("500", "mg", "12"),
        "indication_ids": [
            "mild_moderate_uncomplicated_or_complicated_uti",
        ],
        "matrix": [
            ("below_11", "250", "mg", "24", "adjust_dose"),
            ("crcl_11_to_below_30", "500", "mg", "24", "adjust_dose"),
            ("crcl_30_to_60", "500", "mg", "24", "adjust_dose"),
            ("above_60", "500", "mg", "12", "continue"),
        ],
    },
    "cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml": {
        "regimen_id": "iv_1_g_every_12_hours_over_30_minutes",
        "rule_id": "cefepime_iv_1_g_every_12_hours_renal_rule",
        "base": ("1", "g", "12"),
        "indication_ids": [
            "mild_moderate_uncomplicated_or_complicated_uti",
            "moderate_severe_pneumonia",
        ],
        "matrix": [
            ("below_11", "250", "mg", "24", "adjust_dose"),
            ("crcl_11_to_below_30", "500", "mg", "24", "adjust_dose"),
            ("crcl_30_to_60", "1", "g", "24", "adjust_dose"),
            ("above_60", "1", "g", "12", "continue"),
        ],
    },
    "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml": {
        "regimen_id": "iv_2_g_every_12_hours_over_30_minutes",
        "rule_id": "cefepime_iv_2_g_every_12_hours_renal_rule",
        "base": ("2", "g", "12"),
        "indication_ids": [
            "moderate_severe_pneumonia",
            "severe_uncomplicated_or_complicated_uti",
            "moderate_severe_uncomplicated_skin_structure_infection",
            "complicated_intra_abdominal_infection_with_metronidazole",
        ],
        "matrix": [
            ("below_11", "500", "mg", "24", "adjust_dose"),
            ("crcl_11_to_below_30", "1", "g", "24", "adjust_dose"),
            ("crcl_30_to_60", "2", "g", "24", "adjust_dose"),
            ("above_60", "2", "g", "12", "continue"),
        ],
    },
    "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml": {
        "regimen_id": "iv_2_g_every_8_hours_over_30_minutes",
        "rule_id": "cefepime_iv_2_g_every_8_hours_renal_rule",
        "base": ("2", "g", "8"),
        "indication_ids": [
            "moderate_severe_pneumonia",
            "pseudomonas_aeruginosa_moderate_severe_pneumonia",
            "empiric_febrile_neutropenia",
            "complicated_intra_abdominal_infection_with_metronidazole",
            "pseudomonas_aeruginosa_complicated_intra_abdominal_infection_with_metronidazole",
        ],
        "matrix": [
            ("below_11", "1", "g", "24", "adjust_dose"),
            ("crcl_11_to_below_30", "2", "g", "24", "adjust_dose"),
            ("crcl_30_to_60", "2", "g", "12", "adjust_dose"),
            ("above_60", "2", "g", "8", "continue"),
        ],
    },
}


def _load(filename: str) -> dict[str, object]:
    path = _CONTENT_DIRECTORY / filename
    return load_renal_dose_content_yaml(path.read_text(encoding="utf-8"))


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_44_cefepime_documents_match_selected_exact_regimens(filename: str) -> None:
    expected = _EXPECTED[filename]
    document = _load(filename)

    assert document["content_id"] == f"renal_dose_cefepime_{expected['regimen_id']}"
    assert document["content_version"] == _CONTENT_VERSION
    assert document["rule_id"] == expected["rule_id"]
    assert document["medication"] == {"id": "cefepime", "display": "Cefepime"}

    regimen = document["regimen"]
    base_value, base_unit, base_interval = expected["base"]
    assert regimen["id"] == expected["regimen_id"]
    assert regimen["indication_ids"] == expected["indication_ids"]
    assert regimen["route_id"] == "iv"
    assert regimen["formulation_id"] == "powder_for_solution"
    assert regimen["base_dose"] == {"value": base_value, "unit": base_unit}
    assert regimen["frequency_interval"] == {"value": base_interval, "unit": "hours"}
    assert regimen["infusion_duration"] == {"value": "30", "unit": "minutes"}


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_44_cefepime_documents_preserve_complete_source_matrix(filename: str) -> None:
    expected = _EXPECTED[filename]
    document = _load(filename)

    actual = [
        (
            band["id"],
            band["recommendation"]["dose"]["value"],
            band["recommendation"]["dose"]["unit"],
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
    assert [band["lower"] for band in document["renal_bands"]] == [
        {"value": "0", "inclusive": False},
        {"value": "11", "inclusive": True},
        {"value": "30", "inclusive": True},
        {"value": "60", "inclusive": False},
    ]
    assert [band["upper"] for band in document["renal_bands"]] == [
        {"value": "11", "inclusive": False},
        {"value": "30", "inclusive": False},
        {"value": "60", "inclusive": True},
        None,
    ]


@pytest.mark.parametrize("filename", sorted(_EXPECTED))
def test_day_44_cefepime_documents_remain_draft_and_traceable(filename: str) -> None:
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

    assert len(document["sources"]) == 1
    source = document["sources"][0]
    assert source["id"] == _SOURCE_ID
    assert source["evidence_level"] == "guideline"
    assert source["publication_date"] == "2026-06-23"
    assert source["source_version"] == (
        "DailyMed SPL version 17; labeling revised 10/2022; "
        "DailyMed record updated 2026-06-23"
    )
    assert source["url"].endswith(
        "setid=5fd857e5-591f-44ca-80cf-fd903660b03c&version=17"
    )

    assert all(band["source_ids"] == [_SOURCE_ID] for band in document["renal_bands"])
    assert all(
        len(band["recommendation"]["monitoring"]) == 2
        for band in document["renal_bands"]
    )
    assert any("not for direct clinical use" in item for item in document["limitations"])
    assert any("Draft content is not eligible" in item for item in document["limitations"])


def test_source_display_units_are_preserved_without_hidden_conversion() -> None:
    one_gram = _load("cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml")
    two_gram = _load("cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml")

    assert one_gram["regimen"]["base_dose"] == {"value": "1", "unit": "g"}
    assert one_gram["renal_bands"][0]["recommendation"]["dose"] == {
        "value": "250",
        "unit": "mg",
    }
    assert two_gram["regimen"]["base_dose"] == {"value": "2", "unit": "g"}
    assert two_gram["renal_bands"][0]["recommendation"]["dose"] == {
        "value": "500",
        "unit": "mg",
    }
