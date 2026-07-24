"""Passive data-transfer objects for application input boundaries."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["RenalDoseCLIRequest"]


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseCLIRequest:
    """Preserve one synthetic renal-dose CLI request before mapping.

    Values remain in their JSON wire representation so the later request mapper can make
    date, time, Decimal, enum, identifier, unit, and domain-object conversion explicit.
    Missing source values use ``None``. This passive DTO performs no validation,
    normalization, inference, calculation, content loading, rule matching, serialization,
    I/O, or mutation.
    """

    patient_id: str | None = None
    birth_date: str | None = None
    sex: str | None = None

    weight_value: str | None = None
    weight_unit: str | None = None
    weight_type: str | None = None

    serum_creatinine_result_id: str | None = None
    serum_creatinine_value: str | None = None
    serum_creatinine_unit: str | None = None
    serum_creatinine_collected_at: str | None = None
    serum_creatinine_status: str | None = None

    renal_function_stable: bool | None = None
    renal_replacement_therapy: bool | None = None
    pregnant_or_lactating: bool | None = None

    medication_order_id: str | None = None
    medication_system: str | None = None
    medication_code: str | None = None
    regimen_id: str | None = None
    formulation_id: str | None = None

    dose_value: str | None = None
    dose_unit: str | None = None
    route_system: str | None = None
    route_code: str | None = None
    frequency_interval_value: str | None = None
    frequency_interval_unit: str | None = None
    indication_system: str | None = None
    indication_code: str | None = None
    infusion_duration_value: str | None = None
    infusion_duration_unit: str | None = None

    requested_content_version: str | None = None
    evaluation_date: str | None = None
    evaluated_at: str | None = None
