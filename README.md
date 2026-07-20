# CDS Platform

A Python clinical decision support platform scaffold organized around typed domain models, pure clinical services, simple rules, explicit validation, versioned content, and stable input/output boundaries.

## Architecture

```text
src/cds/
├── app/            # Use-case orchestration and DTOs
├── domain/         # Stable clinical models, enums, constants, exceptions
├── services/       # Pure clinical calculations and workflows
├── rules/          # Simple rule engine, registry, and predicates
├── content/        # Versioned guideline content, initially YAML
├── validation/     # Structural and task-sufficiency validation
├── repositories/   # Content and persistence boundaries
├── mappers/        # External-to-internal and internal-to-external mapping
├── interfaces/     # CLI, API, and EHR adapters
└── utils/          # Narrow shared utilities

tests/
├── unit/           # Mirrors src/cds architecture
├── integration/    # End-to-end application flows
└── contract/       # Input/output schema and boundary contracts
```

## Intended data flow

```text
input -> mapper -> DTO -> validation -> domain models -> use case
      -> repository -> service -> rules -> result -> mapper -> output
```

## Development status

This initial commit contains package scaffolding and deliberately skipped placeholder tests. Replace each placeholder with real behavior-focused tests as modules are implemented.

## Run tests

```bash
python -m pip install -e ".[dev]"
pytest
```
