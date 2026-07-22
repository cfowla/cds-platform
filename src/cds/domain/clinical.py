"""Passive clinical source-of-truth models."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime

from cds.domain.enums import Severity, Sex
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit

__all__ = [
    "Allergy",
    "Encounter",
    "LabResult",
    "MedicationOrder",
    "Patient",
    "Problem",
    "VitalSign",
]


@dataclass(slots=True, kw_only=True)
class Patient:
    """Carry patient facts supplied to CDS without deriving clinical values.

    Missing identifiers, dates, and measurements use ``None``; unknown sex uses
    :class:`~cds.domain.enums.Sex.UNKNOWN`. Weight and height preserve the source value and
    unit. Age, body mass index, ideal or adjusted weight, and other calculations belong in
    services and are intentionally absent from this truth object.
    """

    patient_id: str | None = None
    birth_date: date | None = None
    sex: Sex = Sex.UNKNOWN
    actual_body_weight: ValueWithUnit = field(default_factory=ValueWithUnit)
    height: ValueWithUnit = field(default_factory=ValueWithUnit)
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Encounter:
    """Carry encounter facts as supplied by a source system.

    Every field may be absent so an incomplete source record can still be represented.
    Encounter type preserves source text or coding through ``CodeableConcept`` and timing
    uses ``TimeRange``. Duration, admission status inference, and chronology checks belong
    outside the model.
    """

    encounter_id: str | None = None
    patient_id: str | None = None
    encounter_type: CodeableConcept = field(default_factory=CodeableConcept)
    period: TimeRange = field(default_factory=TimeRange)
    location: str | None = None
    service_line: str | None = None
    attending_clinician_id: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class MedicationOrder:
    """Carry medication-order facts without interpreting or evaluating the regimen.

    Quantitative fields use ``ValueWithUnit`` so units remain explicit. A missing numeric
    value is ``None`` and remains distinct from a supplied zero. Route, medication, and
    indication preserve source coding; dose validation, frequency interpretation, unit
    conversion, active-status inference, and renal evaluation belong outside this model.
    """

    order_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    medication: CodeableConcept = field(default_factory=CodeableConcept)
    dose: ValueWithUnit = field(default_factory=ValueWithUnit)
    route: CodeableConcept = field(default_factory=CodeableConcept)
    frequency_interval: ValueWithUnit = field(default_factory=ValueWithUnit)
    ordered_period: TimeRange = field(default_factory=TimeRange)
    indication: CodeableConcept = field(default_factory=CodeableConcept)
    infusion_duration: ValueWithUnit = field(default_factory=ValueWithUnit)
    prn: bool | None = None
    status: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class LabResult:
    """Carry a laboratory observation exactly as supplied by a source system.

    The result and reference boundaries use ``ValueWithUnit`` to retain explicit units.
    Missing numeric values use ``None`` rather than zero, including when a unit is known.
    Result interpretation, unit normalization, range validation, and status semantics remain
    responsibilities of mapper, validation, or service layers.
    """

    result_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    test: CodeableConcept = field(default_factory=CodeableConcept)
    value: ValueWithUnit = field(default_factory=ValueWithUnit)
    reference_range_low: ValueWithUnit = field(default_factory=ValueWithUnit)
    reference_range_high: ValueWithUnit = field(default_factory=ValueWithUnit)
    collected_at: datetime | None = None
    resulted_at: datetime | None = None
    status: str | None = None
    specimen: CodeableConcept = field(default_factory=CodeableConcept)
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class VitalSign:
    """Carry a measured vital sign without normalization or derived calculations.

    The measured quantity uses ``ValueWithUnit`` so the source unit is explicit. ``None``
    represents a missing number and is distinguishable from a measured zero. Plausibility
    checks, unit conversion, blood-pressure pairing, oxygen interpretation, and score
    calculations belong outside this domain truth object.
    """

    vital_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    vital: CodeableConcept = field(default_factory=CodeableConcept)
    value: ValueWithUnit = field(default_factory=ValueWithUnit)
    measured_at: datetime | None = None
    position: str | None = None
    supplemental_oxygen: bool | None = None
    status: str | None = None
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Problem:
    """Carry a patient problem exactly as supplied by a source system.

    ``problem`` may contain text without terminology coding; ``system`` and ``code`` remain
    ``None`` unless the source supplied them. Unknown severity uses ``Severity.UNKNOWN``.
    Status interpretation, coding lookup, chronology validation, and clinical inference stay
    outside this passive truth object.
    """

    problem_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    problem: CodeableConcept = field(default_factory=CodeableConcept)
    onset_period: TimeRange = field(default_factory=TimeRange)
    recorded_at: datetime | None = None
    status: str | None = None
    severity: Severity = Severity.UNKNOWN
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)


@dataclass(slots=True, kw_only=True)
class Allergy:
    """Carry an allergy or intolerance record without interpreting clinical significance.

    ``substance`` and ``reaction`` may be text-only concepts; coding fields remain ``None``
    unless supplied by the source. An unknown reaction is an empty ``CodeableConcept`` whose
    text, system, and code are all ``None``. Unknown severity uses ``Severity.UNKNOWN``.
    Allergy verification, status inference, terminology lookup, and cross-reactivity logic
    belong outside this domain model.
    """

    allergy_id: str | None = None
    patient_id: str | None = None
    encounter_id: str | None = None
    substance: CodeableConcept = field(default_factory=CodeableConcept)
    reaction: CodeableConcept = field(default_factory=CodeableConcept)
    onset_at: datetime | None = None
    recorded_at: datetime | None = None
    status: str | None = None
    verification_status: str | None = None
    severity: Severity = Severity.UNKNOWN
    assumptions: list[Assumption] = field(default_factory=list)
    warnings: list[WarningNote] = field(default_factory=list)
    evidence: list[EvidenceItem] = field(default_factory=list)
    provenance: Provenance = field(default_factory=Provenance)
