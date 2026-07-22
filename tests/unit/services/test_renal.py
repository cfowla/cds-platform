"""Tests for renal-function calculation services."""

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, getcontext, localcontext, setcontext

import pytest

from cds.domain.clinical import LabResult, Patient
from cds.domain.enums import RenalMethod, Sex, WeightType
from cds.domain.exceptions import CalculationError
from cds.domain.outputs import RenalFunctionResult
from cds.domain.value_objects import ValueWithUnit
from cds.services.renal import (
    calculate_cockcroft_gault,
    derive_age_years,
    require_supplied_weight,
)


def test_evaluation_before_birthday_returns_prior_completed_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 23),
        evaluation_date=date(2026, 7, 22),
    ) == 45


def test_evaluation_on_birthday_increments_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 22),
        evaluation_date=date(2026, 7, 22),
    ) == 46


def test_evaluation_after_birthday_retains_incremented_age() -> None:
    assert derive_age_years(
        birth_date=date(1980, 7, 21),
        evaluation_date=date(2026, 7, 22),
    ) == 46


def test_february_29_birth_does_not_increment_on_february_28_non_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2023, 2, 28),
    ) == 18


def test_february_29_birth_increments_on_march_1_non_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2023, 3, 1),
    ) == 19


def test_february_29_birth_increments_on_february_29_leap_year() -> None:
    assert derive_age_years(
        birth_date=date(2004, 2, 29),
        evaluation_date=date(2024, 2, 29),
    ) == 20


def test_birth_date_equal_to_evaluation_date_returns_zero() -> None:
    same_date = date(2026, 7, 22)

    assert derive_age_years(birth_date=same_date, evaluation_date=same_date) == 0


def test_birth_date_after_evaluation_date_raises_calculation_error() -> None:
    with pytest.raises(CalculationError):
        derive_age_years(
            birth_date=date(2026, 7, 23),
            evaluation_date=date(2026, 7, 22),
        )


def test_identical_explicit_inputs_produce_identical_ages() -> None:
    birth_date = date(1980, 7, 23)
    evaluation_date = date(2026, 7, 22)

    first = derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)
    second = derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)

    assert first == second == 45
    assert isinstance(first, int)


def test_caller_supplied_date_objects_remain_unchanged() -> None:
    birth_date = date(1980, 7, 23)
    evaluation_date = date(2026, 7, 22)
    original_birth_date = date(1980, 7, 23)
    original_evaluation_date = date(2026, 7, 22)

    derive_age_years(birth_date=birth_date, evaluation_date=evaluation_date)

    assert birth_date == original_birth_date
    assert evaluation_date == original_evaluation_date


@pytest.mark.parametrize(
    ("supplied_value", "weight_type"),
    [
        (Decimal("72.40"), WeightType.ACTUAL),
        (Decimal("61.25"), WeightType.IDEAL),
        (Decimal("66.875"), WeightType.ADJUSTED),
        (Decimal("54.321"), WeightType.OTHER),
    ],
)
def test_supported_supplied_weight_is_preserved_without_derivation(
    supplied_value: Decimal,
    weight_type: WeightType,
) -> None:
    weight = ValueWithUnit(value=supplied_value, unit="kg")
    original_value_tuple = supplied_value.as_tuple()

    returned_weight, returned_type = require_supplied_weight(
        weight=weight,
        weight_type=weight_type,
    )

    assert returned_weight is not weight
    assert returned_weight.value is supplied_value
    assert returned_weight.value.as_tuple() == original_value_tuple
    assert returned_weight.unit == "kg"
    assert returned_type is weight_type
    assert weight.value is supplied_value
    assert weight.value.as_tuple() == original_value_tuple
    assert weight.unit == "kg"


def test_repeated_calls_return_equivalent_independently_allocated_weights() -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit="kg")

    first = require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)
    second = require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)

    assert first == second
    assert first[0] is not second[0]
    assert first[0] is not weight
    assert second[0] is not weight


@pytest.mark.parametrize("value", [None, 72.4])
def test_missing_or_non_decimal_weight_value_raises_calculation_error(
    value: object,
) -> None:
    weight = ValueWithUnit(value=value, unit="kg")  # type: ignore[arg-type]

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-0.01")])
def test_non_positive_weight_value_raises_calculation_error(value: Decimal) -> None:
    weight = ValueWithUnit(value=value, unit="kg")

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("unit", [None, "", "KG", " kg", "kg ", " kg ", "lb"])
def test_non_exact_kilogram_unit_raises_calculation_error(unit: str | None) -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit=unit)

    with pytest.raises(CalculationError):
        require_supplied_weight(weight=weight, weight_type=WeightType.ACTUAL)


@pytest.mark.parametrize("weight_type", [WeightType.UNKNOWN, None, "actual"])
def test_unknown_missing_or_raw_string_weight_type_raises_calculation_error(
    weight_type: object,
) -> None:
    weight = ValueWithUnit(value=Decimal("72.40"), unit="kg")

    with pytest.raises(CalculationError):
        require_supplied_weight(  # type: ignore[arg-type]
            weight=weight,
            weight_type=weight_type,
        )


def _cockcroft_gault_inputs(
    *,
    sex: Sex,
) -> tuple[Patient, LabResult, ValueWithUnit]:
    patient = Patient(
        patient_id="synthetic-patient",
        birth_date=date(1980, 7, 23),
        sex=sex,
    )
    serum_creatinine = LabResult(
        result_id="synthetic-creatinine",
        patient_id=patient.patient_id,
        encounter_id="synthetic-encounter",
        value=ValueWithUnit(value=Decimal("1.13"), unit="mg/dL"),
        collected_at=datetime(2026, 7, 22, 8, 30, tzinfo=timezone.utc),
    )
    weight = ValueWithUnit(value=Decimal("72.40"), unit="kg")
    return patient, serum_creatinine, weight


def _calculate_cockcroft_gault(*, sex: Sex):
    patient, serum_creatinine, weight = _cockcroft_gault_inputs(sex=sex)
    result = calculate_cockcroft_gault(
        patient=patient,
        serum_creatinine_result=serum_creatinine,
        weight=weight,
        weight_type=WeightType.ACTUAL,
        evaluation_date=date(2026, 7, 22),
        calculated_at=datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    )
    return result, patient, serum_creatinine, weight


def test_normal_cockcroft_gault_case_matches_hand_calculated_value() -> None:
    patient = Patient(
        patient_id="synthetic-normal-patient",
        birth_date=date(1986, 7, 22),
        sex=Sex.MALE,
    )
    serum_creatinine = LabResult(
        result_id="synthetic-normal-creatinine",
        patient_id=patient.patient_id,
        encounter_id="synthetic-normal-encounter",
        value=ValueWithUnit(value=Decimal("0.9"), unit="mg/dL"),
        collected_at=datetime(2026, 7, 22, 8, 0, tzinfo=timezone.utc),
    )

    result = calculate_cockcroft_gault(
        patient=patient,
        serum_creatinine_result=serum_creatinine,
        weight=ValueWithUnit(value=Decimal("72.5"), unit="kg"),
        weight_type=WeightType.ACTUAL,
        evaluation_date=date(2026, 7, 22),
        calculated_at=datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    )

    assert result.value.value == Decimal("111.8827160493827160493827160")
    assert result.value.unit == "mL/min"
    assert result.age_years == 40


def test_impaired_cockcroft_gault_case_matches_hand_calculated_value() -> None:
    patient = Patient(
        patient_id="synthetic-impaired-patient",
        birth_date=date(1951, 7, 22),
        sex=Sex.MALE,
    )
    serum_creatinine = LabResult(
        result_id="synthetic-impaired-creatinine",
        patient_id=patient.patient_id,
        encounter_id="synthetic-impaired-encounter",
        value=ValueWithUnit(value=Decimal("1.8"), unit="mg/dL"),
        collected_at=datetime(2026, 7, 22, 8, 0, tzinfo=timezone.utc),
    )

    result = calculate_cockcroft_gault(
        patient=patient,
        serum_creatinine_result=serum_creatinine,
        weight=ValueWithUnit(value=Decimal("63.4"), unit="kg"),
        weight_type=WeightType.ACTUAL,
        evaluation_date=date(2026, 7, 22),
        calculated_at=datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    )

    assert result.value.value == Decimal("31.79783950617283950617283951")
    assert result.value.unit == "mL/min"
    assert result.age_years == 75


def test_male_calculation_returns_unquantized_typed_result_and_metadata() -> None:
    result, patient, serum_creatinine, weight = _calculate_cockcroft_gault(
        sex=Sex.MALE
    )

    assert isinstance(result, RenalFunctionResult)
    assert result.value.value == Decimal("84.53785644051130776794493609")
    assert result.value.unit == "mL/min"
    assert result.method is RenalMethod.COCKCROFT_GAULT
    assert result.normalized_to_bsa is False
    assert result.patient_id == patient.patient_id
    assert result.encounter_id == serum_creatinine.encounter_id
    assert result.evaluation_date == date(2026, 7, 22)
    assert result.serum_creatinine_result_id == serum_creatinine.result_id
    assert result.serum_creatinine == serum_creatinine.value
    assert result.serum_creatinine is not serum_creatinine.value
    assert result.serum_creatinine_collected_at == serum_creatinine.collected_at
    assert result.age_years == 45
    assert result.sex is Sex.MALE
    assert result.weight_used == weight
    assert result.weight_used is not weight
    assert result.weight_type_used is WeightType.ACTUAL
    assert result.calculated_at == datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc)
    assert result.provenance.source_type == "calculated"
    assert result.provenance.source_name == "cds.services.renal"
    assert result.provenance.source_identifier == "cockcroft_gault"
    assert result.provenance.version == "1"
    assert result.result_id is None
    assert result.assumptions == []
    assert result.warnings == []
    assert result.evidence == []
    assert result.measured_period == ValueWithUnit()


def test_female_calculation_applies_exact_coefficient() -> None:
    result, _, _, _ = _calculate_cockcroft_gault(sex=Sex.FEMALE)

    assert result.value.value == Decimal("71.85717797443461160275319568")
    assert result.sex is Sex.FEMALE


def test_inputs_are_unchanged_and_repeated_results_are_independently_allocated() -> None:
    patient, serum_creatinine, weight = _cockcroft_gault_inputs(sex=Sex.MALE)
    original_inputs = deepcopy((patient, serum_creatinine, weight))
    arguments = {
        "patient": patient,
        "serum_creatinine_result": serum_creatinine,
        "weight": weight,
        "weight_type": WeightType.ACTUAL,
        "evaluation_date": date(2026, 7, 22),
        "calculated_at": datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    }

    first = calculate_cockcroft_gault(**arguments)
    second = calculate_cockcroft_gault(**arguments)

    assert (patient, serum_creatinine, weight) == original_inputs
    assert first == second
    assert first is not second
    assert first.value is not second.value
    assert first.serum_creatinine is not second.serum_creatinine
    assert first.weight_used is not second.weight_used
    assert first.provenance is not second.provenance


def test_calculation_uses_and_contains_decimal_context() -> None:
    original_context = getcontext().copy()
    try:
        getcontext().prec = 6
        getcontext().rounding = ROUND_DOWN

        result, _, _, _ = _calculate_cockcroft_gault(sex=Sex.MALE)

        assert result.value.value == Decimal("84.53785644051130776794493609")
        assert getcontext().prec == 6
        assert getcontext().rounding == ROUND_DOWN
        with localcontext() as context:
            context.prec = 28
            context.rounding = ROUND_HALF_EVEN
            independently_calculated = (
                (Decimal("140") - Decimal("45")) * Decimal("72.40")
            ) / (Decimal("72") * Decimal("1.13"))
        assert result.value.value == independently_calculated
    finally:
        setcontext(original_context)
