# Model and Interface Reference

> **Prototype only — not for direct clinical use.** Use only synthetic or properly
> de-identified data. This reference describes implemented software contracts; it does not
> authorize diagnosis, prescribing, medication-order verification, or patient-care use.

## Purpose and authority

This document is the implemented reference for CDS domain models, validation result models,
canonical serialization, and the current renal-dose command-line boundary.

Use the repository sources in this order when a statement conflicts:

1. `PROJECT_CHARTER.md` for scope, safety, and change control.
2. `FIRST_VERTICAL_SLICE.md` for the frozen renal workflow.
3. Implemented source and contract tests for current software behavior.
4. `docs/DOMAIN_CONVENTIONS.md` for stable modeling and serialization conventions.
5. This document as a concise field and interface reference.

The models are passive data containers. Validation, calculation, content access, rule matching,
orchestration, serialization, and I/O remain outside the domain objects.

## How to read requiredness

The repository uses two different meanings of requiredness.

### Constructor requiredness

All current domain and validation dataclasses are keyword-only and provide defaults for every
field. They can represent partial source data or an incomplete result. Therefore, no field is
required merely to instantiate these dataclasses.

A defaulted object is not automatically valid or sufficient. `None`, an explicit `UNKNOWN` enum,
an empty `CodeableConcept`, an empty `ValueWithUnit`, or an empty collection preserves missing or
unevaluated state.

### Workflow requiredness

The renal-dose application and its validators decide which facts are required for one evaluation.
A successful first-slice result requires exact identifiers, supported units, explicit population
and renal-context facts, and all regimen facts required by the selected reviewed content.

This reference uses these labels:

- **Required for renal success:** omission or an unsupported value blocks calculation or exact
  content selection.
- **Conditionally required:** required only when the selected content or exact rule requires it.
- **Optional linkage or context:** may support auditability or another future workflow but does not
  independently make the current renal evaluation sufficient.
- **Output-populated:** normally assigned by calculation, rule, application, or mapping code.

## Common missing-data and default rules

- Unknown numeric values use `None`, never zero.
- Unknown booleans use `None` when false must remain distinct from unevaluated.
- Unknown controlled categories use an explicit `UNKNOWN` member when one exists.
- Empty text is not the missing-data convention; use `None`.
- Lists and mappings use independent `default_factory` values.
- Flexible quantities use `ValueWithUnit`; a known unit does not make a missing value known.
- Dates use `date`. Instants use timezone-aware `datetime` values at system boundaries.
- Clinical quantitative values use `Decimal`, normally constructed from strings.
- Domain objects do not infer, normalize, convert, calculate, validate, or serialize themselves.

## Exact first-slice units

The current renal vertical slice accepts exact, case-sensitive unit strings.

- Supplied body weight: `kg`
- Serum creatinine: `mg/dL`
- Unindexed Cockcroft-Gault result: `mL/min`
- Dose, frequency interval, and infusion duration: the exact value and unit in the selected
  reviewed content

No unit aliasing or conversion is performed by the domain models, request mapper, validator,
calculator, or rule matcher.

## Import paths and compatibility

New code should import from the focused modules:

```python
from cds.domain.clinical import LabResult, MedicationOrder, Patient
from cds.domain.enums import ResultStatus, Sex, WeightType
from cds.domain.outputs import RenalFunctionResult, RuleResult
from cds.domain.support import EvidenceItem, Provenance
from cds.domain.value_objects import CodeableConcept, ValueWithUnit
from cds.validation.models import ValidationIssue, ValidationResult
```

Existing imports from `cds.domain.models` remain supported for these compatibility exports:

- `Alert`
- `Allergy`
- `Assumption`
- `CDSRecommendation`
- `CodeableConcept`
- `Contraindication`
- `DoseRecommendation`
- `Encounter`
- `EvidenceItem`
- `LabResult`
- `MedicationOrder`
- `Patient`
- `Problem`
- `Provenance`
- `RenalFunctionResult`
- `RuleResult`
- `TimeRange`
- `ValueWithUnit`
- `VitalSign`
- `WarningNote`

`cds.domain.models` is a compatibility module, not the preferred location for new model
definitions. The package-level `cds.domain` module does not currently re-export these symbols.

## Stable enum wire values

Canonical serialization emits the string values shown below.

### `Sex`

- `male`
- `female`
- `other`
- `unknown`

### `WeightType`

- `actual`
- `ideal`
- `adjusted`
- `other`
- `unknown`

### `RenalMethod`

- `cockcroft_gault`
- `ckd_epi`
- `mdrd`
- `measured_crcl`
- `unknown`

### `Severity`

- `low`
- `moderate`
- `high`
- `critical`
- `unknown`

### `ResultStatus`

- `success`
- `success_with_warnings`
- `incomplete`
- `not_applicable`
- `failed`

The current renal use case does not emit `success_with_warnings`, although the value remains part
of the stable enum.

## Shared value objects

### `ValueWithUnit`

- `value: Decimal | None = None`
- `unit: str | None = None`

Use it for a quantity whose value and unit must remain explicit. The current renal workflow
requires `kg` for supplied body weight and `mg/dL` for serum creatinine.

### `CodeableConcept`

- `text: str | None = None`
- `system: str | None = None`
- `code: str | None = None`

Text-only concepts are valid. The model does not perform terminology lookup or infer coding.

### `TimeRange`

- `start: datetime | None = None`
- `end: datetime | None = None`

A missing endpoint may be unknown or open-ended according to the enclosing model. Chronology and
timezone checks belong to validation.

## Traceability support models

### `Provenance`

- `source_type = "unknown"`
- `source_name: str | None = None`
- `source_identifier: str | None = None`
- `captured_at: datetime | None = None`
- `author: str | None = None`
- `version: str | None = None`

`source_type` accepts `ehr`, `manual_entry`, `interface`, `calculated`, `rule_content`,
`external_api`, or `unknown`.

### `EvidenceItem`

- `summary: str | None = None`
- `level = "unknown"`
- `citation: str | None = None`
- `url: str | None = None`
- `source_document: str | None = None`
- `source_version: str | None = None`
- `provenance: Provenance = Provenance()` through `default_factory`

`level` accepts `guideline`, `primary_literature`, `local_policy`, `expert_opinion`, `computed`, or
`unknown`.

### `Assumption`

- `code: str | None = None`
- `description: str | None = None`
- `applies: bool | None = None`
- `provenance: Provenance = Provenance()` through `default_factory`

`applies=None` means unevaluated or indeterminate. An assumption must not make missing critical
data sufficient.

### `WarningNote`

- `code: str | None = None`
- `message: str | None = None`
- `severity = "unknown"`
- `provenance: Provenance = Provenance()` through `default_factory`

`severity` accepts `info`, `warning`, `high`, `critical`, or `unknown`.

## Shared traceability fields

Each major truth or output model below includes these independent defaults unless stated otherwise:

- `assumptions: list[Assumption] = []` through `default_factory`
- `warnings: list[WarningNote] = []` through `default_factory`
- `evidence: list[EvidenceItem] = []` through `default_factory`
- `provenance: Provenance = Provenance()` through `default_factory`

## Clinical truth models

### `Patient`

Fields:

- `patient_id: str | None = None`
- `birth_date: date | None = None`
- `sex: Sex = Sex.UNKNOWN`
- `actual_body_weight: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `height: ValueWithUnit = ValueWithUnit()` through `default_factory`
- shared traceability fields

Current renal workflow:

- `patient_id` is required and must match the medication order and serum-creatinine result.
- `birth_date` is required as the implemented age source and must establish adult scope.
- `sex` must be exactly `Sex.MALE` or `Sex.FEMALE`.
- `actual_body_weight.value` must be a finite positive `Decimal`.
- `actual_body_weight.unit` must be exactly `kg`.
- The separate declared `WeightType` must not be `UNKNOWN`.
- `height` is optional and is not used by the current renal calculation.

### `Encounter`

Fields:

- `encounter_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_type: CodeableConcept = CodeableConcept()` through `default_factory`
- `period: TimeRange = TimeRange()` through `default_factory`
- `location: str | None = None`
- `service_line: str | None = None`
- `attending_clinician_id: str | None = None`
- shared traceability fields

The current CLI request does not construct an `Encounter`. Encounter fields are optional context
for other boundaries.

### `MedicationOrder`

Fields:

- `order_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `medication: CodeableConcept = CodeableConcept()` through `default_factory`
- `dose: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `route: CodeableConcept = CodeableConcept()` through `default_factory`
- `frequency_interval: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `ordered_period: TimeRange = TimeRange()` through `default_factory`
- `indication: CodeableConcept = CodeableConcept()` through `default_factory`
- `infusion_duration: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `prn: bool | None = None`
- `status: str | None = None`
- shared traceability fields

Current renal workflow:

- `order_id` is required.
- `patient_id` must match `Patient.patient_id`.
- `medication.system` must exactly match the configured coding system.
- `medication.code` and the separate regimen identifier are required exact values.
- Route, dose, frequency, indication, formulation, and infusion facts are conditionally required by
  the selected content and are matched exactly without conversion or inference.
- `encounter_id`, `ordered_period`, `prn`, and `status` are optional current context.

### `LabResult`

Fields:

- `result_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `test: CodeableConcept = CodeableConcept()` through `default_factory`
- `value: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `reference_range_low: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `reference_range_high: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `collected_at: datetime | None = None`
- `resulted_at: datetime | None = None`
- `status: str | None = None`
- `specimen: CodeableConcept = CodeableConcept()` through `default_factory`
- shared traceability fields

Current serum-creatinine workflow:

- `patient_id` must match `Patient.patient_id`.
- `value.value` must be a finite positive `Decimal`.
- `value.unit` must be exactly `mg/dL`.
- `collected_at` is required, timezone-aware, and not after the evaluation time.
- `status` must be exactly `final` or `corrected`.
- `resulted_at` is optional; when present it must be timezone-aware and chronologically valid.
- `result_id`, `test`, reference ranges, `specimen`, and `encounter_id` are optional current links.

### `VitalSign`

Fields:

- `vital_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `vital: CodeableConcept = CodeableConcept()` through `default_factory`
- `value: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `measured_at: datetime | None = None`
- `position: str | None = None`
- `supplemental_oxygen: bool | None = None`
- `status: str | None = None`
- shared traceability fields

`VitalSign` is not used by the current renal CLI. Units remain source values until a mapper or
validator establishes support.

### `Problem`

Fields:

- `problem_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `problem: CodeableConcept = CodeableConcept()` through `default_factory`
- `onset_period: TimeRange = TimeRange()` through `default_factory`
- `recorded_at: datetime | None = None`
- `status: str | None = None`
- `severity: Severity = Severity.UNKNOWN`
- shared traceability fields

`Problem` is not used by the current renal CLI. Text-only problem concepts are valid.

### `Allergy`

Fields:

- `allergy_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `substance: CodeableConcept = CodeableConcept()` through `default_factory`
- `reaction: CodeableConcept = CodeableConcept()` through `default_factory`
- `onset_at: datetime | None = None`
- `recorded_at: datetime | None = None`
- `status: str | None = None`
- `verification_status: str | None = None`
- `severity: Severity = Severity.UNKNOWN`
- shared traceability fields

`Allergy` is not used by the current renal CLI. An empty reaction concept represents an unknown
reaction without fabricating text or coding.

## Output models

### `RenalFunctionResult`

Fields:

- `result_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `method: RenalMethod = RenalMethod.UNKNOWN`
- `value: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `normalized_to_bsa: bool | None = None`
- `evaluation_date: date | None = None`
- `serum_creatinine_result_id: str | None = None`
- `serum_creatinine: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `serum_creatinine_collected_at: datetime | None = None`
- `age_years: int | None = None`
- `sex: Sex = Sex.UNKNOWN`
- `weight_used: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `weight_type_used: WeightType = WeightType.UNKNOWN`
- `measured_period: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `calculated_at: datetime | None = None`
- shared traceability fields

For a current Cockcroft-Gault result, `method` is `cockcroft_gault`, `value.unit` is `mL/min`, and
`normalized_to_bsa` is false. The calculation preserves unrounded output and exact input context.

### `Contraindication`

Fields:

- `code: str | None = None`
- `summary: str | None = None`
- `applies: bool | None = None`
- `rationale: str | None = None`
- `severity: Severity = Severity.UNKNOWN`
- `related_problem: CodeableConcept | None = None`
- `related_medication: CodeableConcept | None = None`
- `related_lab: CodeableConcept | None = None`
- shared traceability fields

`applies=None` means unevaluated or indeterminate, not false.

### `DoseRecommendation`

Fields:

- `medication: CodeableConcept = CodeableConcept()` through `default_factory`
- `recommended_dose: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `recommended_route: CodeableConcept = CodeableConcept()` through `default_factory`
- `frequency_interval: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `infusion_duration: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `max_single_dose: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `max_daily_dose: ValueWithUnit = ValueWithUnit()` through `default_factory`
- `regimen_variant: str | None = None`
- `rationale: str | None = None`
- shared traceability fields

All regimen quantities preserve the content-defined value and unit. Missing quantities remain
`None` and do not imply zero.

### `CDSRecommendation`

Fields:

- `recommendation_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `title: str | None = None`
- `action = "unknown"`
- `strength = "unknown"`
- `summary: str | None = None`
- `rationale: str | None = None`
- `renal_function_result: RenalFunctionResult | None = None`
- `dose_recommendation: DoseRecommendation | None = None`
- `contraindications: list[Contraindication] = []` through `default_factory`
- `suggested_monitoring: list[str] = []` through `default_factory`
- `linked_order_id: str | None = None`
- `linked_rule_id: str | None = None`
- shared traceability fields

`action` accepts `continue`, `adjust_dose`, `hold`, `stop`, `avoid`, `monitor`, `switch`, `clarify`,
`none`, or `unknown`.

`strength` accepts `info`, `suggest`, `recommend`, `strongly_recommend`, or `unknown`.

### `Alert`

Fields:

- `alert_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `category = "unknown"`
- `severity = "unknown"`
- `title: str | None = None`
- `message: str | None = None`
- `interruptive: bool | None = None`
- `recommendation: CDSRecommendation | None = None`
- `linked_order_id: str | None = None`
- `linked_rule_id: str | None = None`
- `deduplication_key: str | None = None`
- shared traceability fields

`category` accepts `dosing`, `contraindication`, `interaction`, `monitoring`, `allergy`,
`duplication`, `general`, or `unknown`.

The domain model does not decide display, interruption, routing, suppression, or deduplication
policy.

### `RuleResult`

Fields:

- `rule_id: str | None = None`
- `patient_id: str | None = None`
- `encounter_id: str | None = None`
- `status: ResultStatus = ResultStatus.INCOMPLETE`
- `applied: bool | None = None`
- `passed: bool | None = None`
- `summary: str | None = None`
- `renal_function_result: RenalFunctionResult | None = None`
- `recommendations: list[CDSRecommendation] = []` through `default_factory`
- `alerts: list[Alert] = []` through `default_factory`
- `supporting_data: dict[str, SupportingValue] = {}` through `default_factory`
- `evaluated_at: datetime | None = None`
- shared traceability fields

The safe default is `incomplete` with `applied=None` and `passed=None`.

Current state semantics:

- `success`: `applied=True`, `passed=True`, and one exact supported recommendation.
- `success_with_warnings`: reserved; not currently emitted by the renal use case.
- `incomplete`: pre-computation validation or sufficiency failure; no recommendation.
- `not_applicable`: validated exact nonmatch or an applied no-recommendation band.
- `failed`: content, calculation, rule, application, or other system failure.

`passed=False` means an applied rule produced an explicit negative or no-recommendation outcome.
It is not interchangeable with `passed=None`.

## Validation models

### `ValidationIssue`

- `code: str | None = None`
- `message: str | None = None`
- `severity = "unknown"`
- `field_path: str | None = None`

`severity` accepts `error`, `warning`, or `unknown`. Current first-slice validators emit blocking
`error` findings.

### `ValidationResult`

- `is_valid: bool | None = None`
- `issues: list[ValidationIssue] = []` through `default_factory`

`is_valid=None` means validation has not run or remains indeterminate. Calculation and rule
matching proceed only when the combined result is exactly true.

## Canonical serialization

Use `cds.utils.serialization.to_jsonable` or `dumps_json` at serialization boundaries.

The canonical serializer:

- converts dataclasses using declared field names;
- emits enum wire values;
- emits `None` as JSON `null`;
- emits `date` values as ISO calendar dates;
- normalizes aware `datetime` values to UTC and emits a `Z` suffix;
- emits `Decimal` values as strings;
- converts lists and tuples to JSON arrays;
- requires string mapping keys;
- fails for naive datetimes and unsupported types; and
- uses compact, deterministic JSON with sorted keys in `dumps_json`.

Do not use ad hoc `asdict` plus `json.dumps` paths. Do not convert clinical `Decimal` values to
binary floating point for serialization.

## Renal-dose CLI request

### Wire rules

`RenalDoseCLIRequest` is a passive, flat DTO. All fields default to `None` so malformed or missing
wire data can be represented before mapping.

The JSON request boundary applies these rules:

- The payload must be one JSON object.
- Field names are exact; unknown fields are rejected.
- Clinical numerics must be JSON strings or `null`, not JSON numbers.
- Boolean context fields must be JSON booleans or `null`.
- Dates use ISO calendar-date strings.
- Datetimes use ISO strings with a usable UTC offset.
- Enum values and identifiers are exact and case-sensitive.
- Mapping performs no clinical validation, normalization, inference, conversion, calculation, or
  content lookup.

### Exact request fields

Required for use-case invocation or renal success:

- `patient_id: string`
- `birth_date: ISO date string`
- `sex: "male" | "female"` for the current calculation
- `weight_value: Decimal string`
- `weight_unit: "kg"`
- `weight_type: exact WeightType wire value other than "unknown"`
- `serum_creatinine_value: Decimal string`
- `serum_creatinine_unit: "mg/dL"`
- `serum_creatinine_collected_at: offset-aware ISO datetime string`
- `serum_creatinine_status: "final" | "corrected"`
- `renal_function_stable: true`
- `renal_replacement_therapy: false`
- `pregnant_or_lactating: false`
- `medication_order_id: string`
- `medication_system: exact configured coding-system string`
- `medication_code: exact supported medication code`
- `regimen_id: exact supported regimen identifier`
- `requested_content_version: exact content version`
- `evaluation_date: ISO date string`
- `evaluated_at: offset-aware ISO datetime string`

`evaluation_date` must equal the calendar date represented by `evaluated_at`.

Conditionally required for an exact successful rule match:

- `formulation_id`
- `dose_value`
- `dose_unit`
- `route_system`
- `route_code`
- `frequency_interval_value`
- `frequency_interval_unit`
- `indication_system`
- `indication_code`
- `infusion_duration_value`
- `infusion_duration_unit`

The selected reviewed content determines which of these regimen facts are required. Supplied facts
must match exactly; the interface does not infer or convert them.

Optional current audit link:

- `serum_creatinine_result_id`

There is no encounter field in the current CLI DTO.

### Shape-only request example

The placeholders below show types and field names. They are not reviewed clinical content and are
not an executable dosing example.

```json
{
  "birth_date": "2000-01-01",
  "dose_unit": "<exact-content-unit>",
  "dose_value": "<decimal-string>",
  "evaluated_at": "2026-07-24T12:00:00-04:00",
  "evaluation_date": "2026-07-24",
  "formulation_id": "<exact-formulation-id>",
  "frequency_interval_unit": "<exact-content-unit>",
  "frequency_interval_value": "<decimal-string>",
  "indication_code": "<exact-indication-code>",
  "indication_system": "<exact-indication-system>",
  "infusion_duration_unit": "<exact-content-unit>",
  "infusion_duration_value": "<decimal-string>",
  "medication_code": "<exact-medication-code>",
  "medication_order_id": "synthetic-order-001",
  "medication_system": "<configured-medication-system>",
  "patient_id": "synthetic-patient-001",
  "pregnant_or_lactating": false,
  "regimen_id": "<exact-regimen-id>",
  "renal_function_stable": true,
  "renal_replacement_therapy": false,
  "requested_content_version": "<exact-content-version>",
  "route_code": "<exact-route-code>",
  "route_system": "<exact-route-system>",
  "serum_creatinine_collected_at": "2026-07-24T08:00:00-04:00",
  "serum_creatinine_result_id": "synthetic-lab-001",
  "serum_creatinine_status": "final",
  "serum_creatinine_unit": "mg/dL",
  "serum_creatinine_value": "<decimal-string>",
  "sex": "female",
  "weight_type": "actual",
  "weight_unit": "kg",
  "weight_value": "<decimal-string>"
}
```

## Renal-dose CLI response

The response mapper fixes two top-level keys:

- `validation`
- `rule_result`

`validation` is the canonical serialization of `ValidationResult`. `rule_result` is the canonical
serialization of `RuleResult`, including nested renal results, recommendations, alerts,
traceability, rule identifiers, supporting data, and content-version metadata when present.

Shape:

```json
{
  "rule_result": {
    "alerts": [],
    "applied": null,
    "assumptions": [],
    "encounter_id": null,
    "evaluated_at": "2026-07-24T16:00:00Z",
    "evidence": [],
    "passed": null,
    "patient_id": "synthetic-patient-001",
    "provenance": {
      "author": null,
      "captured_at": null,
      "source_identifier": null,
      "source_name": null,
      "source_type": "unknown",
      "version": null
    },
    "recommendations": [],
    "renal_function_result": null,
    "rule_id": null,
    "status": "incomplete",
    "summary": null,
    "supporting_data": {},
    "warnings": []
  },
  "validation": {
    "is_valid": false,
    "issues": []
  }
}
```

The shape example illustrates defaults, not a valid completed evaluation. A non-success result must
not contain a dosing recommendation.

## CLI command behavior

`cds.interfaces.cli.main()` accepts:

- one positional input-file path;
- `-o` or `--output` for an optional canonical JSON output path; and
- `--summary` for presentation-only text written to standard error.

Without `--output`, canonical JSON is written to standard output. Summary text is never mixed into
the canonical JSON stream.

Exit codes:

- `0`: success or success with warnings
- `1`: system failure
- `2`: malformed, unmappable, incomplete, or unit-invalid input
- `3`: unsupported or not-applicable request, including exact content not found
- `4`: content repository or content-validation failure

Diagnostics are sanitized. The CLI does not emit exception messages, payloads, tracebacks, or
patient details in error text.

## Current interface limitations

- `cds.interfaces.cli` is dependency-injected and requires a configured `RenalDoseUseCase`.
- There is no installed console-script entry point in `pyproject.toml`.
- There is no standalone production composition root that selects repositories, content, or rules.
- The saved walkthrough injects canned synthetic results and does not calculate from clinical
  content.
- The walkthrough does not make draft content reviewed or patient-care eligible.
- No API or EHR interface is implemented or authorized by the current first-slice contract.
- The CLI accepts one request object at a time; no batch, streaming, persistence, or network
  transport contract is defined.
- The interface does not normalize terminology, alias identifiers, convert units, or infer missing
  clinical context.
- The interface does not replace unit, integration, contract, content, or independent clinical
  verification.

Current reproducible interface verification remains:

```bash
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

Expected output:

```text
7 synthetic CLI walkthrough scenarios verified.
```

## Contract-change boundary

Treat any change to the following as a public or serialized contract change requiring focused
tests and explicit review:

- model field names, types, or safe defaults;
- enum wire values;
- `cds.domain.models` compatibility exports;
- canonical date, datetime, Decimal, collection, or mapping serialization;
- request field names or wire types;
- response top-level keys or nested field names;
- CLI output-stream behavior or exit-code mapping; or
- fail-closed behavior for incomplete, unsupported, or failed evaluations.
