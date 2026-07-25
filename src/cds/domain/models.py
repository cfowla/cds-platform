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
    AlertCategory,  # noqa: F401 - compatibility attribute excluded from __all__
    CDSRecommendation,
    Contraindication,
    DoseRecommendation,
    RecommendationAction,  # noqa: F401 - compatibility attribute excluded from __all__
    RecommendationStrength,  # noqa: F401 - compatibility attribute excluded from __all__
    RenalFunctionResult,
    RuleResult,
    SupportingValue,  # noqa: F401 - compatibility attribute excluded from __all__
)
from cds.domain.support import (
    Assumption,
    EvidenceItem,
    EvidenceLevel,  # noqa: F401 - compatibility attribute excluded from __all__
    Provenance,
    ProvenanceSourceType,  # noqa: F401 - compatibility attribute excluded from __all__
    WarningNote,
    WarningSeverity,  # noqa: F401 - compatibility attribute excluded from __all__
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
