"""Focused tests for pure medication-order task-sufficiency validation."""

from copy import deepcopy
from decimal import Decimal

import pytest

from cds.domain.clinical import MedicationOrder
from cds.domain.support import Assumption, EvidenceItem, Provenance, WarningNote
from cds.domain.value_objects import CodeableConcept, TimeRange, ValueWithUnit
from cds.validation.medication import validate_medication_order_sufficiency

EXPECTED_MEDICATION_SYSTEM = "urn:synthetic:medication-system"
EXPECTED_MEDICATION_CODE = "synthetic-medication-code"
EXPECTED_REGIMEN_IDENTIFIER = "synthetic-regimen-identifier"


def _order(
    *,
    medication_system: str | None = EXPECTED_MEDICATION_SYSTEM,
    medication_code: str | None = EXPECTED_MEDICATION_CODE,
    medication_text: str | None = "Synthetic medication",
    route_system: str | None = "urn:synthetic:route-system",
    route_code: str | None = "synthetic-route-code",
    route_text: str | None = "Synthetic route",
    dose_value: Decimal | None = Decimal("100"),
    dose_unit: str | None = "synthetic-dose-unit",
    frequency_value: Decimal | None = Decimal("8"),
    frequency_unit: str | None = "synthetic-frequency-unit",
    indication_system: str | None = "urn:synthetic:indication-system",
    indication_code: str | None = "synthetic-indication-code",
    indication_text: str | None = "Synthetic indication",
    infusion_value: Decimal | None = Decimal("30"),
    infusion_unit: str | None = "synthetic-infusion-unit",
) -> MedicationOrder:
    return MedicationOrder(
        order_id="synthetic-order-001",
        patient_id="synthetic-patient-001",
        encounter_id="synthetic-encounter-001",
        medication=CodeableConcept(
            text=medication_text,
            system=medication_system,
            code=medication_code,
        ),
        dose=ValueWithUnit(value=dose_value, unit=dose_unit),
        route=CodeableConcept(text=route_text, system=route_system, code=route_code),
        frequency_interval=ValueWithUnit(value=frequency_value, unit=frequency_unit),
        ordered_period=TimeRange(),
        indication=CodeableConcept(
            text=indication_text,
            system=indication_system,
            code=indication_code,
        ),
        infusion_duration=ValueWithUnit(value=infusion_value, unit=infusion_unit),
    )


def _validate(
    *,
    order: MedicationOrder | None = None,
    regimen_identifier: str | None = EXPECTED_REGIMEN_IDENTIFIER,
    expected_medication_system: str = EXPECTED_MEDICATION_SYSTEM,
    expected_medication_code: str = EXPECTED_MEDICATION_CODE,
    expected_regimen_identifier: str = EXPECTED_REGIMEN_IDENTIFIER,
    require_route: bool = True,
    require_dose: bool = True,
    require_frequency: bool = True,
    require_indication: bool = True,
    require_infusion_duration: bool = True,
):
    return validate_medication_order_sufficiency(
        order=order if order is not None else _order(),
        regimen_identifier=regimen_identifier,
        expected_medication_system=expected_medication_system,
        expected_medication_code=expected_medication_code,
        expected_regimen_identifier=expected_regimen_identifier,
        require_route=require_route,
        require_dose=require_dose,
        require_frequency=require_frequency,
        require_indication=require_indication,
        require_infusion_duration=require_infusion_duration,
    )


def _codes(result: object) -> list[str | None]:
    return [issue.code for issue in result.issues]


def test_sufficient_exact_match_with_every_requirement_enabled() -> None:
    result = _validate()

    assert result.is_valid is True
    assert result.issues == []


def test_sufficient_when_rule_specific_facts_are_absent_but_not_required() -> None:
    result = _validate(
        order=_order(
            route_system=None,
            route_code=None,
            dose_value=None,
            dose_unit=None,
            frequency_value=None,
            frequency_unit=None,
            indication_system=None,
            indication_code=None,
            infusion_value=None,
            infusion_unit=None,
        ),
        require_route=False,
        require_dose=False,
        require_frequency=False,
        require_indication=False,
        require_infusion_duration=False,
    )

    assert result == type(result)(is_valid=True, issues=[])


@pytest.mark.parametrize("system", [None, "", " ", "\t\n"])
def test_missing_medication_system_is_distinct(system: str | None) -> None:
    result = _validate(order=_order(medication_system=system))

    assert _codes(result) == ["missing_medication_system"]
    assert result.issues[0].field_path == "order.medication.system"
    assert result.is_valid is False


@pytest.mark.parametrize("code", [None, "", " ", "\t\n"])
def test_missing_medication_code_is_distinct(code: str | None) -> None:
    result = _validate(order=_order(medication_code=code))

    assert _codes(result) == ["missing_medication_code"]
    assert result.issues[0].field_path == "order.medication.code"


def test_medication_display_text_does_not_substitute_for_exact_coding() -> None:
    result = _validate(
        order=_order(
            medication_system=None,
            medication_code=None,
            medication_text="Synthetic display text only",
        )
    )

    assert _codes(result) == ["missing_medication_system", "missing_medication_code"]
    assert "unsupported_medication_identifier" not in _codes(result)


def test_exact_medication_system_mismatch_is_unsupported() -> None:
    result = _validate(order=_order(medication_system="urn:synthetic:other-system"))

    assert _codes(result) == ["unsupported_medication_identifier"]
    assert result.issues[0].field_path == "order.medication"


def test_exact_medication_code_mismatch_is_unsupported() -> None:
    result = _validate(order=_order(medication_code="other-synthetic-code"))

    assert _codes(result) == ["unsupported_medication_identifier"]


@pytest.mark.parametrize(
    ("system", "code"),
    [
        (f" {EXPECTED_MEDICATION_SYSTEM}", EXPECTED_MEDICATION_CODE),
        (EXPECTED_MEDICATION_SYSTEM.upper(), EXPECTED_MEDICATION_CODE),
        (EXPECTED_MEDICATION_SYSTEM, f"{EXPECTED_MEDICATION_CODE} "),
        (EXPECTED_MEDICATION_SYSTEM, EXPECTED_MEDICATION_CODE.upper()),
    ],
)
def test_medication_identifiers_are_not_trimmed_or_case_normalized(
    system: str, code: str
) -> None:
    order = _order(medication_system=system, medication_code=code)

    result = _validate(order=order)

    assert _codes(result) == ["unsupported_medication_identifier"]
    assert order.medication.system == system
    assert order.medication.code == code


@pytest.mark.parametrize("identifier", [None, "", " ", "\t\n"])
def test_missing_regimen_identifier_is_distinct(identifier: str | None) -> None:
    result = _validate(regimen_identifier=identifier)

    assert _codes(result) == ["missing_regimen_identifier"]
    assert result.issues[0].field_path == "regimen_identifier"


def test_exact_regimen_mismatch_is_unsupported() -> None:
    result = _validate(regimen_identifier="other-synthetic-regimen")

    assert _codes(result) == ["unsupported_regimen_identifier"]


@pytest.mark.parametrize(
    "identifier",
    [
        f" {EXPECTED_REGIMEN_IDENTIFIER}",
        f"{EXPECTED_REGIMEN_IDENTIFIER} ",
        EXPECTED_REGIMEN_IDENTIFIER.upper(),
    ],
)
def test_regimen_identifier_is_not_trimmed_or_case_normalized(identifier: str) -> None:
    result = _validate(regimen_identifier=identifier)

    assert _codes(result) == ["unsupported_regimen_identifier"]


def test_missing_required_route_system() -> None:
    result = _validate(order=_order(route_system=None))

    assert _codes(result) == ["missing_required_route_system"]
    assert result.issues[0].field_path == "order.route.system"


def test_missing_required_route_code() -> None:
    result = _validate(order=_order(route_code=None))

    assert _codes(result) == ["missing_required_route_code"]
    assert result.issues[0].field_path == "order.route.code"


def test_route_text_alone_is_insufficient_when_route_is_required() -> None:
    result = _validate(
        order=_order(
            route_system=None,
            route_code=None,
            route_text="Synthetic route text only",
        )
    )

    assert _codes(result) == ["missing_required_route_system", "missing_required_route_code"]


def test_missing_required_dose_value() -> None:
    result = _validate(order=_order(dose_value=None))

    assert _codes(result) == ["missing_required_dose_value"]
    assert result.issues[0].field_path == "order.dose.value"


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_nonpositive_required_dose_values(value: Decimal) -> None:
    result = _validate(order=_order(dose_value=value))

    assert _codes(result) == ["nonpositive_required_dose"]


def test_missing_required_dose_unit() -> None:
    result = _validate(order=_order(dose_unit=None))

    assert _codes(result) == ["missing_required_dose_unit"]
    assert result.issues[0].field_path == "order.dose.unit"


def test_missing_required_frequency_value() -> None:
    result = _validate(order=_order(frequency_value=None))

    assert _codes(result) == ["missing_required_frequency_value"]
    assert result.issues[0].field_path == "order.frequency_interval.value"


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_nonpositive_required_frequency_values(value: Decimal) -> None:
    result = _validate(order=_order(frequency_value=value))

    assert _codes(result) == ["nonpositive_required_frequency"]


def test_missing_required_frequency_unit() -> None:
    result = _validate(order=_order(frequency_unit=None))

    assert _codes(result) == ["missing_required_frequency_unit"]
    assert result.issues[0].field_path == "order.frequency_interval.unit"


def test_missing_required_indication_system() -> None:
    result = _validate(order=_order(indication_system=None))

    assert _codes(result) == ["missing_required_indication_system"]
    assert result.issues[0].field_path == "order.indication.system"


def test_missing_required_indication_code() -> None:
    result = _validate(order=_order(indication_code=None))

    assert _codes(result) == ["missing_required_indication_code"]
    assert result.issues[0].field_path == "order.indication.code"


def test_indication_text_alone_is_insufficient_when_indication_is_required() -> None:
    result = _validate(
        order=_order(
            indication_system=None,
            indication_code=None,
            indication_text="Synthetic indication text only",
        )
    )

    assert _codes(result) == [
        "missing_required_indication_system",
        "missing_required_indication_code",
    ]


def test_missing_required_infusion_duration_value() -> None:
    result = _validate(order=_order(infusion_value=None))

    assert _codes(result) == ["missing_required_infusion_duration_value"]
    assert result.issues[0].field_path == "order.infusion_duration.value"


@pytest.mark.parametrize("value", [Decimal("0"), Decimal("-1")])
def test_nonpositive_required_infusion_duration_values(value: Decimal) -> None:
    result = _validate(order=_order(infusion_value=value))

    assert _codes(result) == ["nonpositive_required_infusion_duration"]


def test_missing_required_infusion_duration_unit() -> None:
    result = _validate(order=_order(infusion_unit=None))

    assert _codes(result) == ["missing_required_infusion_duration_unit"]
    assert result.issues[0].field_path == "order.infusion_duration.unit"


def test_all_optional_fields_may_remain_absent_when_flags_are_false() -> None:
    order = MedicationOrder(
        medication=CodeableConcept(
            system=EXPECTED_MEDICATION_SYSTEM,
            code=EXPECTED_MEDICATION_CODE,
        )
    )

    result = _validate(
        order=order,
        require_route=False,
        require_dose=False,
        require_frequency=False,
        require_indication=False,
        require_infusion_duration=False,
    )

    assert result.is_valid is True
    assert result.issues == []


def test_multiple_findings_follow_exact_requirement_order() -> None:
    result = _validate(
        order=_order(
            medication_system=None,
            medication_code=None,
            route_system=None,
            route_code=None,
            dose_value=Decimal("0"),
            dose_unit=None,
            frequency_value=Decimal("-1"),
            frequency_unit=None,
            indication_system=None,
            indication_code=None,
            infusion_value=None,
            infusion_unit=None,
        ),
        regimen_identifier=None,
    )

    assert _codes(result) == [
        "missing_medication_system",
        "missing_medication_code",
        "missing_regimen_identifier",
        "missing_required_route_system",
        "missing_required_route_code",
        "nonpositive_required_dose",
        "missing_required_dose_unit",
        "nonpositive_required_frequency",
        "missing_required_frequency_unit",
        "missing_required_indication_system",
        "missing_required_indication_code",
        "missing_required_infusion_duration_value",
        "missing_required_infusion_duration_unit",
    ]


def test_every_finding_has_error_severity_message_and_precise_field_path() -> None:
    result = _validate(
        order=_order(
            medication_system=None,
            medication_code=None,
            route_system=None,
            route_code=None,
            dose_value=None,
            dose_unit=None,
            frequency_value=None,
            frequency_unit=None,
            indication_system=None,
            indication_code=None,
            infusion_value=None,
            infusion_unit=None,
        ),
        regimen_identifier=None,
    )

    assert result.is_valid is False
    assert all(issue.severity == "error" for issue in result.issues)
    assert all(issue.message and issue.message.strip() for issue in result.issues)
    assert all(issue.field_path and issue.field_path.strip() for issue in result.issues)


def test_results_issue_lists_and_issue_objects_are_independent_between_calls() -> None:
    first = _validate(order=_order(medication_system=None))
    second = _validate(order=_order(medication_system=None))

    assert first is not second
    assert first.issues is not second.issues
    assert first.issues[0] is not second.issues[0]

    first.issues.clear()

    assert _codes(second) == ["missing_medication_system"]


def test_validator_does_not_mutate_order_nested_objects_or_traceability() -> None:
    order = _order()
    order.assumptions.append(
        Assumption(code="synthetic_fixture", description="Synthetic test data.")
    )
    order.warnings.append(WarningNote(code="synthetic_warning", message="Synthetic."))
    order.evidence.append(EvidenceItem(summary="Synthetic medication-order evidence."))
    order.provenance = Provenance(
        source_type="manual_entry",
        source_identifier="synthetic-order-source-001",
    )
    order_before = deepcopy(order)
    regimen_identifier = EXPECTED_REGIMEN_IDENTIFIER
    expected_values = (
        EXPECTED_MEDICATION_SYSTEM,
        EXPECTED_MEDICATION_CODE,
        EXPECTED_REGIMEN_IDENTIFIER,
        True,
        True,
        True,
        True,
        True,
    )

    result = _validate(order=order, regimen_identifier=regimen_identifier)

    assert result.is_valid is True
    assert order == order_before
    assert regimen_identifier == EXPECTED_REGIMEN_IDENTIFIER
    assert expected_values == (
        EXPECTED_MEDICATION_SYSTEM,
        EXPECTED_MEDICATION_CODE,
        EXPECTED_REGIMEN_IDENTIFIER,
        True,
        True,
        True,
        True,
        True,
    )
    assert order.assumptions is not result.issues
    assert order.warnings is not result.issues
    assert order.evidence is not result.issues


def test_validator_adds_no_calculated_matched_or_derived_clinical_attributes() -> None:
    order = _order()

    result = _validate(order=order)

    assert result.is_valid is True
    for target in (order, result):
        for derived_name in (
            "creatinine_clearance",
            "crcl",
            "renal_function",
            "matched_rule",
            "matched_rule_id",
            "content_version",
            "recommendation",
            "recommendations",
            "alert",
            "alerts",
            "rule_result",
        ):
            assert not hasattr(target, derived_name)
