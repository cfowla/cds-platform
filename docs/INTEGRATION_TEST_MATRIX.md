# Renal-Dose Integration Test Matrix

> **Prototype safety boundary:** This matrix is for research, education, and software development only. Use synthetic or properly de-identified data. It does not validate clinical content and must not be used for patient-care decisions.

## Purpose

This matrix defines the bounded full-flow coverage to implement in Day 72. The tests must exercise the existing renal-dose application path from structural and sufficiency validation through exact content retrieval, unrounded Cockcroft–Gault calculation, deterministic rule selection, and the standard structured result.

The matrix records coverage only. It does not add clinical content, approve draft content, change a renal boundary, or expand the first vertical slice.

## Test-harness rules

- Use only synthetic identifiers and values.
- Use the production `RenalDoseUseCase` orchestration boundary; do not bypass validation or inject a precomputed renal result into a full-flow success case.
- Clone draft content into an in-memory repository with an explicit test-only `reviewed` override. Label the override as software-fixture eligibility, not clinical review.
- Keep the repository YAML unchanged and draft-ineligible.
- Use exact, case-sensitive medication, regimen, formulation, route, indication, unit, and content-version values.
- Drive renal-band ownership with the unrounded calculated `Decimal` value. Do not round before rule matching.
- For every incomplete, unsupported, content-failure, or system-failure case, assert that no recommendation is emitted.
- Assert stage ordering where observable: validation before repository access, repository access before calculation, and calculation before rule evaluation.

## Supported regimen inventory

All six exact regimen variants must appear in the parameterized full-flow suite.

| Matrix key | Medication ID | Regimen ID | Exact parent regimen | Formulation | Renal thresholds |
|---|---|---|---|---|---|
| `CEF-Q8` | `cefepime` | `iv_2_g_every_8_hours_over_30_minutes` | 2 g IV every 8 hours over 30 minutes | `powder_for_solution` | 11, 30, 60 mL/min |
| `CEF-Q12` | `cefepime` | `iv_2_g_every_12_hours_over_30_minutes` | 2 g IV every 12 hours over 30 minutes | `powder_for_solution` | 11, 30, 60 mL/min |
| `PTZ-STD-3375` | `piperacillin_tazobactam` | `standard_infusion_iv_3_375_g_every_6_hours_over_30_minutes` | 3.375 g IV every 6 hours over 30 minutes | `powder_for_solution` | 20, 40 mL/min |
| `PTZ-STD-4500` | `piperacillin_tazobactam` | `standard_infusion_iv_4_5_g_every_6_hours_over_30_minutes` | 4.5 g IV every 6 hours over 30 minutes | `powder_for_solution` | 20, 40 mL/min |
| `PTZ-EI-3375` | `piperacillin_tazobactam` | `extended_infusion_iv_3_375_g_every_8_hours_over_240_minutes` | 3.375 g IV every 8 hours over 240 minutes | `None` | 20 mL/min |
| `FAM-PO-20` | `famotidine` | `oral_film_coated_tablet_20_mg_every_12_hours` | 20 mg PO every 12 hours | `film_coated_tablet` | 30, 60 mL/min |

## Renal-boundary matrix

Use a reproducible helper that constructs synthetic age, sex, weight, and serum-creatinine inputs whose unrounded Cockcroft–Gault result equals the target value. `δ` is `Decimal("0.0001")` mL/min. Each row expands to three full-flow cases: immediately below, exactly at, and immediately above the threshold.

| Case family | Regimen key | Threshold | At `threshold - δ` | At threshold | At `threshold + δ` |
|---|---|---:|---|---|---|
| `BND-CEF-Q8-11` | `CEF-Q8` | 11 | `below_11` | `crcl_11_to_below_30` | `crcl_11_to_below_30` |
| `BND-CEF-Q8-30` | `CEF-Q8` | 30 | `crcl_11_to_below_30` | `crcl_30_to_60` | `crcl_30_to_60` |
| `BND-CEF-Q8-60` | `CEF-Q8` | 60 | `crcl_30_to_60` | `crcl_30_to_60` | `above_60` |
| `BND-CEF-Q12-11` | `CEF-Q12` | 11 | `below_11` | `crcl_11_to_below_30` | `crcl_11_to_below_30` |
| `BND-CEF-Q12-30` | `CEF-Q12` | 30 | `crcl_11_to_below_30` | `crcl_30_to_60` | `crcl_30_to_60` |
| `BND-CEF-Q12-60` | `CEF-Q12` | 60 | `crcl_30_to_60` | `crcl_30_to_60` | `above_60` |
| `BND-PTZ-3375-20` | `PTZ-STD-3375` | 20 | `below_20` | `crcl_20_to_40` | `crcl_20_to_40` |
| `BND-PTZ-3375-40` | `PTZ-STD-3375` | 40 | `crcl_20_to_40` | `crcl_20_to_40` | `above_40` |
| `BND-PTZ-4500-20` | `PTZ-STD-4500` | 20 | `below_20` | `crcl_20_to_40` | `crcl_20_to_40` |
| `BND-PTZ-4500-40` | `PTZ-STD-4500` | 40 | `crcl_20_to_40` | `crcl_20_to_40` | `above_40` |
| `BND-PTZ-EI-20` | `PTZ-EI-3375` | 20 | `at_or_below_20` | `at_or_below_20` | `above_20` |
| `BND-FAM-30` | `FAM-PO-20` | 30 | `below_30` | `crcl_30_to_below_60` | `crcl_30_to_below_60` |
| `BND-FAM-60` | `FAM-PO-20` | 60 | `crcl_30_to_below_60` | `at_or_above_60` | `at_or_above_60` |

Every expanded boundary case must assert:

1. validation is valid;
2. the exact repository key is requested once;
3. the calculator and engine are each invoked once;
4. the unrounded renal value and unit are retained;
5. exactly one expected renal band is selected;
6. the expected action, dose, route, interval, and infusion duration match the selected test content;
7. the result retains rule ID, content version, evidence, provenance, evaluated time, and linked order information; and
8. canonical serialization preserves Decimal strings and UTC datetimes.

## Data-completeness and validation matrix

These cases are representative partitions, not a Cartesian product. Unless stated otherwise, vary one fact from a valid `CEF-Q8` baseline and assert `status=incomplete`, `applied=false`, `passed=None`, no repository access when failure occurs during initial validation, and no recommendation.

| Case ID | Changed fact | Expected issue or invariant |
|---|---|---|
| `DATA-PATIENT-ID` | patient ID missing | `missing_patient_identifier`; stop before repository access |
| `DATA-PATIENT-MISMATCH` | order or lab patient ID differs | `order_patient_mismatch` or `lab_patient_mismatch`; stop before repository access |
| `DATA-ENCOUNTER-MISMATCH` | order and lab encounter IDs differ | `encounter_mismatch`; stop before repository access |
| `DATA-BIRTH-DATE` | birth date missing, future, or not adult | explicit structural or supported-population issue; no calculation |
| `DATA-SEX` | sex missing or unsupported for the equation | explicit renal-sufficiency issue; no calculation |
| `DATA-WEIGHT-VALUE` | weight value is `None` | `missing_weight_value`; no calculation |
| `DATA-WEIGHT-UNIT` | weight unit missing or not exact `kg` | explicit unit issue; no conversion |
| `DATA-WEIGHT-TYPE` | supplied and declared weight types conflict or are unsupported | explicit issue; no silent method selection |
| `DATA-SCR-VALUE` | serum-creatinine value is `None`, nonpositive, or out of supported range | explicit structural issue; no calculation |
| `DATA-SCR-UNIT` | serum-creatinine unit missing or not exact `mg/dL` | explicit unit issue; no conversion |
| `DATA-SCR-STATUS` | result is not an eligible final result | explicit status issue; no calculation |
| `DATA-SCR-TIME` | timestamp missing, naive, future, or inconsistent | explicit timestamp issue; no calculation |
| `DATA-RENAL-STABILITY` | stability is `None` or `false` | incomplete or unsupported; no recommendation |
| `DATA-RRT` | renal-replacement-therapy state is `None` or `true` | incomplete or unsupported; no recommendation |
| `DATA-PREGNANCY` | pregnancy/lactation state is `None` or `true` | incomplete or unsupported; no recommendation |
| `DATA-MEDICATION-CODE` | medication code missing | `missing_medication_code`; no repository access |
| `DATA-REGIMEN-ID` | regimen ID missing | `missing_regimen_identifier`; no repository access |
| `DATA-CONTENT-VERSION` | content version missing | `missing_content_version`; no repository access |
| `DATA-DOSE` | exact content exists but dose is missing | content-specific validation fails after repository lookup and before calculation |
| `DATA-ROUTE` | exact content exists but route is missing | content-specific validation fails after repository lookup and before calculation |
| `DATA-FREQUENCY` | exact content exists but interval is missing | content-specific validation fails after repository lookup and before calculation |
| `DATA-INDICATION` | required exact indication is missing | content-specific validation fails after repository lookup and before calculation |
| `DATA-FORMULATION` | required formulation is missing | `missing_required_formulation_identifier`; no calculation |
| `DATA-INFUSION` | required infusion duration is missing | content-specific validation fails after repository lookup and before calculation |

## Unsupported exact-context matrix

Use one valid renal value in a non-boundary band. These cases must not normalize, infer, alias, convert, interpolate, or fall back. Expected status may be `incomplete`, `unsupported`, or structured `failed` according to the existing boundary, but every case must emit no recommendation.

| Case ID | Unsupported change | Required assertion |
|---|---|---|
| `UNSUP-MEDICATION` | unknown medication code | exact repository key fails closed; no fallback rule |
| `UNSUP-CASE` | uppercase or otherwise case-varied medication/regimen identifier | exact value is preserved; no normalization |
| `UNSUP-REGIMEN` | valid medication with unlisted regimen | no adjacent-regimen fallback |
| `UNSUP-VERSION` | valid medication/regimen with unavailable version | `content_not_found`; no recommendation |
| `UNSUP-ROUTE` | wrong route | no route inference |
| `UNSUP-FORMULATION` | wrong or extraneous formulation | no formulation substitution |
| `UNSUP-DOSE` | wrong parent dose | no dose conversion or nearest-dose matching |
| `UNSUP-FREQUENCY` | wrong interval | no nearest-regimen matching |
| `UNSUP-INFUSION` | wrong infusion duration | no standard/extended-infusion substitution |
| `UNSUP-INDICATION` | unlisted indication | no indication inference |
| `UNSUP-PEDIATRIC` | age below 18 years | no extrapolation outside adult scope |
| `UNSUP-FAM-WEIGHT` | famotidine patient weight below 40 kg | no recommendation |
| `UNSUP-RRT` | dialysis or other renal replacement therapy | no recommendation |
| `UNSUP-UNSTABLE` | acute or changing renal function | no recommendation |

## Content and system-failure matrix

Inject failures at one boundary at a time. Assert sanitized structured output, no stack trace or exception detail, no sensitive payload echo, and no recommendation.

| Case ID | Injected failure | Expected failure stage and code |
|---|---|---|
| `FAIL-VALIDATION-TYPED` | validator raises `ValidationError` | `initial_validation` / `validation_boundary_failure` |
| `FAIL-CONTENT-MISSING` | repository raises `ContentNotFound` | `content_repository` / `content_not_found` |
| `FAIL-CONTENT-UNEXPECTED` | repository raises unexpected exception | `content_repository` / `unexpected_content_repository_failure` |
| `FAIL-CONTENT-DEFECT` | retrieved content is draft-ineligible, mismatched, gapped, overlapping, or otherwise invalid | content validation or rule result fails closed; no recommendation |
| `FAIL-CONTEXT` | context construction raises unexpected exception | `context_assembly` / `unexpected_application_failure` |
| `FAIL-CALC-TYPED` | calculator raises `CalculationError` | `renal_calculation` / `calculation_failure` |
| `FAIL-CALC-UNEXPECTED` | calculator raises unexpected exception | `renal_calculation` / sanitized unexpected failure code |
| `FAIL-RULE` | engine or rule raises unexpected exception | `rule_evaluation` / sanitized unexpected rule failure code; retain calculated renal audit data |
| `FAIL-AMBIGUOUS-MATCH` | engine observes zero eligible rules or more than one eligible rule for otherwise supported content | explicit unmatched or failed outcome; no recommendation |

## Cross-case invariants

The Day 72 suite must make these assertions reusable rather than duplicating them inconsistently:

- Critical validation failure always prevents calculation and rule matching.
- Exact content lookup uses medication ID, regimen ID, and content version without normalization.
- A successful case has one and only one matched renal band and one structured recommendation.
- A non-successful case has zero recommendations.
- Missing numeric values remain `None`; zero is never used as a missing-value sentinel.
- Calculated and matched renal values remain unrounded `Decimal` values until presentation.
- Canonical JSON uses decimal strings and UTC datetimes.
- Successful recommendations include evidence, provenance, rule ID, content version, rationale, and linkage to the evaluated order.
- Failures do not expose stack traces, exception messages, source payloads, or synthetic case details unnecessarily.
- Draft repository content remains ineligible unless copied into a clearly labeled test-only reviewed fixture.

## Day 72 implementation target

Create a focused parameterized integration test module, expected at `tests/integration/test_renal_dose_matrix.py`, that implements this matrix in bounded families rather than one monolithic Cartesian product. Reuse small synthetic fixture builders, give every parameter a stable matrix ID, and keep medication-specific expected values explicit.

The first implementation pass should prioritize:

1. all 39 below/at/above boundary cases;
2. one complete success case for each of the six regimen variants;
3. the initial-validation stop cases;
4. exact-context unsupported cases; and
5. the content, calculation, and rule-failure cases.
