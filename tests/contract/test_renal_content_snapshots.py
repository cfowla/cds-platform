"""Review-oriented snapshots for explicitly selected clinical-content documents."""

from __future__ import annotations

from hashlib import sha1
from pathlib import Path
from typing import Any

import yaml

_REPOSITORY_ROOT = Path(__file__).parents[2]
_CONTENT_DIRECTORY = _REPOSITORY_ROOT / "src" / "cds" / "content" / "renal"

# Git blob identities intentionally protect each complete selected document, including clinical
# facts, source transcription, renal bands, limitations, comments, and review metadata. Update one
# identity only after reviewing the corresponding file diff.
_EXPECTED_SELECTED_BLOBS = {
    "cefepime_iv_500_mg_every_12_hours_over_30_minutes.yaml": (
        "1ae0f27a5a5008d0d8f2070c71107b907d97153a"
    ),
    "cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml": (
        "c126935224f8988a8be7ba26c3f46bad6632d335"
    ),
    "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml": (
        "750a72ee6acbf71c2faa041c1f20f5cd7b7fa8e9"
    ),
    "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml": (
        "3ed7eaa2062e5f0cfaa62cf2f1c150df3763a0b9"
    ),
    (
        "piperacillin_tazobactam_standard_infusion_iv_3_375_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): "fd12a44ae6927aeb4e234d3fc9d4db0d59848fcd",
    (
        "piperacillin_tazobactam_standard_infusion_iv_4_5_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): "4e4a04c1bc4fede52a97cb5b4b20814c124dd2ee",
    (
        "piperacillin_tazobactam_extended_infusion_iv_3_375_g_"
        "every_8_hours_over_240_minutes.yaml"
    ): "37ba49e3facbca8a6539f038a8b35837b629e6a5",
    "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml": (
        "7600bda8dffdb54972ae351b651bc03889ad76e1"
    ),
}

_EXPECTED_REVIEW = {
    "status": "reviewed",
    "reviewed_content_version": "1.0.0-draft",
    "reviewer": "Connor Fowler, PharmD",
    "reviewer_role": "independent qualified clinical-content reviewer",
    "reviewed_on": "2026-07-26",
}


def _git_blob_sha(payload: bytes) -> str:
    header = f"blob {len(payload)}\0".encode()
    return sha1(header + payload, usedforsecurity=False).hexdigest()


def _load_selected_documents() -> dict[str, dict[str, Any]]:
    documents: dict[str, dict[str, Any]] = {}

    for filename, expected_blob in sorted(_EXPECTED_SELECTED_BLOBS.items()):
        path = _CONTENT_DIRECTORY / filename
        assert path.is_file(), f"Selected renal-content document is missing: {filename}"

        payload = path.read_bytes()
        assert _git_blob_sha(payload) == expected_blob, (
            f"Selected renal-content document changed without an updated reviewed snapshot: {filename}"
        )

        document = yaml.safe_load(payload)
        assert isinstance(document, dict), f"{filename} must contain a YAML mapping"
        documents[filename] = document

    return documents


def test_selected_renal_content_matches_review_snapshot() -> None:
    """Any selected clinical-content change must produce an inspectable file and hash diff."""

    documents = _load_selected_documents()
    assert set(documents) == set(_EXPECTED_SELECTED_BLOBS)


def test_selected_snapshot_records_exact_independent_review_metadata() -> None:
    documents = _load_selected_documents()
    assert documents

    for filename, document in documents.items():
        assert document["content_version"] == "1.0.0-draft", filename
        review = document["review"]
        assert {field: review[field] for field in _EXPECTED_REVIEW} == _EXPECTED_REVIEW, filename
        assert review["reviewed_content_version"] == document["content_version"], filename


def test_selected_snapshot_preserves_source_traceability() -> None:
    documents = _load_selected_documents()

    for filename, document in documents.items():
        source_ids = {source["id"] for source in document["sources"]}
        assert source_ids, filename
        for band in document["renal_bands"]:
            assert band["source_ids"], f"{filename}:{band['id']}"
            assert set(band["source_ids"]) <= source_ids, f"{filename}:{band['id']}"


def test_synthetic_fixture_is_outside_selected_clinical_snapshot() -> None:
    filename = "cefepime_synthetic_fixture.yaml"

    assert filename not in _EXPECTED_SELECTED_BLOBS
    assert (_CONTENT_DIRECTORY / filename).is_file()
