# Synthetic CLI Walkthrough

> **Prototype only — not for direct clinical use.** Use only synthetic or properly
> de-identified data. These saved scenarios verify the dependency-injected CLI
> interface; they do not validate clinical content, dosing logic, or patient-care use.

## Purpose

Day 70 saves one reproducible interface walkthrough for each supported medication and
for incomplete, unsupported, content-failure, and system-failure behavior. The harness
injects deterministic canned use-case results into `cds.interfaces.cli.main()` because
the production CLI boundary intentionally does not select content or configure rules.

Saved request objects, canned structured results, canonical JSON snapshots, exit codes,
and required stderr fragments are in
[`examples/cli_walkthrough_cases.json`](../examples/cli_walkthrough_cases.json).

## Verify all saved scenarios

Run from the repository root.

### macOS or Linux

```bash
PYTHONPATH=src python examples/cli_walkthrough.py --verify
```

Expected output:

```text
7 synthetic CLI walkthrough scenarios verified.
```

### Windows PowerShell

```powershell
$env:PYTHONPATH = "src"
python examples/cli_walkthrough.py --verify
```

Expected output:

```text
7 synthetic CLI walkthrough scenarios verified.
```

## Run individual walkthroughs

Canonical JSON is written to stdout unless `--output` is supplied. `--summary` writes
presentation-only text to stderr without changing canonical JSON.

```bash
PYTHONPATH=src python examples/cli_walkthrough.py cefepime --summary
PYTHONPATH=src python examples/cli_walkthrough.py piperacillin_tazobactam --summary
PYTHONPATH=src python examples/cli_walkthrough.py famotidine --summary
PYTHONPATH=src python examples/cli_walkthrough.py incomplete --summary
PYTHONPATH=src python examples/cli_walkthrough.py unsupported --summary
PYTHONPATH=src python examples/cli_walkthrough.py content_failure --summary
PYTHONPATH=src python examples/cli_walkthrough.py system_failure --summary
```

To save one canonical output:

```bash
PYTHONPATH=src python examples/cli_walkthrough.py cefepime \
  --output /tmp/cefepime-walkthrough.json --summary
```

## Expected outcomes

| Scenario | Canonical status | Exit code | Recommendation |
|---|---:|---:|---|
| `cefepime` | `success` | `0` | Synthetic walkthrough recommendation |
| `piperacillin_tazobactam` | `success` | `0` | Synthetic walkthrough recommendation |
| `famotidine` | `success` | `0` | Synthetic walkthrough recommendation |
| `incomplete` | `incomplete` | `2` | None |
| `unsupported` | `failed` / `content_not_found` | `3` | None |
| `content_failure` | `failed` / content repository | `4` | None |
| `system_failure` | `failed` / system stage | `1` | None |

The exact canonical JSON for every row is stored in the corresponding `response` object
in `examples/cli_walkthrough_cases.json`. Verification compares the CLI output
byte-for-byte against deterministic canonical serialization of that saved object,
confirms the saved exit code, checks required sanitized stderr text, requires exactly
one configured use-case invocation, and confirms all fail-closed scenarios contain no
recommendation.

## Limitations

- Results are canned synthetic interface snapshots, not calculations from clinical
  content.
- The harness does not mark draft content reviewed or eligible for patient-care use.
- It does not replace unit, integration, contract, content, or independent clinical
  verification.
- It does not make `cds.interfaces.cli` a standalone production composition root.
