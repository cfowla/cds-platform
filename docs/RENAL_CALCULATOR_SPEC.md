# Adult Cockcroft–Gault Renal Calculator Specification

> **Prototype only — not for direct clinical use.** This specification is for research,
> education, and software development with synthetic or properly de-identified data. It does
> not authorize patient-care use.

## 1. Purpose and authority

This document is the normative calculation contract for the pure adult Cockcroft–Gault renal
calculator in the frozen first vertical slice. It clarifies calculation behavior without changing
the supported population, renal method, medications, clinical-content scope, intended users,
interfaces, or safety behavior defined elsewhere in the repository.

When implementing the calculator, this specification governs calculation details. Structural and
task-sufficiency validation remain governed by the validation contracts and must complete
successfully before the calculator is invoked.

## 2. Scope and component boundary

This specification applies only to:

- adults within the frozen first-slice population;
- unindexed Cockcroft–Gault creatinine clearance;
- output in the exact canonical unit `mL/min`;
- validated, explicitly supplied clinical facts; and
- a pure, deterministic calculation service with no I/O, content loading, system clock access,
  or mutable global state.

The calculator accepts only already-validated inputs. Expected missing, invalid, unsupported,
ambiguous, or out-of-scope clinical facts must be handled by structured validation before the
calculator boundary. Those expected clinical gaps must not be converted into calculator
assumptions or calculator exceptions.

The calculator does not select clinical content, match renal bands, construct a dosing
recommendation, or determine the final application-level evaluation status.

## 3. Equation contract

The future calculator must implement exactly this equation:

```text
base_crcl =
    ((140 - age_years) * weight_kg)
    / (72 * serum_creatinine_mg_dl)

crcl =
    base_crcl                         for Sex.MALE
    base_crcl * Decimal("0.85")       for Sex.FEMALE
```

Contract requirements:

- The result is unindexed creatinine clearance, not normalized estimated glomerular filtration
  rate.
- The calculator does not select a body-weight method.
- The supplied weight value and declared `WeightType` are used unchanged after validation.
- Interpolation, normalization, extrapolation, and alternate renal equations are prohibited.
- The `Decimal("0.85")` coefficient is applied only to `Sex.FEMALE`.
- `Sex.OTHER` and `Sex.UNKNOWN` fail closed during validation and never reach the calculator with
  an inferred coefficient.

No equation implementation is added by Day 29.

## 4. Decimal arithmetic contract

The future calculator must:

- use `Decimal` for clinical numeric operands;
- convert the integer `age_years` operand exactly to `Decimal` for calculation;
- perform arithmetic inside a local `decimal.localcontext()`;
- set the local calculation precision to 28 significant digits;
- set the local rounding mode to `ROUND_HALF_EVEN`;
- construct constants from strings, including `Decimal("140")`, `Decimal("72")`, and
  `Decimal("0.85")`;
- never construct calculation operands from binary `float`;
- never modify the process-wide Decimal context;
- never call `quantize()` on the stored renal result; and
- store the Decimal produced by the defined local calculation context as the underlying result.

Canonical serialization continues to emit the stored `Decimal` as a string.

In this specification, **unrounded** means that no presentation quantization is applied to the
stored result. Finite Decimal division still operates within the documented 28-significant-digit,
`ROUND_HALF_EVEN` calculation context.

## 5. Rounding and rule-matching boundary

The calculator returns only the underlying unquantized result.

- Renal-band matching must use that underlying value.
- A rounded display value must never replace, mutate, or be substituted for the underlying value.
- Display formatting belongs outside the calculator.
- Day 29 adds no display-rounding implementation.

A later presentation contract may choose a display scale or notation, but it cannot alter the
stored result or the value used for renal-band matching.

## 6. Serum-creatinine floors, caps, and substitutions

The first slice applies:

- no serum-creatinine floor;
- no serum-creatinine cap;
- no age-based substitution;
- no rounding of a low serum-creatinine value to another value;
- no adjustment based on body composition or clinical judgment; and
- no hidden correction factor other than the explicitly specified female coefficient.

The calculator must use the exact validated positive serum-creatinine value supplied to it. Zero,
negative, missing, or otherwise invalid values must be rejected before calculation rather than
altered.

## 7. Exact unit contract

The implemented first-slice unit vocabulary is:

| Quantity | Exact accepted unit |
|---|---|
| Body weight | `kg` |
| Serum creatinine | `mg/dL` |
| Renal result | `mL/min` |

Matching is case-sensitive and whitespace-sensitive. The first slice performs no unit
normalization or conversion.

For body weight, values such as `KG`, `" kg "`, `lb`, `g`, or any other non-exact unit are
unsupported. For serum creatinine, values such as `MG/DL`, `" mg/dL "`, `mg%`, `mg/L`, and
`µmol/L` are unsupported even when a conversion might be mathematically possible. The exact
canonical `kg` and `mg/dL` spellings remain the only accepted calculator-input units.

No conversion helper or broader unit vocabulary is part of this specification.

## 8. Renal-stability contract

Renal stability is an explicit caller-supplied clinical fact.

- `renal_function_stable=True` is required before calculation.
- `renal_function_stable=None` means required information is missing and maps to an incomplete
  evaluation at the application boundary.
- `renal_function_stable=False` means the patient is outside the first-slice calculation scope and
  maps to a not-applicable evaluation at the application boundary.
- The calculator does not infer stability from creatinine values, collection times, trends,
  diagnoses, or encounter context.
- Acute or rapidly changing renal function produces no renal calculation and no dosing
  recommendation.

Day 29 does not add renal-trend analysis or an acute-kidney-injury detector.

## 9. Age derivation contract

`Patient.birth_date` plus an explicit caller-supplied `evaluation_date` is the only first-slice
age-input API. The first-slice calculator does not accept an independently supplied integer age
as an alternative input. No function may obtain the current date or time implicitly.

The public pure helper is:

```python
derive_age_years(*, birth_date: date, evaluation_date: date) -> int
```

It returns completed calendar years:

- on the day before a birthday, the new year of age has not been reached;
- on the birthday, the new year of age has been reached; and
- after the birthday, the incremented age remains in effect.

For a February 29 birth, age increments on February 29 in a leap evaluation year. In a non-leap
evaluation year, age does not increment on February 28 and increments on March 1. The adult
structural-validation boundary uses the same convention.

The expected workflow is to run structural validation and task-sufficiency validation before age
derivation. A birth date after the evaluation date is ordinary invalid clinical input and is
reported by structural validation through the `birth_date_after_evaluation` issue. As defensive
enforcement of the validated-service boundary, `derive_age_years` raises the existing typed
`CalculationError` if such a date reaches the service. The helper does not clamp the date, return
zero, fabricate an age, or create a second user-facing validation mechanism.

The returned integer is the exact age later stored in `RenalFunctionResult.age_years` and used by
the Cockcroft–Gault equation. Identical explicit inputs must always produce the same result. Day 30
implements age derivation only; the Cockcroft–Gault equation remains unimplemented.

## 10. Reproducibility metadata

The future calculator must populate the existing `RenalFunctionResult` structure with at least:

- `method=RenalMethod.COCKCROFT_GAULT`;
- `value.value` containing the unquantized Decimal result;
- `value.unit="mL/min"`;
- `normalized_to_bsa=False`;
- an explicit `evaluation_date`;
- the source serum-creatinine result identifier;
- the exact serum-creatinine value and unit;
- the serum-creatinine collection time;
- the exact `age_years` used;
- the exact `Sex` used;
- the exact weight value and unit;
- the exact `WeightType` used;
- a caller-supplied timezone-aware `calculated_at`;
- calculation provenance; and
- an equation or implementation version.

The minimum calculated-output provenance is:

```text
source_type: calculated
source_name: cds.services.renal
source_identifier: cockcroft_gault
version: 1
```

These values use the existing traceability models. Day 29 adds no output fields. A future service
module may define a module-level implementation-version constant, but this task does not create
one.

The calculator must not generate a hidden timestamp. Both `evaluation_date` and `calculated_at`
are supplied explicitly by the caller, and `calculated_at` must be timezone-aware.

## 11. Failure boundary

The future calculator accepts only inputs that have already passed structural and task-sufficiency
validation. Expected clinical gaps must never reach it.

A typed `CalculationError` is reserved for unexpected calculation or internal contract failures,
such as an impossible denominator reaching the calculator despite successful validation. It must
not represent ordinary missing data, unsupported sex, unstable renal function, unsupported units,
or other expected clinical gaps.

The calculator must not:

- construct a dosing recommendation;
- select or load clinical content;
- match a medication rule; or
- map the final top-level workflow status.

## 12. Future implementation-verification matrix

These are specification acceptance cases for later implementation. Day 29 does not implement or
unskip calculator tests.

| Case | Required proof |
|---|---|
| Independently calculated male case | Exact equation result agrees with an independent Decimal calculation. |
| Independently calculated female case | Exact equation result agrees with an independent Decimal calculation including `Decimal("0.85")`. |
| Sex coefficient boundary | The `0.85` coefficient is applied only to `Sex.FEMALE`; unsupported sex values are rejected before calculation. |
| Weight preservation | Exact supplied weight value, unit, and `WeightType` are retained and used unchanged. |
| No creatinine floor or cap | Low and high positive validated values are used exactly as supplied. |
| Local Decimal context | Result is deterministic when the process-wide Decimal precision or rounding mode has been changed by unrelated code. |
| Unrounded storage | Stored `value.value` is the unquantized result produced by the 28-digit local context. |
| Rule boundary | A renal-band boundary case proves matching uses the unrounded stored value, not a display value. |
| Exact accepted units | Only `kg`, `mg/dL`, and result unit `mL/min` satisfy the first-slice contract. |
| Unsupported units | Non-exact or convertible units are rejected by validation before calculator invocation. |
| Renal stability meanings | Missing stability yields incomplete; explicitly unstable function yields not applicable; neither invokes calculation. |
| Input immutability | Patient, laboratory, weight, and traceability input objects remain unchanged. |
| Explicit times | Caller-supplied evaluation date and timezone-aware calculation time are retained exactly. |
| Reproducibility metadata | Method, input snapshot, provenance, and implementation version are populated as specified. |
| Independent equivalent result | Identical validated input produces an equivalent independently allocated result with no shared mutable state. |

## 13. Day 29 non-goals

Day 29 does not implement a calculator, service module, age derivation, validation change, unit
conversion, body-weight derivation, clinical content, renal bands, medication rules,
recommendations, orchestration, mapper, repository, interface, dependency, or compatibility
export. The existing skipped calculator placeholder remains skipped.
