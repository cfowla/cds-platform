# CDS Platform Architecture

This document defines the stable architectural boundaries of the CDS Platform. It describes how components may interact, not the current implementation status or feature schedule. `PROJECT_CHARTER.md` remains authoritative for safety and scope, and `FIRST_VERTICAL_SLICE.md` defines the supported clinical workflow.

## Architectural principles

1. **Validate before computation.** Structural validity, clinical task sufficiency, explicit units, supported context, and internal consistency are checked before any calculation or rule matching occurs.
2. **Use typed domain objects.** Clinical facts and results cross internal boundaries as typed objects rather than unstructured dictionaries or interface-specific payloads.
3. **Keep domain models passive.** Domain models represent facts, concepts, and result structures. They contain no file access, network access, persistence, workflow orchestration, or clinical calculations.
4. **Keep services pure and deterministic.** Calculators and evaluators receive typed inputs and return typed outputs. They do not read files, call APIs, depend on hidden mutable state, or silently obtain the current time.
5. **Separate clinical content from logic.** Medication rules, thresholds, citations, versions, and review metadata are data. They are not embedded throughout calculation or orchestration code.
6. **Access content through repositories.** Repositories are the boundary for loading and validating clinical content. Services and rules do not read YAML or other files directly.
7. **Keep interfaces free of clinical logic.** CLI and other interface adapters collect input, invoke application use cases, and render output. They do not calculate, validate clinical sufficiency, or select recommendations.
8. **Return a standard structured result.** Every workflow produces an auditable result shape that distinguishes success, warnings, incomplete evaluation, unsupported context, and system failure.

## Dependency direction

Dependencies point inward toward stable domain types and pure logic:

```text
interfaces
  -> mappers
  -> app use cases
       -> validation
       -> repositories
       -> services
       -> rules
  -> domain
```

Lower-level modules must not import interface or application orchestration code. Domain modules must not import services, repositories, mappers, or interfaces.

## Processing flow

```text
external input
  -> input mapper
  -> typed input or domain objects
  -> structural and task-sufficiency validation
  -> application use case
       -> repository supplies versioned content
       -> service performs calculation
       -> rule matcher evaluates supported content
  -> structured evaluation result
  -> output mapper
  -> interface output
```

A critical validation issue stops the workflow before calculation or rule matching. Unsupported or insufficient cases return a structured non-success result and no dosing recommendation.

## Module responsibilities

### `domain`

Defines the stable vocabulary shared across the system:

- enums and constants;
- clinical fact models;
- shared value objects;
- traceability objects;
- recommendation, alert, and rule-result models; and
- typed domain exceptions when needed.

Domain objects preserve missing data explicitly. Unknown numeric values are `None`, not zero. Unknown categories use explicit unknown values where the distinction is clinically meaningful. Units, assumptions, warnings, evidence, and provenance remain visible.

### `validation`

Performs two kinds of checks:

- **structural validation:** required fields, types, units, ranges, timestamps, and internal consistency;
- **task-sufficiency validation:** whether the supplied information and context are adequate for the requested CDS operation.

Validation returns typed issues and results. Expected clinical gaps are represented as validation findings, warnings, incomplete results, or unsupported results rather than unhandled exceptions.

### `services`

Implements clinical calculations and deterministic evaluation logic. A service:

- accepts typed input;
- returns typed output;
- has no direct I/O;
- does not load content;
- does not mutate shared global state; and
- exposes all assumptions through inputs or results.

Rounding for display must not replace the unrounded value needed for reproducibility.

### `rules`

Performs simple, inspectable matching against validated, versioned content. Rule behavior must make boundary inclusivity explicit and detect missing, overlapping, or unreachable ranges. Prefer straightforward composition over a domain-specific language, metaclasses, or implicit magic.

### `content`

Stores versioned clinical guidance as data. Content records include the supported context, boundaries, recommendation, rationale, source citation, source version or publication date, content version, review metadata, and important limitations.

Content files do not execute logic.

### `repositories`

Load, parse, and validate clinical content and expose it through typed repository interfaces. Repositories isolate storage details from application and service code. File reads and future storage substitutions occur behind this boundary.

### `app`

Application use cases orchestrate a complete workflow. They control the sequence:

```text
validate -> load content -> calculate -> match rules -> assemble result
```

Use cases coordinate components but do not duplicate calculator formulas, rule predicates, repository parsing, or interface rendering.

### `mappers`

Convert between external representations and internal typed objects. Mappers make unit handling, missing-data behavior, identifiers, and serialization decisions explicit. They do not determine clinical recommendations.

### `interfaces`

Interfaces handle user or system interaction only. They gather input, call one application use case, and present the structured result. Clinical validation, calculations, rule matching, and content selection remain outside the interface layer.

## Structured output contract

A workflow result must preserve enough information to reproduce and audit the outcome. As applicable, it includes:

- outcome status;
- validated inputs and units;
- calculation method and implementation version;
- unrounded calculated value and display value;
- matched rule identifier and content version;
- recommendation and rationale;
- assumptions and warnings;
- evidence and source citations;
- provenance and evaluation timestamp; and
- structured error or validation issues.

Expected clinical gaps and unsupported cases are not system crashes. System failures are converted at the application boundary into structured failed results. User-facing output must not expose stack traces.

## Cross-cutting constraints

- No silent unit conversion, weight-method selection, indication inference, interpolation, or extrapolation.
- No direct clinical-content reads from services or rule evaluators.
- No clinical logic in mappers or interfaces.
- No hidden network calls or mutable global state in deterministic logic.
- Composition is preferred over inheritance.
- New abstractions must be justified by the supported workflow rather than hypothetical future features.
