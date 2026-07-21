# First End-to-End Feature: Renal Function and Limited Renal-Dose Evaluation

> **Prototype only — not for direct clinical use.** This scope is for software design and testing with synthetic or properly de-identified cases. It does not authorize patient-care use.

## Single deliverable

Freeze one auditable vertical-slice contract before implementing clinical logic: Cockcroft–Gault renal-function calculation followed by renal-dose evaluation for exactly three explicitly supported medications.

## Scope statement

The first end-to-end feature accepts a synthetic adult case containing the evaluation date or calculated age, the sex value required by the configured Cockcroft–Gault implementation, a stable serum creatinine value in `mg/dL` with collection time, a body weight in kilograms with its declared weight type, an explicit supported medication identifier, and the current or proposed dose, route, frequency, infusion duration, indication, and regimen variant when those facts are required by the selected rule; it validates structure and task sufficiency, calculates unindexed Cockcroft–Gault creatinine clearance in `mL/min`, matches only versioned renal-adjustment content for cefepime, piperacillin–tazobactam, or famotidine, and returns a structured status plus the renal result, matched rule and content version, recommendation, rationale, assumptions, warnings, evidence, provenance, and evaluation timestamp; it excludes patients younger than 18 years, pregnancy or lactation, acute or rapidly changing kidney function, dialysis or any renal replacement therapy, renal methods other than Cockcroft–Gault, ambiguous units or undeclared weight selection, fuzzy medication matching, unsupported formulations, indications, regimens, routes, doses, frequencies, or infusion strategies, and assessment of allergies, interactions, hepatic impairment, therapeutic drug monitoring, initial therapy selection, duration of therapy, EHR integration, protected health information, autonomous action, and production clinical use.

## Why these medications were selected

- **Cefepime** represents a medication whose renal evaluation can require multiple clearance bands and regimen context, providing enough complexity to test explicit boundaries without beginning with a large formulary.
- **Piperacillin–tazobactam** adds a second antimicrobial with materially different regimen and infusion variants, testing whether content remains separate from the generic calculator and rule-matching path.
- **Famotidine** provides a simpler non-antimicrobial comparison case, testing whether the same architecture generalizes across therapeutic classes rather than becoming an antibiotic-specific implementation.

The three medications are diverse enough to expose boundary, regimen, and content-model requirements while remaining small enough for manual source review, independent golden-case verification, and complete boundary testing.

## Checkpoint

- Prior note reviewed: `PROJECT_CHARTER.md`, with the repository architecture and build-order guidance used as constraints.
- Current relevant tests checked: the existing domain-model and renal-service tests are skipped placeholders; executing those two current files produced `2 skipped` and no failures.
- Scope contract check: the scope statement names required inputs, structured outputs, and excluded edge cases, and the medication rationale is recorded above.
- **Next exact action:** implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace the corresponding placeholder with value and unknown-state tests in `tests/unit/domain/test_enums.py`.

## Packaging checkpoint — 2026-07-21

- **Single deliverable:** make the `src/cds` scaffold editable-installable through explicit package metadata while retaining zero runtime dependencies.
- `pyproject.toml` now declares setuptools package discovery, project keywords and classifiers, repository URLs, Python `>=3.11`, and `dependencies = []`.
- Current test scaffold check: `pytest -q` completed with `31 skipped` and no failures.
- Installation check: `python -m pip install -e .` succeeded on Python 3.13; `import cds` resolved and package metadata reported version `0.1.0` with Python `>=3.11`.
- **Next exact action:** implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace `tests/unit/domain/test_enums.py` with value, string-serialization, and explicit unknown-state tests.

## Test runner checkpoint — 2026-07-21

- **Single deliverable:** configure a strict pytest runner that imports the package successfully and preserves a named placeholder for the first renal calculator test.
- Prior checkpoint reviewed: the package was editable-installable and the existing suite completed with `31 skipped` and no failures.
- `pyproject.toml` now enforces pytest `>=8.0`, limits collection to `tests`, adds `src` to the test import path, and enables strict configuration and marker validation.
- `tests/test_smoke.py` imports the top-level `cds` package and verifies the imported module name.
- `tests/unit/services/test_renal.py` now names the pending Cockcroft–Gault calculator behavior instead of using a generic placeholder.
- Validation check: `python -m pytest -q` completed with `1 passed, 31 skipped`, and no failures.
- **Next exact action:** implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace `tests/unit/domain/test_enums.py` with value, string-serialization, and explicit unknown-state tests.

## Development commands checkpoint — 2026-07-21

- **Single deliverable:** document an exact, reproducible command sequence for creating the environment, installing development dependencies, running tests, and invoking the future CLI.
- Prior checkpoint reviewed: the strict pytest suite last completed with `1 passed, 31 skipped`, and no failures.
- `README.md` now provides repository-root commands for Windows PowerShell and macOS/Linux using an isolated `.venv`, editable development installation, `python -m pytest -q`, and the canonical future CLI invocation `python -m cds.interfaces.cli`.
- Relevant command validation: editable installation succeeded; the package smoke test and renal placeholder completed with `1 passed, 1 skipped`; the current CLI scaffold exited successfully without output.
- **Next exact action:** implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace `tests/unit/domain/test_enums.py` with value, string-serialization, and explicit unknown-state tests.

## Initial scope freeze checkpoint — 2026-07-21

- **Single deliverable:** reduce the active repository plan to the first renal-dosing vertical slice so the next development week can focus only on domain implementation.
- Prior note and charter reviewed: `FIRST_VERTICAL_SLICE.md` and `PROJECT_CHARTER.md` already limit the feature to adult Cockcroft–Gault plus three supported medications and require unsupported work to fail closed.
- Removed deferred service scaffolds and matching placeholder tests for anticoagulation, general risk scoring, vancomycin, and IV-to-PO conversion.
- Removed API and EHR adapter scaffolds and their placeholder tests because both are explicit non-goals for the first feature.
- Replaced the README’s platform-wide active architecture with the exact renal-only implementation path and an explicit rule that expansion requires a separately approved scope change.
- Added `BACKLOG.md` for unresolved calculation, validation, serialization, content, and review questions, plus all deferred features.
- Relevant current tests rerun: `python -m pytest -q tests/test_smoke.py tests/unit/services/test_renal.py` completed with `1 passed, 1 skipped`, and no failures; the skip remains the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` in `src/cds/domain/enums.py`, then replace `tests/unit/domain/test_enums.py` with value, string-serialization, and explicit unknown-state tests.

## Domain enums checkpoint — 2026-07-21

- **Single deliverable:** establish the stable string vocabulary required by the first renal-dosing domain layer without using blank strings to represent uncertainty.
- Implemented `Sex`, `ResultStatus`, `RenalMethod`, and `WeightType` as standard-library `StrEnum` classes in `src/cds/domain/enums.py`.
- `Sex`, `RenalMethod`, and `WeightType` include an explicit `UNKNOWN = "unknown"` member. `ResultStatus` preserves the five chartered workflow states; insufficient or uncertain evaluation state is represented by `INCOMPLETE`, not an additional unchartered status.
- Replaced the enum placeholder with exact value-contract, direct JSON string-serialization, explicit unknown-state, and nonblank-value tests.
- Relevant fetched-file validation: `PYTHONPATH=src python -m pytest -q` across the current smoke, renal placeholder, and enum tests completed with `16 passed, 1 skipped`; the remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement the shared traceability and value objects in `src/cds/domain/models.py`—`Provenance`, `EvidenceItem`, `Assumption`, `WarningNote`, `CodeableConcept`, and `TimeRange`—then replace `tests/unit/domain/test_models.py` with constructor, safe-default, missing-data, and serialization tests.

## Traceability support models checkpoint — 2026-07-21

- **Single deliverable:** implement the four shared objects needed to attach provenance, evidence, assumptions, and warnings to later renal-domain results.
- Prior note reviewed: the domain-enums checkpoint established the typed vocabulary and named traceability support models as the next domain-layer dependency.
- Implemented `Provenance`, `EvidenceItem`, `Assumption`, and `WarningNote` as standard-library, keyword-only, slotted dataclasses in `src/cds/domain/models.py`.
- Safe defaults use explicit `"unknown"` categorical states and `None` for missing text, timestamps, identifiers, and unevaluated assumption applicability; no default invents evidence, a source, or a warning message.
- `EvidenceItem`, `Assumption`, and `WarningNote` each receive an independent `Provenance` through `default_factory`, preventing shared mutable traceability state.
- Replaced the model placeholder with constructor, safe-default, independent-provenance, explicit-value, and default JSON-safe dictionary tests.
- Relevant fetched-file validation: `PYTHONPATH=src python -m pytest -q` across the current smoke, renal placeholder, enum, and model tests completed with `32 passed, 1 skipped`; the remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `CodeableConcept` and `TimeRange` in `src/cds/domain/models.py`, then extend `tests/unit/domain/test_models.py` with safe-default, explicit-value, and time-boundary tests.

## Shared value objects checkpoint — 2026-07-21

- **Single deliverable:** implement the passive, typed value objects needed to carry quantities, coded concepts, and clinical time intervals without embedding service or I/O behavior.
- Prior note reviewed: the traceability checkpoint named `CodeableConcept` and `TimeRange` as the next domain dependency; this task also added the quantity wrapper `ValueWithUnit`.
- Implemented `ValueWithUnit`, `CodeableConcept`, and `TimeRange` as standard-library, keyword-only, slotted dataclasses in `src/cds/domain/models.py`.
- Missing observations, concept fields, and temporal boundaries use `None`; `ValueWithUnit` permits a known unit with a missing value and uses `Decimal` for supplied quantitative values.
- Docstrings define unit, missing-data, coding, timezone, and open-boundary conventions while leaving conversion, normalization, lookup, chronology validation, serialization, and all I/O outside the models.
- Extended `tests/unit/domain/test_models.py` with zero-argument construction, missing-data, decimal precision, text-only and coded concept, open/equal time-boundary, and JSON-safe default tests.
- Relevant fetched-file validation: `PYTHONPATH=src python -m pytest -q` completed with `47 passed, 1 skipped`; `python -m compileall -q src tests` also completed successfully. The remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `Patient` in `src/cds/domain/models.py` with identifier, birth date, `Sex`, anthropometric value objects, traceability collections, and safe missing-data defaults; then add constructor and missing-data tests.

## Patient and encounter models checkpoint — 2026-07-21

- **Single deliverable:** implement passive `Patient` and `Encounter` truth objects that preserve partial source data without embedding calculations, validation, service behavior, or I/O.
- Prior note reviewed: the shared-value-object checkpoint named `Patient` as the next domain dependency and established `ValueWithUnit`, `CodeableConcept`, and `TimeRange` as the reusable field types.
- Implemented both models as standard-library, keyword-only, slotted dataclasses with safe zero-argument construction and the existing traceability collections.
- `Patient` carries the source identifier, birth date, explicit `Sex`, actual body weight, and height. Age, BMI, ideal body weight, adjusted body weight, and other derived values are intentionally absent.
- `Encounter` carries source identifiers, coded encounter type, optional time boundaries, location, service line, and attending-clinician identifier. Duration, chronology validation, and inferred status remain outside the model.
- Missing scalar data uses `None`, unknown sex uses `Sex.UNKNOWN`, and nested values, traceability collections, and provenance use independent factories so partial records do not share mutable state.
- Extended `tests/unit/domain/test_models.py` with default and representative partial-data constructors, explicit absence of derived patient fields, independent mutable-default checks, and JSON-safe default serialization.
- Relevant fetched-file validation: `PYTHONPATH=src python -m pytest -q` completed with `57 passed, 1 skipped`; `python -m compileall -q src tests` also completed successfully. The remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `LabResult` in `src/cds/domain/models.py` with patient and encounter links, a coded test, `ValueWithUnit`, collection/result timestamps, status, traceability, and partial-data tests.

## Medication and observation models checkpoint — 2026-07-21

- **Single deliverable:** implement passive `MedicationOrder`, `LabResult`, and `VitalSign` truth objects that preserve source coding, explicit units, partial data, and traceability without embedding validation, conversion, or clinical logic.
- Prior note reviewed: the patient-and-encounter checkpoint named `LabResult` as the next dependency; this task completed the related medication and observation objects required by the renal vertical slice.
- Added all three as standard-library, keyword-only, slotted dataclasses in `src/cds/domain/models.py`, reusing `CodeableConcept`, `TimeRange`, `ValueWithUnit`, and the shared traceability collections.
- Medication dose, frequency interval, infusion duration, laboratory values and reference boundaries, and vital-sign measurements all use `ValueWithUnit`, preserving supplied unit text and `Decimal` precision.
- Missing scalar values use `None`; a known unit may be retained while its numeric value is absent. Focused tests explicitly distinguish `None` from `Decimal("0")` for medication, laboratory, and vital-sign quantities.
- Added representative partial-data, independent mutable-default, and JSON-safe serialization tests in `tests/unit/domain/test_medication_observation_models.py`.
- Relevant local-mirror validation: `python -m pytest -q` completed with `70 passed, 1 skipped`; `python -m compileall -q src tests` also completed successfully. The remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `RenalFunctionResult` in `src/cds/domain/models.py` with an explicit `RenalMethod`, unit-bearing result, normalization flag, reproducible input snapshot, traceability, and partial-data tests; keep the calculation itself in the renal service layer.

## Problem and allergy models checkpoint — 2026-07-21

- **Single deliverable:** implement passive `Problem` and `Allergy` truth objects that preserve partial, text-only clinical concepts without fabricating terminology coding.
- Prior note reviewed: the medication-and-observation checkpoint named `RenalFunctionResult` as the next renal dependency; this user-directed domain task was completed without adding service, validation, mapper, or I/O behavior.
- Added `Severity` as a stable `StrEnum` with an explicit `UNKNOWN = "unknown"` state, then used it for both models.
- `Problem.problem`, `Allergy.substance`, and `Allergy.reaction` use `CodeableConcept`; free text can be supplied while `system` and `code` remain `None` unless a source provides them.
- Unknown reaction is represented by the default empty `CodeableConcept` with `text`, `system`, and `code` all `None`; unknown severity is represented by `Severity.UNKNOWN`, never a blank string or inferred value.
- Added focused tests for safe partial defaults, text-only concepts, explicit unknown states, independent mutable defaults, JSON-safe serialization, and the expanded enum contract.
- Relevant local-mirror validation before the change: `python -m pytest -q` completed with `70 passed, 1 skipped`. After the change, `python -m pytest -q` completed with `82 passed, 1 skipped`; `python -m compileall -q src tests` also completed successfully. The remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- **Next exact action:** implement `RenalFunctionResult` in `src/cds/domain/models.py` with `RenalMethod`, an explicit unit-bearing result, normalization flag, reproducible input snapshot, traceability, and partial-data tests; keep renal calculation logic in the service layer.

## Week 2 model construction review checkpoint — 2026-07-21

- **Single deliverable:** close Day 14 by verifying that every Week 2 dataclass supports safe incomplete and representative construction and that nested mutable defaults are never shared.
- Prior note reviewed: the problem-and-allergy checkpoint completed the final Week 2 implementation task; the full baseline suite completed with `82 passed, 1 skipped`.
- Added `tests/unit/domain/test_week_two_model_review.py` with parameterized incomplete and representative construction cases for all 14 Week 2 dataclasses.
- Representative cases cover traceability objects, value objects, patient and encounter facts, medication and observation records, and problem and allergy records without adding clinical logic.
- Added cross-model default-factory checks for the 10 models containing nested dataclasses or lists, confirming separate instances for every default-created nested value and collection.
- Full local-mirror validation: `python -m pytest -q` completed with `106 passed, 1 skipped`; `python -m compileall -q src tests` also completed successfully. The remaining skip is the intentionally unimplemented Cockcroft–Gault calculator.
- Day 14 is complete, bringing the first two weeks to `14 / 14` completed tasks.
- **Next exact action:** implement `RenalFunctionResult`, `Contraindication`, and `DoseRecommendation` in `src/cds/domain/models.py` with explicit units, `RenalMethod`, reproducible input context, traceability, safe partial-data defaults, and focused construction tests; keep calculations and clinical evaluation logic outside the models.
