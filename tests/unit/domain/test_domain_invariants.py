"""Generic invariants shared by all passive domain dataclasses."""

import json
from dataclasses import fields, is_dataclass

import pytest

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
from cds.utils.serialization import dumps_json, to_jsonable

DOMAIN_MODELS = [
    Provenance,
    EvidenceItem,
    Assumption,
    WarningNote,
    ValueWithUnit,
    CodeableConcept,
    TimeRange,
    Patient,
    Encounter,
    MedicationOrder,
    LabResult,
    VitalSign,
    Problem,
    Allergy,
    RenalFunctionResult,
    Contraindication,
    DoseRecommendation,
    CDSRecommendation,
    Alert,
    RuleResult,
]

MODELS_WITH_NESTED_DEFAULTS = [
    EvidenceItem,
    Assumption,
    WarningNote,
    Patient,
    Encounter,
    MedicationOrder,
    LabResult,
    VitalSign,
    Problem,
    Allergy,
    RenalFunctionResult,
    Contraindication,
    DoseRecommendation,
    CDSRecommendation,
    Alert,
    RuleResult,
]


@pytest.mark.parametrize("model_type", DOMAIN_MODELS, ids=lambda model_type: model_type.__name__)
def test_domain_models_support_safe_incomplete_construction(
    model_type: type[object],
) -> None:
    assert isinstance(model_type(), model_type)


@pytest.mark.parametrize(
    "model_type",
    MODELS_WITH_NESTED_DEFAULTS,
    ids=lambda model_type: model_type.__name__,
)
def test_nested_mutable_defaults_are_independent(model_type: type[object]) -> None:
    first = model_type()
    second = model_type()
    checked_fields: list[str] = []

    for model_field in fields(first):
        first_value = getattr(first, model_field.name)
        second_value = getattr(second, model_field.name)
        if isinstance(first_value, (list, dict)) or is_dataclass(first_value):
            checked_fields.append(model_field.name)
            assert first_value is not second_value

    assert checked_fields


@pytest.mark.parametrize("model_type", DOMAIN_MODELS, ids=lambda model_type: model_type.__name__)
def test_domain_models_use_the_canonical_serializer(model_type: type[object]) -> None:
    model = model_type()
    serialized = to_jsonable(model)

    assert isinstance(serialized, dict)
    assert json.loads(dumps_json(model)) == serialized
