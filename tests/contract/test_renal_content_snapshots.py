"""Review-oriented snapshots for all versioned renal-dose content documents."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_REPOSITORY_ROOT = Path(__file__).parents[2]
_CONTENT_DIRECTORY = _REPOSITORY_ROOT / "src" / "cds" / "content" / "renal"

_CONTEXT = {
    "minimum_age_years": 18,
    "renal_method": "cockcroft_gault",
    "renal_unit": "mL/min",
    "renal_function_stable": True,
    "renal_replacement_therapy": False,
}
_DOMAIN = {"lower": {"value": "0", "inclusive": False}, "upper": None}
_DRAFT_REVIEW = {
    "status": "draft",
    "reviewed_content_version": None,
    "reviewer": None,
    "reviewer_role": None,
    "reviewed_on": None,
}
_CEFEPIME_SOURCE = {
    "id": "fda_dailymed_cefepime_for_injection_wgcc_spl_v17",
    "evidence_level": "guideline",
    "source_version": (
        "DailyMed SPL version 17; labeling revised 10/2022; "
        "DailyMed record updated 2026-06-23"
    ),
    "publication_date": "2026-06-23",
}
_PIPERACILLIN_TAZOBACTAM_SOURCE = {
    "id": "fda_dailymed_piperacillin_tazobactam_wgcc_spl_v14",
    "evidence_level": "guideline",
    "source_version": (
        "DailyMed SPL version 14; labeling revised 11/2025; "
        "DailyMed record updated 2026-06-24; version 14 published 2026-07-03"
    ),
    "publication_date": "2026-06-24",
}
_EXTENDED_INFUSION_SOURCE = {
    "id": "patel_2010_piperacillin_tazobactam_extended_infusion_renal_adjustment",
    "evidence_level": "primary_literature",
    "source_version": (
        "Antimicrobial Agents and Chemotherapy 54(1):460-465; "
        "e-published 2009-10-26; DOI 10.1128/AAC.00296-09"
    ),
    "publication_date": "2009-10-26",
}
_FAMOTIDINE_SOURCE = {
    "id": "fda_dailymed_famotidine_sportpharm_spl_v1",
    "evidence_level": "guideline",
    "source_version": (
        "DailyMed SPL version 1; labeling revised 06/2026; "
        "DailyMed record updated 2026-06-26"
    ),
    "publication_date": "2026-06-26",
}


def _quantity(value: str, unit: str) -> dict[str, str]:
    return {"value": value, "unit": unit}


def _bound(value: str, inclusive: bool) -> dict[str, Any]:
    return {"value": value, "inclusive": inclusive}


def _band(
    band_id: str,
    lower: dict[str, Any],
    upper: dict[str, Any] | None,
    action: str,
    dose: dict[str, str],
    interval_hours: str,
    route_id: str,
    infusion_duration: dict[str, str] | None,
    source_ids: list[str],
) -> dict[str, Any]:
    return {
        "id": band_id,
        "lower": lower,
        "upper": upper,
        "outcome": "recommendation",
        "recommendation": {
            "action": action,
            "dose": dose,
            "route_id": route_id,
            "frequency_interval": _quantity(interval_hours, "hours"),
            "infusion_duration": infusion_duration,
        },
        "source_ids": source_ids,
    }


def _document(
    content_id: str,
    rule_id: str,
    medication: dict[str, str],
    regimen: dict[str, Any],
    renal_bands: list[dict[str, Any]],
    sources: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "content_id": content_id,
        "content_version": "1.0.0-draft",
        "rule_id": rule_id,
        "medication": medication,
        "regimen": regimen,
        "supported_context": _CONTEXT,
        "renal_domain": _DOMAIN,
        "renal_bands": renal_bands,
        "sources": sources,
        "review": _DRAFT_REVIEW,
    }


_CEFEPIME_BOUNDS = [
    ("below_11", _bound("0", False), _bound("11", False)),
    ("crcl_11_to_below_30", _bound("11", True), _bound("30", False)),
    ("crcl_30_to_60", _bound("30", True), _bound("60", True)),
    ("above_60", _bound("60", False), None),
]
_CEFEPIME_INFUSION = _quantity("30", "minutes")


def _cefepime_document(
    regimen_id: str,
    rule_id: str,
    base_dose: dict[str, str],
    base_interval: str,
    indication_ids: list[str],
    matrix: list[tuple[str, str, str, str]],
) -> dict[str, Any]:
    bands = [
        _band(
            band_id,
            lower,
            upper,
            action,
            _quantity(dose_value, dose_unit),
            interval,
            "iv",
            _CEFEPIME_INFUSION,
            [_CEFEPIME_SOURCE["id"]],
        )
        for (band_id, lower, upper), (dose_value, dose_unit, interval, action)
        in zip(_CEFEPIME_BOUNDS, matrix, strict=True)
    ]
    return _document(
        f"renal_dose_cefepime_{regimen_id}",
        rule_id,
        {"id": "cefepime", "display": "Cefepime"},
        {
            "id": regimen_id,
            "indication_ids": indication_ids,
            "route_id": "iv",
            "formulation_id": "powder_for_solution",
            "base_dose": base_dose,
            "frequency_interval": _quantity(base_interval, "hours"),
            "infusion_duration": _CEFEPIME_INFUSION,
        },
        bands,
        [_CEFEPIME_SOURCE],
    )


def _piperacillin_tazobactam_document(
    regimen_id: str,
    rule_id: str,
    base_dose: str,
    base_interval: str,
    infusion_minutes: str,
    formulation_id: str | None,
    indication_ids: list[str],
    matrix: list[
        tuple[str, dict[str, Any], dict[str, Any] | None, str, str, str]
    ],
    sources: list[dict[str, Any]],
    band_source_id: str,
) -> dict[str, Any]:
    infusion = _quantity(infusion_minutes, "minutes")
    bands = [
        _band(
            band_id,
            lower,
            upper,
            action,
            _quantity(dose_value, "g"),
            interval,
            "iv",
            infusion,
            [band_source_id],
        )
        for band_id, lower, upper, dose_value, interval, action in matrix
    ]
    return _document(
        f"renal_dose_piperacillin_tazobactam_{regimen_id}",
        rule_id,
        {"id": "piperacillin_tazobactam", "display": "Piperacillin–tazobactam"},
        {
            "id": regimen_id,
            "indication_ids": indication_ids,
            "route_id": "iv",
            "formulation_id": formulation_id,
            "base_dose": _quantity(base_dose, "g"),
            "frequency_interval": _quantity(base_interval, "hours"),
            "infusion_duration": infusion,
        },
        bands,
        sources,
    )


_EXPECTED_DOCUMENTS = {
    "cefepime_iv_500_mg_every_12_hours_over_30_minutes.yaml": _cefepime_document(
        "iv_500_mg_every_12_hours_over_30_minutes",
        "cefepime_iv_500_mg_every_12_hours_renal_rule",
        _quantity("500", "mg"),
        "12",
        ["mild_moderate_uncomplicated_or_complicated_uti"],
        [
            ("250", "mg", "24", "adjust_dose"),
            ("500", "mg", "24", "adjust_dose"),
            ("500", "mg", "24", "adjust_dose"),
            ("500", "mg", "12", "continue"),
        ],
    ),
    "cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml": _cefepime_document(
        "iv_1_g_every_12_hours_over_30_minutes",
        "cefepime_iv_1_g_every_12_hours_renal_rule",
        _quantity("1", "g"),
        "12",
        [
            "mild_moderate_uncomplicated_or_complicated_uti",
            "moderate_severe_pneumonia",
        ],
        [
            ("250", "mg", "24", "adjust_dose"),
            ("500", "mg", "24", "adjust_dose"),
            ("1", "g", "24", "adjust_dose"),
            ("1", "g", "12", "continue"),
        ],
    ),
    "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml": _cefepime_document(
        "iv_2_g_every_12_hours_over_30_minutes",
        "cefepime_iv_2_g_every_12_hours_renal_rule",
        _quantity("2", "g"),
        "12",
        [
            "moderate_severe_pneumonia",
            "severe_uncomplicated_or_complicated_uti",
            "moderate_severe_uncomplicated_skin_structure_infection",
            "complicated_intra_abdominal_infection_with_metronidazole",
        ],
        [
            ("500", "mg", "24", "adjust_dose"),
            ("1", "g", "24", "adjust_dose"),
            ("2", "g", "24", "adjust_dose"),
            ("2", "g", "12", "continue"),
        ],
    ),
    "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml": _cefepime_document(
        "iv_2_g_every_8_hours_over_30_minutes",
        "cefepime_iv_2_g_every_8_hours_renal_rule",
        _quantity("2", "g"),
        "8",
        [
            "moderate_severe_pneumonia",
            "pseudomonas_aeruginosa_moderate_severe_pneumonia",
            "empiric_febrile_neutropenia",
            "complicated_intra_abdominal_infection_with_metronidazole",
            (
                "pseudomonas_aeruginosa_complicated_intra_abdominal_"
                "infection_with_metronidazole"
            ),
        ],
        [
            ("1", "g", "24", "adjust_dose"),
            ("2", "g", "24", "adjust_dose"),
            ("2", "g", "12", "adjust_dose"),
            ("2", "g", "8", "continue"),
        ],
    ),
    (
        "piperacillin_tazobactam_standard_infusion_iv_3_375_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): _piperacillin_tazobactam_document(
        "standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes",
        (
            "piperacillin_tazobactam_standard_infusion_iv_3_375_g_"
            "every_6_hours_renal_rule"
        ),
        "3.375",
        "6",
        "30",
        "powder_for_solution",
        [
            "adult_intra_abdominal_infection",
            "adult_skin_and_skin_structure_infection",
            "adult_female_pelvic_infection",
            "adult_moderate_community_acquired_pneumonia",
        ],
        [
            (
                "below_20",
                _bound("0", False),
                _bound("20", False),
                "2.25",
                "8",
                "adjust_dose",
            ),
            (
                "crcl_20_to_40",
                _bound("20", True),
                _bound("40", True),
                "2.25",
                "6",
                "adjust_dose",
            ),
            ("above_40", _bound("40", False), None, "3.375", "6", "continue"),
        ],
        [_PIPERACILLIN_TAZOBACTAM_SOURCE],
        _PIPERACILLIN_TAZOBACTAM_SOURCE["id"],
    ),
    (
        "piperacillin_tazobactam_standard_infusion_iv_4_5_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): _piperacillin_tazobactam_document(
        "standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes",
        (
            "piperacillin_tazobactam_standard_infusion_iv_4_5_g_"
            "every_6_hours_renal_rule"
        ),
        "4.5",
        "6",
        "30",
        "powder_for_solution",
        ["adult_nosocomial_pneumonia_initial_presumptive_with_aminoglycoside_context"],
        [
            (
                "below_20",
                _bound("0", False),
                _bound("20", False),
                "2.25",
                "6",
                "adjust_dose",
            ),
            (
                "crcl_20_to_40",
                _bound("20", True),
                _bound("40", True),
                "3.375",
                "6",
                "adjust_dose",
            ),
            ("above_40", _bound("40", False), None, "4.5", "6", "continue"),
        ],
        [_PIPERACILLIN_TAZOBACTAM_SOURCE],
        _PIPERACILLIN_TAZOBACTAM_SOURCE["id"],
    ),
    (
        "piperacillin_tazobactam_extended_infusion_iv_3_375_g_"
        "every_8_hours_over_240_minutes.yaml"
    ): _piperacillin_tazobactam_document(
        "extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes",
        (
            "piperacillin_tazobactam_extended_infusion_iv_3_375_g_"
            "every_8_hours_renal_rule"
        ),
        "3.375",
        "8",
        "240",
        None,
        ["hospitalized_serious_gram_negative_infection"],
        [
            (
                "at_or_below_20",
                _bound("0", False),
                _bound("20", True),
                "3.375",
                "12",
                "adjust_dose",
            ),
            ("above_20", _bound("20", False), None, "3.375", "8", "continue"),
        ],
        [_EXTENDED_INFUSION_SOURCE, _PIPERACILLIN_TAZOBACTAM_SOURCE],
        _EXTENDED_INFUSION_SOURCE["id"],
    ),
    "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml": _document(
        (
            "renal_dose_famotidine_oral_film_coated_tablet_"
            "20_mg_every_12_hours"
        ),
        (
            "famotidine_oral_film_coated_tablet_20_mg_"
            "every_12_hours_renal_rule"
        ),
        {"id": "famotidine", "display": "Famotidine"},
        {
            "id": "oral_film_coated_tablet_20_mg_every_12_hours",
            "indication_ids": ["adult_symptomatic_nonerosive_gerd"],
            "route_id": "po",
            "formulation_id": "film_coated_tablet",
            "base_dose": _quantity("20", "mg"),
            "frequency_interval": _quantity("12", "hours"),
            "infusion_duration": None,
        },
        [
            _band(
                "below_30",
                _bound("0", False),
                _bound("30", False),
                "adjust_dose",
                _quantity("20", "mg"),
                "48",
                "po",
                None,
                [_FAMOTIDINE_SOURCE["id"]],
            ),
            _band(
                "crcl_30_to_below_60",
                _bound("30", True),
                _bound("60", False),
                "adjust_dose",
                _quantity("20", "mg"),
                "24",
                "po",
                None,
                [_FAMOTIDINE_SOURCE["id"]],
            ),
            _band(
                "at_or_above_60",
                _bound("60", True),
                None,
                "continue",
                _quantity("20", "mg"),
                "12",
                "po",
                None,
                [_FAMOTIDINE_SOURCE["id"]],
            ),
        ],
        [_FAMOTIDINE_SOURCE],
    ),
}

_REVIEW_FIELDS = (
    "status",
    "reviewed_content_version",
    "reviewer",
    "reviewer_role",
    "reviewed_on",
)
_SOURCE_FIELDS = ("id", "evidence_level", "source_version", "publication_date")
_SUPPORTED_CONTEXT_FIELDS = tuple(_CONTEXT)
_RECOMMENDATION_FIELDS = (
    "action",
    "dose",
    "route_id",
    "frequency_interval",
    "infusion_duration",
)


def _select(mapping: dict[str, Any], fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: mapping[field] for field in fields}


def _snapshot_document(document: dict[str, Any]) -> dict[str, Any]:
    regimen = document["regimen"]
    return {
        "schema_version": document["schema_version"],
        "content_id": document["content_id"],
        "content_version": document["content_version"],
        "rule_id": document["rule_id"],
        "medication": document["medication"],
        "regimen": {
            "id": regimen["id"],
            "indication_ids": regimen["indication_ids"],
            "route_id": regimen["route_id"],
            "formulation_id": regimen["formulation_id"],
            "base_dose": regimen["base_dose"],
            "frequency_interval": regimen["frequency_interval"],
            "infusion_duration": regimen["infusion_duration"],
        },
        "supported_context": _select(
            document["supported_context"],
            _SUPPORTED_CONTEXT_FIELDS,
        ),
        "renal_domain": document["renal_domain"],
        "renal_bands": [
            {
                "id": band["id"],
                "lower": band["lower"],
                "upper": band["upper"],
                "outcome": band["outcome"],
                "recommendation": _select(
                    band["recommendation"],
                    _RECOMMENDATION_FIELDS,
                ),
                "source_ids": band["source_ids"],
            }
            for band in document["renal_bands"]
        ],
        "sources": [_select(source, _SOURCE_FIELDS) for source in document["sources"]],
        "review": _select(document["review"], _REVIEW_FIELDS),
    }


def _load_actual_documents() -> dict[str, Any]:
    documents: dict[str, Any] = {}
    for path in sorted(_CONTENT_DIRECTORY.glob("*.yaml")):
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(document, dict), f"{path.name} must contain a YAML mapping"
        documents[path.name] = _snapshot_document(document)
    return documents


def test_renal_content_matches_review_snapshot() -> None:
    """Any selected clinical-content change must produce an inspectable diff."""

    assert _load_actual_documents() == _EXPECTED_DOCUMENTS


def test_snapshot_does_not_mark_draft_content_as_reviewed() -> None:
    """Software snapshot coverage must not imply independent clinical approval."""

    documents = _load_actual_documents()
    assert documents
    for document in documents.values():
        assert document["content_version"].endswith("-draft")
        assert document["review"] == _DRAFT_REVIEW
