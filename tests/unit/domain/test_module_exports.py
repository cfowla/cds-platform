"""Tests for focused domain modules and legacy compatibility exports."""

import pytest

import cds.domain.models as compatibility
from cds.domain.clinical import (
    Allergy,
    Encounter,
    LabResult,
    MedicationOrder,
    Patient,
    Problem,
    VitalSign,
)
from cds.domain.outputs import (
    Alert,
    CDSRecommendation,
    Contraindication,
    DoseRecommendation,
    RenalFunctionResult,
    RuleResult,
)
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit


@pytest.mark.parametrize(
    ("name", "focused_model"),
    [
        ("Alert", Alert),
        ("Allergy", Allergy),
        ("Assumption", Assumption),
        ("CDSRecommendation", CDSRecommendation),
        ("CodeableConcept", CodeableConcept),
        ("Contraindication", Contraindication),
        ("DoseRecommendation", DoseRecommendation),
        ("Encounter", Encounter),
        ("EvidenceItem", EvidenceItem),
        ("LabResult", LabResult),
        ("MedicationOrder", MedicationOrder),
        ("Patient", Patient),
        ("Problem", Problem),
        ("Provenance", Provenance),
        ("RenalFunctionResult", RenalFunctionResult),
        ("RuleResult", RuleResult),
        ("TimeRange", TimeRange),
        ("ValueWithUnit", ValueWithUnit),
        ("VitalSign", VitalSign),
        ("WarningNote", WarningNote),
    ],
)
def test_legacy_model_imports_reference_focused_definitions(
    name: str,
    focused_model: type[object],
) -> None:
    """Existing imports resolve to the same classes exposed by focused modules."""
    assert getattr(compatibility, name) is focused_model


def test_legacy_models_all_is_unchanged() -> None:
    """Star-import behavior retains the previously published model list."""
    assert compatibility.__all__ == [
        "Alert",
        "Allergy",
        "Assumption",
        "CDSRecommendation",
        "CodeableConcept",
        "Contraindication",
        "DoseRecommendation",
        "Encounter",
        "EvidenceItem",
        "LabResult",
        "MedicationOrder",
        "Patient",
        "Problem",
        "Provenance",
        "RenalFunctionResult",
        "RuleResult",
        "TimeRange",
        "ValueWithUnit",
        "VitalSign",
        "WarningNote",
    ]


def test_legacy_type_aliases_remain_importable() -> None:
    """Aliases previously available as module attributes remain available."""
    for name in (
        "AlertCategory",
        "EvidenceLevel",
        "ProvenanceSourceType",
        "RecommendationAction",
        "RecommendationStrength",
        "SupportingValue",
        "WarningSeverity",
    ):
        assert hasattr(compatibility, name)
