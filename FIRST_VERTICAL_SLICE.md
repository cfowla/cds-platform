# First End-to-End Feature: Renal Function and Limited Renal-Dose Evaluation

> **Prototype only — not for direct clinical use.** This scope is for software design and testing with synthetic or properly de-identified cases. It does not authorize patient-care use.

## Single deliverable

Implement one auditable vertical slice that calculates adult Cockcroft–Gault renal function and evaluates renal-dose guidance for exactly three explicitly supported medications.

## Stable scope statement

The feature accepts a synthetic adult case, validates structural correctness and task sufficiency, calculates unindexed Cockcroft–Gault creatinine clearance in `mL/min`, evaluates only versioned renal-adjustment content for cefepime, piperacillin–tazobactam, or famotidine, and returns a structured, traceable result. Unsupported or insufficient cases must fail closed without inventing data or recommendations.

## Why these medications were selected

- **Cefepime** represents a medication with multiple renal-function bands and regimen context, providing enough complexity to test explicit boundaries.
- **Piperacillin–tazobactam** adds materially different regimen and infusion variants, testing separation between clinical content, calculation, and rule matching.
- **Famotidine** provides a simpler non-antimicrobial comparison, testing whether the architecture generalizes beyond antibiotics.

Together, the three medications expose boundary, regimen, and content-model requirements while remaining small enough for manual source review, independent golden-case verification, and complete boundary testing.

## Supported inputs

- Birth date plus an explicit caller-supplied evaluation date; age is derived as completed
  calendar years and is not accepted as an independently supplied first-slice input.
- Adult age of at least 18 years.
- Sex value required by the configured Cockcroft–Gault implementation.
- Stable serum creatinine in `mg/dL` with collection time.
- Body weight in kilograms with an explicitly declared weight type.
- Exact supported medication identifier.
- Current or proposed dose, route, and frequency when required by the selected rule.
- Infusion duration, indication, and regimen variant when required by the selected rule.

## Supported processing

- Structural validation before calculation.
- Task-sufficiency validation before calculation or dose evaluation.
- Unindexed Cockcroft–Gault creatinine-clearance calculation in `mL/min`.
- Exact matching against versioned content for the three supported medications.
- Explicit handling of unmatched, insufficient, and unsupported cases.

## Supported outputs

- Structured evaluation status.
- Renal-function result, method, unit, and reproducible input snapshot.
- Matched rule identifier and clinical-content version.
- Dose recommendation or explicit statement that no supported recommendation was produced.
- Clinician-readable rationale.
- Assumptions and warnings.
- Evidence and provenance.
- Evaluation timestamp.

## Exclusions

- Patients younger than 18 years.
- Pregnancy or lactation.
- Acute or rapidly changing kidney function.
- Dialysis or any renal replacement therapy.
- Renal methods other than Cockcroft–Gault.
- Ambiguous units, missing critical inputs, or undeclared weight selection.
- Fuzzy medication matching.
- Unsupported formulations, indications, regimens, routes, doses, frequencies, or infusion strategies.
- Allergy, interaction, hepatic-impairment, or therapeutic-drug-monitoring assessment.
- Initial therapy selection or duration-of-therapy recommendations.
- EHR integration, protected health information, autonomous action, or production clinical use.

## Acceptance criteria

- The system validates structure and task sufficiency before computing.
- Missing or ambiguous critical data produce an incomplete or unsupported result, not an inferred value.
- The renal result is explicitly identified as unindexed Cockcroft–Gault creatinine clearance in `mL/min`.
- Only exact supported medication and regimen combinations can match clinical content.
- Every matched recommendation identifies the rule and content version used.
- Results preserve assumptions, warnings, evidence, provenance, and evaluation time.
- Boundary and golden cases can be independently verified with synthetic data.
- Unsupported cases fail closed and do not produce a dose recommendation.
