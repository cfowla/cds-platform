"""Tests for problem and allergy truth objects."""

import json
from dataclasses import asdict
from datetime import UTC, datetime

import pytest

from cds.domain.enums import Severity
from cds.domain.models import (
    Allergy,
    CodeableConcept,
    Problem,
    Provenance,
    TimeRange,
    WarningNote,
)


@pytest.mark.parametrize("model_type", [Problem, Allergy])
def test_problem_and_allergy_have_safe_partial_defaults(model_type: type[object]) -> None:
    """Each truth object can represent a source record before optional facts arrive."""
    assert isinstance(model_type(), model_type)


def test_problem_supports_a_text_only_concept_without_fabricated_coding() -> None:
    """Free-text problem data remains usable without implying a terminology match."""
    problem = Problem(
        problem_id="problem-123",
        patient_id="patient-123",
        problem=CodeableConcept(text="Chronic kidney disease"),
        onset_period=TimeRange(start=datetime(2025, 4, 1, tzinfo=UTC)),
        status="active",
        severity=Severity.HIGH,
    )

    assert problem.problem.text == "Chronic kidney disease"
    assert problem.problem.system is None
    assert problem.problem.code is None
    assert problem.severity is Severity.HIGH


def test_allergy_supports_text_only_substance_and_reaction() -> None:
    """Uncoded allergy text is preserved without pretending RxNorm or SNOMED coding exists."""
    allergy = Allergy(
        allergy_id="allergy-123",
        patient_id="patient-123",
        substance=CodeableConcept(text="Penicillin"),
        reaction=CodeableConcept(text="Pruritic rash"),
        severity=Severity.MODERATE,
        verification_status="confirmed",
    )

    assert allergy.substance == CodeableConcept(text="Penicillin")
    assert allergy.reaction == CodeableConcept(text="Pruritic rash")
    assert allergy.substance.system is None
    assert allergy.substance.code is None
    assert allergy.reaction.system is None
    assert allergy.reaction.code is None


def test_unknown_reaction_and_severity_are_explicit() -> None:
    """Unknown facts are distinct from blank strings or asserted clinical values."""
    problem = Problem()
    allergy = Allergy()

    assert problem.severity is Severity.UNKNOWN
    assert allergy.reaction == CodeableConcept()
    assert allergy.reaction.text is None
    assert allergy.severity is Severity.UNKNOWN


def test_problem_and_allergy_mutable_defaults_are_independent() -> None:
    """Concepts and traceability collections are never shared across records."""
    first_problem, second_problem = Problem(), Problem()
    first_allergy, second_allergy = Allergy(), Allergy()

    first_problem.problem.text = "Hypertension"
    first_problem.warnings.append(WarningNote(code="problem-warning"))
    first_allergy.reaction.text = "Angioedema"
    first_allergy.warnings.append(WarningNote(code="allergy-warning"))

    assert second_problem.problem.text is None
    assert second_problem.warnings == []
    assert second_allergy.reaction.text is None
    assert second_allergy.warnings == []


@pytest.mark.parametrize("model", [Problem(), Allergy()])
def test_default_problem_and_allergy_models_have_json_safe_dicts(
    model: Problem | Allergy,
) -> None:
    """Default instances convert to JSON-safe primitive dictionaries."""
    serialized = json.loads(json.dumps(asdict(model)))

    assert isinstance(serialized, dict)
    assert serialized["severity"] == "unknown"
    assert serialized["provenance"] == asdict(Provenance())
