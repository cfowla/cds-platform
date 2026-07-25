"""Tests for renal-function calculation services."""

from copy import deepcopy
from datetime import date, datetime, timezone
from decimal import ROUND_DOWN, ROUND_HALF_EVEN, Decimal, getcontext, localcontext, setcontext

import pytest

import cds.services.renal as renal_service
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


def _valid_calculation_arguments() -> dict[str, object]:
    patient, serum_creatinine, weight = _cockcroft_gault_inputs(sex=Sex.MALE)
    return {
        "patient": patient,
        "serum_creatinine_result": serum_creatinine,
        "weight": weight,
        "weight_type": WeightType.ACTUAL,
        "evaluation_date": date(2026, 7, 22),
        "calculated_at": datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    }


def _decimal_context_state() -> dict[str, object]:
    context = getcontext()
    return {
        "prec": context.prec,
        "rounding": context.rounding,
        "Emin": context.Emin,
        "Emax": context.Emax,
        "capitals": context.capitals,
        "clamp": context.clamp,
        "traps": context.traps.copy(),
        "flags": context.flags.copy(),
    }


def _assert_calculation_error_without_result(
    arguments: dict[str, object],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fail_if_result_is_constructed(**_: object) -> RenalFunctionResult:
        pytest.fail("A defensive failure must not construct a renal result.")

    monkeypatch.setattr(
        renal_service,
        "RenalFunctionResult",
        fail_if_result_is_constructed,
    )
    with pytest.raises(CalculationError):
        calculate_cockcroft_gault(**arguments)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("argument_name", "invalid_value"),
    [
        ("patient", None),
        ("patient", object()),
        ("serum_creatinine_result", None),
        ("serum_creatinine_result", object()),
        ("weight", None),
        ("weight", object()),
        ("evaluation_date", None),
        ("evaluation_date", "2026-07-22"),
        ("evaluation_date", datetime(2026, 7, 22, tzinfo=timezone.utc)),
        ("calculated_at", None),
        ("calculated_at", "2026-07-22T09:00:00Z"),
        ("calculated_at", datetime(2026, 7, 22, 9, 0)),
    ],
)
def test_missing_or_malformed_required_inputs_raise_calculation_error(
    argument_name: str,
    invalid_value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    arguments[argument_name] = invalid_value

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize("birth_date", [None, "1980-07-23"])
def test_missing_or_malformed_birth_date_raises_calculation_error(
    birth_date: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    patient = arguments["patient"]
    assert isinstance(patient, Patient)
    patient.birth_date = birth_date  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize("sex", [Sex.UNKNOWN, Sex.OTHER, None, "male"])
def test_unsupported_sex_raises_calculation_error(
    sex: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    patient = arguments["patient"]
    assert isinstance(patient, Patient)
    patient.sex = sex  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize(
    "value",
    [
        None,
        1.13,
        Decimal("NaN"),
        Decimal("sNaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        Decimal("0"),
        Decimal("-0.01"),
    ],
)
def test_invalid_serum_creatinine_raises_only_calculation_error(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    lab = arguments["serum_creatinine_result"]
    assert isinstance(lab, LabResult)
    lab.value.value = value  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize(
    "unit",
    [None, "", " ", "MG/DL", " mg/dL ", "mg/L", "µmol/L"],
)
def test_non_exact_creatinine_unit_raises_calculation_error_without_conversion(
    unit: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    lab = arguments["serum_creatinine_result"]
    assert isinstance(lab, LabResult)
    lab.value.unit = unit

    _assert_calculation_error_without_result(arguments, monkeypatch)
    assert lab.value.value == Decimal("1.13")
    assert lab.value.unit == unit


@pytest.mark.parametrize("value", [None, object()])
def test_missing_or_malformed_creatinine_quantity_raises_calculation_error(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    lab = arguments["serum_creatinine_result"]
    assert isinstance(lab, LabResult)
    lab.value = value  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize(
    "collected_at",
    [None, date(2026, 7, 22), datetime(2026, 7, 22, 8, 30)],
)
def test_missing_or_malformed_collection_time_raises_calculation_error(
    collected_at: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    lab = arguments["serum_creatinine_result"]
    assert isinstance(lab, LabResult)
    lab.collected_at = collected_at  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize(
    "value",
    [
        None,
        72.4,
        Decimal("NaN"),
        Decimal("sNaN"),
        Decimal("Infinity"),
        Decimal("-Infinity"),
        Decimal("0"),
        Decimal("-0.01"),
    ],
)
def test_invalid_supplied_weight_raises_only_calculation_error(
    value: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    weight = arguments["weight"]
    assert isinstance(weight, ValueWithUnit)
    weight.value = value  # type: ignore[assignment]

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize("unit", [None, "", " ", "KG", " kg ", "lb", "g"])
def test_non_exact_weight_unit_raises_calculation_error_without_conversion(
    unit: str | None,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    weight = arguments["weight"]
    assert isinstance(weight, ValueWithUnit)
    weight.unit = unit

    _assert_calculation_error_without_result(arguments, monkeypatch)
    assert weight.value == Decimal("72.40")
    assert weight.unit == unit


@pytest.mark.parametrize("weight_type", [None, WeightType.UNKNOWN, "actual", object()])
def test_unknown_or_malformed_weight_type_raises_calculation_error(
    weight_type: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    arguments["weight_type"] = weight_type

    _assert_calculation_error_without_result(arguments, monkeypatch)


def test_future_birth_date_raises_calculation_error_without_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    arguments = _valid_calculation_arguments()
    patient = arguments["patient"]
    assert isinstance(patient, Patient)
    patient.birth_date = date(2026, 7, 23)

    _assert_calculation_error_without_result(arguments, monkeypatch)


@pytest.mark.parametrize(
    "creatinine",
    [Decimal("0.000001"), Decimal("1000000")],
)
def test_finite_positive_extreme_creatinine_is_used_exactly_as_supplied(
    creatinine: Decimal,
) -> None:
    arguments = _valid_calculation_arguments()
    patient = arguments["patient"]
    lab = arguments["serum_creatinine_result"]
    weight = arguments["weight"]
    assert isinstance(patient, Patient)
    assert isinstance(lab, LabResult)
    assert isinstance(weight, ValueWithUnit)
    lab.value.value = creatinine
    original_context_state = _decimal_context_state()

    result = calculate_cockcroft_gault(**arguments)  # type: ignore[arg-type]

    with localcontext() as context:
        context.prec = 28
        context.rounding = ROUND_HALF_EVEN
        expected = (
            (Decimal("140") - Decimal("45")) * weight.value
        ) / (Decimal("72") * creatinine)
    assert result.value.value == expected
    assert result.serum_creatinine.value is creatinine
    assert result.serum_creatinine.value.as_tuple() == creatinine.as_tuple()
    assert _decimal_context_state() == original_context_state


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


@pytest.mark.parametrize(
    ("serum_creatinine", "expected_value", "expected_relation"),
    [
        (
            Decimal("0.99999"),
            Decimal("60.00060000600006000060000600"),
            1,
        ),
        (Decimal("1"), Decimal("60"), 0),
        (
            Decimal("1.00001"),
            Decimal("59.99940000599994000059999400"),
            -1,
        ),
    ],
)
def test_future_band_comparison_preserves_unrounded_value(
    serum_creatinine: Decimal,
    expected_value: Decimal,
    expected_relation: int,
) -> None:
    """Keep synthetic threshold cases distinct before any future band match."""

    patient = Patient(
        patient_id="synthetic-threshold-patient",
        birth_date=date(1958, 7, 22),
        sex=Sex.MALE,
    )
    lab = LabResult(
        result_id="synthetic-threshold-creatinine",
        patient_id=patient.patient_id,
        encounter_id="synthetic-threshold-encounter",
        value=ValueWithUnit(value=serum_creatinine, unit="mg/dL"),
        collected_at=datetime(2026, 7, 22, 8, 0, tzinfo=timezone.utc),
    )

    result = calculate_cockcroft_gault(
        patient=patient,
        serum_creatinine_result=lab,
        weight=ValueWithUnit(value=Decimal("60"), unit="kg"),
        weight_type=WeightType.ACTUAL,
        evaluation_date=date(2026, 7, 22),
        calculated_at=datetime(2026, 7, 22, 9, 0, tzinfo=timezone.utc),
    )

    stored_value = result.value.value
    assert stored_value == expected_value
    if expected_relation < 0:
        assert stored_value < Decimal("60")
    elif expected_relation > 0:
        assert stored_value > Decimal("60")
    else:
        assert stored_value == Decimal("60")

    with localcontext() as context:
        context.prec = 28
        context.rounding = ROUND_HALF_EVEN
        assert stored_value.quantize(Decimal("0.1")) == Decimal("60.0")


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
