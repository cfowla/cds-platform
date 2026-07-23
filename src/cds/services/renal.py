"""Pure renal-function calculation helpers."""

from datetime import date, datetime
from decimal import ROUND_HALF_EVEN, Decimal, localcontext

from cds.domain.clinical import LabResult, Patient
from cds.domain.enums import RenalMethod, Sex, WeightType
from cds.domain.exceptions import CalculationError
from cds.domain.outputs import RenalFunctionResult
from cds.domain.support import Provenance
from cds.domain.value_objects import ValueWithUnit

__all__ = ["calculate_cockcroft_gault", "derive_age_years", "require_supplied_weight"]


def _has_usable_utc_offset(value: object) -> bool:
    if not isinstance(value, datetime) or value.tzinfo is None:
        return False
    try:
        return value.utcoffset() is not None
    except (TypeError, ValueError, OverflowError):
        return False


def _is_finite_positive_decimal(value: object) -> bool:
    return (
        isinstance(value, Decimal)
        and value.is_finite()
        and value > Decimal("0")
    )


def derive_age_years(*, birth_date: date, evaluation_date: date) -> int:
    """Return completed calendar years at an explicit evaluation date.

    For a February 29 birth, age advances on February 29 in leap years and
    on March 1 in non-leap years. Callers must complete structural and
    sufficiency validation before invoking this service.

    Raises:
        CalculationError: If the birth date is after the evaluation date,
            indicating a breach of the validated-service boundary.
    """

    if not isinstance(birth_date, date) or isinstance(birth_date, datetime):
        raise CalculationError("Birth date must be a date.")
    if not isinstance(evaluation_date, date) or isinstance(evaluation_date, datetime):
        raise CalculationError("Evaluation date must be a date.")
    if birth_date > evaluation_date:
        raise CalculationError("Birth date cannot be after the evaluation date.")

    years = evaluation_date.year - birth_date.year
    birthday_not_reached = (evaluation_date.month, evaluation_date.day) < (
        birth_date.month,
        birth_date.day,
    )
    return years - int(birthday_not_reached)


def require_supplied_weight(
    *,
    weight: ValueWithUnit,
    weight_type: WeightType,
) -> tuple[ValueWithUnit, WeightType]:
    """Return an independently allocated copy of a validated supplied weight.

    Callers must complete structural and task-sufficiency validation before
    invoking this helper. It preserves the exact supplied Decimal, kilogram
    unit, and explicit supported weight type without derivation or conversion.

    Raises:
        CalculationError: If the validated-service contract is breached.
    """

    if not isinstance(weight, ValueWithUnit):
        raise CalculationError("Supplied weight must be a ValueWithUnit.")
    if not _is_finite_positive_decimal(weight.value):
        raise CalculationError(
            "Supplied weight value must be a finite positive Decimal."
        )
    if weight.unit != "kg":
        raise CalculationError('Supplied weight unit must be exactly "kg".')
    if not isinstance(weight_type, WeightType) or weight_type not in {
        WeightType.ACTUAL,
        WeightType.IDEAL,
        WeightType.ADJUSTED,
        WeightType.OTHER,
    }:
        raise CalculationError("Supplied weight type must be explicit and supported.")

    return ValueWithUnit(value=weight.value, unit=weight.unit), weight_type


def calculate_cockcroft_gault(
    *,
    patient: Patient,
    serum_creatinine_result: LabResult,
    weight: ValueWithUnit,
    weight_type: WeightType,
    evaluation_date: date,
    calculated_at: datetime,
) -> RenalFunctionResult:
    """Calculate unindexed Cockcroft-Gault creatinine clearance from validated inputs.

    Structural and task-sufficiency validation must complete before this pure
    calculator is invoked. Defensive failures indicate a breach of that boundary.

    Raises:
        CalculationError: If a required typed input violates the validated-service
            contract.
    """

    if (
        not isinstance(patient, Patient)
        or not isinstance(patient.birth_date, date)
        or isinstance(patient.birth_date, datetime)
    ):
        raise CalculationError("Patient birth date is required for calculation.")
    if not isinstance(patient.sex, Sex) or patient.sex not in {Sex.MALE, Sex.FEMALE}:
        raise CalculationError("Patient sex must be supported for calculation.")
    if not isinstance(evaluation_date, date) or isinstance(evaluation_date, datetime):
        raise CalculationError("Evaluation date must be a date.")
    if not isinstance(serum_creatinine_result, LabResult):
        raise CalculationError("Serum creatinine result must be a LabResult.")

    serum_creatinine = serum_creatinine_result.value
    if not isinstance(serum_creatinine, ValueWithUnit):
        raise CalculationError("Serum creatinine must be a ValueWithUnit.")
    if not _is_finite_positive_decimal(serum_creatinine.value):
        raise CalculationError(
            "Serum creatinine value must be a finite positive Decimal."
        )
    if serum_creatinine.unit != "mg/dL":
        raise CalculationError('Serum creatinine unit must be exactly "mg/dL".')
    if not _has_usable_utc_offset(serum_creatinine_result.collected_at):
        raise CalculationError(
            "Serum creatinine collection time must be timezone-aware."
        )
    if not _has_usable_utc_offset(calculated_at):
        raise CalculationError("Calculation time must be timezone-aware.")

    weight_used, weight_type_used = require_supplied_weight(
        weight=weight,
        weight_type=weight_type,
    )
    age_years = derive_age_years(
        birth_date=patient.birth_date,
        evaluation_date=evaluation_date,
    )

    try:
        with localcontext() as context:
            context.prec = 28
            context.rounding = ROUND_HALF_EVEN
            crcl = (
                (Decimal("140") - Decimal(age_years)) * weight_used.value
            ) / (Decimal("72") * serum_creatinine.value)
            if patient.sex is Sex.FEMALE:
                crcl *= Decimal("0.85")
            crcl = Decimal(format(crcl, "f"))
    except ArithmeticError as error:
        raise CalculationError("Cockcroft-Gault calculation failed.") from error

    return RenalFunctionResult(
        patient_id=patient.patient_id,
        encounter_id=serum_creatinine_result.encounter_id,
        method=RenalMethod.COCKCROFT_GAULT,
        value=ValueWithUnit(value=crcl, unit="mL/min"),
        normalized_to_bsa=False,
        evaluation_date=evaluation_date,
        serum_creatinine_result_id=serum_creatinine_result.result_id,
        serum_creatinine=ValueWithUnit(
            value=serum_creatinine.value,
            unit=serum_creatinine.unit,
        ),
        serum_creatinine_collected_at=serum_creatinine_result.collected_at,
        age_years=age_years,
        sex=patient.sex,
        weight_used=weight_used,
        weight_type_used=weight_type_used,
        calculated_at=calculated_at,
        provenance=Provenance(
            source_type="calculated",
            source_name="cds.services.renal",
            source_identifier="cockcroft_gault",
            version="1",
        ),
    )
