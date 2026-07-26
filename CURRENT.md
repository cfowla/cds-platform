# Current Project State

## Execution mode

- Repository: `cfowla/cds-platform`
- Active implementation branch: `experimental/generic-evaluation-contracts`
- Branch purpose: unrestricted experimental architecture work; not a release candidate.
- Prototype remains nonclinical and is not authorized for patient-care use.
- Development and tests must use synthetic or properly de-identified data.
- Repository files, not prior chat history, are the durable source of truth.

## Roadmap position

- The bounded renal-dose vertical slice on `main` remains the only clinically implemented feature.
- The historical release decision remains `no-go`; this experimental branch does not select, verify,
  or replace a release candidate.
- Broad refactors and incomplete intermediate states are permitted on this branch, but fail-closed
  behavior, exact identifiers, explicit units, inspectable content, provenance, sanitized failures,
  and the clinical-use prohibition remain mandatory.

## Completed experimental milestone

The first platform-contract package is implemented additively without changing the renal execution
path:

- `src/cds/domain/calculations.py`
  - adds immutable, feature-neutral `CalculationResult`;
  - preserves exact `Decimal | None`, unit, method, implementation version, inputs, assumptions,
    warnings, and provenance.
- `src/cds/domain/failures.py`
  - adds sanitized `FailureDetail` and shared failure categories;
  - excludes exception text and traceback fields.
- `src/cds/app/results.py`
  - adds canonical application-owned `EvaluationResult`;
  - uses empty recommendation and alert tuples as safe defaults;
  - records validation, calculations, evidence, provenance, evaluation time, failure details, and
    evaluated rule identifiers.
- `src/cds/app/features.py`
  - adds exact `FeatureDefinition` and `FeatureRegistry` contracts;
  - rejects duplicate feature identifiers and performs no normalization or fallback.
- `src/cds/app/composition.py`
  - adds an explicit composition-root contract;
  - performs no environment lookup, file discovery, implicit content selection, or clinical
    registration.
- `src/cds/rules/rule.py`
  - adds generic `EvaluationContext`, `Rule`, and `RuleOutcome` contracts;
  - performs no I/O, content loading, normalization, or calculation.
- `ARCHITECTURE.md`
  - distinguishes stable renal behavior, implemented experimental contracts, compatibility layers,
    and planned migration work.

## Compatibility and safety disposition

The following remain unchanged:

- `RenalDoseUseCase` and `RenalDoseUseCaseResult`;
- `RenalDoseRuleEngine` and `RenalDoseRuleRegistry`;
- renal validators, calculators, clinical-content models, YAML documents, and exact lookup behavior;
- renal response mapper and CLI contract;
- supported medications, populations, indications, formulations, regimens, and content versions;
- calculation equations, unrounded values, boundary ownership, and recommendation behavior;
- prototype warning and release `no-go`.

The generic contracts do not make any additional feature clinically supported merely because it can
be registered by identifier.

## Verification status

The GitHub connector was used to inspect the current repository and publish the additive files. This
environment did not provide a complete runnable checkout, so pytest, Ruff, architecture tests, and
serialization contracts were not executed. No passing test or release claim is made.

Static review performed through repository reads confirms:

- new `domain` modules import only `domain`;
- new `rules` contracts import only `domain` and `rules`-local concepts;
- new `app` contracts import inward application dependencies;
- no existing renal implementation file was modified;
- no clinical content, tests, snapshots, goldens, dependencies, or interface files were modified.

## Deferred work

- renal calculation adapter to `CalculationResult`;
- renal rule adapter to generic `RuleOutcome`;
- generic `EvaluationResult` assembly with a legacy renal compatibility adapter;
- feature-aware generic rule engine and registry behavior;
- shared content-model extraction;
- second low-risk experimental feature;
- CLI composition-root migration;
- legacy result or compatibility deletion;
- full test and lint reconciliation.

## Next exact action

Implement the renal compatibility adapter package without changing the existing renal response
contract:

1. add a pure adapter from `RenalFunctionResult` to `CalculationResult`;
2. add a pure adapter from `RuleResult` plus `ValidationResult` to `EvaluationResult`;
3. add focused unit tests proving success and every non-success state preserve no-recommendation
   fail-closed behavior;
4. leave `RenalDoseUseCase`, the renal mapper, CLI, content contracts, clinical behavior, and exact
   identifiers unchanged.

Do not begin content-model extraction or a second clinical feature in that package.
