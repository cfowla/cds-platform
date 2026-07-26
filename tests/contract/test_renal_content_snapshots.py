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
        "823b1659ae09f0e932de7ee2e7b993c218f8e4c7"
    ),
    "cefepime_iv_1_g_every_12_hours_over_30_minutes.yaml": (
        "cc31f5c9af01bc75ee9f0c0f2d8a9fcff6cc5456"
    ),
    "cefepime_iv_2_g_every_12_hours_over_30_minutes.yaml": (
        "969313aee45aaf14f053a95bbaa858f893e67801"
    ),
    "cefepime_iv_2_g_every_8_hours_over_30_minutes.yaml": (
        "4e3076a5ef8aefd3d19c6ec267210b7dedba6d79"
    ),
    (
        "piperacillin_tazobactam_standard_infusion_iv_3_375_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): "66d0453fc04e7328f0f5794a2fd53e858dced7a2",
    (
        "piperacillin_tazobactam_standard_infusion_iv_4_5_g_"
        "every_6_hours_over_30_minutes.yaml"
    ): "68f8cdf5f8994c80adf686b00629b959e7eac9d8",
    (
        "piperacillin_tazobactam_extended_infusion_iv_3_375_g_"
        "every_8_hours_over_240_minutes.yaml"
    ): "e3e5fb78be11277ddb26ea2f25508c1332e9e63a",
    "famotidine_oral_film_coated_tablet_20_mg_every_12_hours.yaml": (
        "10415a4be5214545d84e7cf8cb0dec8c775ceda5"
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
