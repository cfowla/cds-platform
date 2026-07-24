# CDS Platform Architecture

This document defines the stable component boundaries and implemented prototype shape of the CDS
Platform. It describes permitted dependencies, processing flow, and result contracts rather than
feature history or roadmap status.

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
8. Return one structured result that distinguishes success, warnings, incomplete evaluation,
   unsupported context, and system failure.

## Implemented package map

```text
src/cds/
  app/           request DTOs, use-case orchestration, compatibility exports
  content/       versioned YAML clinical-content documents
  domain/        passive clinical, support, value, exception, and output types
  interfaces/    CLI I/O, arguments, presentation, diagnostics, and exit behavior
  mappers/       request and response representation conversion
  repositories/  typed content contracts, schema validation, and storage adapters
  rules/         evaluation context, predicates, medication rules, registry, and engine
  services/      pure renal calculation helpers
  utils/         generic serialization and diagnostic logging helpers
  validation/    structural and task-sufficiency validators and passive findings
```

`tests/contract/test_architecture_boundaries.py` enforces layer-directory presence, permitted
internal imports, and the absence of I/O imports from the pure `domain`, `services`, and `rules`
layers.

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

The practical inward flow is:

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

Lower-level packages do not import application orchestration or interface code. Domain modules do
not import validation, services, rules, repositories, mappers, interfaces, or storage libraries.

## Processing flow

```text
synthetic JSON file
  -> CLI reads and parses JSON
  -> request mapper creates a passive app DTO
  -> request mapper converts wire values to typed domain and application inputs
  -> CLI requires explicit evaluation date and timezone-aware evaluation time
  -> use case performs structural and task-sufficiency validation
       -> invalid or insufficient input returns incomplete with no recommendation
  -> repository retrieves exact medication + regimen + content-version content
  -> content-specific medication and regimen sufficiency checks run
  -> app assembles the validated rule-evaluation context
  -> pure service calculates unrounded Cockcroft-Gault creatinine clearance
  -> rule engine selects one exact registered rule and evaluates typed content
  -> app returns RenalDoseUseCaseResult(validation, rule_result)
  -> response mapper fixes the top-level response shape
  -> canonical serializer emits deterministic JSON
  -> CLI may render a non-authoritative human-readable summary
```

Repository lookup is exact and case-sensitive. It does not trim, normalize, alias, fuzzy-match,
fall back to another regimen, or select a content version. Critical validation issues stop the flow
before calculation or matching. Unsupported or insufficient cases fail closed with no dosing
recommendation.

## Module responsibilities

| Module | Responsibility |
| --- | --- |
| `domain` | Passive clinical facts, enums, value objects, traceability, exceptions, and outputs. |
| `validation` | Structural and task-sufficiency checks returning typed findings. |
| `services` | Pure calculations using validated typed inputs and unrounded values. |
| `rules` | Validated context, predicates, medication rules, registry, and deterministic engine. |
| `content` | Non-executable, versioned YAML guidance and review metadata. |
| `repositories` | Content contracts, schema validation, typed conversion, storage access, lookup. |
| `app` | DTOs, workflow order, component coordination, result assembly, failure mapping. |
| `mappers` | Exact wire-to-internal conversion and canonical response shaping. |
| `interfaces` | I/O, invocation, presentation, sanitized diagnostics, and exit behavior. |
| `utils` | Generic serialization and controlled diagnostic logging only. |

Important implemented details:

- Unknown numerics are `None`, never zero; unknown categories use explicit unknown states.
- `ValidationResult` has tri-state `is_valid` and structured `ValidationIssue` entries.
- The renal service requires explicit dates, supplied weight, declared weight type, exact supported
  units, and timezone-aware timestamps.
- Rules receive validated context, calculated renal function, and typed content; they perform no
  loading, normalization, calculation, logging, or I/O.
- The YAML repository reads only explicit paths during construction, validates the closed schema,
  converts documents to immutable typed content, and rejects duplicate exact keys.
- Request mapping rejects unknown fields and unsafe wire types before explicit conversion to
  `Decimal`, dates, datetimes, enums, value objects, and domain models.
- The CLI invokes an already configured use case and contains no clinical validation, calculation,
  content selection, or rule matching.
- Canonical serialization preserves declared field names, enum wire values, exact decimal strings,
  ISO dates, UTC datetimes, lists, tuples, and string-keyed mappings.

## Structured output contract

The application returns:

```text
RenalDoseUseCaseResult
  validation: ValidationResult
    is_valid: bool | None
    issues: list[ValidationIssue]
  rule_result: RuleResult
```

The response mapper fixes exactly two top-level JSON objects:

```json
{
  "validation": {},
  "rule_result": {}
}
```

`RuleResult` preserves, as applicable:

- rule, patient, encounter, content-version, and evaluation-time links;
- status: `success`, `success_with_warnings`, `incomplete`, `not_applicable`, or `failed`;
- tri-state `applied` and `passed` values;
- summary and structured supporting data;
- the unrounded `RenalFunctionResult` and reproducible calculation inputs;
- recommendations, dose details, contraindications, monitoring, and alerts; and
- assumptions, warnings, evidence, provenance, and sanitized failure stage or code.

Canonical JSON is authoritative; the CLI summary is presentation only. Expected clinical gaps and
unsupported contexts become `incomplete` or `not_applicable` without a recommendation. Internal
failures become sanitized `failed` results. User-facing output never includes a traceback.

## Approved prototype deviations and limitations

1. **Typed content models live in `repositories.renal_content`.** Rules import these immutable types
   because the repository contract currently defines the content boundary. A separate content-model
   package is not justified until another workflow demonstrates a concrete need.
2. **The canonical evaluation context lives in `rules.context`.** `app.context` is a compatibility
   export and must not become a second ownership location.
3. **The CLI request DTO lives in `app.dto`.** Mappers may depend on this passive
   boundary type while parsing and domain conversion remain in `mappers`.
4. **The CLI is dependency injected.** Callers provide a configured use case; a standalone
   production composition root is outside the current prototype interface.
5. **Only the renal-dose vertical slice is implemented.** Existing package names do not authorize an
   additional medication, population, renal method, interface, or clinical domain.

Compatibility exports preserve public imports without authorizing reverse dependencies.

## Cross-cutting constraints

- Preserve the prototype warning and use only synthetic or properly de-identified data.
- Do not fabricate missing values, convert ambiguous units, or silently infer clinical context.
- Use unrounded values for calculation, matching, and audit; round only for presentation.
- Do not read clinical content from services or rule evaluators.
- Do not place clinical logic in domain models, mappers, interfaces, or generic utilities.
- Do not expose patient identifiers, clinical payloads, exception messages, or tracebacks in
  diagnostic output.
- Prefer explicit composition over inheritance, metaprogramming, or a domain-specific language.
- Add abstractions only when the supported workflow demonstrates a concrete need.
