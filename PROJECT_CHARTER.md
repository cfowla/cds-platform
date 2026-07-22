# CDS Platform Project Charter

## Project status

**Prototype — research, education, and software development only.**

> **This prototype is not for direct clinical use.** It must not be used to diagnose, prescribe, verify medication orders, direct patient care, or replace a clinician's judgment, current prescribing information, institutional policy, or an independently validated clinical system.

Any interface or output produced by this project must preserve a clear version of this warning until the project has completed separate clinical validation, governance, security, regulatory, and deployment reviews. Completion of the prototype does not remove this restriction.

## Document authority and use

This charter is the governing source for project scope, safety constraints, and change control. Routine implementation tasks should use [`docs/SAFETY_INVARIANTS.md`](docs/SAFETY_INVARIANTS.md) as the concise working checklist, but that summary does not replace or override this charter.

The full charter must be reread before any scope expansion, clinical-content change, or safety-policy change.

## Purpose

The CDS Platform is a Python project for learning how to build clinical decision-support software with:

- typed clinical data models;
- strict input and task-sufficiency validation;
- pure, deterministic calculations;
- simple and inspectable rule matching;
- versioned clinical content separated from application logic;
- structured results containing rationale, assumptions, warnings, evidence, and provenance; and
- behavior-focused automated tests.

The immediate objective is to prove this architecture with one narrowly bounded renal-function and renal-dose-adjustment workflow.

## Intended user

The primary intended user is the project's developer, a clinical pharmacist, using synthetic or properly de-identified cases to design, inspect, and test CDS behavior.

Secondary users may include software reviewers and qualified clinical-content reviewers evaluating the prototype in a non-production environment.

The intended user is **not** a clinician relying on the application during patient care, a patient, a caregiver, or an automated production system.

## First use case: renal calculator and limited renal-adjustment rules

### Goal

Given a complete, manually supplied test case, the prototype will:

1. validate the input structure, units, ranges, and sufficiency;
2. calculate an adult Cockcroft–Gault creatinine clearance estimate in `mL/min`;
3. record the inputs used, including the selected body weight and its declared type;
4. match the result to a versioned renal-adjustment rule for a supported medication and regimen; and
5. return a structured evaluation result with the calculation, matched rule, recommendation, rationale, assumptions, warnings, evidence, content version, and provenance.

### Supported medications

The first rule set is limited to:

- cefepime;
- piperacillin–tazobactam; and
- famotidine.

Medication names must be normalized to an explicit supported identifier. The prototype must not use fuzzy name matching to infer a medication.

### Required input context

A case must provide, at minimum:

- patient age on the evaluation date;
- sex value required by the configured Cockcroft–Gault implementation;
- serum creatinine value, unit, and collection time;
- body weight value in kilograms;
- the declared weight type used by the calculation, such as actual, ideal, or adjusted;
- medication identity;
- the current or proposed dose, route, frequency, and infusion duration when applicable; and
- the supported indication or regimen variant when the medication's renal adjustment depends on that context.

The prototype will adjust only an explicitly supported base regimen. It will not invent an initial regimen, infer an indication, or extrapolate from a partially matching rule.

### Initial population and workflow boundaries

The first use case is limited to:

- adults aged 18 years or older;
- a single point-in-time evaluation;
- non-dialysis patients who are not receiving renal replacement therapy;
- cases in which serum creatinine is considered sufficiently stable for the test scenario;
- Cockcroft–Gault creatinine clearance, reported as an unindexed `mL/min` estimate; and
- medication and regimen combinations explicitly represented in the versioned rule content.

The first use case does not determine whether renal function is stable. That fact must be supplied or established by the test scenario. Cases involving acute or rapidly changing kidney function must return an unsupported or incomplete result rather than a dose recommendation.

### Expected output states

The workflow must distinguish among:

- `success`: calculation completed and a supported rule matched;
- `success_with_warnings`: a supported result was produced with explicit non-fatal limitations;
- `incomplete`: critical data are missing or invalid;
- `not_applicable`: the population, medication, indication, or regimen is outside scope; and
- `failed`: a system or content error prevented evaluation.

Missing critical data, ambiguous units, unsupported contexts, overlapping rules, or missing content must fail closed. In those cases, the system must not return a dosing recommendation.

## Non-goals

The prototype is not intended to provide or perform:

- direct clinical decision support or patient-care guidance;
- autonomous prescribing, order verification, dose changes, or alerting;
- EHR, FHIR, pharmacy-system, or production API integration;
- storage or processing of protected health information;
- pediatric, neonatal, pregnancy, or lactation dosing;
- dosing during intermittent hemodialysis, peritoneal dialysis, CRRT, or other renal replacement therapy;
- dosing during acute kidney injury or rapidly changing renal function;
- diagnosis or staging of chronic kidney disease;
- replacement of measured creatinine clearance, clinical assessment, or pharmacist review;
- medication selection, indication determination, empiric therapy selection, or duration-of-therapy recommendations;
- comprehensive renal dosing beyond cefepime, piperacillin–tazobactam, and famotidine;
- automatic extrapolation to unsupported doses, routes, frequencies, infusion strategies, indications, or populations;
- assessment of allergies, drug interactions, hepatic impairment, pharmacogenomics, pregnancy, therapeutic drug monitoring, or other patient-specific modifiers unless added in a separately chartered feature;
- machine-learned, generative, or opaque dosing recommendations; or
- regulatory compliance, clinical validation, or production readiness merely because software tests pass.

## Safety constraints

### Clinical-use prohibition

Every user-facing interface, serialized result, example output, and release artifact must state that the prototype is not for direct clinical use. A dosing recommendation produced by the prototype is test output, not a clinical instruction.

### Data handling

Development and testing must use synthetic or properly de-identified data. Real patient identifiers and protected health information must not be committed to the repository, fixtures, logs, issues, pull requests, screenshots, or example outputs.

### Validation before computation

The application must validate before calculating or matching rules. Validation must include:

- required fields;
- explicit units;
- plausible ranges;
- internally consistent timestamps and values;
- task sufficiency; and
- supported population, medication, and regimen checks.

Critical missing or invalid data must stop the workflow. Unknown numeric values must be represented as missing, never as zero.

### No silent assumptions

The system must not silently:

- choose a body-weight method;
- convert an ambiguous unit;
- infer an indication or regimen;
- substitute an unsupported medication formulation;
- interpolate between rule ranges;
- extrapolate beyond content boundaries; or
- treat missing information as normal.

Any permitted assumption must be explicit in the structured result and traceable to the code or content that introduced it.

### Inspectable and versioned clinical content

Renal-adjustment rules must be stored separately from calculation logic and include, at minimum:

- medication and supported regimen identifier;
- renal-function boundaries and boundary inclusivity;
- resulting adjustment;
- source citation;
- source version or publication date;
- content version;
- review date;
- reviewer; and
- notes describing important limitations.

Rule changes require clinical-content review and corresponding test updates. The rule engine must detect missing, overlapping, or unreachable ranges rather than resolving them silently.

### Deterministic implementation

Calculators and rule evaluators must be pure and deterministic: typed input, typed output, no network calls, no direct file reads, and no hidden mutable state. Content must enter through a repository boundary.

### Traceable output

Each result must preserve enough information to reproduce and audit the outcome, including:

- input values and units;
- equation and implementation version;
- weight value and declared weight type;
- calculated creatinine clearance before display rounding;
- matched rule identifier and content version;
- recommendation and rationale;
- assumptions and warnings;
- evidence or source citation; and
- provenance and evaluation timestamp.

### Testing expectations

Before a rule is considered implemented, the project must include:

- unit tests for the calculator and each rule boundary;
- parameterized tests immediately below, at, and immediately above each cutoff;
- tests for missing, invalid, and contradictory inputs;
- tests for unsupported populations and regimens;
- tests proving unsupported cases produce no recommendation;
- golden cases reviewed against the cited source content;
- integration tests for the complete validation-to-result flow; and
- contract tests for the serialized input and output shape.

Passing tests demonstrates consistency with encoded expectations; it does not establish clinical safety or authorize clinical use.

## Definition of done for the first feature

The first feature is complete only when:

1. Cockcroft–Gault input requirements and calculation behavior are explicit and tested.
2. Supported population and unsupported stop conditions are enforced.
3. Versioned renal-adjustment content exists only for cefepime, piperacillin–tazobactam, and famotidine.
4. Every supported regimen and renal boundary is unambiguous and covered by tests.
5. Unsupported or insufficient cases return a structured non-success state with no dosing recommendation.
6. Results include rationale, assumptions, warnings, evidence, and provenance.
7. The clinical-use prohibition is visible in every user-facing output.
8. No EHR integration, autonomous action, or production deployment is included.

## Change control

Any expansion of medication coverage, population, renal method, clinical setting, data source, or delivery interface must be proposed as a separately scoped feature. The project charter must be revised when an expansion changes the intended user, clinical risk, supported use case, non-goals, or safety constraints.
