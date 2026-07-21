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
