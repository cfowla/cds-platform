# CDS Platform Architecture

This document defines the stable component boundaries and implemented prototype shape of the CDS
Platform. It also records experimental contracts separately from stable renal behavior. It describes
permitted dependencies, processing flow, and result contracts rather than feature history or roadmap
status.

`PROJECT_CHARTER.md` remains authoritative for safety and scope. `FIRST_VERTICAL_SLICE.md` defines
the supported clinical workflow. This prototype is for research, education, and software development
only; it is not for direct clinical use and must use synthetic or properly de-identified data.

## Architectural principles

1. Validate structural integrity and task sufficiency before calculation or rule matching.
2. Pass typed objects across internal boundaries; keep external dictionaries at mapper boundaries.
3. Keep domain models passive and free of validation, calculation, orchestration, serialization,
   persistence, network access, and file I/O.
4. Keep services and rule evaluators pure, deterministic, and explicit about time and assumptions.
5. Keep medication guidance, thresholds, sources, versions, review metadata, and limitations as
   inspectable clinical-content data.
6. Load and validate content only through repository implementations.
7. Keep mappers and interfaces free of clinical recommendation logic.
8. Return structured results that distinguish success, warnings, incomplete evaluation, unsupported
   context, and system failure.
9. Treat experimental platform contracts as additive until a feature is explicitly migrated and its
   compatibility contract is retired.

## Implemented stable package map

```text
src/cds/
  app/           renal request DTOs, use-case orchestration, compatibility exports
  content/       versioned YAML clinical-content documents
  domain/        passive clinical, support, value, exception, and output types
  interfaces/    CLI I/O, arguments, presentation, diagnostics, and exit behavior
  mappers/       renal request and response representation conversion
  repositories/  typed renal content contracts, schema validation, and storage adapters
  rules/         renal evaluation context, predicates, rules, registry, and engine
  services/      pure renal calculation helpers
  utils/         generic serialization and diagnostic logging helpers
  validation/    structural and task-sufficiency validators and passive findings
```

The stable renal vertical slice remains unchanged by the initial experimental contract package.
`RenalDoseUseCaseResult(validation, rule_result)` remains the implemented interface and serialized
response ownership remains with the existing renal mapper.

## Experimental platform contracts

The following additive modules are implemented on the experimental branch but are not yet the stable
renal execution path:

```text
src/cds/domain/calculations.py  feature-neutral CalculationResult
src/cds/domain/failures.py      sanitized FailureDetail taxonomy
src/cds/app/results.py          canonical EvaluationResult contract
src/cds/app/features.py         exact FeatureDefinition and FeatureRegistry
src/cds/app/composition.py      explicit composition-root contract
src/cds/rules/rule.py           generic EvaluationContext, Rule, and RuleOutcome
```

These contracts contain no medication-specific thresholds or clinical content. They do not authorize
a second clinical feature, change supported medications or populations, replace the renal result
contract, or alter the current CLI. They are intended to support later adapters and feature migration.

## Dependency direction

The implementation uses an explicit allowlist rather than a single linear dependency chain. A layer
may import only the internal layers shown below, including itself for package-local composition.

| Source | Permitted internal dependencies |
| --- | --- |
| `domain` | `domain` |
| `validation` | `domain`, `utils`, `validation` |
| `services` | `domain`, `services`, `utils` |
| `rules` | `domain`, `repositories`, `rules`, `utils` |
| `content` | `content`, `domain` |
| `repositories` | `domain`, `repositories`, `utils` |
| `app` | `app`, `domain`, `repositories`, `rules`, `services`, `utils`, `validation` |
| `mappers` | `app`, `domain`, `mappers`, `utils` |
| `interfaces` | `app`, `domain`, `interfaces`, `mappers`, `utils` |
| `utils` | `utils` |

The practical inward flow remains:

```text
interfaces -> mappers -> app DTOs and domain inputs
interfaces -> injected app use case
app -> validation + repositories + services + rules
validation -> domain
services -> domain
rules -> domain + typed repository content
repositories -> domain and storage-specific helpers
content -> versioned data only
```

The experimental composition root adds one prospective path:

```text
interfaces -> ApplicationComposition -> exact FeatureDefinition -> feature use case
```

No interface uses that path yet.

## Stable renal processing flow

```text
synthetic JSON file
  -> CLI reads and parses JSON
  -> request mapper creates a passive app DTO
  -> request mapper converts wire values to typed domain and application inputs
  -> CLI requires explicit evaluation date and timezone-aware evaluation time
  -> renal use case performs structural and task-sufficiency validation
       -> invalid or insufficient input returns incomplete with no recommendation
  -> repository retrieves exact medication + regimen + content-version content
  -> content-specific medication and regimen sufficiency checks run
  -> app assembles the validated renal rule-evaluation context
  -> pure service calculates unrounded Cockcroft-Gault creatinine clearance
  -> renal rule engine selects one exact registered rule and evaluates typed content
  -> app returns RenalDoseUseCaseResult(validation, rule_result)
  -> response mapper fixes the existing top-level response shape
  -> canonical serializer emits deterministic JSON
  -> CLI may render a non-authoritative human-readable summary
```

Repository lookup is exact and case-sensitive. It does not trim, normalize, alias, fuzzy-match,
fall back to another regimen, or select a content version. Critical validation issues stop the flow
before calculation or matching. Unsupported or insufficient cases fail closed with no dosing
recommendation.

## Experimental result contract

`EvaluationResult` is an application-owned, feature-neutral target contract with:

- exact evaluation and feature identifiers;
- `ResultStatus`;
- structured validation;
- recommendation, alert, and calculation tuples;
- assumptions, warnings, evidence, and provenance;
- timezone-aware evaluation timestamp supplied by the caller;
- optional sanitized `FailureDetail`; and
- evaluated rule identifiers.

Empty recommendation and alert tuples are safe defaults. A non-success result therefore cannot
accidentally contain a recommendation unless orchestration explicitly supplies one. The contract does
not store exception messages or traceback data.

`CalculationResult` preserves a `Decimal | None`, explicit unit, exact method and implementation
version, stable inputs, assumptions, warnings, and provenance. Unknown numeric output remains `None`,
not zero.

## Feature and composition contracts

`FeatureRegistry` performs exact, case-sensitive feature lookup with no normalization, aliasing, or
fallback. Duplicate identifiers fail at construction. `ApplicationComposition` receives explicitly
assembled definitions; it performs no file discovery, environment lookup, implicit content selection,
or clinical registration.

The first package deliberately does not adapt the renal use case, genericize renal repository types,
change the CLI, or introduce a second feature.

## Stable module responsibilities

| Module | Responsibility |
| --- | --- |
| `domain` | Passive clinical facts, enums, value objects, traceability, exceptions, outputs, generic calculations, and sanitized failures. |
| `validation` | Structural and task-sufficiency checks returning typed findings. |
| `services` | Pure calculations using validated typed inputs and unrounded values. |
| `rules` | Validated contexts, predicates, medication rules, registries, deterministic engines, and additive generic contracts. |
| `content` | Non-executable, versioned YAML guidance and review metadata. |
| `repositories` | Content contracts, schema validation, typed conversion, storage access, lookup. |
| `app` | DTOs, workflow order, component coordination, result assembly, failure mapping, feature registry, and composition contracts. |
| `mappers` | Exact wire-to-internal conversion and canonical response shaping. |
| `interfaces` | I/O, invocation, presentation, sanitized diagnostics, and exit behavior. |
| `utils` | Generic serialization and controlled diagnostic logging only. |

## Compatibility layers and planned migration

- `RenalDoseUseCaseResult` remains the stable renal application result.
- `RuleResult` remains the stable renal rule output.
- `RenalDoseRuleEngine` and `RenalDoseRuleRegistry` remain unchanged.
- `app.context` remains a compatibility export for the canonical `rules.context` owner.
- The current renal response mapper and CLI invocation remain unchanged.

Planned later work, not implemented here:

1. adapt renal calculations into `CalculationResult`;
2. adapt renal rule outcomes into generic `RuleOutcome`;
3. assemble `EvaluationResult` while preserving the legacy mapper contract;
4. introduce feature-aware rule registration only after compatibility coverage exists;
5. extract neutral content contracts only after a second workflow proves the abstraction;
6. remove compatibility aliases only at an explicit breaking-change checkpoint.

## Approved prototype deviations and limitations

1. **Typed renal content models remain in `repositories.renal_content`.** Rules continue importing
   these immutable types. A separate content-model package remains deferred until another workflow
   demonstrates a concrete need.
2. **The canonical renal evaluation context remains in `rules.context`.** `app.context` is a
   compatibility export and must not become a second ownership location.
3. **The CLI request DTO remains in `app.dto`.** Mappers may depend on this passive boundary type.
4. **The current CLI remains dependency injected.** The new composition contract is not wired into
   the interface yet.
5. **Only the renal-dose vertical slice is clinically implemented.** Generic package names and
   feature registration contracts do not authorize additional medication, population, method,
   interface, or clinical domain.
6. **The experimental branch is not a release candidate.** Intermediate architectural work may be
   incomplete, but fail-closed safety behavior and the clinical-use prohibition remain mandatory.

## Cross-cutting constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Do not fabricate missing values, convert ambiguous units, or silently infer clinical context.
- Use unrounded values for calculation, matching, and audit; round only for presentation.
- Do not read clinical content from services or rule evaluators.
- Do not place clinical logic in domain models, mappers, interfaces, or generic utilities.
- Do not expose patient identifiers, clinical payloads, exception messages, or tracebacks in
  diagnostic output.
- Prefer explicit composition over inheritance, metaprogramming, or a domain-specific language.
- Add abstractions only when a workflow demonstrates a concrete need.
