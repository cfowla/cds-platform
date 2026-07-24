# Domain Conventions

This document defines the stable modeling conventions for the CDS domain layer. It centralizes how
models represent missing data, categorical uncertainty, units, concepts, time, precision,
traceability, validation findings, and result states.

`PROJECT_CHARTER.md` remains authoritative for safety and scope. `FIRST_VERTICAL_SLICE.md` defines
the supported clinical workflow, and `ARCHITECTURE.md` defines component boundaries. Existing
public interfaces and tests remain authoritative for implemented behavior.

## Domain objects are passive truth and result objects

Domain models represent supplied facts, clinical concepts, and structured results. They do not
calculate, validate, normalize, load content, perform I/O, obtain the current time, or select
recommendations.

Task-specific requiredness is enforced by the validation layer. A domain object may therefore be
constructed from partial source data without pretending that the record is sufficient for a
calculation or recommendation.

Derived values such as age, body mass index, selected dosing weight, creatinine clearance, dose
adjustments, and alert policy belong outside source truth objects.

## Missing values, zero, false, and empty values

Use the following distinctions consistently:

- `None` means a value was not supplied, is unknown, is unavailable, or has not been evaluated. The
  enclosing field or result status provides the specific context.
- Numeric zero is a real supplied value. Never use `0`, `Decimal("0")`, a negative sentinel, or an
  empty string to mean missing.
- `False` means an explicitly negative finding. Use `bool | None` when unknown or unevaluated must
  remain distinct from false.
- An empty string is not a missing-data convention. Use `None` when text is absent.
- An empty collection means no items are attached to that object. Mutable collections must use
  `default_factory`.
- `NOT_APPLICABLE`, `INCOMPLETE`, and `FAILED` are outcome states, not synonyms for missing data.

Examples:

```python
from decimal import Decimal

from cds.domain.models import ValueWithUnit

missing_creatinine = ValueWithUnit(value=None, unit="mg/dL")
measured_zero = ValueWithUnit(value=Decimal("0"), unit="mg/dL")
```

The known unit on `missing_creatinine` does not make the numeric value known.

## Unknown categorical values

Use an explicit `UNKNOWN` member when a controlled vocabulary must represent uncertainty. Stable
domain enums use string wire values, such as `Sex.UNKNOWN`, `Severity.UNKNOWN`,
`RenalMethod.UNKNOWN`, and `WeightType.UNKNOWN`.

Keep these meanings distinct:

- `UNKNOWN`: the category was not supplied or cannot be determined.
- `OTHER`: the category is known but is outside the enumerated named options.
- `NOT_APPLICABLE`: the category or result does not apply in the evaluated context.

For controlled `Literal` type aliases, include an explicit `"unknown"` value when uncertainty must
be representable. Do not represent an unknown category with `None`, `""`, or an arbitrary free-text
placeholder when the domain defines an explicit unknown value.

Do not silently infer a category from another field. For example, do not infer route from a
medication name, severity from reaction text, or renal method from a numeric unit.

## Quantities and units

Flexible clinical quantities use `ValueWithUnit`:

```python
@dataclass(slots=True, kw_only=True)
class ValueWithUnit:
    value: Decimal | None = None
    unit: str | None = None
```

Conventions:

- Preserve the supplied numeric value and unit explicitly.
- A value may be missing while its expected or supplied unit remains known.
- Do not infer a unit from a field name, test name, medication, route, or local custom.
- Do not silently normalize, convert, or declare units compatible inside a domain model.
- Unit parsing, compatibility checks, conversion, and supported-unit enforcement belong in mapper,
  validation, or service boundaries.
- Preserve source precision. Do not round a domain quantity for display.
- Related quantities, such as a result and reference range, retain their own units until validation
  establishes compatibility.

An unsupported or ambiguous unit must prevent calculation or rule matching rather than trigger a
guessed conversion.

## First-slice accepted units

The renal vertical slice uses exact, case-sensitive unit strings. A mathematically convertible unit
is not accepted unless a future mapper or validation contract explicitly adds that conversion.

- Supplied body weight must use `kg`.
- Serum creatinine must use `mg/dL`.
- Cockcroft-Gault output is unindexed creatinine clearance in `mL/min`.
- Medication dose, frequency interval, and infusion-duration values must use the exact unit stored
  in the selected reviewed content document. The rule compares both value and unit and performs no
  conversion or alias matching.
- Datetimes used for collection, evaluation, calculation, mapping, or serialization must include a
  usable UTC offset. A naive datetime is not assigned an assumed timezone.

A missing unit and an unsupported unit are separate validation findings, but both stop the first
slice before calculation or recommendation matching when the unit is required.

## Text-only clinical concepts

`CodeableConcept` preserves source text and optional terminology coding:

```python
@dataclass(slots=True, kw_only=True)
class CodeableConcept:
    text: str | None = None
    system: str | None = None
    code: str | None = None
```

Text-only concepts are valid. A problem, allergy substance, allergy reaction, medication, route,
indication, specimen, or other concept may contain text while `system` and `code` remain `None`.

Do not:

- invent a code or terminology system;
- treat text as a validated code;
- discard source text because coding is absent;
- use `"unknown"` or an empty string as fabricated concept text; or
- perform terminology lookup or normalization inside the domain model.

A completely absent concept is represented by a `CodeableConcept` whose fields are all `None`.
Validation decides whether that absence is acceptable for the requested task.

## Dates, datetimes, and ranges

Use `date` for date-only clinical facts and `datetime` for actual instants.

Conventions:

- Datetimes crossing a system boundary must be timezone-aware.
- Naive datetimes are not assigned an assumed timezone.
- Canonical serialization normalizes aware datetimes to UTC and emits an ISO 8601 value with a `Z`
  suffix.
- Domain models do not call `datetime.now()` or otherwise obtain hidden time. Evaluation time is
  supplied explicitly by the caller or application layer.
- `TimeRange.start=None` and `TimeRange.end=None` preserve missing or open boundaries. The enclosing
  model defines whether an absent endpoint means unknown or open-ended.
- Chronology checks, such as end before start, belong in validation.
- Do not derive duration, age, recency, or active status inside a passive model.

## Decimal precision and rounding

Use `Decimal` for clinical quantitative values represented by the domain layer.

Conventions:

- Prefer construction from strings, for example `Decimal("1.20")`, rather than from binary
  floating-point values.
- Preserve the supplied precision and scale where possible.
- Calculators and rule matching use unrounded values.
- Rounding is an explicit presentation or reporting operation and must not replace the reproducible
  underlying value.
- Canonical JSON-compatible serialization emits `Decimal` values as strings so precision and scale
  are not lost.
- Do not coerce `Decimal` to `float` merely to satisfy JSON serialization.

## Validation layers and execution order

Validation is performed before calculation, content-dependent matching, or rule evaluation. The
implemented first-slice workflow uses two distinct validation layers plus application-level identity
and exact-selection checks.

### Structural validation

Structural validation asks whether supplied source facts are internally usable without deriving
clinical values. It includes:

- required value and unit pairing;
- finite and positive quantitative values where required;
- impossible dates and timestamp ordering;
- timezone-aware collection and evaluation times;
- supported laboratory status;
- adult-scope facts that can be established from supplied dates; and
- explicit declaration of a weight type when a weight is supplied.

Structural validators do not calculate age, choose a weight, convert units, infer categories, load
content, or mutate the supplied objects.

### Task-sufficiency validation

Sufficiency validation asks whether structurally usable data are complete enough for one specific
workflow. For the first renal slice, it requires the exact Cockcroft-Gault and rule-selection facts,
including:

- birth date as the implemented age source;
- `Sex.MALE` or `Sex.FEMALE` for the configured coefficient;
- supplied body weight in `kg` and an explicit non-unknown `WeightType`;
- serum creatinine in `mg/dL` with an explicit collection time;
- stable renal function;
- no renal replacement therapy;
- no pregnancy or lactation;
- exact medication, regimen, and content-version identifiers; and
- route, dose, frequency, indication, formulation, and infusion facts required by the selected
  reviewed content.

Sufficiency validation does not make missing data sufficient by adding assumptions. It does not
select a close medication, regimen, content version, or unit.

### Combined validation result

`ValidationResult.is_valid` has three states:

- `None`: validation has not run or remains indeterminate;
- `True`: validation ran and no error-severity issue remains; and
- `False`: at least one error-severity issue prevents the next workflow stage.

Application orchestration combines the structural, sufficiency, identity, and exact-selection
findings. Calculation, content matching, and rule evaluation proceed only when the combined result
is exactly `True`. Expected missing, invalid, or unsupported clinical facts are represented as
validation issues rather than exceptions.

## Validation issue severity

`ValidationIssue` carries a stable `code`, clinician- or developer-readable `message`, optional
`field_path`, and one of these severities:

- `error`: the finding blocks calculation or rule matching. All currently implemented first-slice
  validators emit error-severity issues.
- `warning`: the finding is non-fatal only when the workflow remains supported and sufficient. A
  warning cannot override an error, make missing data sufficient, or authorize a recommendation.
- `unknown`: the passive default before a validator assigns severity. It must not be treated as
  proof that input is valid.

A validation warning is distinct from a result `WarningNote`. Validators describe input findings;
result warnings preserve non-fatal limitations or unsupported-context information with the
structured outcome. Neither type may conceal a critical gap.

## Result-state mapping

`RuleResult.status`, `applied`, and `passed` describe different dimensions and must remain separate.
The first-slice mapping is:

- `success`: exact reviewed content matched one renal band and produced exactly one structured
  recommendation. The rule uses `applied=True` and `passed=True`.
- `success_with_warnings`: a supported result exists with non-fatal limitations. The enum is
  reserved, but the current renal use case does not emit it. A future producer must assign the
  tri-state fields explicitly and may return a recommendation only when all critical requirements
  remain satisfied.
- `incomplete`: missing, invalid, indeterminate, or pre-computation unsupported facts prevented
  calculation or matching, or required reviewed content facts were incomplete. The rule uses
  `applied=False`, `passed=None`, and no recommendation.
- `not_applicable`: a validated calculation or rule context did not match an exact supported rule,
  regimen, content domain, or recommendation-bearing band. Most paths use `applied=False` and
  `passed=None`. A matched no-recommendation band uses `applied=True` and `passed=False`. No path
  returns a recommendation.
- `failed`: a content repository, validation boundary, calculation boundary, rule boundary, or
  unexpected system failure prevented evaluation. The rule uses `applied=False`, `passed=None`, and
  no recommendation.

`passed=False` is not interchangeable with `passed=None`. The former means an applied rule produced
an explicit negative or no-recommendation outcome; the latter means the rule was not applied or was
not evaluable.

## Unsupported and indeterminate contexts

The word "unsupported" describes a cause, not one universal top-level status. Current behavior
depends on the stage at which the condition is identified:

- Missing, invalid, ambiguous, or unsupported facts detected before computation are validation
  errors and produce `ResultStatus.INCOMPLETE`. This currently includes out-of-adult-scope facts,
  unsupported Cockcroft-Gault sex values, unstable renal function, renal replacement therapy,
  pregnancy or lactation, unsupported required units, and missing exact identifiers.
- After valid renal calculation and exact content retrieval, a nonmatching medication, regimen,
  indication, route, formulation, dose, frequency, infusion strategy, renal method, renal unit,
  indexing state, content domain, or registered rule produces `ResultStatus.NOT_APPLICABLE` and no
  recommendation. Unsupported rule outcomes may attach a warning.
- A reviewed renal band that explicitly permits no recommendation produces
  `ResultStatus.NOT_APPLICABLE`, with `applied=True`, `passed=False`, and no recommendation.
- Missing or ineligible required content facts encountered by the rule remain `INCOMPLETE`.
- Missing content at the repository boundary, defective content, calculation-boundary failures, and
  unexpected internal errors produce `FAILED`, not an inferred clinical outcome.

Every non-success path fails closed. It must preserve structured issue or outcome metadata and must
not return a dosing recommendation.

## Assumptions, warnings, evidence, and provenance

Major domain truth and result objects may attach the standard traceability structures.

### `Assumption`

Records an explicit assumption introduced by mapping, validation, calculation, or evaluation. An
assumption must not conceal missing data or silently broaden supported scope. When an assumption
affects an output, attach it to that output.

`applies=None` means the assumption's applicability is unknown or not evaluated; it is distinct from
`False`.

### `WarningNote`

Records a non-fatal limitation, uncertainty, or validation concern. A warning does not make
insufficient data sufficient and must not allow a workflow to bypass a critical validation issue.

### `EvidenceItem`

Records evidence supporting a calculation, rule, warning, or recommendation. Preserve the citation,
source document, evidence level, and source version when available. Evidence metadata does not
execute clinical logic.

### `Provenance`

Records where a fact, content item, or decision originated. Preserve source type, source name,
stable source identifier, capture time, author or reviewer, and version when available.

`captured_at` must be timezone-aware when it crosses a system boundary. Calculated outputs should
preserve the method, inputs, versions, and evaluation time needed for audit and reproduction.

### Safe traceability defaults

Use independent default factories:

```python
assumptions: list[Assumption] = field(default_factory=list)
warnings: list[WarningNote] = field(default_factory=list)
evidence: list[EvidenceItem] = field(default_factory=list)
provenance: Provenance = field(default_factory=Provenance)
```

Never use a shared mutable list or shared nested object as a dataclass default.

## Passive dataclass rules

Domain dataclasses should normally use:

```python
@dataclass(slots=True, kw_only=True)
```

Apply these rules:

- Keep fields explicit, typed, and inspectable.
- Use `None`, explicit unknown categories, and empty default-factory collections as safe incomplete
  defaults.
- Use composition rather than inheritance for shared traceability and value objects.
- Do not perform hidden conversion, inference, lookup, validation, or mutation in `__post_init__`.
- Do not add file, network, database, environment, repository, or interface access.
- Do not add clinical calculations, rule matching, workflow orchestration, or recommendation
  selection.
- Do not add properties that derive clinical values from other fields.
- Do not serialize from model methods; use the canonical serialization utility.
- Keep each instance independent by using `default_factory` for mutable or nested values.

Validation models may describe issues and validity, but validation rule execution remains in
validation functions or services rather than in passive result objects.

## Canonical serialization

Use `cds.utils.serialization.to_jsonable` or `cds.utils.serialization.dumps_json` at serialization
boundaries.

The canonical serializer:

- converts dataclasses using declared field names;
- emits enum wire values;
- emits `date` values as ISO 8601 dates;
- normalizes timezone-aware `datetime` values to UTC with a `Z` suffix;
- emits `Decimal` values as strings;
- converts lists and tuples to JSON arrays;
- requires string dictionary keys; and
- fails explicitly for naive datetimes and unsupported types.

Do not use ad hoc `asdict` plus `json.dumps` paths that bypass these rules. A change to canonical
serialized behavior is a contract change and requires focused tests.

## Review checklist

Before adding or changing a domain model, validator, or result mapping, verify that:

- missing numeric data remains distinguishable from zero;
- unknown booleans remain distinguishable from false where necessary;
- unknown categories have an explicit representation;
- supplied units remain visible and no conversion is hidden;
- first-slice units and content-defined quantity units are matched exactly;
- structural and sufficiency validation remain distinct and run before computation;
- error-severity issues stop the workflow and warnings do not bypass errors;
- non-success states preserve the reason and contain no dosing recommendation;
- text-only concepts remain valid without fabricated coding;
- datetimes are handled as timezone-aware values at boundaries;
- `Decimal` precision is preserved through serialization;
- mutable and nested defaults are independent;
- assumptions, warnings, evidence, and provenance can be attached where needed; and
- the model contains no validation execution, clinical logic, I/O, or orchestration.
