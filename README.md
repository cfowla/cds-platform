# CDS Platform

A Python prototype for one auditable clinical decision-support vertical slice: adult Cockcroft–Gault creatinine-clearance calculation followed by limited renal-dose evaluation.

> **Prototype only — not for direct clinical use.** Use synthetic or properly de-identified cases. This repository does not authorize diagnosis, prescribing, medication-order verification, or patient-care use.

## Frozen initial scope

The first feature is limited to:

- adults aged 18 years or older;
- a single point-in-time evaluation;
- stable serum creatinine supplied in `mg/dL`;
- a supplied body weight in kilograms with an explicit weight type;
- unindexed Cockcroft–Gault creatinine clearance in `mL/min`;
- explicit medication and regimen identifiers; and
- versioned renal-adjustment content for cefepime, piperacillin–tazobactam, and famotidine.

The workflow must fail closed when required data are missing, units are ambiguous, renal function is unstable, renal replacement therapy is present, or the medication, population, indication, formulation, or regimen is unsupported.

`PROJECT_CHARTER.md` is the governing safety and scope document. `FIRST_VERTICAL_SLICE.md` is the implementation contract. Open design decisions that are not required for the next domain-model task belong in `BACKLOG.md`, not in the active implementation scope.

## Active implementation path

```text
src/cds/domain/        # Enums, typed models, constants, and typed exceptions
src/cds/validation/    # Structural and renal-task sufficiency checks
src/cds/services/renal.py
                       # Pure Cockcroft–Gault calculation and renal workflow logic
src/cds/content/       # Versioned rules for the three supported medications
src/cds/repositories/  # Content-loading boundary
src/cds/rules/         # Simple, inspectable renal rule matching
src/cds/app/           # One renal-evaluation use case and DTOs
src/cds/mappers/       # Manual input and structured output mapping
src/cds/interfaces/cli.py
                       # Future non-production manual interface

tests/unit/            # Domain, validation, calculator, content, and boundary tests
tests/integration/     # Complete renal-evaluation flow
tests/contract/        # Serialized renal input/output shape
```

Anything outside this path is deferred. Do not add another calculator, medication set, clinical domain, API, EHR integration, alerting system, or production interface without a separately approved scope change.

## Development status

The package, strict pytest runner, smoke test, and renal-calculator placeholder are established. The next implementation task is the domain enum layer named in `FIRST_VERTICAL_SLICE.md`.

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

The CLI module is currently a scaffold and exits without output. Reuse the environment in later sessions by activating `.venv` and beginning with the test command.
