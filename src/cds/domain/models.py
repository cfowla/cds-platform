"""Compatibility re-exports for CDS domain models.

New code may import from the focused domain modules. Existing imports from
``cds.domain.models`` remain supported.
"""

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
    AlertCategory,
    CDSRecommendation,
    Contraindication,
    DoseRecommendation,
    RecommendationAction,
    RecommendationStrength,
    RenalFunctionResult,
    RuleResult,
    SupportingValue,
)
from cds.domain.support import (
    Assumption,
    EvidenceItem,
    EvidenceLevel,
    Provenance,
    ProvenanceSourceType,
    WarningNote,
    WarningSeverity,
)
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit

__all__ = [
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
