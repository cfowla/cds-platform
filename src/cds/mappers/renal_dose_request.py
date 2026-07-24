"""Map synthetic renal-dose CLI wire values to typed application inputs."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, fields
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import Any, TypeVar

from cds.app.dto import RenalDoseCLIRequest
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import Sex, WeightType
from cds.domain.value_objects import CodeableConcept, ValueWithUnit

__all__ = [
    "RenalDoseMappedInput",
    "RequestMappingError",
    "dto_from_mapping",
    "map_renal_dose_request",
]


class RequestMappingError(ValueError):
    """Report malformed external request data without clinical interpretation."""


@dataclass(frozen=True, slots=True, kw_only=True)
class RenalDoseMappedInput:
    """Carry mapped values needed by the renal-dose application boundary.

    Missing source values remain ``None`` where the target type permits it. Missing enum values use
    the domain's explicit ``UNKNOWN`` member. The CLI layer must require non-missing evaluation
    dates and times before invoking the existing renal-dose use case.
    """

    patient: Patient
    serum_creatinine_result: LabResult
    medication_order: MedicationOrder
    weight_type: WeightType
    regimen_id: str | None
    formulation_id: str | None
    renal_function_stable: bool | None
    renal_replacement_therapy: bool | None
    pregnant_or_lactating: bool | None
    requested_content_version: str | None
    evaluation_date: date | None
    evaluated_at: datetime | None


_BOOLEAN_FIELDS = {
    "renal_function_stable",
    "renal_replacement_therapy",
    "pregnant_or_lactating",
}
_REQUEST_FIELDS = {field.name for field in fields(RenalDoseCLIRequest)}


def dto_from_mapping(payload: Mapping[str, object]) -> RenalDoseCLIRequest:
    """Create the passive CLI DTO from one parsed JSON object without coercion.

    Field names are exact and unknown fields are rejected so a misspelled clinical fact cannot be
    silently converted into missing data. String and Boolean wire types are preserved unchanged;
    JSON numbers are not accepted for clinical numerics because later Decimal conversion must start
    from a string rather than binary ``float``.
    """

    if not isinstance(payload, Mapping):
        raise RequestMappingError("The renal-dose request must be a JSON object.")

    non_string_keys = [key for key in payload if not isinstance(key, str)]
    if non_string_keys:
        raise RequestMappingError("Request field names must be strings.")

    unknown_fields = sorted(set(payload) - _REQUEST_FIELDS)
    if unknown_fields:
        joined = ", ".join(unknown_fields)
        raise RequestMappingError(f"Unknown request field(s): {joined}.")

    values: dict[str, Any] = {}
    for field_name in _REQUEST_FIELDS:
        value = payload.get(field_name)
        if value is None:
            values[field_name] = None
            continue
        if field_name in _BOOLEAN_FIELDS:
            if type(value) is not bool:
                raise RequestMappingError(
                    f"Request field {field_name!r} must be a Boolean or null."
                )
        elif not isinstance(value, str):
            raise RequestMappingError(
                f"Request field {field_name!r} must be a string or null."
            )
        values[field_name] = value

    return RenalDoseCLIRequest(**values)


def map_renal_dose_request(request: RenalDoseCLIRequest) -> RenalDoseMappedInput:
    """Convert one passive request DTO to typed domain and application inputs.

    This conversion performs no clinical validation, identifier lookup, unit normalization,
    calculation, content loading, or rule matching. Exact identifiers and units are copied as
    supplied. Syntactically malformed Decimal, date, datetime, or enum values raise
    :class:`RequestMappingError`.
    """

    if not isinstance(request, RenalDoseCLIRequest):
        raise TypeError("request must be a RenalDoseCLIRequest")

    patient = Patient(
        patient_id=request.patient_id,
        birth_date=_parse_date(request.birth_date, field_name="birth_date"),
        sex=_parse_enum(request.sex, Sex, field_name="sex"),
        actual_body_weight=ValueWithUnit(
            value=_parse_decimal(request.weight_value, field_name="weight_value"),
            unit=request.weight_unit,
        ),
    )
    serum_creatinine_result = LabResult(
        result_id=request.serum_creatinine_result_id,
        patient_id=request.patient_id,
        value=ValueWithUnit(
            value=_parse_decimal(
                request.serum_creatinine_value,
                field_name="serum_creatinine_value",
            ),
            unit=request.serum_creatinine_unit,
        ),
        collected_at=_parse_datetime(
            request.serum_creatinine_collected_at,
            field_name="serum_creatinine_collected_at",
        ),
        status=request.serum_creatinine_status,
    )
    medication_order = MedicationOrder(
        order_id=request.medication_order_id,
        patient_id=request.patient_id,
        medication=CodeableConcept(
            system=request.medication_system,
            code=request.medication_code,
        ),
        dose=ValueWithUnit(
            value=_parse_decimal(request.dose_value, field_name="dose_value"),
            unit=request.dose_unit,
        ),
        route=CodeableConcept(
            system=request.route_system,
            code=request.route_code,
        ),
        frequency_interval=ValueWithUnit(
            value=_parse_decimal(
                request.frequency_interval_value,
                field_name="frequency_interval_value",
            ),
            unit=request.frequency_interval_unit,
        ),
        indication=CodeableConcept(
            system=request.indication_system,
            code=request.indication_code,
        ),
        infusion_duration=ValueWithUnit(
            value=_parse_decimal(
                request.infusion_duration_value,
                field_name="infusion_duration_value",
            ),
            unit=request.infusion_duration_unit,
        ),
    )

    return RenalDoseMappedInput(
        patient=patient,
        serum_creatinine_result=serum_creatinine_result,
        medication_order=medication_order,
        weight_type=_parse_enum(request.weight_type, WeightType, field_name="weight_type"),
        regimen_id=request.regimen_id,
        formulation_id=request.formulation_id,
        renal_function_stable=request.renal_function_stable,
        renal_replacement_therapy=request.renal_replacement_therapy,
        pregnant_or_lactating=request.pregnant_or_lactating,
        requested_content_version=request.requested_content_version,
        evaluation_date=_parse_date(request.evaluation_date, field_name="evaluation_date"),
        evaluated_at=_parse_datetime(request.evaluated_at, field_name="evaluated_at"),
    )


def _parse_decimal(value: str | None, *, field_name: str) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise RequestMappingError(
            f"Request field {field_name!r} must contain a valid Decimal string."
        ) from exc


def _parse_date(value: str | None, *, field_name: str) -> date | None:
    if value is None:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError as exc:
        raise RequestMappingError(
            f"Request field {field_name!r} must contain an ISO calendar date."
        ) from exc


def _parse_datetime(value: str | None, *, field_name: str) -> datetime | None:
    if value is None:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError as exc:
        raise RequestMappingError(
            f"Request field {field_name!r} must contain an ISO datetime."
        ) from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise RequestMappingError(
            f"Request field {field_name!r} must include a usable UTC offset."
        )
    return parsed


_EnumT = TypeVar("_EnumT", bound=StrEnum)


def _parse_enum(
    value: str | None,
    enum_type: type[_EnumT],
    *,
    field_name: str,
) -> _EnumT:
    if value is None:
        return enum_type("unknown")
    try:
        return enum_type(value)
    except ValueError as exc:
        raise RequestMappingError(
            f"Request field {field_name!r} contains an unsupported exact value."
        ) from exc
