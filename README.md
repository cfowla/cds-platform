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

## Development commands

Run these commands from the repository root. Python 3.11 or newer is required.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
python -m cds.interfaces.cli
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
python -m cds.interfaces.cli
```

The CLI module is currently a scaffold, so the final command exits without output until CLI behavior is implemented. In later sessions, reuse the environment by activating `.venv` and starting with the test command.
