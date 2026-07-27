# CDS Platform

A Python prototype for one auditable clinical decision-support vertical slice: adult Cockcroft–Gault creatinine-clearance calculation followed by limited renal-dose evaluation.

> **Prototype only — not for direct clinical use.** Use synthetic or properly de-identified cases. This repository does not authorize diagnosis, prescribing, medication-order verification, or patient-care use.
> **Deactivating repo for analysis and planning.**

## Scope

The first vertical slice is limited to a point-in-time adult Cockcroft–Gault creatinine-clearance calculation and versioned renal-dose evaluation for cefepime, piperacillin–tazobactam, and famotidine. The workflow fails closed when required data are missing, units are ambiguous, renal function is unstable, renal replacement therapy is present, or the medication, population, indication, formulation, or regimen is unsupported. See [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) for governing safety and scope requirements and [`FIRST_VERTICAL_SLICE.md`](FIRST_VERTICAL_SLICE.md) for the complete implementation contract.

## Repository map

Source code is organized by architectural layer under `src/cds/`, with unit, integration, and contract tests under `tests/`. See [`ARCHITECTURE.md`](ARCHITECTURE.md) for component responsibilities, dependency direction, and processing flow.

## Current status

See [`CURRENT.md`](CURRENT.md) for the active deliverable and next exact action.

## Governing documents

- [`PROJECT_CHARTER.md`](PROJECT_CHARTER.md) — governing safety and scope document
- [`FIRST_VERTICAL_SLICE.md`](FIRST_VERTICAL_SLICE.md) — supported workflow and implementation contract
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — stable component boundaries and dependency rules
- [`docs/SAFETY_INVARIANTS.md`](docs/SAFETY_INVARIANTS.md) — concise implementation safety checklist
- [`CURRENT.md`](CURRENT.md) — active deliverable and next exact action

## Development commands

Run these commands from the repository root. Python 3.11 or newer is required.

### Windows PowerShell

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
$env:PYTHONPATH = "src"
python examples/cli_walkthrough.py --verify
```

### macOS or Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m pytest -q
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

The renal-dose CLI is a dependency-injected interface boundary rather than a standalone composition root. See [`docs/CLI_WALKTHROUGH.md`](docs/CLI_WALKTHROUGH.md) for saved synthetic commands, canonical-output snapshots, exit behavior, and current limitations. Reuse the environment in later sessions by activating `.venv` and beginning with the test command.
